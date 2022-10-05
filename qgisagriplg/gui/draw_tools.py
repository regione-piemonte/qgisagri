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
from PyQt5.QtGui import QColor
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.gui import QgsMapToolCapture, QgsRubberBand
from qgis.core import (Qgis, QgsProject, QgsWkbTypes, QgsCsException, QgsGeometry, QgsFeature,
                       QgsPoint, QgsMultiPoint, QgsCurvePolygon,QgsPolygon, QgsVectorDataProvider)

from qgis_agri.gui.layer_util import QGISAgriLayers

# 
#-----------------------------------------------------------    
class MapToolDigitizeFeature(QgsMapToolCapture):
      
    digitizingCompleted = pyqtSignal(QgsFeature)
    digitizingFinished = pyqtSignal()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, iface, layer):
        """Constructor"""
        canvas = iface.mapCanvas()
        widget = iface.cadDockWidget()
        super().__init__(canvas, widget, QgsMapToolCapture.CaptureMode.CaptureNone)
        self.toolName = self.tr( "MapToolDigitizeFeature" )
        self.canvas = canvas
        self.iface = iface
        self.layer = layer
        self.__checkGeometryType = True
        self.iface.newProjectCreated.connect( self.stopCapturing )
        self.iface.projectRead.connect( self.stopCapturing )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __del__(self):
        self.iface.newProjectCreated.disconnect( self.stopCapturing ) #SMXX
        self.iface.projectRead.disconnect( self.stopCapturing ) #SMXX
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def checkGeometryType(self):
        """ Returns checkGeometryType flag"""
        return self.__checkGeometryType
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @checkGeometryType.setter 
    def checkGeometryType(self, checkGeometryType): 
        self.__checkGeometryType = checkGeometryType
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def digitized(self, f):
        self.digitizingCompleted.emit( f )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def checkGeom(self):
        return True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def clearChecks(self):
        pass
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def activate(self):
        super().activate()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def deactivate(self):
        self.stopCapturing()
        super().deactivate()
        self.digitizingFinished.emit()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def cadCanvasReleaseEvent(self,e):
                 
        provider = self.layer.dataProvider()
        layerWKBType = self.layer.wkbType()
                   
        # POINT CAPTURING
        if self.mode() == QgsMapToolCapture.CaptureMode.CapturePoint:
            if e.button() != Qt.LeftButton:
                return

            #check we only use this tool for point/multipoint layers
            if ( self.layer.geometryType() != QgsWkbTypes.PointGeometry and 
                 self.__checkGeometryType ):
                self.messageEmitted.emit( self.tr( "Wrong editing tool, cannot apply the 'capture point' tool on this vector layer" ), Qgis.Warning )
                return
            
            savePoint = QgsPoint() #point in layer coordinates
            isMatchPointZ = False
            try:
                fetchPoint = QgsPoint()
                res = self.fetchLayerPoint( e.mapPointMatch(), fetchPoint )
                if QgsWkbTypes.hasZ( fetchPoint.wkbType() ):
                    isMatchPointZ = True
        
                if res == 0:
                    if isMatchPointZ:
                        savePoint = fetchPoint
                    else:
                        savePoint = QgsPoint( fetchPoint.x(), fetchPoint.y() )
                else:
                    layerPoint = self.toLayerCoordinates( self.layer, e.mapPoint() )
                    if isMatchPointZ:
                        savePoint = QgsPoint( QgsWkbTypes.PointZ, layerPoint.x(), layerPoint.y(), fetchPoint.z() )
                    else:
                        savePoint = QgsPoint( layerPoint.x(), layerPoint.y() )
            
            except QgsCsException as cse:
                self.messageEmitted.emit( self.tr( "Cannot transform the point to the layers coordinate system" ), Qgis.Warning )
                return
            
            #only do the rest for provider with feature addition support
            #note that for the grass provider, this will return false since
            #grass provider has its own mechanism of feature addition
            if ( provider.capabilities() & QgsVectorDataProvider.AddFeatures ):
                f = QgsFeature( self.layer.fields() )

                g = None
                if layerWKBType == QgsWkbTypes.Point:
                    g = QgsGeometry( savePoint )
                
                elif ( not(QgsWkbTypes.isMultiType( layerWKBType )) and QgsWkbTypes.hasZ( layerWKBType ) ):
                    z = savePoint.z() if isMatchPointZ else self.defaultZValue()
                    g = QgsGeometry( savePoint.x(), savePoint.y(), z )
                
                elif ( QgsWkbTypes.isMultiType( layerWKBType ) and not(QgsWkbTypes.hasZ( layerWKBType )) ):
                    g = QgsGeometry.fromMultiPointXY( [savePoint] )
                
                elif ( QgsWkbTypes.isMultiType( layerWKBType ) and QgsWkbTypes.hasZ( layerWKBType ) ):
                    mp = QgsMultiPoint() 
                    z = savePoint.z() if isMatchPointZ else self.defaultZValue()
                    mp.addGeometry( QgsPoint( QgsWkbTypes.PointZ, savePoint.x(), savePoint.y(), z ) )
                    g = QgsGeometry( )
                    g.set( mp )
                
                else:
                    # if layer supports more types (mCheckGeometryType is false)
                    g = QgsGeometry( savePoint )
                
                if QgsWkbTypes.hasM( layerWKBType ):
                    g.get().addMValue()
                    
                f.setGeometry( g )
                f.setValid( True )
                
                # The snapping result needs to be added so it's available in the @snapping_results variable of default value etc. expression contexts
                self.addVertex( e.mapPoint(), e.mapPointMatch() )
                
                self.digitized( f )
                
                self.stopCapturing()
                
                # we are done with digitizing for now so instruct advanced digitizing dock to reset its CAD points
                self.cadDockWidget().clearPoints()

        
        # LINE AND POLYGON CAPTURING
        elif ( self.mode() == QgsMapToolCapture.CaptureMode.CaptureLine or 
               self.mode() == QgsMapToolCapture.CaptureMode.CapturePolygon ):
            
            #add point to list and to rubber band
            if e.button() == Qt.LeftButton:
                error = self.addVertex( e.mapPoint(), e.mapPointMatch() )
                if error == 1:
                    #current layer is not a vector layer
                    return
                
                elif error == 2:
                    #problem with coordinate transformation
                    self.messageEmitted.emit( self.tr( "Cannot transform the point to the layers coordinate system" ), Qgis.Warning )
                    return
                
                # check geometry
                if self.checkGeom():
                    self.clearChecks()
                
                self.startCapturing()
                
            elif e.button() == Qt.RightButton:
                # check geometry
                if not self.checkGeom():
                    return
                
                self.clearChecks()
                
                # End of string
                self.deleteTempRubberBand()
                
                #lines: bail out if there are not at least two vertices
                if ( self.mode() == QgsMapToolCapture.CaptureMode.CaptureLine and self.size() < 2 ):
                    self.stopCapturing()
                    return
                
                #polygons: bail out if there are not at least two vertices
                if ( self.mode() == QgsMapToolCapture.CaptureMode.CapturePolygon and self.size() < 3 ):
                    self.stopCapturing()
                    return
                
                if ( self.mode() == QgsMapToolCapture.CaptureMode.CapturePolygon ):
                    self.closePolygon()

                #create QgsFeature with wkb representation
                f = QgsFeature(self.layer.fields())

                #does compoundcurve contain circular strings?
                #does provider support circular strings?
                hasCurvedSegments = self.captureCurve().hasCurvedSegments()
                providerSupportsCurvedSegments = self.layer.dataProvider().capabilities() & QgsVectorDataProvider.CircularGeometries
                
                
                snappingMatchesList = []
                curveToAdd = None
                if ( hasCurvedSegments and providerSupportsCurvedSegments ):
                    curveToAdd = self.captureCurve().clone()
                    
                else:
                    curveToAdd = self.captureCurve().curveToLine()
                    snappingMatchesList = self.snappingMatches()
                    
                if ( self.mode() == QgsMapToolCapture.CaptureMode.CaptureLine ):
                    g = QgsGeometry( curveToAdd )
                    f.setGeometry( g )
                else:
                    poly = None
                    if ( hasCurvedSegments and providerSupportsCurvedSegments ):
                        poly = QgsCurvePolygon()
                        
                    else:
                        poly = QgsPolygon()
                    
                    poly.setExteriorRing( curveToAdd )
                    g = QgsGeometry( poly )
                    f.setGeometry( g )
            
                    featGeom = f.geometry()
                    avoidIntersectionsReturn = featGeom.avoidIntersections( QgsProject.instance().avoidIntersectionsLayers() )
                    f.setGeometry( featGeom )
                    if avoidIntersectionsReturn == 1:
                        #not a polygon type. Impossible to get there
                        pass
                        
                    if f.geometry().isEmpty(): #avoid intersection might have removed the whole geometry
                        self.messageEmitted.emit( self.tr( "The feature cannot be added because it's geometry collapsed due to intersection avoidance" ), Qgis.Critical )
                        self.stopCapturing()
                        return
                
                f.setValid( True )
                self.digitized(f)
                self.stopCapturing()
                

# 
#-----------------------------------------------------------                
class MapToolDigitizePolygon(MapToolDigitizeFeature):
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, iface, layer=None, initAttribs=None):
        """Constructor"""
        super().__init__( iface, layer )
        self.toolName = self.tr( "MapToolDigitizePolygon" )
        self.nerr = 0
        self.providerSupportsCurvedSegments = None
        self.initAttribs = initAttribs
        self.digitizingCompleted.connect( self.onDigitizingCompleted )
        self.initialize( layer, initAttribs )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initialize(self, layer=None, initAttribs=None):
        self.layer = layer or self.canvas.currentLayer()
        self.nerr = 0
        self.providerSupportsCurvedSegments = None
        self.initAttribs = initAttribs
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def activate(self):
        super(MapToolDigitizePolygon, self).activate()
        if self.layer is not None:
            self.providerSupportsCurvedSegments = self.layer.dataProvider().capabilities() & QgsVectorDataProvider.CircularGeometries
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def checkGeom(self):
        if not self.isCapturing():
            return True
        if self.size() < 3:
            return True
        # check geometry
        exteriorRing = self.captureCurve().curveToLine()
        exteriorRing.close()
        polygon = QgsPolygon()
        polygon.setExteriorRing( exteriorRing )
        g = QgsGeometry( polygon )
        errors = g.validateGeometry()
        if not errors:
            return True
        
        self.nerr = self.nerr +1
        
        # undo last point 
        self.undo()
        
        # emit message
        self.messageEmitted.emit( self.tr('Geometria con errori: rimosso ultimo punto battuto'), Qgis.Warning )
        
        return False
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def clearChecks(self):
        if self.nerr > 0:
            self.iface.messageBar().clearWidgets()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onDigitizingCompleted(self, feature):
        """Complete digitazing slot"""
        if feature is None:
            return
        
        # create a temporary rubber band
        rb = QgsRubberBand(self.canvas, True)
        color = QColor(255, 71, 25, 150)
        rb.setColor(color)
        rb.setFillColor(color)
        
        self.layer.beginEditCommand('MapToolDigitizePolygon')
        try:
            ####layer = QgsVectorLayer("Polygon?crs="+self.iface.mapCanvas().mapSettings().destinationCrs().authid()+"&field="+self.tr('Drawings')+":string(255)", name, "memory")
            #layer.startEditing()
            
            ###symbols = layer.renderer().symbols(QgsRenderContext())
            ###symbols[0].setColor(self.settings.getColor())
            self.layer.addFeature(feature)
            
            # set initial attibutes
            if self.initAttribs:
                QGISAgriLayers.change_attribute_values( self.layer, [feature], self.initAttribs )
            
            rb.setToGeometry( feature.geometry(), None )
            
            
            # show attribute form
            res = self.iface.openFeatureForm( self.layer, feature, showModal=True )
            rb.reset(True)
            if res:
                self.layer.endEditCommand()
            else:
                self.layer.destroyEditCommand()
    
            #layer.commitChanges()
        except Exception as e:
            self.layer.destroyEditCommand()
            raise e
            
        finally:
            self.canvas.scene().removeItem(rb)
            if self.iface.mapCanvas().isCachingEnabled():
                self.layer.triggerRepaint()
            else:
                self.iface.mapCanvas().refresh()
        