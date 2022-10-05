# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISAgri
                                 A QGIS plugin
 QGIS Agri Plugin
 Created by Sandro Moretti: sandro.moretti@ngi.it
                              -------------------
        begin                : 2019-06-07
        git sha              : $Format:%H$
        copyright            : (C) 2019 by CSI Piemonte
        email                : qgisagri@csi.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from qgis.gui import QgsMapTool
from qgis.core import ( QgsProject,
                        QgsRectangle,
                        #QgsGeometry,
                        QgsWkbTypes,
                        QgsFields,
                        QgsFeatureRequest,
                        QgsRenderContext,
                        QgsVectorLayerUtils )

from qgis_agri import agriConfig
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.gui.geometry_util import QGISAgriGeometry


# 
#-----------------------------------------------------------
class DissolveSuoliTool(QgsMapTool):
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, 
                 iface, 
                 layer, 
                 copyAttribs=None, 
                 holeMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO, 
                 snapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE, 
                 suoliSnapLayers=None,
                 msgTitle='QGIS Agri'):
        
        """ Constructor """
        super().__init__( iface.mapCanvas() )
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.layer = layer
        self.copyAttribs = copyAttribs
        self.holeMinArea = holeMinArea
        self.snapTolerance = snapTolerance
        self.suoliSnapLayers = suoliSnapLayers
        self.cursor = QCursor( Qt.CrossCursor )
        self.msgTitle = msgTitle
        self.selectedFeatureIds = []
        self.startFeatureId = None
        self.initialize( layer, copyAttribs )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __del__(self):
        """ Destructor """
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initialize(self, layer, copyAttribs=None):
        # init
        self.selectedFeatureIds = []
        self.startFeatureId = None
        self.layer = layer
        self.copyAttribs = copyAttribs
  
    # --------------------------------------
    # 
    # -------------------------------------- 
    def activate(self):
        # set cursor
        super().activate()
        self.canvas.setCursor( self.cursor )
        self.layer.removeSelection()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deactivate(self):
        super().deactivate()
        #self.canvas.unsetMapTool( self )

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isZoomTool(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isTransient(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isEditTool(self):
        return True

    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasPressEvent(self, event):
        pass

    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasMoveEvent(self, event):
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasReleaseEvent(self, event):
        """"Manage selection when clicking on the canvas."""
        
        # check end command
        if event.button() == Qt.RightButton:
            # dissolve selected features
            return self.dissolveFeatures() 
        
        # calculate selection retangle
        x = event.pos().x()
        y = event.pos().y()
        
        canvas = self.canvas
        coo_tranf = canvas.getCoordinateTransform()
        w = canvas.mapUnitsPerPixel() * 3
        rect = QgsRectangle(
            coo_tranf.toMapCoordinates(x-w, y-w),
            coo_tranf.toMapCoordinates(x+w, y+w) )
             
     
        # check if layer is visible
        layer = self.layer
        root = QgsProject.instance().layerTreeRoot()
        layNode = root.findLayer( layer.id() )
        if not layNode.isVisible():
            return
        
        # get features
        l_rect = canvas.mapSettings().mapToLayerCoordinates( layer, rect )
        featuresIter = layer.getFeatures( QgsFeatureRequest()
                                     .setFilterRect( l_rect )
                                     .setFlags( QgsFeatureRequest.ExactIntersect | QgsFeatureRequest.NoGeometry )
                                     .setNoAttributes() )
        
        # filter not visible features by style
        renderer = layer.renderer().clone()
        ctx = QgsRenderContext()
        renderer.startRender( ctx, QgsFields() )
        
        features = []
        for feature in featuresIter:
            feature = layer.getFeature( feature.id() )
            if renderer.willRenderFeature( feature, ctx ):
                features.append( feature )
    
        renderer.stopRender( ctx )
        featuresIter.close()
        
        # check if feature found
        if not features:
            return
        
        # find first new select feature
        fid = None
        selFeature = None
        for feat in features:
            if not feat.id() in self.selectedFeatureIds:
                selFeature = feat
                fid = feat.id()
                break
        
        # check selected feature geometry
        if not selFeature:
            return
        
        elif not self.selectedFeatureIds:
            # if first feature selected, 
            # store id and procede
            self.startFeatureId = fid
            
        elif not self.isJointFeature( selFeature ):
            # if feature is disjoint with the
            # already selected ones, does noting
            return
 
        # store feature found
        self.selectedFeatureIds.append( fid )
        
        # update layer selection
        layer.selectByIds( self.selectedFeatureIds )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def updateLayer(self):
        self.layer.removeSelection()
        if self.canvas.isCachingEnabled():
            self.layer.triggerRepaint()
        else:
            self.canvas.refresh()
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def resetSelection(self):
        # initilize members
        self.selectedFeatureIds = []
        self.startFeatureId = None
        # update
        self.updateLayer()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def isJointFeature(self, inFeature):
        """ Check if a feature geometry is joint to the stored ones """
        geom = inFeature.geometry()
        for fid in self.selectedFeatureIds:
            feat = self.layer.getFeature( fid )
            if not feat.geometry().disjoint( geom ):
                return True
        return False
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def repairHoles(self, geom):
        ringGeoms = QGISAgriGeometry.get_geometries_from_rings( geom )
        for partNum, part in enumerate(ringGeoms):
            for ringNum, ringGeom in enumerate(part):
                if ringNum == 0:
                    # skip geometry from exterior ring
                    continue
                
                # check if hole geometry area in tolerance
                area = ringGeom.area()
                if area < self.holeMinArea:
                    geom.deleteRing( ringNum, partNum )
                    return False, geom
                
        return True, geom
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def snapFeature(self, feat, suoliSnapLayers):
        """ """
        return QGISAgriLayers.snapFeature( suoliSnapLayers, 
                                           feat, 
                                           snapTolerance=self.snapTolerance )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def dissolveFeatures(self):
        """ Dissolve the selected features """
        
        # check num of selected features
        if len(self.selectedFeatureIds) < 2:
            self.updateLayer()
            return
        
        #
        suoliSnapLayers = None#QGISAgriLayers.get_vectorlayer( self.suoliSnapLayers )
        ##snapSubTolerance= agriConfig.TOLERANCES.VERTEX_TOLERANCE * 2
        
        # create union of geometries
        layer = self.layer
        fidLst = list( filter( lambda x : x != self.startFeatureId, self.selectedFeatureIds ) )
        mainFeat = layer.getFeature( self.startFeatureId )
        unionGeoms = self.snapFeature( mainFeat, suoliSnapLayers )
        for fid in fidLst:
            feature = layer.getFeature( fid )
            geom = self.snapFeature( feature, suoliSnapLayers )
            unionGeoms = unionGeoms.combine( geom )
            ##unionGeoms = unionGeoms.combine( QgsGeometry( geom ).buffer( agriConfig.TOLERANCES.CLEAN_VERTEX_TOLERANCE, 0 ) )
            ##unionGeoms = QGISAgriLayers.snapGeometry( unionGeoms, [geom], snapTolerance=snapSubTolerance )
        
        # check union geometry type
        if unionGeoms.type() != QgsWkbTypes.PolygonGeometry:
            logger.msgbar( logger.Level.Warning, 
                   self.tr( "Unione delle geometrie non possibile: controllare le singole geometrie" ),
                   title=self.msgTitle )
            # reset
            self.resetSelection()
            return 
           
        # remove small holes
        nLoops = 0
        res = False
        while not res and nLoops < 100:
            nLoops += 1
            res, unionGeoms = self.repairHoles( unionGeoms )
            
        
        # start command
        layer.beginEditCommand( 'dissolvesuoli' )
        try:
            # define new features attributes
            # add new feature
            attribBaseMap = QGISAgriLayers.map_attribute_values( mainFeat )
            attribSetMap = QGISAgriLayers.map_attribute_values( mainFeat, self.copyAttribs ) 
            attribSetMap = { **attribBaseMap, **attribSetMap }
       
            # create new feature
            newFeat = QgsVectorLayerUtils.createFeature( layer, geometry=unionGeoms, attributes=attribSetMap )   
            layer.addFeature( newFeat )
            
            # delete old features
            layer.deleteFeatures( self.selectedFeatureIds )
            
            # repair geometry
            QGISAgriLayers.repair_feature(layer, 
                                           newFeat, 
                                           attr_dict=None, 
                                           splitMultiParts=True,
                                           autoSnap=False,
                                           suoliMinArea=self.holeMinArea,
                                           suoliSnapTolerance=self.snapTolerance,
                                           suoliSnapLayerUris=None)
         
            # end command
            layer.endEditCommand()
            
        except Exception as e:
            # rollback command
            layer.destroyEditCommand()
            raise e
            
        finally:
            # reset
            self.resetSelection()
    
