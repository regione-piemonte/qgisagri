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
from qgis.core import (QgsFeature,
                       #QgsFields,
                       QgsFeatureSink,
                       #QgsGeometry,
                       #QgsWkbTypes,
                       #QgsFeatureRequest,
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterFeatureSource,
                       #QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink)
# pylint: disable=import-error
from .algs.QgisAlgorithm import QgisAlgorithm

# 
#-----------------------------------------------------------
class ForceRHR(QgisAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    # --------------------------------------
    # 
    # -------------------------------------- 
    def tags(self):
        return self.tr('geometry,lines,polygons,convert').split(',')
    
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
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              self.tr('Input layer'), types=[QgsProcessing.TypeVector]))
        
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Force RHR'), QgsProcessing.TypeVectorPolygon))
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def name(self):
        return 'forcerighthandrule'
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def displayName(self):
        return self.tr('Force geometry Right Hand Rule')
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        fields = source.fields()

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               fields, source.wkbType(), source.sourceCrs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        features = source.getFeatures()
        feedback.setProgress(0)
        feedback.pushInfo(QCoreApplication.translate('ForceRHR', 'Processing geometries'))
        total = (100.0 / source.featureCount()) if source.featureCount() else 1
        for current, inFeat in enumerate(features):
            if feedback.isCanceled():
                break

            if inFeat.geometry():
                outFeat = QgsFeature()
                geom = inFeat.geometry().forceRHR()
                outFeat.setGeometry(geom)
                attrs = inFeat.attributes()
                outFeat.setAttributes(attrs)
                sink.addFeature(outFeat, QgsFeatureSink.FastInsert)
                
            feedback.setProgress(int(current * total))

        return {self.OUTPUT: dest_id}
    