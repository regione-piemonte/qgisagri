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
from qgis.core import ( QgsFields,
                        QgsRectangle, 
                        QgsVectorLayer, 
                        QgsFeatureRequest,
                        QgsRenderContext,
                        QgsVectorDataProvider )
# 
#-----------------------------------------------------------    
class DeleteFeatureTool(QgsMapTool):
    
    featureDeleted = pyqtSignal(QgsVectorLayer)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, iface, multiselect=False):
        canvas = iface.mapCanvas()
        QgsMapTool.__init__(self, canvas)
        self.name = 'DeleteFeatureTool'
        self.canvas = canvas
        self.iface = iface
        self.selfeat = []
        self.multisel = False
        self.multiselect = multiselect
        self.layer = None
        self.cursor = QCursor(Qt.CrossCursor)
        self.initialize()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initialize(self, layer=None):
        self.layer = layer or self.canvas.currentLayer()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _deselect_all(self):
        self.selfeat = []
        self.layer.removeSelection()   
        if self.iface.mapCanvas().isCachingEnabled():
            self.layer.triggerRepaint()
        else:
            self.iface.mapCanvas().refresh()

    # --------------------------------------
    # 
    # --------------------------------------         
    def activate(self):
        self._deselect_all()
        self.canvas.setCursor(self.cursor)
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasPressEvent(self, e):
        """"Manage selection when clicking on the canvas."""
        if e.button() == Qt.LeftButton:
            # select features by pickpoint
            x = e.pos().x()
            y = e.pos().y()
            
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
            featuresIter = self.layer.getFeatures( featRequest )
            featuresId = [ feature.id() for feature in featuresIter ]
            featuresIter.close()  
            featuresId.reverse()
            
            # filter not visible features by style
            renderer = self.layer.renderer().clone()
            ctx = QgsRenderContext()
            renderer.startRender( ctx, QgsFields() )
            
            for fid in featuresId:
                if fid in self.selfeat:
                    self.selfeat.remove( fid )
                    break
                
                feature = self.layer.getFeature( fid )
                if renderer.willRenderFeature( feature, ctx ):
                    self.selfeat.append( fid )
                    if self.multiselect:
                        break
        
            renderer.stopRender( ctx )
            
            
            # update layer selection
            self.layer.selectByIds( self.selfeat )
         
            """
            multiselect = self.multiselect or self.multisel
         
            l_rect = canvas.mapSettings().mapToLayerCoordinates(self.layer, rect)
            self.layer.selectByRect(l_rect, QgsVectorLayer.AddToSelection if multiselect else False)
            feats = self.layer.selectedFeatures()
            self.selfeat = self.selfeat + feats
            """
        else:
            # check if selected features
            if not self.selfeat:
                return
            # remove selected features
            caps = self.layer.dataProvider().capabilities()
            if caps & QgsVectorDataProvider.DeleteFeatures:
                self.layer.beginEditCommand(self.name)    
                self.layer.deleteSelectedFeatures()
                self.layer.endEditCommand()
                self.featureDeleted.emit(self.layer) 
              
               
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasMoveEvent(self, event):
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasReleaseEvent(self, event):
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def keyPressEvent(self, e):
        self.multisel = ( e.key() == Qt.Key_Shift )
     
    # --------------------------------------
    # 
    # --------------------------------------      
    def keyReleaseEvent(self, e): 
        if e.key() == Qt.Key_Shift:
            self.multisel = False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deactivate(self):
        self._deselect_all()
        QgsMapTool.deactivate(self)

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
    
    