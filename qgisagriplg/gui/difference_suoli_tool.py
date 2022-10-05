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
from PyQt5.QtGui import QCursor, QColor

from qgis.gui import ( QgsMapTool, 
                       QgsHighlight )
from qgis.core import ( QgsFields,
                        QgsRectangle, 
                        QgsGeometry, 
                        QgsFeatureRequest,
                        QgsRenderContext)

from qgis_agri import agriConfig, tr
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.gui.layer_util import QGISAgriLayers

# 
#-----------------------------------------------------------    
class DifferenceSuoliTool(QgsMapTool):
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, 
                 iface, 
                 layer, 
                 suoliRefLayers=None,
                 suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO, 
                 snapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE,
                 suoliSnapLayers=None,
                 msgTitle='QGIS Agri'):
        
        """ Constructor """
        super().__init__( iface.mapCanvas() )
        self.name = 'DifferenceSuoliTool'
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.layer = layer
        self.suoliRefLayers = suoliRefLayers
        self.suoliMinArea = suoliMinArea
        self.snapTolerance = snapTolerance
        self.suoliSnapLayers = suoliSnapLayers
        self.highlightGeoms = []
        self.cursor = QCursor(Qt.CrossCursor)
        self.msgTitle = msgTitle
        self.initialize( layer, suoliRefLayers )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initialize(self, layer, suoliRefLayers=None):
        self.layer = layer
        self.suoliRefLayers = suoliRefLayers
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def activate(self):
        super().activate()
        self._deselect_all()
        self.canvas.setCursor(self.cursor)
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def deactivate(self):
        super().deactivate()
        self._deselect_all()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasPressEvent(self, e):
        """"Manage selection when clicking on the canvas."""
        
        self.deleteHighlightGeoms()
        
        ##if e.button() != Qt.LeftButton:
        ##    return 
        
        # get selected feature
        selFeature = self._select_feature_by_point( e.pos() )
        if selFeature is None:
            return   
         
        # update feature geometry by diffeerence
        self._doDifference( selFeature )
              
               
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasMoveEvent(self, e):
        self.deleteHighlightGeoms()
        # get feature under cursor
        feature = self._select_feature_by_point( e.pos() )
        if feature is None:
            return
        # highlight feature geometry
        self.highlightGeom( feature.geometry() )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasReleaseEvent(self, e):
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def keyPressEvent(self, e):
        pass
     
    # --------------------------------------
    # 
    # --------------------------------------      
    def keyReleaseEvent(self, e): 
        pass

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
    def highlightGeom(self, geometry, color=None, fillColor=None, width=1):
        # init
        color = color or QColor( 255,0,0,255 ) 
        fillColor = fillColor or self.canvas.selectionColor() or QColor( 255,0,0,100 )
        fillColor.setAlpha(100) 
        # create highlight object
        h = QgsHighlight( self.canvas, geometry, self.layer ) 
        h.setColor( color )
        h.setWidth( width )
        h.setFillColor( fillColor )
        self.highlightGeoms.append( h )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteHighlightGeoms(self):
        for h in self.highlightGeoms:
            self.canvas.scene().removeItem( h )
        self.highlightGeoms = []
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _deselect_all(self):
        self.deleteHighlightGeoms()
        if self.iface.mapCanvas().isCachingEnabled():
            self.layer.triggerRepaint()
        else:
            self.iface.mapCanvas().refresh()
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _select_feature_by_point(self, po):
        """Get feature by point"""
        
        # init
        x = po.x()
        y = po.y()
        
        canvas = self.canvas
        coo_tranf = canvas.getCoordinateTransform()
        w = canvas.mapUnitsPerPixel() * 3
        rect = QgsRectangle(
            coo_tranf.toMapCoordinates(x-w, y-w),
            coo_tranf.toMapCoordinates(x+w, y+w)
        )
        rect.normalize()
        
        
        featRequest = QgsFeatureRequest()\
                             .setFilterRect( rect )\
                             .setFlags( QgsFeatureRequest.ExactIntersect | QgsFeatureRequest.NoGeometry )\
                             .setNoAttributes()
                             
        ##if self.selectionFilter is not None:
        ##    featRequest.setFilterExpression( str( self.selectionFilter ) )
        
        # get features
        selFeature = None
        featuresIter = self.layer.getFeatures( featRequest )
        featuresId = [ feature.id() for feature in featuresIter ]
        featuresIter.close()  
        featuresId.reverse()
        
        # filter not visible features by style
        renderer = self.layer.renderer().clone()
        ctx = QgsRenderContext()
        renderer.startRender( ctx, QgsFields() )
        
        for fid in featuresId:
            feature = self.layer.getFeature( fid )
            if renderer.willRenderFeature( feature, ctx ):
                selFeature = feature
                break
    
        renderer.stopRender( ctx )
        
        
        return selFeature
    
    # --------------------------------------
    # 
    # --------------------------------------
    def _doDifference(self, inFeature):
        """ Update feature geometry by difference with others """
        
        # init
        inGeometry = QgsGeometry( inFeature.geometry() )
        
        # list all difference layers
        cutLayers = [ self.layer ]
        cutLayers.extend(x for x in self.suoliRefLayers if x not in cutLayers)
        
        # loop over all difference layers
        nFeatFound = 0
        for layer in cutLayers: 
            # get features that insersect the input feature
            outFeats_ids = QGISAgriLayers.getFeaturesIdByGeom( layer, 
                                                               inGeometry, 
                                                               expression=None )
            
            # loop features for intersection\difference
            for fid in outFeats_ids:
                if fid == inFeature.id():
                    continue
                
                # get feature geometry
                feat = layer.getFeature( fid )
                featGeom = QgsGeometry( feat.geometry() )
                
                # check if there are intersections
                if not inGeometry.intersects( featGeom ):
                    continue
                
                # create difference feature
                inGeometry = inGeometry.difference( featGeom )
                if inGeometry.isEmpty():
                    logger.msgbar( logger.Level.Warning, 
                           tr( "Il suolo selezionato tende ad annullarsi: controllare le sovrapposizioni di geometrie" ),
                           title=self.msgTitle )
                    return 
                
                # increment counter
                nFeatFound += 1
                
        # check if difference found
        if nFeatFound == 0:
            return
            
        # start edit command   
        self.layer.beginEditCommand( 'DifferenceSuoliTool' )
        try:
            # update feature geometry
            inFeature.setGeometry( inGeometry )
            
            # repair geometry
            QGISAgriLayers.repair_feature(self.layer, 
                                           inFeature, 
                                           attr_dict=None, 
                                           splitMultiParts=True,
                                           autoSnap=False,
                                           suoliMinArea=self.suoliMinArea,
                                           suoliSnapTolerance=self.snapTolerance,
                                           suoliSnapLayerUris=None,
                                           addTopologicalPoints=True)
            
            
            # end edit command
            self.layer.endEditCommand()
            
        except Exception as e:
            self.layer.destroyEditCommand()
            raise e
        
        