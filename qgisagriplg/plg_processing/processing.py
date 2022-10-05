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
import os
import sys
import traceback

from PyQt5.QtCore import QCoreApplication

from qgis_agri.gui.layer_util import QGISAgriLayers

# pylint: disable=no-name-in-module,import-error
from qgis.core import (
    
    QgsProcessingException,
    QgsProcessingOutputVectorLayer,
    QgsProcessingOutputRasterLayer,
    QgsProcessingOutputMapLayer,
    QgsProcessingOutputMultipleLayers,
    
    QgsSettings,
    QgsProcessingContext,
    QgsFeatureRequest,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsExpressionContextScope,
    
    NULL, 
    
    Qgis, QgsProject, QgsProviderRegistry, QgsField, 
    QgsProcessingFeedback, QgsProcessingUtils, QgsMapLayer, 
    QgsWkbTypes,QgsMessageLog,QgsProcessingAlgorithm, QgsApplication, 
    QgsProcessingParameterFeatureSink, QgsProcessingParameterVectorDestination,
    QgsProcessingParameterRasterDestination,QgsProcessingOutputLayerDefinition 
)
from qgis.utils import iface

##################################################################################################

class QGISAgriSetting:

    """A simple config parameter that will appear on the config dialog.
    """
    STRING = 0
    FILE = 1
    FOLDER = 2
    SELECTION = 3
    FLOAT = 4
    INT = 5
    MULTIPLE_FOLDERS = 6

class QGISAgriProcessingConfig:
    
    RASTER_STYLE = 'RASTER_STYLE'
    VECTOR_POINT_STYLE = 'VECTOR_POINT_STYLE'
    VECTOR_LINE_STYLE = 'VECTOR_LINE_STYLE'
    VECTOR_POLYGON_STYLE = 'VECTOR_POLYGON_STYLE'
    FILTER_INVALID_GEOMETRIES = 'FILTER_INVALID_GEOMETRIES'
    USE_FILENAME_AS_LAYER_NAME = 'USE_FILENAME_AS_LAYER_NAME'
    
    settings = {}
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def getSetting(name, readable=False):
        if name in list(QGISAgriProcessingConfig.settings.keys()):
            v = QGISAgriProcessingConfig.settings[name].value
            try:
                if v == NULL:
                    v = None
            except:
                pass
            if QGISAgriProcessingConfig.settings[name].valuetype == QGISAgriSetting.SELECTION:
                if readable:
                    return v
                return QGISAgriProcessingConfig.settings[name].options.index(v)
            else:
                return v
        else:
            return None

class QGISAgriRenderingStyles:
    
    styles = {}
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def getStyle(algname, outputname):
        if algname in QGISAgriRenderingStyles.styles:
            if outputname in QGISAgriRenderingStyles.styles[algname]:
                return QGISAgriRenderingStyles.styles[algname][outputname]
        return None

##################################################################################################


class QGISAgriMessageBarProgress(QgsProcessingFeedback):
    pass

##################################################################################################

class QGISAgridataobjects:
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def createContext(feedback=None):
        """
        Creates a default processing context
        """
        context = QgsProcessingContext()
        context.setProject(QgsProject.instance())
        context.setFeedback(feedback)
    
        invalid_features_method = QGISAgriProcessingConfig.getSetting(QGISAgriProcessingConfig.FILTER_INVALID_GEOMETRIES)
        if invalid_features_method is None:
            invalid_features_method = QgsFeatureRequest.GeometryAbortOnInvalid
        context.setInvalidGeometryCheck(invalid_features_method)
    
        settings = QgsSettings()
        context.setDefaultEncoding(settings.value("/Processing/encoding", "System"))
    
        context.setExpressionContext(QGISAgridataobjects.createExpressionContext())
    
        return context
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def createExpressionContext():
        context = QgsExpressionContext()
        context.appendScope(QgsExpressionContextUtils.globalScope())
        context.appendScope(QgsExpressionContextUtils.projectScope(QgsProject.instance()))
    
        if iface and iface.mapCanvas():
            context.appendScope(QgsExpressionContextUtils.mapSettingsScope(iface.mapCanvas().mapSettings()))
    
        processingScope = QgsExpressionContextScope()
    
        if iface and iface.mapCanvas():
            extent = iface.mapCanvas().fullExtent()
            processingScope.setVariable('fullextent_minx', extent.xMinimum())
            processingScope.setVariable('fullextent_miny', extent.yMinimum())
            processingScope.setVariable('fullextent_maxx', extent.xMaximum())
            processingScope.setVariable('fullextent_maxy', extent.yMaximum())
    
        context.appendScope(processingScope)
        return context


##################################################################################################

class QGISAgriBaseProcessing:
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def tr(string, context=''):
        if context == '':
            context = 'Processing'
        return QCoreApplication.translate(context, string)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def execute(alg, parameters, context=None, feedback=None):
        """Executes a given algorithm, showing its progress in the
        progress object passed along.
    
        Return true if everything went OK, false if the algorithm
        could not be completed.
        """
    
        if feedback is None:
            feedback = QgsProcessingFeedback()
        if context is None:
            context = QGISAgridataobjects.createContext(feedback)
    
        try:
            results, ok = alg.run(parameters, context, feedback)
            return ok, results
        except QgsProcessingException as e:
            QgsMessageLog.logMessage(str(sys.exc_info()[0]), 'Processing', Qgis.Critical)
            if feedback is not None:
                feedback.reportError(e.msg)
            return False, {}
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def runAlgorithm(algOrName, parameters, onFinish=None, feedback=None, context=None):
        if isinstance(algOrName, QgsProcessingAlgorithm):
            alg = algOrName
        else:
            alg = QgsApplication.processingRegistry().createAlgorithmById(algOrName)

        if feedback is None:
            feedback = QgsProcessingFeedback()

        if alg is None:
            msg = QGISAgriBaseProcessing.tr('Error: Algorithm {0} not found\n').format(algOrName)
            feedback.reportError(msg)
            raise QgsProcessingException(msg)

        if context is None:
            context = QGISAgridataobjects.createContext(feedback)

        if context.feedback() is None:
            context.setFeedback(feedback)

        ok, msg = alg.checkParameterValues(parameters, context)
        if not ok:
            msg = QGISAgriBaseProcessing.tr('Unable to execute algorithm\n{0}').format(msg)
            feedback.reportError(msg)
            raise QgsProcessingException(msg)

        if not alg.validateInputCrs(parameters, context):
            feedback.pushInfo(
                QGISAgriBaseProcessing.tr('Warning: Not all input layers use the same CRS.\nThis can cause unexpected results.'))

        ret, results = QGISAgriBaseProcessing.execute(alg, parameters, context, feedback)
        if ret:
            feedback.pushInfo(
                QGISAgriBaseProcessing.tr('Results: {}').format(results))

            if onFinish is not None:
                onFinish(alg, context, feedback)
            else:
                # auto convert layer references in results to map layers
                for out in alg.outputDefinitions():
                    if out.name() not in results:
                        continue

                    if isinstance(out, (QgsProcessingOutputVectorLayer, QgsProcessingOutputRasterLayer, QgsProcessingOutputMapLayer)):
                        result = results[out.name()]
                        if not isinstance(result, QgsMapLayer):
                            layer = context.takeResultLayer(result) # transfer layer ownership out of context
                            if layer:
                                results[out.name()] = layer # replace layer string ref with actual layer (+ownership)
                    elif isinstance(out, QgsProcessingOutputMultipleLayers):
                        result = results[out.name()]
                        if result:
                            layers_result = []
                            for l in result:
                                if not isinstance(result, QgsMapLayer):
                                    layer = context.takeResultLayer(l) # transfer layer ownership out of context
                                    if layer:
                                        layers_result.append(layer)
                                    else:
                                        layers_result.append(l)
                                else:
                                    layers_result.append(l)

                            results[out.name()] = layers_result # replace layers strings ref with actual layers (+ownership)

        else:
            msg = QGISAgriBaseProcessing.tr("There were errors executing the algorithm.")
            feedback.reportError(msg)
            raise QgsProcessingException(msg)

        if isinstance(feedback, QGISAgriMessageBarProgress):
            feedback.close()
        return results

# 
#-----------------------------------------------------------
class QGISAgriProcessing:
    """Processing class."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, toc_grp_name="ERRORI"):
        """Constructor."""
        self._toc_grp_name = toc_grp_name
        self._destLayer = None
        self._deleteOldFeature = False
        self._loadInToc = True
        self._readonly = False
        self._groupToc = None
        self._indexToc = 0
        self._alias = None
        self._resultsAsErrors = False
        self._num_err = 0
        self._storeTmpIdLayers = []
        self._renameFields = {}
        self._resLayerId = None
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def hasErrors(self):
        return self._num_err > 0 
    
    
    # --------------------------------------
    # 
    # --------------------------------------
    def default_processing_context(self):
        """Returns a default processing context"""
        feedback = QgsProcessingFeedback()            
        context = QGISAgridataobjects.createContext( feedback )
        context.setInvalidGeometryCheck( QgsFeatureRequest.GeometryAbortOnInvalid )
        return context
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _set_layer_name(self, layer, context_layer_details):
        """
        Sets the name for the given layer, either using the layer's file name
        (or database layer name), or the name specified by the parameter definition.
        """
        if self._alias is None:
            lay_name = "{0}__{1}".format( layer.name(), context_layer_details.name )
            
        elif not self._alias:
            lay_name = layer.name()
               
        else:
            lay_name = "{0}__{1}".format( layer.name(), self._alias )
        
        use_filename_as_layer_name = QGISAgriProcessingConfig.getSetting(QGISAgriProcessingConfig.USE_FILENAME_AS_LAYER_NAME)
        
        if use_filename_as_layer_name or not context_layer_details.name:
            source_parts = QgsProviderRegistry.instance().decodeUri(layer.dataProvider().name(), layer.source())
            layer_name = source_parts.get('layerName', '')
            
            # if source layer name exists, use that -- else use
            if layer_name:
                layer.setName(layer_name)
            else:
                path = source_parts.get('path', '')
                
                if path:
                    layer.setName(os.path.splitext(os.path.basename(path))[0])
                elif context_layer_details.name:
                    # fallback to parameter's name -- shouldn't happen!
                    layer.setName(lay_name)
        else:
            layer.setName(lay_name)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _adjustOutputLayer(self, outLayer, destLayer):
        """Adjust processing output layer for feature import in other layer"""
        badattributeList = []
        destProvider = destLayer.dataProvider()
        outProvider = outLayer.dataProvider()
        outattributeList = outProvider.fields().toList()
        for attrib in outattributeList:
            if destProvider.fieldNameIndex(attrib.name())==-1:
                badattributeList.append(QgsField(attrib.name(),attrib.type()))
                
        outProvider.deleteAttributes(badattributeList)
        outLayer.updateFields()
        return outLayer
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _importAlgorithmResults(self, alg, context, feedback=None, showResults=True):
        """ """
        # check if defined a destination layer, else import result as different layers
        if self._destLayer is None: 
            return self._handleAlgorithmResults(alg, context, feedback=feedback, showResults=showResults)
        destLayer = self._destLayer
        
        # check if more of one layer result
        if len(context.layersToLoadOnCompletion()) > 1:
            # import processing results as new layers
            return self._handleAlgorithmResults(alg, context, feedback=feedback, showResults=showResults)
        
        # init
        wrongLayers = []
        if feedback is None:
            feedback = QgsProcessingFeedback()
        feedback.setProgressText(QCoreApplication.translate('Postprocessing', 'Loading resulting layers'))
        i = 0
         
        # loop result: MUST BE ONLY ONE (?)
        for l, details in context.layersToLoadOnCompletion().items():
            if feedback.isCanceled():
                return False
            
            if len(context.layersToLoadOnCompletion()) > 2:
                # only show progress feedback if we're loading a bunch of layers
                feedback.setProgress(100 * i / float(len(context.layersToLoadOnCompletion())))
    
            try:
                outLayer = QgsProcessingUtils.mapLayerFromString(l, context, typeHint=details.layerTypeHint)
                if outLayer is None:
                    wrongLayers.append(str(l))
                    
                elif outLayer.type() == QgsMapLayer.VectorLayer and outLayer.featureCount() == 0:
                    pass
                
                elif outLayer.type() != destLayer.type():
                    # need conversion?
                    pass
                
                #elif outLayer.geometryType() != destLayer.geometryType(): ???
                    
                else:
                    # correct output layer fields
                    self._adjustOutputLayer(outLayer, destLayer)
                    
                    # import feature form result layer to destination layer
                    try:
                        # collect new features from result layer
                        cfeatures = [feat for feat in outLayer.getFeatures()]
                        # start edit mode on destination layer
                        destLayer.startEditing()
                        # remove old features from destination layer
                        if self._deleteOldFeature:
                            listOfIds = [feat.id() for feat in destLayer.getFeatures()]
                            destLayer.deleteFeatures( listOfIds )
                        # add new feature in destination layer
                        destLayer.addFeatures(cfeatures)
                        # commit changes
                        destLayer.commitChanges()
                        
                    except Exception as e:
                        destLayer.rollBack()
                        raise e
                    
                    if details.postProcessor():
                        details.postProcessor().postProcessLayer(outLayer, context, feedback)
    
            except Exception:
                QgsMessageLog.logMessage(QCoreApplication.translate('Postprocessing', "Error loading result layer:") + "\n" + traceback.format_exc(), 'Processing', Qgis.Critical)
                wrongLayers.append(str(l))
            i += 1
                
        feedback.setProgress(100)
    
        if wrongLayers:
            msg = QCoreApplication.translate('Postprocessing', "The following layers were not correctly generated.")
            msg += "<ul>" + "".join(["<li>%s</li>" % lay for lay in wrongLayers]) + "</ul>"
            msg += QCoreApplication.translate('Postprocessing', "You can check the 'Log Messages Panel' in QGIS main window to find more information about the execution of the algorithm.")
            feedback.reportError(msg)
    
        # check if errors
        if len(wrongLayers) > 0:
            self._num_err = self._num_err + 1
            return False
         
        return True
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _handleAlgorithmResults(self, alg, context, feedback=None, showResults=True):
        """ """
        # init
        wrongLayers = []
        if feedback is None:
            feedback = QgsProcessingFeedback()
        feedback.setProgressText(QCoreApplication.translate('Postprocessing', 'Loading resulting layers'))
        i = 0
        
        # loop result layers
        for l, details in context.layersToLoadOnCompletion().items():
            if feedback.isCanceled():
                return False
            
            if len(context.layersToLoadOnCompletion()) > 2:
                # only show progress feedback if we're loading a bunch of layers
                feedback.setProgress(100 * i / float(len(context.layersToLoadOnCompletion())))
    
            try:
                layer = QgsProcessingUtils.mapLayerFromString(l, context, typeHint=details.layerTypeHint)
                if layer is None:
                    wrongLayers.append(str(l))
                    
#                 elif layer.type() == QgsMapLayer.VectorLayer and layer.featureCount() == 0:
#                     pass
                    
                else:
                    # check if empty result layer
                    loadInToc = self._loadInToc
                    if layer.type() == QgsMapLayer.VectorLayer and layer.featureCount() == 0:
                        loadInToc = False
                                      
                    
                    ########num_err = num_err + layer.featureCount()
                    self._set_layer_name(layer, details)
                    style = None
                    if details.outputName:
                        style = QGISAgriRenderingStyles.getStyle(alg.id(), details.outputName)
                    if style is None:
                        if layer.type() == QgsMapLayer.RasterLayer:
                            style = QGISAgriProcessingConfig.getSetting(QGISAgriProcessingConfig.RASTER_STYLE)
                        else:
                            if layer.geometryType() == QgsWkbTypes.PointGeometry:
                                style = QGISAgriProcessingConfig.getSetting(QGISAgriProcessingConfig.VECTOR_POINT_STYLE)
                            elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                                style = QGISAgriProcessingConfig.getSetting(QGISAgriProcessingConfig.VECTOR_LINE_STYLE)
                            else:
                                style = QGISAgriProcessingConfig.getSetting(QGISAgriProcessingConfig.VECTOR_POLYGON_STYLE)
                    if style:
                        layer.loadNamedStyle(style)
                    
                    # rename fields
                    renameFields = self._renameFields or {}
                    if renameFields:
                        provider = layer.dataProvider()
                        layer.startEditing()
                        for oldFldName, newFldName in renameFields.items():
                            index = provider.fieldNameIndex( oldFldName )
                            if index != -1:
                                layer.renameAttribute( index, newFldName )
                        layer.commitChanges()
    
                    # add layer in current project
                    vlayer = details.project.addMapLayer(context.temporaryLayerStore().takeMapLayer(layer), addToLegend=False)
                    vlayer.setReadOnly( self._readonly )
                    self._resLayerId = vlayer.id()
                    
                    # load layer in toc
                    if loadInToc:
                        # check if group node exists
                        root_node = grp_node = QgsProject.instance().layerTreeRoot()
                        tocGroup = self._groupToc if self._groupToc is not None else self._toc_grp_name
                        _, grp_node = QGISAgriLayers.create_toc_group_path( tocGroup, root_node, 0 )
                    
                        grp_node.insertLayer(self._indexToc, vlayer)
                    else:
                        self._storeTmpIdLayers.append( vlayer.id() )
                    
                    
                    # 
                    if self._resultsAsErrors:
                        self._num_err = self._num_err + 1
                    
                    if details.postProcessor():
                        details.postProcessor().postProcessLayer(layer, context, feedback)
    
            except Exception:
                QgsMessageLog.logMessage(QCoreApplication.translate('Postprocessing', "Error loading result layer:") + "\n" + traceback.format_exc(), 'Processing', Qgis.Critical)
                wrongLayers.append(str(l))
            i += 1
                
        feedback.setProgress(100)
    
        if wrongLayers:
            msg = QCoreApplication.translate('Postprocessing', "The following layers were not correctly generated.")
            msg += "<ul>" + "".join(["<li>%s</li>" % lay for lay in wrongLayers]) + "</ul>"
            msg += QCoreApplication.translate('Postprocessing', "You can check the 'Log Messages Panel' in QGIS main window to find more information about the execution of the algorithm.")
            feedback.reportError(msg)
    
        # check if errors
        if len(wrongLayers) > 0:
            self._num_err = self._num_err + 1
            return False
         
        return True
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _run(self, algOrName, parameters, onFinish=None, feedback=None, context=None, row=None):
        """Executes given algorithm and call requested results handler."""
        
        QgsMessageLog.logMessage( '{0}: {1}{2}'.format(
                                        QCoreApplication.translate('Postprocessing', "Execute processing"), 
                                        '' if row is None else '{}) '.format( row ),
                                        algOrName ), 
                                  'Processing', 
                                  Qgis.Info)
        
        
        #init
        self._resLayerId = None
        self._num_err = 0
        if isinstance(algOrName, QgsProcessingAlgorithm):
            alg = algOrName
        else:
            alg = QgsApplication.processingRegistry().createAlgorithmById(algOrName)
            
        if alg is None:
            msg = QCoreApplication.translate( 'Postprocessing', "Algoritmo di processing non reperito: '{0}'".format( algOrName ) )
            raise Exception( msg )
    
        # output destination parameters to point to current project
        for param in alg.parameterDefinitions():
            if not param.name() in parameters:
                continue
    
            if isinstance(param, (QgsProcessingParameterFeatureSink, QgsProcessingParameterVectorDestination, QgsProcessingParameterRasterDestination)):
                p = parameters[param.name()]
                if not isinstance(p, QgsProcessingOutputLayerDefinition):
                    parameters[param.name()] = QgsProcessingOutputLayerDefinition(p, QgsProject.instance())
                else:
                    p.destinationProject = QgsProject.instance()
                    parameters[param.name()] = p
                    
        # pylint: disable=no-member
        if onFinish: ##or not is_child_algorithm: TODO
            return QGISAgriBaseProcessing.runAlgorithm(alg, parameters, onFinish, feedback, context)
        else:
            # for child algorithms, we disable to default post-processing step where layer ownership
            # is transferred from the context to the caller. In this case, we NEED the ownership to remain
            # with the context, so that further steps in the algorithm have guaranteed access to the layer.
            def post_process(_alg, _context, _feedback):
                return
    
            return QGISAgriBaseProcessing.runAlgorithm(algOrName, parameters, onFinish=post_process, feedback=feedback, context=context)
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def runAndImport(self, 
                     algOrName, 
                     parameters, 
                     destLayer, 
                     deleteOldFeature=True,
                     feedback=None, 
                     context=None):
        """Executes given algorithm and import resulting features in existing layer"""
        self._destLayer = destLayer
        self._deleteOldFeature = deleteOldFeature
        self._resultsAsErrors = False
        self._loadInToc = False
        self._indexToc = 0
        self._alias = None
        return self._run(algOrName, parameters, onFinish=self._importAlgorithmResults, feedback=feedback, context=context)
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def runAndLoadResults(self, 
                          algOrName, 
                          parameters, 
                          resultsAsErrors=False, 
                          loadInToc=True, 
                          groupToc=None, 
                          indexToc=0,
                          readonly=False,
                          alias=None,
                          renameFields=None,
                          row=None,
                          feedback=None, 
                          context=None):
        """Executes given algorithm and load its results into QGIS project when possible."""
        self._destLayer = None
        self._deleteOldFeature = False
        self._resultsAsErrors = resultsAsErrors
        self._loadInToc = loadInToc
        self._readonly = readonly
        self._groupToc = groupToc
        self._indexToc = indexToc
        self._alias = alias
        self._renameFields = renameFields
        return self._run(algOrName, parameters, onFinish=self._handleAlgorithmResults, feedback=feedback, context=context, row=row)
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getResultLayer(self):
        """Returns result layer id"""
        if self._resLayerId is None:
            return None
        return QgsProject.instance().mapLayer( self._resLayerId )
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def clearResults(self):
        """Clear processing results."""
        
        # remove temp processing layer (if any from previous processing)
        self.removeTempLayers()
        
        # find toc node
        root_node = grp_node = QgsProject.instance().layerTreeRoot()
        if self._toc_grp_name is not None:         
            grp_node = root_node.findGroup(self._toc_grp_name)
            if grp_node is None:
                return
        
        # remove results layers
        players = []
        layers = grp_node.findLayers()
        for node in layers:
            layer = node.layer()
            if layer: # FILTER RESULT LAYERS
                players.append(layer)
                
        # remove results layers
        for layer in players:
            QgsProject.instance().removeMapLayer(layer.id())
            
        # remove node layer
        root_node.removeChildrenGroupWithoutLayers()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def removeTempLayers(self):
        """Remove temporary processing layers"""
        QgsProject.instance().removeMapLayers( self._storeTmpIdLayers )
        self._storeTmpIdLayers = []
