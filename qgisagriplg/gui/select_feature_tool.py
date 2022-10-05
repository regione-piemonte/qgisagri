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

from qgis.PyQt.QtCore import pyqtSignal
from qgis.gui import QgsMapTool
from qgis.core import ( QgsProject,
                        #QgsTolerance,
                        QgsRectangle,
                        QgsFeatureSource,
                        QgsVectorLayer,
                        QgsFields,
                        QgsFeatureRequest,
                        QgsRenderContext )

# 
#-----------------------------------------------------------
class SelectFeatureTool(QgsMapTool):
    
    featureSelected = pyqtSignal(QgsVectorLayer,list,int)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, iface, layers, 
                 single=False,
                 singleClick=False,
                 unsetMapToolOnSelect=False, 
                 deselectOnStart=True,
                 onSelectFeature=None,
                 selectionFilter=None,
                 selMMTolerance=None):
        
        """ Constructor """
        super().__init__( iface.mapCanvas() )
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.layer_ids = [l.id() for l in layers if l]
        self.single = single
        self.singleClick = singleClick
        self.deselectOnStart = deselectOnStart
        self.cursor = QCursor( Qt.CrossCursor )
        self.unsetMapToolOnSelect = unsetMapToolOnSelect
        self.onSelectFeature = onSelectFeature
        self.selectionFilter = selectionFilter
        self.MMtolerance = selMMTolerance
        self.isDoubleClickEvent = False
       
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __del__(self):
        """ Destructor """
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onLayerWillBeRemoved(self, layer):
        if not self.isActive():
            return 
        
        if layer.id() in self.layer_ids:
            self.deactivate()
            self.canvas.unsetMapTool( self )
            self.iface.actionPan().trigger()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def deselect_all_layers(self):
        for layer in self.canvas.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()   
        self.canvas.refresh()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _send_result(self, layer, features, mouseBtn):
        #deactivate the select tool
        if self.unsetMapToolOnSelect:
            self.deactivate()
            self.canvas.unsetMapTool( self )
            self.iface.actionPan().trigger()
            
        # Do operations using selected features. Here we run a function
        self.featureSelected.emit( layer, 
                                   features if not self.single else [features[0]], 
                                   mouseBtn )
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initialize(self, layers, onSelectFeature=None):
        # disconnect signal
        for lay_id in self.layer_ids:
            layer = QgsProject.instance().mapLayer( lay_id )
            if layer is None:
                continue
            
            try:
                layer.willBeDeleted.disconnect( self.deactivate )
            except:
                pass
        try:
            if self.onSelectFeature:
                self.featureSelected.disconnect( self.onSelectFeature )
        except:
            pass
        
        # assign members    
        self.layer_ids = [l.id() for l in layers]
        self.onSelectFeature = onSelectFeature
        
        # connect signals
        for layer in layers:
            layer.willBeDeleted.connect( self.deactivate )
            
        if self.onSelectFeature is not None:
            self.featureSelected.connect( self.onSelectFeature ) 
  
    # --------------------------------------
    # 
    # -------------------------------------- 
    def activate(self):
        # set cursor
        self.canvas.setCursor( self.cursor )
        # init selection 
        if self.deselectOnStart:
            self.deselect_all_layers()
        else:
            # check if there are selected features
            for layer in self.canvas.layers():
                features = [ f for f in layer.getSelectedFeatures() ]
                if features:
                    return self._send_result( layer, features ) 

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
    
    """TEST
    # --------------------------------------
    # 
    # -------------------------------------- 
    def prepareRubberBand(self, geom):
        from PyQt5.QtGui import  QColor
        from qgis.gui import QgsRubberBand
        from qgis.core import QgsWkbTypes
        
        color = QColor( "red" )
        color.setAlphaF( 0.78 )
        fillColor = QColor(255, 71, 25, 150)

        geomType = QgsWkbTypes.LineGeometry
        self.rubberBand = QgsRubberBand( self.canvas, geomType )
        self.rubberBand.setWidth( 1 )
        self.rubberBand.setColor( color )
        self.rubberBand.setFillColor( fillColor )
        self.rubberBand.addGeometry( geom )
        self.rubberBand.show()
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasReleaseEvent(self, event):
        """"Manage selection when clicking on the canvas."""
        
        # check if double click event detected
        double_click = self.isDoubleClickEvent
        self.isDoubleClickEvent = False
        if double_click:
            # if double click event, skip second click
            return
        
        # init
        mouseBtn = int( event.button() )
        
        # calculate selection retangle
        x = event.pos().x()
        y = event.pos().y()
        
        canvas = self.canvas
        coo_tranf = canvas.getCoordinateTransform()
        
        root = QgsProject.instance().layerTreeRoot()
     
        for lay_id in self.layer_ids:
            vl_to_query = QgsProject.instance().mapLayer( lay_id )
            if vl_to_query is None:
                continue
            if vl_to_query.hasFeatures() == QgsFeatureSource.NoFeaturesAvailable:
                continue
             
            # check if layer is visible
            layNode = root.findLayer( vl_to_query.id() )
            if not layNode.isVisible():
                continue
            
            #
            if self.MMtolerance:
                fact = 1000.0 / self.canvas.scale() * 5.0
                ms = self.canvas.mapSettings()
                rc = QgsRenderContext.fromMapSettings( ms )
                w = self.MMtolerance * rc.scaleFactor() * rc.mapToPixel().mapUnitsPerPixel() * fact
            else:
                w = canvas.mapUnitsPerPixel() * 3
            
            rect = QgsRectangle(
                coo_tranf.toMapCoordinates(x-w, y-w),
                coo_tranf.toMapCoordinates(x+w, y+w) )
             
            # compose feature request 
            l_rect = canvas.mapSettings().mapToLayerCoordinates( vl_to_query, rect )
            
            """ TEST
            from qgis.core import QgsGeometry
            self.prepareRubberBand( QgsGeometry.fromRect( rect ) )
            """
            
            featRequest = QgsFeatureRequest()\
                                 .setFilterRect( l_rect )\
                                 .setFlags( QgsFeatureRequest.ExactIntersect | QgsFeatureRequest.NoGeometry )\
                                 .setNoAttributes()
                                 
            if self.selectionFilter is not None:
                featRequest.setFilterExpression( str( self.selectionFilter ) )
            
            # get features
            featuresIter = vl_to_query.getFeatures( featRequest )
            
            # filter not visible features by style
            renderer = vl_to_query.renderer().clone()
            ctx = QgsRenderContext()
            renderer.startRender( ctx, QgsFields() )
            
            features = []
            for feature in featuresIter:
                feature = vl_to_query.getFeature( feature.id() )
                if renderer.willRenderFeature( feature, ctx ):
                    features.append( feature )
        
            renderer.stopRender( ctx )
            featuresIter.close()  
            
            # check if features found
            if features:
                # send result
                self._send_result( vl_to_query, features, mouseBtn )
                return 
            
        # send result if single click
        if self.singleClick:
            self._send_result( None, [None], mouseBtn )
                    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasDoubleClickEvent(self, event):
        """"Manage double clicking on the canvas."""
        # catch double click event and accept
        self.isDoubleClickEvent = True
        event.accept()
    
              
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
    
    
