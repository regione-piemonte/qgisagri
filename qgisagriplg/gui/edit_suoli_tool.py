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

# imports
from math import sqrt, sin, cos, pi, pow

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor, QColor, QPen, QBrush, QIcon
from PyQt5.QtWidgets import QMenu, QGraphicsTextItem

from qgis.PyQt.QtCore import pyqtSignal
from qgis.gui import ( QgsMapToolEdit, 
                       QgsRubberBand,
                       QgsHighlight,
                       QgsSnapIndicator )

from qgis.core import ( QgsApplication,
                        QgsWkbTypes,
                        QgsProject, 
                        QgsPointXY, 
                        QgsPoint,
                        QgsFields,
                        QgsGeometry,
                        QgsRenderContext,
                        QgsFeatureRequest )

from qgis_agri import agriConfig, tr
from qgis_agri.gui.layer_util import QGISAgriLayers

# 
#-----------------------------------------------------------
class SuoliEditTool(QgsMapToolEdit):
    
    captureChanged = pyqtSignal(int)
    operationChanged = pyqtSignal(object)
    
    from enum import Enum
    class operation(Enum):
        DRAW = 0
        MOVE = 5
        
    maxDistanceHitTest = 5
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, 
                 iface, 
                 layer, 
                 suoliRefLayers=None, 
                 copyAttribs=None,
                 suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO, 
                 snapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE, 
                 suoliSnapLayers=None):
        
        """ Constructor """
        super().__init__( iface.mapCanvas() )
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.scene = self.canvas.scene()
        self.currentOper = SuoliEditTool.operation.DRAW
        self.canAutoSelect = True
        self.canRedrawAreas = True
        self.lineClosed = False
        self.autoClosure = False
        self.rubberBand = None
        self.tempRubberBand = None
        self.tempRubberBandPol = None
        self.movingLineInitialPoint = None
        self.movingVertex = -1
        self.capturing = False
        self.capturedPoints = []
        self.labels = []
        self.vertices = []
        self.highlightGeoms = []
        self.layer = layer
        self.suoliRefLayers = suoliRefLayers
        self.copyAttribs = copyAttribs
        self.suoliMinArea = suoliMinArea
        self.snapTolerance = snapTolerance
        self.suoliSnapLayers = suoliSnapLayers
        self.selectedFeatures = None
        self.drawingLine = False
        self.cursor = None
        self.customCursor = None
        self.initialize( layer, suoliRefLayers, copyAttribs )
        
        self.snapIndicator = QgsSnapIndicator( self.canvas )
        self.snapper = self.canvas.snappingUtils()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def currentOperation(self):
        """ Returns current operation """
        return self.currentOper
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def isLineClosed(self):
        """ Returns true if closed cutting line """
        return self.lineClosed
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def defaultOperation(self):
        """ Returns default operation enum """
        return SuoliEditTool.operation.DRAW
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def emitCaptureChanged(self):
        self.captureChanged.emit( len(self.capturedPoints) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initialize(self, layer, suoliRefLayers=None, copyAttribs=None):
        self.layer = layer
        self.suoliRefLayers = suoliRefLayers
        self.copyAttribs = copyAttribs
        try:
            self.canvas.renderStarting.disconnect(self.mapCanvasChanged)
        except:
            pass
        self.canvas.renderStarting.connect(self.mapCanvasChanged)
        self.reset()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def reset(self):
        self.stopCapturing()
        self.currentOper = SuoliEditTool.operation.DRAW
        self.movingLineInitialPoint = None
        self.selectedFeatures = None
        self.rubberBand = None
        self.tempRubberBand = None
        self.tempRubberBandPol = None
        self.capturing = False
        self.lineClosed = False
        self.movingVertex = -1
        self.capturedPoints = []
        self.labels = []
        self.vertices = []
        self.highlightGeoms = []
        self.setEditCursor()
        self.emitCaptureChanged()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def activate(self):
        # set cursor
        self.setEditCursor()
        super().activate()
        self.layer.removeSelection()
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def deactivate(self):
        super().deactivate()
        self.stopCapturing()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def mapCanvasChanged(self):
        self.redrawAreas()
        if self.currentOper == SuoliEditTool.operation.MOVE :
            self.redrawVertices()   
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasMoveEvent(self, event):
        
        snapMatch = self.snapper.snapToMap( event.pos() )
        self.snapIndicator.setMatch( snapMatch )
        
        if self.currentOper == SuoliEditTool.operation.DRAW:
            if not self.capturing:
                pass
            
            elif self.tempRubberBand is None and \
                 self.tempRubberBandPol is None:
                pass
            
            elif self.lineClosed and not self.autoClosure:
                pass
            
            else:
                snapPos = self.toCanvasCoordinates( event.snapPoint () )
                pt = self.toMapCoordinates( snapPos )
                if self.tempRubberBand is not None:
                    self.tempRubberBand.movePoint( pt )
                if self.tempRubberBandPol is not None:
                    self.tempRubberBandPol.movePoint( pt )
                self.updateSelection( snapPos )
                
        if self.currentOper == SuoliEditTool.operation.MOVE:
            redraw = False
            
            if self.movingVertex >= 0:
                redraw = True
                snapPos = self.toCanvasCoordinates( event.snapPoint () )
                layerPoint = self.toLayerCoordinates( self.layer, snapPos )
                self.capturedPoints[self.movingVertex] = layerPoint
            
                if self.lineClosed and self.movingVertex == 0:
                    self.capturedPoints[len(self.capturedPoints) - 1] = layerPoint
                
            elif self.movingLineInitialPoint is not None:
                redraw = True
                currentPoint = self.toLayerCoordinates( self.layer, event.pos() )
                distance = self.distancePoint( currentPoint, self.movingLineInitialPoint )
                bearing = self.movingLineInitialPoint.azimuth( currentPoint )
                for i in range(len(self.capturedPoints)):
                    self.capturedPoints[i] = self.projectPoint( self.capturedPoints[i], distance, bearing )
                self.redraw()
                self.movingLineInitialPoint = currentPoint

            if redraw:
                self.updateSelection()
                self.redrawVertices()
                
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasPressEvent(self, event):
        
        if self.currentOper == SuoliEditTool.operation.MOVE:
            for i in range(len(self.capturedPoints)):
                point = self.toMapCoordinates( self.layer, self.capturedPoints[i] )
                currentVertex = self.toCanvasCoordinates( QgsPointXY( point.x(), point.y() ) )
                if self.distancePoint( event.pos(), currentVertex ) <= SuoliEditTool.maxDistanceHitTest:
                    self.movingVertex = i
                    break
                
        self.movingLineInitialPoint = self.toLayerCoordinates( self.layer, event.pos() )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasReleaseEvent(self, event):
        
        if event.button() == Qt.RightButton:
            if self.currentOper == SuoliEditTool.operation.DRAW:
                self.finishOperation()
                
            else:
                # create and show popup menu
                menu = QMenu()
                
                icon_path = ':/plugins/qgis_agri/images/action-split-add-vertex-icon.png'
                addVxAction = menu.addAction( QIcon( icon_path ), tr("Aggiungi vertice (doppio click)") )
                addVxAction.setEnabled( False )
                
                icon_path = ':/plugins/qgis_agri/images/action-split-del-vertex-icon.png'
                delVxAction = menu.addAction( QIcon( icon_path ), tr("Rimuovi vertice") )
                delVxAction.setEnabled( self.movingVertex >= 0 )
                
                lineCloseAction = None
                if not self.autoClosure:
                    actionText = tr( "Chiudi linea" )
                    icon_path = ':/plugins/qgis_agri/images/action-split-close-line-icon.png' 
                    if self.lineClosed:
                        actionText = tr( "Apri linea" )
                        icon_path = ':/plugins/qgis_agri/images/action-split-open-line-icon.png'  
                    lineCloseAction = menu.addAction( QIcon( icon_path ), actionText )
                
                menu.addSeparator()
                finishAction = menu.addAction( tr("Completa il comando") )
                
                action = menu.exec_( self.canvas.mapToGlobal( QPoint( event.pos().x()+5, event.pos().y()) ) )
                if action == finishAction:
                    self.finishOperation()
                elif action == delVxAction:
                    self.removeVertex( event.pos() )
                elif action == lineCloseAction:
                    self.lineClose( not self.lineClosed )
            
        elif event.button() == Qt.LeftButton:
            if self.currentOper == SuoliEditTool.operation.DRAW:
                if not self.lineClosed or self.autoClosure:
                    if not self.capturing:
                        self.startCapturing()
                        
                    snapPos = self.toCanvasCoordinates( event.snapPoint () )
                    self.addEndingVertex( snapPos )
       
        self.movingVertex = -1        
        self.movingLineInitialPoint = None
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasDoubleClickEvent(self, event):
        if self.currentOper == SuoliEditTool.operation.MOVE:
            self.addVertex( event.pos() )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.stopCapturing()
            
        if event.key() == Qt.Key_Delete: #or event.key() == Qt.Key_Backspace
            if self.currentOper == self.operation.DRAW:
                self.removeLastVertex()
                self.updateSelection()
                
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.finishOperation()
            
        if event.key() == Qt.Key_Shift:
            if self.currentOper == self.operation.MOVE:
                self.startOperation( self.operation.DRAW )
            else:
                self.startOperation( self.operation.MOVE )
            
        if event.key() == Qt.Key_C:
            self.lineClose()

        event.accept()     
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def startCapturing(self):
        self.drawingLine = True
        self.capturing = True
        self.prepareRubberBand()
        self.prepareTempRubberBand()
        ##self.updateSelection()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def stopCapturing(self):
        #self.layer.removeSelection()
        self.deleteLabels()
        self.deleteHighlightGeoms()
        self.deleteVertices()
        if self.rubberBand:
            self.canvas.scene().removeItem(self.rubberBand)
            self.rubberBand = None
        if self.tempRubberBand:
            self.canvas.scene().removeItem(self.tempRubberBand)
            self.tempRubberBand = None
        if self.tempRubberBandPol:
            self.canvas.scene().removeItem(self.tempRubberBandPol)
            self.tempRubberBandPol = None
        self.drawingLine = False
        self.capturing = False
        self.capturedPoints = []
        self.canvas.refresh()
        self.emitCaptureChanged()
    
   
    
    #-----------------------------------------------------------------------------------------------
    # DRAWING\SELECTION
    #-----------------------------------------------------------------------------------------------
    def updateSelection(self, lastPt=None):
        
        # check if auto selection needed
        if not self.canAutoSelect:
            # redraw selected areas
            self.redrawAreas( lastPt )
            return
        
        # init
        self.selectedFeatures = []
        selectedFeatures = self.selectedFeatures
        
        layer = self.layer
        layer.removeSelection()
        
        # check if layer is visible
        root = QgsProject.instance().layerTreeRoot()
        layNode = root.findLayer( layer.id() )
        if not layNode.isVisible():
            return
        
        # get cutter points
        cutterPoints = list(self.capturedPoints)
        if lastPt is not None:
            cutterPoints.append( self.toLayerCoordinates( layer, lastPt ) ) 
        if len(cutterPoints) < 2:
            return self.redrawAreas( lastPt )
        
        # select feature by captured points
        geomSel = QgsGeometry.fromPolylineXY( cutterPoints )
        bbRect = geomSel.boundingBox()
        
        bbRect.normalize()
        
        featuresIter = layer.getFeatures( QgsFeatureRequest()
                                         .setFilterRect( bbRect )
                                         .setFlags( QgsFeatureRequest.ExactIntersect | QgsFeatureRequest.NoGeometry )
                                         .setNoAttributes() )
        
        # filter invalid feature from selection
        renderer = layer.renderer().clone()
        ctx = QgsRenderContext()
        renderer.startRender( ctx, QgsFields() )
        for feature in featuresIter:
            feature = layer.getFeature( feature.id() )
            g = feature.geometry()
            if not g:
                # invalid geometry
                pass
            elif not renderer.willRenderFeature( feature, ctx ):
                # hidden geometry
                pass
            elif not geomSel.intersects(g):
                # not intersecting geometry
                pass
            else:
                selectedFeatures.append( feature.id() )
                

        renderer.stopRender(ctx)
        featuresIter.close()
            
        # redraw selected areas
        self.redrawAreas( lastPt )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def prepareRubberBand(self):
        color = QColor( "red" )
        color.setAlphaF( 0.78 )
        fillColor = QColor(255, 71, 25, 150)

        geomType = QgsWkbTypes.PolygonGeometry if self.autoClosure else QgsWkbTypes.LineGeometry
        self.rubberBand = QgsRubberBand( self.canvas, geomType )
        self.rubberBand.setWidth( 1 )
        self.rubberBand.setColor( color )
        self.rubberBand.setFillColor( fillColor )
        self.rubberBand.show()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def prepareTempRubberBand(self):
        color = QColor( "red" )
        color.setAlphaF( 0.78 )
        
        if self.autoClosure:
            fillColor = QColor(255, 71, 25, 150)
            self.tempRubberBandPol = QgsRubberBand( self.canvas, QgsWkbTypes.PolygonGeometry )
            self.tempRubberBandPol.setWidth( 1 )
            self.tempRubberBandPol.setColor( color )
            self.tempRubberBandPol.setLineStyle( Qt.DotLine )
            self.tempRubberBandPol.setFillColor( fillColor )
            self.tempRubberBandPol.show()
        else:
            # first temp rubber band
            self.tempRubberBand = QgsRubberBand( self.canvas, QgsWkbTypes.LineGeometry )
            self.tempRubberBand.setWidth( 1 )
            self.tempRubberBand.setColor( color )
            self.tempRubberBand.setLineStyle( Qt.DotLine )
            self.tempRubberBand.show()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def removeTempRubberBand(self):
        # remove first temp rubber band
        if self.tempRubberBand:
            self.canvas.scene().removeItem( self.tempRubberBand )
            self.tempRubberBand = None
        # remove second temp rubber band    
        if self.tempRubberBandPol:
            self.canvas.scene().removeItem( self.tempRubberBandPol )
            self.tempRubberBandPol = None
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def redraw(self, regenTempRb=False):
        if regenTempRb:
            # redraw first temp rubber band
            if self.tempRubberBand is not None:
                if self.autoClosure and self.lineClosed:
                    po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 2] )
                else:
                    po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 1] )
                self.tempRubberBand.reset( QgsWkbTypes.LineGeometry )
                self.tempRubberBand.addPoint( po )
                
            # redraw second temp rubber band
            if self.tempRubberBandPol is not None:
                self.tempRubberBandPol.reset( QgsWkbTypes.PolygonGeometry )
                po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 1] )
                self.tempRubberBandPol.addPoint( po )
                po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 2] )
                self.tempRubberBandPol.addPoint( po )
                po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 1] )
                self.tempRubberBandPol.addPoint( po )
                
        self.redrawAreas()
        if self.currentOper == SuoliEditTool.operation.MOVE:
            self.redrawVertices()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def redrawRubberBand(self):
        
        # redraw rubber band 
        self.canvas.scene().removeItem( self.rubberBand )
        self.prepareRubberBand()
        for i in range( len(self.capturedPoints) ):
            point = self.capturedPoints[i]
            if point.__class__ == QgsPoint:
                vertexCoord = self.toMapCoordinatesV2( self.layer, self.capturedPoints[i] )
                vertexCoord = QgsPointXY( vertexCoord.x(), vertexCoord.y() )
            else:
                vertexCoord = self.toMapCoordinates( self.layer, self.capturedPoints[i] )

            self.rubberBand.addPoint( vertexCoord )
         
        # redraw first temporary rubber band   
        if self.tempRubberBand is not None:
            self.canvas.scene().removeItem( self.tempRubberBand )
            self.canvas.scene().addItem( self.tempRubberBand )
            
        # redraw second temporary rubber band   
        if self.tempRubberBandPol is not None:
            self.canvas.scene().removeItem( self.tempRubberBandPol )
            self.canvas.scene().addItem( self.tempRubberBandPol )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def redrawAreas(self, lastPt=None):
        
        # check if can redar areas
        if not self.canRedrawAreas:
            # readraw rubber band
            self.redrawRubberBand()
            return
        
        # remove labels\highlights
        self.deleteLabels()
        self.deleteHighlightGeoms()
        if not self.selectedFeatures:
            self.redrawRubberBand()
            return

        # redraw areas
        if self.capturing and len(self.capturedPoints) > 0:
            proj = QgsProject.instance()
            layer = self.layer
            
            for i in range( len(self.selectedFeatures) ):
                feature = layer.getFeature( self.selectedFeatures[i] )
                geometry = QgsGeometry( feature.geometry() )
                cutterPoints = list(self.capturedPoints)
                
                if lastPt is not None:
                    cutterPoints.append(self.toLayerCoordinates( self.layer, lastPt ))

                result, newGeometries, topoTestPoints = geometry.splitGeometry( cutterPoints, proj.topologicalEditing() )
                numNewGeom = len(newGeometries)
                if newGeometries is not None and numNewGeom > 0:
                    # highlight geometry
                    self.highlightGeom( feature.geometry() )
                    # add area labels
                    self.addLabel( geometry )
                    for j in range( numNewGeom ):
                        self.addLabel( newGeometries[j] )
                               
                # readraw rubber band
                self.redrawRubberBand()
                    
    
    # --------------------------------------
    # 
    # --------------------------------------
    def setEditCursor(self):
        if self.customCursor is not None:
            self.setCursor( self.customCursor )
        else:
            self.setCursor( QCursor( QgsApplication.getThemeCursor( QgsApplication.CrossHair ) ) )
   
    
    #-----------------------------------------------------------------------------------------------
    # OPERATIONS
    #-----------------------------------------------------------------------------------------------
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def doOperation(self):
        raise NotImplementedError

    # --------------------------------------
    # 
    # -------------------------------------- 
    def startOperation(self, oper):
        # check if valid operation
        regenTempRb = False
        nPoints = len(self.capturedPoints)
        if oper == SuoliEditTool.operation.MOVE:
            if nPoints < 1:
                return False
            self.setCursor( QCursor( Qt.SizeAllCursor ) )
            self.canvas.scene().removeItem( self.tempRubberBand )
            self.canvas.scene().removeItem( self.tempRubberBandPol )
            regenTempRb = True
                    
        elif oper == SuoliEditTool.operation.DRAW:
            self.setEditCursor()
            oper = SuoliEditTool.operation.DRAW
            regenTempRb = True
            
        else:
            return
            
        self.currentOper = oper
        self.deleteVertices()
        self.redraw( regenTempRb=regenTempRb )
        self.operationChanged.emit( self.currentOper )
        return True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def finishOperation(self):
        # execute operation
        self.doOperation()
        self.stopCapturing()
        self.reset()
        self.startCapturing()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def lineClose(self, close=True):
        # check if auto close option
        if self.autoClosure:
            return
        
        regenTempRb = False
        if len(self.capturedPoints) < 3:
            return False
        
        elif self.lineClosed == close:
            return False
        
        elif close:
            self.capturedPoints.append( self.capturedPoints[0] )
            self.canvas.scene().removeItem( self.tempRubberBand )
            self.canvas.scene().removeItem( self.tempRubberBandPol )
            regenTempRb = True
            
        else:
            del self.capturedPoints[-1]
        
        self.lineClosed = close    
        self.redraw( regenTempRb=regenTempRb )
        self.emitCaptureChanged()
        return True
        
                
    #-----------------------------------------------------------------------------------------------
    # UTILITIES
    #-----------------------------------------------------------------------------------------------
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def lineMagnitude(self, x1, y1, x2, y2):
        return sqrt(pow((x2 - x1), 2) + pow((y2 - y1), 2))
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def distancePoint(self, eventPos, vertexPos):
        return sqrt( (eventPos.x() - vertexPos.x())**2 + (eventPos.y() - vertexPos.y())**2 )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def distancePointLine(self, px, py, x1, y1, x2, y2):
        magnitude = self.lineMagnitude(x1, y1, x2, y2)
    
        if magnitude < 0.00000001:
            distance = 9999
            return distance

        u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
        u = u1 / (magnitude * magnitude)

        if (u < 0.00001) or (u > 1):
            ix = self.lineMagnitude(px, py, x1, y1)
            iy = self.lineMagnitude(px, py, x2, y2)
            if ix > iy:
                distance = iy
            else:
                distance = ix
        else:
            ix = x1 + u * (x2 - x1)
            iy = y1 + u * (y2 - y1)
            distance = self.lineMagnitude(px, py, ix, iy)
    
        return distance
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def projectPoint(self, point, distance, bearing):
        rads = bearing * pi / 180.0
        dx = distance * sin(rads)
        dy = distance * cos(rads)
        return QgsPointXY( point.x() + dx, point.y() + dy )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def snapFeature(self, feat, suoliSnapLayers):
        """ """
        return QGISAgriLayers.snapFeature( suoliSnapLayers, 
                                           feat, 
                                           snapTolerance=self.snapTolerance )
        
    #-----------------------------------------------------------------------------------------------
    # HIGHLIGHT
    #-----------------------------------------------------------------------------------------------
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def highlightGeom(self, geometry, color=None, fillColor=None, width=5):
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
        
    #-----------------------------------------------------------------------------------------------
    # LABELS
    #-----------------------------------------------------------------------------------------------
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def addLabel(self, geometry):
        area = geometry.area()
        labelPoint = geometry.pointOnSurface().vertexAt( 0 )
        label = QGraphicsTextItem( "%.2f" % round(area,2) )
        label.setHtml(
            "<div style=\"color:#ffffff;background:#111111;padding:5px\">{0:.2f} m<sup>2</sup></div>".format( round(area,2) ) )
        point = self.toMapCoordinatesV2( self.layer, labelPoint )
        label.setPos( self.toCanvasCoordinates( QgsPointXY(point.x(), point.y()) ) )

        self.scene.addItem( label )
        self.labels.append( label )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteLabels(self):
        for i in range( len(self.labels) ):
            self.scene.removeItem( self.labels[i] )
        self.labels = []
        
    #-----------------------------------------------------------------------------------------------
    # VERTICIES
    #-----------------------------------------------------------------------------------------------
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def addEndingVertex(self, canvasPoint):
        # transform point
        mapPoint = self.toMapCoordinates( canvasPoint )
        layerPoint = self.toLayerCoordinates( self.layer, canvasPoint )
        
        # check if auto closure 
        if self.autoClosure:
            # check if closed
            numPoints = len(self.capturedPoints)
            if numPoints > 3:
                # remove last point
                self.rubberBand.removePoint( -1, doUpdate=False )
                del self.capturedPoints[-1]
                self.lineClosed = False
        
            # add captured point 
            doClosure = len(self.capturedPoints) >= 2
            self.rubberBand.addPoint( mapPoint, doUpdate=not doClosure )
            self.capturedPoints.append( layerPoint )
        
            # add closure point
            if doClosure:
                self.rubberBand.addPoint( self.rubberBand.getPoint(0) )
                self.capturedPoints.append( self.capturedPoints[0] )
                self.lineClosed = True
        else:
            # add captured point 
            self.rubberBand.addPoint( mapPoint )
            self.capturedPoints.append( layerPoint )
            

        # reset first temp rubber band
        if self.tempRubberBand is not None:
            self.tempRubberBand.reset( QgsWkbTypes.LineGeometry )
            self.tempRubberBand.addPoint( mapPoint )
        
        # reset second temp rubber band
        if self.tempRubberBandPol is not None:
            self.tempRubberBandPol.reset( QgsWkbTypes.PolygonGeometry )
            po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 1] )
            self.tempRubberBandPol.addPoint( po )
            po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 2] )
            self.tempRubberBandPol.addPoint( po )
            po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 1] )
            self.tempRubberBandPol.addPoint( po )
        
        # emit signal
        self.emitCaptureChanged()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def removeLastVertex(self):
        if not self.capturing: return

        # check num of points
        numPoints = len(self.capturedPoints)
        if numPoints < 1:
            return

        # check if auto closure 
        if self.autoClosure:
            # check if closed
            if numPoints > 3:
                # remove last point
                self.rubberBand.removePoint( -1, doUpdate=False )
                del self.capturedPoints[-1]
                self.lineClosed = False
            
            doClosure = len(self.capturedPoints) > 3    
            self.rubberBand.removePoint( -1, doUpdate=doClosure )
            del self.capturedPoints[-1]
            
            # add closure point
            if doClosure:
                self.rubberBand.addPoint( self.rubberBand.getPoint(0) )
                self.capturedPoints.append( self.capturedPoints[0] )
                self.lineClosed = True
        
        else:
            self.rubberBand.removePoint( -1 )
            del self.capturedPoints[-1]
            self.lineClosed = False        
        
        # reset first temp rubber band
        numPoints = len(self.capturedPoints)
        if self.tempRubberBand is not None:
            self.tempRubberBand.reset( QgsWkbTypes.LineGeometry )
            if numPoints > 0:
                po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 1] )
                self.tempRubberBand.addPoint( po )
        
        # reset second temp rubber band
        if self.tempRubberBandPol is not None:
            self.tempRubberBandPol.reset( QgsWkbTypes.PolygonGeometry )
            if numPoints > 0:
                po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 1] )
                self.tempRubberBandPol.addPoint( po )
                po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 2] )
                self.tempRubberBandPol.addPoint( po )
                po = self.toMapCoordinates( self.layer, self.capturedPoints[len(self.capturedPoints) - 1] )
                self.tempRubberBandPol.addPoint( po )
            
        
        self.emitCaptureChanged()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def addVertex(self, pos):
        newCapturedPoints = []
        for i in range(len(self.capturedPoints) - 1):
            newCapturedPoints.append(self.capturedPoints[i])
            vertex1 = self.toMapCoordinates(self.layer, self.capturedPoints[i])
            currentVertex1 = self.toCanvasCoordinates(QgsPointXY(vertex1.x(), vertex1.y()))
            vertex2 = self.toMapCoordinates(self.layer, self.capturedPoints[i + 1])
            currentVertex2 = self.toCanvasCoordinates(QgsPointXY(vertex2.x(), vertex2.y()))

            distance = self.distancePointLine(pos.x(), pos.y(), currentVertex1.x(), currentVertex1.y(), currentVertex2.x(), currentVertex2.y())
            if distance <= SuoliEditTool.maxDistanceHitTest:
                layerPoint = self.toLayerCoordinates(self.layer, pos)
                newCapturedPoints.append(layerPoint)

        newCapturedPoints.append(self.capturedPoints[len(self.capturedPoints) - 1])
        self.capturedPoints = newCapturedPoints

        self.redrawAreas()
        self.redrawVertices()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def removeVertex(self, pos):
        deletedFirst = False
        deletedLast = False
        newCapturedPoints = []
        for i in range(len(self.capturedPoints)):
            vertex = self.toMapCoordinates(self.layer, self.capturedPoints[i])
            currentVertex = self.toCanvasCoordinates(QgsPointXY(vertex.x(), vertex.y()))
            if not self.distancePoint(pos, currentVertex) <= SuoliEditTool.maxDistanceHitTest:
                newCapturedPoints.append(self.capturedPoints[i])
            elif i == 0:
                deletedFirst = True
            elif i == len(self.capturedPoints) - 1:
                deletedLast = True

        if deletedFirst or deletedLast:
            if self.autoClosure:
                return
            self.lineClosed = False

        self.capturedPoints = newCapturedPoints

        self.redrawAreas()
        self.redrawVertices()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def redrawVertices(self, regen=True):
        #
        if regen:
            self.deleteVertices()
        #
        for i in range(len(self.capturedPoints)):
            vertexc = self.toMapCoordinates(self.layer, self.capturedPoints[i])
            vertexCoords = self.toCanvasCoordinates(QgsPointXY(vertexc.x(), vertexc.y()))
            if i == self.movingVertex:
                vertex = self.scene.addRect(vertexCoords.x() - 5, vertexCoords.y() - 5, 10, 10, QPen(QColor("green")), QBrush(QColor("green")))
                self.vertices.append(vertex)
            elif i == len(self.capturedPoints) - 1 and self.movingVertex == 0 and self.lineClosed:
                vertex = self.scene.addRect(vertexCoords.x() - 5, vertexCoords.y() - 5, 10, 10, QPen(QColor("green")), QBrush(QColor("green")))
                self.vertices.append(vertex)
            else:
                vertex = self.scene.addRect(vertexCoords.x() - 4, vertexCoords.y() - 4, 8, 8, QPen(QColor("red")), QBrush(QColor("red")))
                self.vertices.append(vertex)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteVertices(self):
        for i in range(len(self.vertices)):
            self.scene.removeItem(self.vertices[i])
        self.vertices = []
        
 