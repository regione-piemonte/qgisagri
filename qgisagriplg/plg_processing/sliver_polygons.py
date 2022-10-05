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

__author__ = 'Sandro Moretti'
__date__ = 'August 2019'
__copyright__ = '(C) 2019 by CSI Piemonte'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProject,
                       #QgsFields,
                       QgsFeature,
                       QgsFeatureSink,
                       #QgsGeometry,
                       QgsWkbTypes,
                       #QgsFeatureRequest,
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterFeatureSource,
                       #QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink, 
                       QgsCoordinateTransform)
# pylint: disable=import-error
from .algs.QgisAlgorithm import QgisAlgorithm

# 
#-----------------------------------------------------------
class SliverPolygons(QgisAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    THICKNESS = 'THICKNESS'
    MINAREA = 'MINAREA'
    MAXAREA = 'MAXAREA'
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def tags(self):
        return self.tr('geometry,polygons,sliver').split(',')
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def group(self):
        return self.tr('Vector geometry')
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def groupId(self):
        return 'vectorgeometry'
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self):
        super().__init__()
        self._layerToMapUnits = 1
        self._layerToMapUnits2 = 1
        self._thickness = 20
        self._maxArea = 0
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input layer'), types=[QgsProcessing.TypeVectorPolygon]))
        
        self.addParameter(QgsProcessingParameterNumber(self.THICKNESS,
                                                       self.tr('Thickness (sliver polygons)'),
                                                       minValue=0, defaultValue=20, type=QgsProcessingParameterNumber.Double))
        
        self.addParameter(QgsProcessingParameterNumber(self.MINAREA,
                                                       self.tr('Min area'),
                                                       minValue=0, defaultValue=0, type=QgsProcessingParameterNumber.Double))
        
        self.addParameter(QgsProcessingParameterNumber(self.MAXAREA,
                                                       self.tr('Max area (sliver polygons)'),
                                                       minValue=0, defaultValue=0, type=QgsProcessingParameterNumber.Double))
        
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Sliver Polygons'), QgsProcessing.TypeVectorPolygon))
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def name(self):
        return 'sliverpolygons'
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def displayName(self):
        return self.tr('Find sliver polygons')
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        fields = source.fields()

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               fields, QgsWkbTypes.Polygon, source.sourceCrs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        
        self._thickness = self.parameterAsDouble(parameters, self.THICKNESS, context)
        minArea = self.parameterAsDouble(parameters, self.MINAREA, context)
        self._maxArea = self.parameterAsDouble(parameters, self.MAXAREA, context)
        self._layerToMapUnits = self._scaleFactor(source)
        self._layerToMapUnits2 = self._layerToMapUnits * self._layerToMapUnits

        features = source.getFeatures()
        feedback.setProgress(0)
        feedback.pushInfo(QCoreApplication.translate('Sliver Polygons', 'Processing geometries'))
        total = (100.0 / source.featureCount()) if source.featureCount() else 1
        for current, inFeat in enumerate(features):
            if feedback.isCanceled():
                break

            value = 0
            errMsg = None
            attrs = inFeat.attributes()
            geom = inFeat.geometry()
            if not inFeat.hasGeometry():
                pass
            
            elif geom.area() < minArea:
                errMsg = 'Little polygon'  
            
            elif self._checkThicknessThreshold(geom, value):
                errMsg = 'Sliver polygon'
                
            if errMsg is not None:
                outFeat = QgsFeature()
                outFeat.setGeometry(geom)
                outFeat.setAttributes(attrs)
                sink.addFeature(outFeat, QgsFeatureSink.FastInsert)
           
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _scaleFactor(self, sourceLayer):
        scaleFactor = 1.0
        if sourceLayer:
            p = QgsProject.instance()
            ct = QgsCoordinateTransform( sourceLayer.sourceCrs(), p.crs(), p )
            scaleFactor = ct.scaleFactor( sourceLayer.sourceExtent() )
        return scaleFactor
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _checkThicknessThreshold(self, geom, value):
        maxArea = self._maxArea / self._layerToMapUnits2
        bb = geom.boundingBox()
        maxDim = max( bb.width(), bb.height() )
        area = geom.area()
        value = ( maxDim * maxDim ) / area
        if ( maxArea > 0. and area > maxArea ):
            return False
        return value > self._thickness # the sliver threshold is actually a map unit independent number, just abusing QgsGeometryAreaCheck::mThresholdMapUnits to store it