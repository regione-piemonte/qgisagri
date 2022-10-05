# -*- coding: utf-8 -*-
"""Modulo per verifica geometrica e topologica dei suoli in lavorazione. 

Descrizione
-----------

Implementazione della classe dedicata alle verifiche geometriche e topologiche 
dei suoli:

- verifica della geometria e dei dati dei suoli;
- verifica topologica dei suoli (sovrapposizioni, buchi, ecc.).

La verifica topologica viene eseguita solo in presenza di suoli validi: richiama
la procedura di verifica geometrica e degli attributo, quindi in assenza di errori
procede con le ulteriori verifiche.
 
  
Le verifiche vengono richiamte come singolo comando di lavorazione e sempre all'inizio 
della procedura di salvataggio di un foglio lavorato.

Librerie/Moduli
-----------------
    
Note
-----


TODO
----
 

Autore
-------

- Creato da Sandro Moretti il 23/09/2019.
- Modificato da Sandro Moretti il 28/10/2020.

Copyright (c) 2019 CSI Piemonte.

Membri
-------
"""
# system modules import
import json

# qgis modules
from qgis.core import (NULL,
                       QgsApplication,
                       QgsDataSourceUri, 
                       QgsProject, 
                       QgsCoordinateTransform, 
                       QgsSpatialIndex, 
                       QgsVectorLayer)

from PyQt5.QtWidgets import QMessageBox

# plugin modules
from qgis_agri import __PLG_DB3__, tr, QGISAgriMessageLevel
from qgis_agri import agriConfig
from qgis_agri.settings.config import ConfigBase
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.util.exception import formatException
from qgis_agri.util.dictionary import dictUtil
from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.gui.geometry_util import QGISAgriGeometry
from qgis_agri.plg_processing.processing import QGISAgriProcessing
from qgis_agri.qgis_agri_identify_dlg import QGISAgriIdentifyDialogWrapper

#
#-----------------------------------------------------------
class QGISAgriChecker:
    
    # constants
    TOC_ERR_GRP_NAME = "ERRORI"
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, plugin):
        """Constructor"""
        self.__plugin = plugin
        self.__processing = QGISAgriProcessing( toc_grp_name=self.TOC_ERR_GRP_NAME )
        self.__processing_config = ConfigBase()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def plugin(self):
        """ Returns plugin instance (readonly) """
        return self.__plugin
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def errorsBox(self):
        """ Returns error dialog """
        return self.plugin.errorsbox
     
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def run_processing(self, algOrName, params, clearResults=False):
        """Run processing module"""
        
        # clear previous processing results
        if clearResults:
            self.__processing.clearResults()
        
        # run processing
        return self.__processing.runAndLoadResults(
            algOrName, params, context=self.__processing.default_processing_context())
    
    
    def can_proceed_if_disabled_checks(self):
        """
        Checks if any validation disabled and ask confirm by user
        """
        # Check if any validation disabled
        errBox = self.errorsBox
        disable_verif = False
        disable_verif = disable_verif or not errBox.checkCessatiSuoli
        disable_verif = disable_verif or not errBox.checkAreaMinSuoli
        if self.plugin.particelle.isParticelleWorkingEnabled:
            disable_verif = disable_verif or not errBox.checkPartLavorate
        else:
            disable_verif = disable_verif or not errBox.checkDiffAreaSuoli
        
        if disable_verif:
            # confirm by user
            reply = QMessageBox.warning(
                self.plugin.iface.mainWindow(), 
                tr('Continuare?'), 
                tr("<b>ATTENZIONE</b>: "
                        "<br/>"
                        "<b>disattivate alcune verifiche topologiche dal pannello errori.</b>"
                        "<br/>"
                        "<br/>"
                        "Desideri procedere?"), 
                QMessageBox.Yes, 
                QMessageBox.No)
            if reply != QMessageBox.Yes:
                # cannot proceed
                return False
        # can proceed
        return True
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def run_processing_script_list(self, 
                              scriptNameList, 
                              variables, 
                              destLayer, 
                              clearResults=False, 
                              callback=None, 
                              layersLoadOnly=False,
                              showWrnMessage=True):
        """Run processing module"""
        while scriptNameList:
            scriptName = scriptNameList.pop(0)
            showWrnMsg = False if scriptNameList or not showWrnMessage else True
            res = self.run_processing_script( scriptName, 
                                              variables, 
                                              destLayer, 
                                              clearResults, 
                                              callback, 
                                              layersLoadOnly,
                                              showErrMessage=showWrnMsg )
            if res:
                return True
        
        # all processing scripts failed
        return False
         
    # --------------------------------------
    # 
    # -------------------------------------- 
    def run_processing_script(self, 
                              scriptName, 
                              variables, 
                              destLayer, 
                              clearResults=False, 
                              callback=None, 
                              layersLoadOnly=False,
                              showErrMessage=True):
        """Run processing module"""
        
        # init 
        errMsg = ""
        variables = variables or {}
             
        try:
            # show / retrieve Agri layers
            vlayers = self.plugin.controller.load_suoli_layers( 
                except_unfound=QGISAgriMessageLevel.Debug, load_only=layersLoadOnly )
            for lay in vlayers:
                uri = lay.dataProvider().uri()
                in_key = "LAYER_{}".format( uri.table() ) 
                variables[in_key] = uri.uri()
            
            # init processing config file
            if not self.__processing_config.initialized:
                self.__processing_config.initialize( 
                    agriConfig.get_config_file_fullame( agriConfig.CFG_PROCESSING_FILE_NAME ) )
            cfg = self.__processing_config.get_value( 'processing', {} )
            script_cfg = cfg.get( scriptName, None )
            if script_cfg is None:
                raise Exception(tr("Script processing non reperito: ")+str(scriptName))
            
            # clear previous processing results
            if clearResults:
                self.__processing.clearResults()
                
            # format destination layer
            if destLayer:
                if isinstance( destLayer, QgsDataSourceUri ):
                    vlayers = QGISAgriLayers.get_vectorlayer([destLayer])
                    if not vlayers:
                        destLayer = None
                    destLayer = vlayers[0]
            
            # loop algorithms in script
            i = 0
            out_prev = ''
            hasError = False
            for alg in script_cfg.get('alghoritms', []):
                
                # init
                algOrName = str( alg.get('name', '') ).strip()
                alias = alg.get( 'alias', None )
                outputAttributeName = str( alg.get( 'outputAttributeName', 'OUTPUT' ) )
                
                # check if native algorithm exists
                alg_obj = QgsApplication.processingRegistry().algorithmById(algOrName)
                if alg_obj is None:
                    # check if python algorithm exists
                    alg_alt_name = algOrName.replace("native:", "qgis:")
                    alg_obj = QgsApplication.processingRegistry().createAlgorithmById(alg_alt_name)
                    if alg_obj is not None:
                        # replace native algorithm name with python one
                        algOrName = alg_alt_name
                
                # errorr message incipit
                errMsg = "Script processing: '{0}' - Algoritmo: '{1} {2}'".format(
                    scriptName, 
                    algOrName, 
                    ("[Alias: '{}']".format(alias) if algOrName is not None else "")
                )
                
                # prepare paramaters
                variables['OUTPUT_PREVIUOS'] = out_prev
                # replace variable in parameters
                params = alg.get('parameters', {})
                params = dictUtil.substituteVariables( params, variables )
                
                # run processing
                res = None
                if alg.get('import', False):
                    res = self.__processing.runAndImport(
                        algOrName, params, destLayer, context=self.__processing.default_processing_context())
                else:
                    res = self.__processing.runAndLoadResults(
                        algOrName, 
                        params, 
                        resultsAsErrors = alg.get('resultAsError', False),
                        loadInToc = alg.get('loadInToc', True),
                        groupToc = alg.get('groupToc', None),
                        indexToc = alg.get('indexToc', True),
                        readonly = alg.get('readOnly', False),
                        renameFields = alg.get('renameFields', None),
                        alias = alias,
                        row = i+1,
                        context=self.__processing.default_processing_context())
                
                # store output layer name of current processing
                out_key = str(i) if alias is None else alias
                out_key = 'OUTPUT_'+out_key
                variables[out_key] = out_prev = ''
                if res is not None:    
                    variables[out_key] = out_prev = res[outputAttributeName]
                
                # set error flag
                has_error_proc = self.__processing.hasErrors()
                hasError = hasError or has_error_proc
                i += 1
                if has_error_proc and alg.get('stopOnErrors', True):
                    break
            
            # call callback function
            if not hasError and callback is not None:
                # collect feature errors    
                resLayer = self.__processing.getResultLayer()
                callback( resLayer )
            
            # return if has errors
            return not hasError
        
        except Exception as e:
            # handle exception
            errMsg = '{0}\n{1}'.format(errMsg, formatException(e))
            if showErrMessage:
                logger.msgbox( logger.Level.Critical, errMsg, title=tr('ERRORE') )
            else:
                logger.log( logger.Level.Critical, errMsg )         
            return False
        
        finally:
            # terminate processing script
            self.__processing.removeTempLayers()
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _scaleFactor(self, layer):
        scaleFactor = 1.0
        if layer:
            p = QgsProject.instance()
            ct = QgsCoordinateTransform( layer.sourceCrs(), p.crs(), p )
            scaleFactor = ct.scaleFactor( layer.sourceExtent() )
        return scaleFactor
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _checkThicknessThreshold(self, layer, feat):
        geom = feat.geometry()
        ##layerToMapUnits = self._scaleFactor( layer )
        ##layerToMapUnits2 = layerToMapUnits * layerToMapUnits
        ##maxCalcArea = agriConfig.TOLERANCES.THICKNESS_MAXAREA / layerToMapUnits2
        bb = geom.boundingBox()
        maxDim = max( bb.width(), bb.height() )
        area = geom.area()
        value = ( maxDim * maxDim ) / area
        return value > agriConfig.TOLERANCES.THICKNESS_TOLERANCE
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def clear_processing_results(self):
        """Clear processing result layers"""
        self.__processing.clearResults()
        self.plugin.iface.mapCanvas().refresh()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def checkSuoliTopology(self, suoloLayer, errorData, options):
        """ Check topology of 'Suoli' layer geometries """
        try:
            # init
            options = options or {}
            
            # check if PARTICELL working 
            if options.get( 'isParticelleWorking', False ):
                return self.checkParticelleTopology( suoloLayer, errorData, options )
            
            layerAliasName = suoloLayer.name() #options.get( 'layerAliasName', None )
            layersLoadOnly = options.get( 'layersLoadOnly', False )
            showWrnMessage = options.get( 'showWrnMessage', True )
            
            ########################################################################################
            # get suoli layer
            ########################################################################################
            
            # get 'confine_foglio' vector layer
            vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='chkTopoSuoli|suoliCondLayer' )
            if len(vlayers) == 0:
                raise Exception( tr( "Nessun layer dei suoli in conduzione definito per il comando 'chkTopoSuoli'" ) )
            suoliCondLayer = vlayers[0]
            
            # get suoli no conduzione corrotti layer
            vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='chkTopoSuoli|suoliNoCondErrLayer' )
            if len(vlayers) == 0:
                raise Exception( tr( "Nessun layer dei suoli non in conduzione corrotti definito per il comando 'chkTopoSuoli'" ) )
            suoliNoCondErrLayer = vlayers[0]
            
            # get suoli no conduzione layer
            vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='chkTopoSuoli|suoliNoCondLayer' )
            if len(vlayers) == 0:
                raise Exception( tr( "Nessun layer dei suoli non in conduzione definito per il comando 'chkTopoSuoli'" ) )
            suoliNoCondLayer = vlayers[0]
            
            ########################################################################################
            # check suoli outside of confine limit
            ########################################################################################
            if __PLG_DB3__:
                # get 'confine_foglio' vector layer
                vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='chkTopoConfine' )
                if len(vlayers) == 0:
                    raise Exception( tr('Nessun layer definito per il confine foglio') )
                
                confineLayer = vlayers[0]
                
                # process 'suoli lavorazione', 'confine_foglio' layer difference
                res = self.run_processing_script( 'checkConfineFoglio', {
                
                        'suoliLayer': suoloLayer.dataProvider().uri().uri(),
                        'confineLayer': confineLayer.dataProvider().uri().uri(),
                        
                    },  
                    None, 
                    clearResults = True, 
                    layersLoadOnly = layersLoadOnly,
                    callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer, 
                        tr('Suolo fuori confine foglio'), 
                        layerAliasName = layerAliasName, 
                        isWarning = True,
                        fictitious = True,
                        addCounter = True,
                        addArea = True ) 
                )
                if not res:
                    errorData.append( tr('Errore nella verifica confine foglio dei suoli in lavorazione') )
            
            ########################################################################################
            # check suoli overlaps
            ########################################################################################
            if suoloLayer == suoliCondLayer:
                # get filter warning expression "Suoli non in conduzione"
                filterWarnExpr = agriConfig.get_value( 'commands/checkSuoli/checks/suoliOverlaps/filterWarnExprNoCond', None )
                filterWarnExpr = None if not filterWarnExpr else filterWarnExpr
                
                # process 'suoli lavorazione', 'confine_foglio' layer difference
                res = self.run_processing_script( 'checkTopoSuoli', {
                
                        'suoliCondLayer': suoliCondLayer.dataProvider().uri().uri(),
                        'suoliNoCondErrLayer': suoliNoCondErrLayer.dataProvider().uri().uri(),
                        'suoliNoCondLayer': suoliNoCondLayer.dataProvider().uri().uri(),
                        
                    },  
                    None, 
                    clearResults = False, 
                    layersLoadOnly = layersLoadOnly,
                    callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer, 
                        tr('Suoli sovrapposti'), 
                        layerAliasName = layerAliasName,
                        filterWarnExpr = filterWarnExpr,
                        msgWarnExpr = tr('Suoli sovrapposti in conduzione e non in conduzione'),
                        fictitious = True,
                        addCounter = True,
                        addArea = True ) 
                )
                if not res:
                    errorData.append( tr('Errore nella verifica sovrapposizione dei suoli') )
             
            ########################################################################################
            # check suoli holes
            ########################################################################################
            if suoloLayer == suoliCondLayer:
                res = self.run_processing_script_list(
                    
                    ['checkHoleSuoli','checkHoleSuoli2', 'checkHoleSuoli3'],
                                                 
                    {
                        'suoliCondLayer': suoliCondLayer.dataProvider().uri().uri(),
                        'suoliNoCondErrLayer': suoliNoCondErrLayer.dataProvider().uri().uri(),
                        'suoliNoCondLayer': suoliNoCondLayer.dataProvider().uri().uri(),
                        
                    },
                      
                    None,
                     
                    clearResults = False,
                     
                    layersLoadOnly = layersLoadOnly,
                    
                    callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer, 
                        tr('Buco nella copertura dei suoli in lavorazione'), 
                        layerAliasName = layerAliasName, 
                        isWarning = True,
                        fictitious = True,
                        addCounter = True,
                        addArea = True ),
                    
                    showWrnMessage = showWrnMessage
                )
                if not res:
                    errorData.append( 
                        tr('Errore nella verifica della presenza di buchi nei suoli'),
                        isWarning= True )      
                    
            ########################################################################################
            # check difference on 'Particelle in conduzione' and 'Suoli in lavorazione' layers
            ########################################################################################
            if suoloLayer == suoliCondLayer:
                vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='salvasuoli|particelle' )
                if len(vlayers) == 0:
                    raise Exception( tr('Nessun layer definito per le particelle catastali') )
                particelleLayer = vlayers[0]
                
                # process 'suoli lavorazione', 'particelle_catastali' layer intersection
                res = self.run_processing_script_list( 
                    
                    ['checkCoverSuoli','checkCoverSuoli2'], 
                    {
                        'suoliLayer': suoloLayer.dataProvider().uri().uri(),
                        'particelleLayer': particelleLayer.dataProvider().uri().uri(),
                        'TOLL_COMP_SUOLO': agriConfig.TOLERANCES.TOLL_COMP_SUOLO   
                    },  
                    None, 
                    clearResults = False, 
                    layersLoadOnly = layersLoadOnly,
                    callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer, 
                        tr('Differenza area suoli - particelle fuori tolleranza'),
                        layerAliasName ="{} \\ Particelle".format(layerAliasName),
                        isWarning = not self.errorsBox.checkDiffAreaSuoli,
                        isForcedWarning = True,
                        fictitious = True,
                        addCounter = True,
                        addArea = True,
                        minAreaForAppend = agriConfig.TOLERANCES.TOLL_COMP_SUOLO,
                        msgCode = 'U110' )
                )
                if not res:
                    errorData.append( 
                        tr('Errore nella verifica della copertura totale dei suoli in conduzione'),
                        isWarning = not self.errorsBox.checkDiffAreaSuoli,
                        isForcedWarning = True,
                        msgCode = 'U110' )
                    
            ########################################################################################
            # check suoli without parent
            ########################################################################################
            if suoloLayer == suoliCondLayer:
                vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='salvasuoli|particelle' )
                if len(vlayers) == 0:
                    raise Exception( tr('Nessun layer definito per le particelle catastali') )
                particelleLayer = vlayers[0]
                
                # process 'suoli lavorazione', 'particelle_catastali' layer intersection
                res = self.run_processing_script_list( 
                    
                    ['checkCoverSuoliPart'], 
                    {
                        'suoliLayer': suoloLayer.dataProvider().uri().uri(),
                        'particelleLayer': particelleLayer.dataProvider().uri().uri()
                    },  
                    None, 
                    clearResults = False, 
                    layersLoadOnly = layersLoadOnly,
                    callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer, 
                        tr('Suolo non coperto da alcuna particella in conduzione'),
                        layerAliasName ="{} \\ Particelle".format(layerAliasName),
                        isWarning = False,
                        isForcedWarning = False,
                        fictitious = True,
                        addCounter = True,
                        addArea = True,
                        #minAreaForAppend = agriConfig.TOLERANCES.TOLL_COMP_SUOLO,
                        msgCode = 'U111' )
                )
                if not res:
                    errorData.append( 
                        tr('Errore nella verifica dei suoli senza padre'),
                        isWarning = True,
                        isForcedWarning = False,
                        msgCode = 'U111' )
                    
            ########################################################################################
            # check if there are holes with deleted suoli
            ########################################################################################
            if suoloLayer == suoliCondLayer:
                # clone layer without filter
                suoloLayerNoFilter = suoloLayer.clone() #QgsVectorLayer(suoloLayer.source(), suoloLayer.name(), suoloLayer.providerType())
                suoloLayerNoFilter.setSubsetString('')
                QgsProject.instance().addMapLayer( suoloLayerNoFilter, False )
                
                suoloNoCondLayerNoFilter = suoliNoCondErrLayer.clone() #QgsVectorLayer(suoliNoCondErrLayer.source(), suoliNoCondErrLayer.name(), suoliNoCondErrLayer.providerType())
                suoloNoCondLayerNoFilter.setSubsetString('')
                QgsProject.instance().addMapLayer( suoloNoCondLayerNoFilter, False )
        
                # process 'suoli lavorazione'
                res = self.run_processing_script_list( 
                    
                    ['checkDeletedSuoli','checkDeletedSuoli2'], 
                    {
                        'suoliLayer': suoloLayerNoFilter.dataProvider().uri().uri(),
                        'suoliCondLayer': suoloLayerNoFilter.dataProvider().uri().uri(),
                        'suoliNoCondErrLayer': suoloNoCondLayerNoFilter.dataProvider().uri().uri(),
                        'TOLL_COMP_CESSATI': agriConfig.TOLERANCES.TOLL_COMP_CESSATI   
                    },  
                    None, 
                    clearResults = False, 
                    layersLoadOnly = layersLoadOnly,
                    callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer,
                        tr('Suoli cessati non coperti da quelli in lavorazione'),
                        layerAliasName = suoloLayer.name(),
                        isWarning = not self.errorsBox.checkCessatiSuoli,
                        isForcedWarning = True,
                        fictitious = True,
                        addCounter = True,
                        addArea = True,
                        minAreaForAppend = agriConfig.TOLERANCES.TOLL_COMP_CESSATI,
                        msgCode = 'U112' )
                )
                
                QgsProject.instance().removeMapLayer(suoloLayerNoFilter.id())
                QgsProject.instance().removeMapLayer(suoloNoCondLayerNoFilter.id())
                
                if not res:
                    errorData.append( 
                        tr('Errore nella verifica dei suoli cessati'),
                        isWarning = not self.errorsBox.checkCessatiSuoli,
                        isForcedWarning = True,
                        msgCode = 'U112' )
                    
                    
            ########################################################################################
            # check Suoli-Particelle logical tier
            ########################################################################################
            if True:
                # get Particelle layer
                vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='salvasuoli|particelle' )
                if len(vlayers) == 0:
                    raise Exception( tr('Nessun layer definito per le particelle catastali') )
                particelleLayer = vlayers[0]
                
                # get command configuration for current layer
                dsUri = QgsDataSourceUri( suoloLayer.dataProvider().dataSourceUri() )
                suoloLayerName = dsUri.table()
                cmd_save_cfg = agriConfig.get_value( f'commands/salvasuoli/suoliLavorazione/{suoloLayerName}', {} )
                suoliFilter = cmd_save_cfg.get( 'suoliFilter', '1!=1' )
                particelleFilter = cmd_save_cfg.get( 'particelleFilter', '1!=1' )
                
                # process 'suoli lavorazione', 'particelle_catastali' layer intersection
                res = self.run_processing_script_list( 
                    
                    ['checkSuoliParticelle','checkSuoliParticelle2'], 
                    {
                        'inputLayer': suoloLayer.dataProvider().uri().uri(),
                        'particelleLayer': particelleLayer.dataProvider().uri().uri(),
                        'suoliFilter': suoliFilter,
                        'particelleFilter': particelleFilter,
                        'TOLL_AREA_MIN_SUOLO': agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO #agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO
                    },  
                    None, 
                    clearResults = False, 
                    layersLoadOnly = layersLoadOnly,
                    callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer, 
                        tr('Suolo non relazionabile ad alcuna particella per lo stato di conduzione.'),
                        layerAliasName ="Suoli-Particelle",
                        isWarning = False,
                        isForcedWarning = False,
                        fictitious = True,
                        addCounter = True,
                        addArea = True,
                        #minAreaForAppend = agriConfig.TOLERANCES.TOLL_COMP_SUOLO,
                        msgCode = 'U113' )
                )
                if not res:
                    errorData.append( tr('Errore nella verifica della relazione Suoli-Particelle') )
            
            # return successful
            return True
        
        except Exception as e:
            # handle exception
            logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
            return False
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def checkParticelleTopology(self, partLayer, errorData, options):
        """ Check topology of 'PARTICELLE' layer geometries """
        try:
            # init
            options = options or {}
            layerAliasName = partLayer.name() #options.get( 'layerAliasName', None )
            layersLoadOnly = options.get( 'layersLoadOnly', False )
            #showWrnMessage = options.get( 'showWrnMessage', True )
            
            # check if PARTICELL working 
            if not options.get( 'isParticelleWorking', False ):
                return False
            
            ########################################################################################
            # get suoli layer
            ########################################################################################
            
            # get 'confine_foglio' vector layer
            vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='chkTopoSuoli|suoliCondLayer' )
            if len(vlayers) == 0:
                raise Exception( tr( "Nessun layer dei suoli in conduzione definito per il comando 'chkTopoSuoli'" ) )
            suoliCondLayer = vlayers[0]
            
            # get suoli no conduzione corrotti layer
            vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='chkTopoSuoli|suoliNoCondErrLayer' )
            if len(vlayers) == 0:
                raise Exception( tr( "Nessun layer dei suoli non in conduzione corrotti definito per il comando 'chkTopoSuoli'" ) )
            suoliNoCondErrLayer = vlayers[0]
            
            # get suoli no conduzione layer
            vlayers = self.plugin.controller.get_suolo_vector_layers( filter_cmd='chkTopoSuoli|suoliNoCondLayer' )
            if len(vlayers) == 0:
                raise Exception( tr( "Nessun layer dei suoli non in conduzione definito per il comando 'chkTopoSuoli'" ) )
            suoliNoCondLayer = vlayers[0]
            
            ########################################################################################
            # check PARTICELLE overlaps
            ########################################################################################
            
            # process 
            res = self.run_processing_script_list( 
                
                ['checkTopoParticelle'], 
                
                {
                    'particelleLayer': partLayer.dataProvider().uri().uri(),
                },
                  
                None,
                 
                clearResults = False, 
                
                layersLoadOnly = layersLoadOnly,
                
                callback = lambda resLayer: errorData.appendFromLayer( 
                    resLayer, 
                    tr('Particelle sovrapposte'), 
                    layerAliasName = layerAliasName,
                    fictitious = True,
                    addCounter = True,
                    addArea = True ) 
            )
            if not res:
                errorData.append( tr('Errore nella verifica sovrapposizione delle particelle') )
            
            ########################################################################################
            # check worked PARTICELLE not covered by SUOLI
            ########################################################################################
            
            # process 
            res = self.run_processing_script_list( 
                
                ['checkCoverParticelleSuoli', 'checkCoverParticelleSuoli2'], #['checkCoverParticelleLavorate'], 
                
                {
                    'particelleLayer': partLayer.dataProvider().uri().uri(),
                    'suoliCondLayer': suoliCondLayer.dataProvider().uri().uri(),
                    'suoliNoCondErrLayer': suoliNoCondErrLayer.dataProvider().uri().uri(),
                    'suoliNoCondLayer': suoliNoCondLayer.dataProvider().uri().uri(),
                },
                  
                None,
                 
                clearResults = False, 
                
                layersLoadOnly = layersLoadOnly,
                
                callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer, 
                        tr('Particella e suolo non coperti completamente'),
                        layerAliasName = layerAliasName,
                        isWarning = not self.errorsBox.checkPartLavorate,
                        isForcedWarning = True,
                        fictitious = True,
                        addCounter = True,
                        addArea = True,
                        minAreaForAppend = agriConfig.TOLERANCES.TOLL_COMP_SUOLO,
                        msgCode = 'U120' )
            )
            if not res:
                errorData.append( 
                    tr('Errore nella verifica copertura particelle e suoli'),
                    isWarning = not self.errorsBox.checkPartLavorate,
                    isForcedWarning = True,
                    msgCode = 'U120' )
            
            ########################################################################################
            # check Suoli-Particelle logical tier
            ########################################################################################
            
            # process 
            res = self.run_processing_script_list( 
                
                ['checkSuoliLavParticelle'],
                
                {
                    'particelleLayer': partLayer.dataProvider().uri().uri(),
                    'suoliCondLayer': suoliCondLayer.dataProvider().uri().uri(),
                    'suoliNoCondErrLayer': suoliNoCondErrLayer.dataProvider().uri().uri(),
                    'suoliNoCondLayer': suoliNoCondLayer.dataProvider().uri().uri(),
                    'TOLL_AREA_MIN_SUOLO': agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO #agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO
                },
                  
                None,
                 
                clearResults = False, 
                
                layersLoadOnly = layersLoadOnly,
                
                callback = lambda resLayer: errorData.appendFromLayer( 
                        resLayer, 
                        tr('Particella lavorata con suoli non lavorati.'),
                        layerAliasName = "Suoli-Particelle",
                        isWarning = False, #not self.errorsBox.checkPartLavorate,
                        isForcedWarning = False, #True,
                        fictitious = True,
                        addCounter = True,
                        addArea = True,
                        #minAreaForAppend = agriConfig.TOLERANCES.TOLL_COMP_SUOLO,
                        msgCode = 'U121' )
            ) 
            if not res:
                errorData.append( 
                    tr('Errore nella verifica della relazione Suoli-Particelle (Lavorazione Particelle)'),
                    isWarning = False, #not self.errorsBox.checkPartLavorate,
                    isForcedWarning = False, #True,
                    msgCode = 'U121' )
            
            # return successful
            return True
        
        except Exception as e:
            # handle exception
            logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
            return False
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def _checkSuoliValidityHole(self, holeGeom):
        # init
        if not holeGeom.isGeosValid():
            # repair invalid geometry
            holeGeom = holeGeom.makeValid()
            
        # get suoli no conduzione layer
        vlayers_nocond = self.plugin.controller.get_suolo_vector_layers( filter_cmd='chkTopoSuoli|suoliNoCondLayer' )
        
        # check each layer
        for vlayer in vlayers_nocond:
            # create spatial index
            index = QgsSpatialIndex( vlayer.getFeatures() )
            # Find all features that intersect the bounding box of the geometry selector
            bbox = holeGeom.boundingBox()
            bbox.grow( 2*0.0001 )
            intersecting_ids = index.intersects( bbox )
            if not intersecting_ids:
                continue
            
            # check found features
            for fid in intersecting_ids:
                # get feature
                feat = vlayer.getFeature( fid )
                geom = feat.geometry()
                if not geom:
                    continue
                
                # check if valid geom
                if not geom.isGeosValid():
                    geom = geom.makeValid()
                    
                # check if feature geometry intersects input geomtry
                if holeGeom.intersects( geom ) and \
                   holeGeom.contains( geom ):
                    return True
            
        return False
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def checkSuoliValidity(self, suoloLayerOrig, errorData, options):
        """ Check validity of 'Suoli' layer geometries """
        try:
            # init
            options = options or {}
            
            # check if PARTICELL working 
            if options.get( 'isParticelleWorking', False ):
                return self.checkParticelleValidity( suoloLayerOrig, errorData, options )
            
            # init
            suoloLayer = suoloLayerOrig.clone()
            # load all fogli <--------
            suoloLayer.setSubsetString( None )
            layName = suoloLayer.name()
            dsUri = QgsDataSourceUri( suoloLayer.dataProvider().dataSourceUri() )
            layDbName = dsUri.table()
            
            # get tolerances
            suoliMinArea = agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO
            suoliTollArea = agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO
            
            
            # get command configuration for current layer
            cmd_check_cfg = agriConfig.get_value( f'commands/salvasuoli/suoliLavorazione/{layDbName}', {} )
            checkIfEmpty = cmd_check_cfg.get( 'checkIfEmpty', True )
        
            # get command configuration
            cmd_check_cfg = agriConfig.get_value( 'commands/salvasuoli', {} )
            att_check_cfg = cmd_check_cfg.get( 'checkFields', {} )
            
            fld_def = att_check_cfg.get( 'cessato', {} )
            fld_cessato_filter = fld_def.get( 'filter', '' )
            
            # get 'IdFeture' config
            ctx_cfg = agriConfig.get_value( 'context/suolo/id', {} )
            suoloIdField = ctx_cfg.get( 'fieldValue', None )
            
            ctx_cfg = agriConfig.get_value( 'context/suolo/idParent', {} )
            suoloIdParentField = ctx_cfg.get( 'fieldValue', None )
            
            # get 'tipoSuolo' config
            ctx_cfg = agriConfig.get_value( 'context/suolo/type', {} )
            suoloTpField = ctx_cfg.get( 'fieldValue', None )
            suoloTpValues = ctx_cfg.get( 'layers', {} ).get( layDbName, {} ).get( 'fieldValues', [] )
            
            # get 'Eleggibilità' config
            ctx_cfg = agriConfig.get_value( 'context/suolo/eleggibilita', {} )
            elegCodeField = ctx_cfg.get( 'fieldValue', None )
            
            # get 'Sospeso' config
            ctx_cfg = agriConfig.get_value( 'context/suolo/sospeso', {} )
            flagSospField = ctx_cfg.get( 'fieldValue', None )
            flagSospValue = ctx_cfg.get( 'fieldAssignValue', 1 )
            flagSospLayTpValues = ctx_cfg.get( 'checkLayers', {} ).get( layDbName, {} )
            flagSospSuoloTpValues = flagSospLayTpValues.get( 'fieldLavValues', [] )
            
            # get 'idTipoMotivoSospensione' config
            ctx_cfg = agriConfig.get_value( 'context/suolo/sospensione', {} )
            flagIdTpSospField = ctx_cfg.get( 'fieldValue', None )
            
            # get 'flagLavorato' config
            ctx_cfg = agriConfig.get_value( 'context/suolo/lavorato', {} )
            flagLavField = ctx_cfg.get( 'fieldValue', None )
            flagLavValue = ctx_cfg.get( 'fieldAssignValue', None )
            flagLavLayTpValues = ctx_cfg.get( 'checkLayers', {} ).get( layDbName, {} )
            flagLavSuoloTpValues = flagLavLayTpValues.get( 'fieldLavValues', [] )
            flagErrSuoloTpValues = flagLavLayTpValues.get( 'fieldErrValues', [] )
            
            # compose feature filter expression
            featureSelExpr = f"NOT ({fld_cessato_filter})" if fld_cessato_filter else '' 
            
            # do checks (for example: forceCW)
            
            # check if 'suoli' features well defined
            featureIdColl = {}
            totLavFeatures = 0
            for feature in suoloLayer.getFeatures( featureSelExpr ):
                fid = feature.id()
                totLavFeatures += 1
                
                # check feature geometry
                geom = feature.geometry()
                if geom.isNull():
                    errorData.append( tr( "Geometria suolo nulla" ), layer=layName, fid=fid, geom=geom )
                    
                if not geom.isGeosValid():
                    errorData.append( geom.lastError() or tr( "Geometria suolo non valida" ), layer=layName, fid=fid, geom=geom  )
                
                # check if multi parts geometry
                if geom.isMultipart() and len( geom.asGeometryCollection() ) > 1:
                    errorData.append( tr( "Geometria multiparte non ammessa" ), layer=layName, fid=fid, geom=geom  )
                
                # check if geometry area in tollerance
                area = geom.area()
                if area < suoliMinArea:
                    # is really too small?
                    too_small = not(suoliTollArea < area)
                    
                    # compose error\warning message
                    msg = tr( "Superficie suolo troppo piccola" )
                    if too_small:
                        msg = "{} {} {:.3g} mq".format( 
                            msg, tr( "fuori tolleranza di" ), suoliTollArea )
                        
                    # add error\warning
                    errorData.append(
                        "{} [{:.{prec}f} mq]".format( msg, area, prec=agriConfig.display_decimals ),
                        layer = layName, 
                        fid = fid, 
                        geom = geom, 
                        isWarning = not( self.errorsBox.checkAreaMinSuoli or too_small ),
                        isForcedWarning = True,
                        msgCode = 'U100' )
                
                # check geometry thickness    
                if self._checkThicknessThreshold( suoloLayer, feature ):
                    errorData.append( tr( "Superficie con possibile contorno degradato" ), layer=layName, fid=fid, geom=geom, isWarning=True )
                    
                # check holes
                ringGeoms = QGISAgriGeometry.get_geometries_from_rings( geom )
                for part in ringGeoms:
                    for i, ringGeom in enumerate(part):
                        if i == 0:
                            # skip geometry from exterior ring
                            continue
                        
                        # check if hole geometry area in tollerance
                        area = ringGeom.area()
                        if area < suoliMinArea:
                            # check if hole on 'no conduzione suoli'
                            nocond_hole = False
                            try:
                                nocond_hole = self._checkSuoliValidityHole( ringGeom )
                            except:
                                nocond_hole = True
                            # emit error\warning
                            errorData.append( 
                                tr( "Area buco suolo troppo piccola [{:.{prec}f} mq]".format( area, prec=agriConfig.display_decimals ) ), 
                                layer=layName, 
                                fid=fid, 
                                geom=ringGeom,
                                isWarning=nocond_hole )
                
                
                
                # check if feature to exclude
                
                # check attributes
                attibs = QGISAgriLayers.get_attribute_values( feature )
                for attName, attDef in att_check_cfg.items():
                    attDef = attDef or {}
                    
                    # check if attribute exists in feature
                    if attName not in attibs:
                        errorData.append( "{0}: {1}".format( tr( "Attributo mancante" ), attName ), 
                                          layer=layName, fid=fid, geom=geom )
                        
                    # get attribute value by feature
                    nullValue = attDef.get( 'nullValue', NULL ) or NULL
                    attValue = attibs.get( attName, nullValue )
                    
                    # check if attribute is valorized
                    nullable = attDef.get( 'nullable', False )
                    if not nullable and attValue == NULL:
                        errorData.append( "{0}: {1}".format( tr( "Attributo non valorizzato" ), attName ), 
                                          layer=layName, fid=fid, geom=geom )
                    # check if attribute is empty
                    notEmpty = attDef.get( 'notEmpty', False )
                    if notEmpty and (attValue == NULL or not str(attValue).strip()):
                        errorData.append( "{0}: {1}".format( tr( "Attributo non valorizzato" ), attName ), 
                                          layer=layName, fid=fid, geom=geom ) 
                    
                    
                    # check if valid value
                    valid_values = attDef.get( 'values', [] )
                    if valid_values and attValue not in valid_values:
                        errorData.append( "{0}: {1}".format( tr( "Attributo non valido" ), attName ), 
                                          layer=layName, fid=fid, geom=geom )
                    
                    # idFeature checks
                    if attName == suoloIdField:
                        # check if idFeature is unique
                        if attValue != NULL and attValue in featureIdColl: 
                            duplFeat = suoloLayer.getFeature( featureIdColl[attValue] )
                            errorData.append( "{0}: {1}".format( tr( "idFeature duplicato" ), attValue ), 
                                              layer=layName, fid=duplFeat.id(), geom=duplFeat.geometry() )
                            errorData.append( "{0}: {1}".format( tr( "idFeature duplicato" ), attValue ), 
                                              layer=layName, fid=fid, geom=geom )
                        else:
                            featureIdColl[attValue] = fid
                       
                    # idFeaturePadre checks
                    if attName == suoloIdParentField:
                        try:
                            if type(attValue) == str:
                                attValue = json.loads(attValue)
                            if type(attValue) != list:
                                errorData.append( 
                                    tr( "Campo 'IdFeaturePadre' con tipo errato <===" ), 
                                    layer=layName, fid=fid, geom=geom, isWarning=True  )
                                
                            elif not attValue:
                                errorData.append( 
                                    tr( "Campo 'IdFeaturePadre' non valorizzato <===" ), 
                                    layer=layName, fid=fid, geom=geom, isWarning=True  )
                                
                        except (json.decoder.JSONDecodeError, TypeError):
                            errorData.append( 
                                tr( "Campo 'IdFeaturePadre' malformato <===" ), 
                                layer=layName, fid=fid, geom=geom, isWarning=True  )   
                       
                    # check field tipoSuolo
                    elif attName == suoloTpField:
                        if attValue != NULL and attValue not in suoloTpValues:
                            errorData.append( "{0}: '{1}'".format( tr( "Tipo suolo non valido" ), attValue ), 
                                              layer=layName, fid=fid, geom=geom )
                    
                    # check field 'codiceEleggibilitaRilevata'
                    elif attName == elegCodeField:
                        elegValid, elegAssignable = QGISAgriIdentifyDialogWrapper.isValidEleggibilitaCode( attValue )
                        # check if valid: code exists in table ClassiEleggibilita
                        if not elegValid:
                            errorData.append( tr( "Codice di eleggibilità non valido" ), layer=layName, fid=fid, geom=geom )
                        # check if code is assegnable
                        elif not elegAssignable:
                            errorData.append( tr( "Codice di eleggibilità non assegnabile" ), layer=layName, fid=fid, geom=geom )
                    
                    # check field "flagSospensione"
                    elif attName == flagSospField:
                        if attValue == flagSospValue:
                            tpSuoloValue = attibs.get( suoloTpField, None )
                            if tpSuoloValue not in flagSospSuoloTpValues:
                                errorData.append( tr( "Suolo sospeso, ma non in lavorazione" ), layer=layName, fid=fid, geom=geom )
                            
                            # check if 'idTipoMotivoSospensione' assigned
                            idTipoMotivoSospensione = attibs.get( flagIdTpSospField, NULL )
                            if not idTipoMotivoSospensione or idTipoMotivoSospensione == NULL:
                                errorData.append( tr( "Motivo sospensione non valorizzato" ), layer=layName, fid=fid, geom=geom )
                             
                    # check field "flagLavorato"
                    elif attName == flagLavField:
                        if attValue != flagLavValue:
                            tpSuoloValue = attibs.get( suoloTpField, None )
                            if tpSuoloValue in flagErrSuoloTpValues:
                                errorData.append( tr( "Suolo corrotto non lavorato" ), layer=layName, fid=fid, geom=geom )
                            elif tpSuoloValue in flagLavSuoloTpValues:
                                errorData.append( tr( "Suolo in lavorazione non lavorato" ), layer=layName, fid=fid, geom=geom )
                    
            
            # check if found any geometry
            if checkIfEmpty:     
                # count features removed
                totRemFeatures = 0
                for feature in suoloLayer.getFeatures( fld_cessato_filter ):
                    attValue = feature.attribute( suoloIdField )
                    if attValue == NULL or not str(attValue).strip():
                        # exclude deleted feature without idFeatue (not from remote DB)
                        pass
                    else:
                        totRemFeatures += 1
                        
                # check if any Suolo found
                total = totLavFeatures + totRemFeatures
                if total == 0:
                    if self.plugin.particelle.isParticelleWorkingEnabled:
                        # return false, but don't add error
                        return False
                    # error: no features found
                    errorData.append( tr( "Nessun suolo lavorato reperito" ), layer=layName )
                
            return True
        
        except Exception as e:
            # handle exception
            logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
            return False
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def checkParticelleValidity(self, partLayerOrig, errorData, options):
        """ Check validity of 'PARTICELLE' layer geometries """
        try:
            # init
            options = options or {}
            
            # check if PARTICELL working 
            if not options.get( 'isParticelleWorking', False ):
                return False
            
            # init
            def get_mappale_key(mappale, subalterno):
                mappale = str( mappale ).strip().lstrip( '0' )
                mappale_sub = str( subalterno ).strip()
                return f"{mappale}-{mappale_sub}"
            
            # init
            partLayer = partLayerOrig.clone()
            partLayer.setSubsetString( None )
            layName = partLayer.name()
            dsUri = QgsDataSourceUri( partLayer.dataProvider().dataSourceUri() )
            layDbName = dsUri.table()
            
            # get tolerances
            partMinArea = agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO
            partTollArea = agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO
            
            # get command configuration for current layer
            cmd_check_cfg = agriConfig.get_value( f'commands/salvasuoli/suoliLavorazione/{layDbName}', {} )
            checkIfEmpty = cmd_check_cfg.get( 'checkIfEmpty', True )
            
            # get command configuration
            cmd_check_cfg = agriConfig.get_value( 'commands/salvasuoli', {} )
            att_check_cfg = cmd_check_cfg.get( 'checkParticelleFields', {} )
            
            fld_def = att_check_cfg.get( 'OGC_FID', {} )
            featureSelExpr = fld_def.get( 'filter', '' )
            
            fld_def = att_check_cfg.get( 'flagCessato', {} )
            fld_cessato_filter = fld_def.get( 'filter', '' )
            
            # get 'IdFeture' config
            ctx_cfg = agriConfig.get_value( 'context/particella/id', {} )
            partIdField = ctx_cfg.get( 'fieldValue', None )
            
            # get 'mappale' config
            ctx_cfg = agriConfig.get_value( 'context/particella/mappale', {} )
            partMappaleField = ctx_cfg.get( 'fieldValue', None )
            partMappaleSubField = ctx_cfg.get( 'fieldSubValue', None )
            
            # get 'Sospeso' config
            ctx_cfg = agriConfig.get_value( 'context/suolo/sospeso', {} )
            flagSospField = ctx_cfg.get( 'fieldValue', None )
            flagSospValue = ctx_cfg.get( 'fieldAssignValue', 1 )
            
            # get 'flagLavorato' config
            ctx_cfg = agriConfig.get_value( 'context/particella/lavorato', {} )
            flagLavField = ctx_cfg.get( 'fieldValue', None )
            flagLavValue = ctx_cfg.get( 'fieldAssignValue', None )
            
            # do checks (for example: forceCW)
            
            # collect keys
            featureSelAllExpr = f"NOT ({fld_cessato_filter})" if fld_cessato_filter else ''
            featureIdColl = {}
            particelleColl = {}
            for feature in partLayer.getFeatures( featureSelAllExpr ):
                fid = feature.id()
                
                # collect id field values
                attValue = feature.attribute( partIdField )
                if attValue and attValue != NULL:
                    featureIdColl[attValue] = featureIdColl.get( attValue, [] )
                    featureIdColl[attValue].append( fid )
                    
                # collect mappale values
                attValue = feature.attribute( partMappaleField )
                if attValue and attValue != NULL:
                    mappale = get_mappale_key( attValue, feature.attribute( partMappaleSubField ) )
                    particelleColl[mappale] = particelleColl.get( mappale, [] )
                    particelleColl[mappale].append( fid )
            
            # check if 'suoli' features well defined
            totLavFeatures = 0
            for feature in partLayer.getFeatures( featureSelExpr ):
                fid = feature.id()
                totLavFeatures += 1
                
                # check feature geometry
                geom = feature.geometry()
                if geom.isNull():
                    errorData.append( tr( "Geometria particella nulla" ), layer=layName, fid=fid, geom=geom )
                    
                if not geom.isGeosValid():
                    errorData.append( geom.lastError() or tr( "Geometria particella non valida" ), layer=layName, fid=fid, geom=geom  )
                
                # check if multi parts geometry
                if geom.isMultipart() and len( geom.asGeometryCollection() ) > 1:
                    errorData.append( tr( "Geometria multiparte non ammessa" ), layer=layName, fid=fid, geom=geom  )
                
                # check if geometry area in tollerance
                area = geom.area()
                if area < partMinArea:
                    # is really too small?
                    too_small = not(partTollArea < area)
                    
                    # compose error\warning message
                    msg = tr( "Superficie particella troppo piccola" )
                    if too_small:
                        msg = "{} {} {:.3g} mq".format( 
                            msg, tr( "fuori tolleranza di" ), partTollArea )
                        
                    # add error\warning
                    errorData.append(
                        "{} [{:.{prec}f} mq]".format( msg, area, prec=agriConfig.display_decimals ),
                        layer = layName, 
                        fid = fid, 
                        geom = geom, 
                        isWarning = not( self.errorsBox.checkAreaMinSuoli or too_small ) )
                
                # check geometry thickness    
                if self._checkThicknessThreshold( partLayer, feature ):
                    errorData.append( tr( "Superficie con possibile contorno degradato" ), layer=layName, fid=fid, geom=geom, isWarning=True )
                    
                # check holes
                ringGeoms = QGISAgriGeometry.get_geometries_from_rings( geom )
                for part in ringGeoms:
                    for i, ringGeom in enumerate(part):
                        if i == 0:
                            # skip geometry from exterior ring
                            continue
                        
                        # check if hole geometry area in tollerance
                        area = ringGeom.area()
                        if area < partMinArea:
                            # check if hole on 'no conduzione suoli'
                            nocond_hole = False
                            try:
                                nocond_hole = self._checkSuoliValidityHole( ringGeom )
                            except:
                                nocond_hole = True
                            # emit error\warning
                            errorData.append( 
                                tr( "Area buco suolo troppo piccola [{:.{prec}f} mq]".format( area, prec=agriConfig.display_decimals ) ), 
                                layer=layName, 
                                fid=fid, 
                                geom=ringGeom,
                                isWarning=nocond_hole )
                
                
                
                # check if feature to exclude
                
                # check attributes
                attibs = QGISAgriLayers.get_attribute_values( feature )
                for attName, attDef in att_check_cfg.items():
                    attDef = attDef or {}
                    
                    # check if attribute exists in feature
                    if attName not in attibs:
                        errorData.append( "{0}: {1}".format( tr( "Attributo mancante" ), attName ), 
                                          layer=layName, fid=fid, geom=geom )
                        
                    # get attribute value by feature
                    nullValue = attDef.get( 'nullValue', NULL ) or NULL
                    attValue = attibs.get( attName, nullValue )
                    
                    # check if attribute is valorized
                    nullable = attDef.get( 'nullable', False )
                    if not nullable:
                        if attValue == NULL:
                            errorData.append( "{0}: {1}".format( tr( "Attributo non valorizzato" ), attName ), 
                                              layer=layName, fid=fid, geom=geom )
                    
                    # check if attribute is empty
                    notEmpty = attDef.get( 'notEmpty', False )
                    if notEmpty:
                        if attValue == NULL or not str(attValue).strip():
                            errorData.append( "{0}: {1}".format( tr( "Attributo non valorizzato" ), attName ), 
                                              layer=layName, fid=fid, geom=geom )        
                    
                        
                    # check if valid value
                    valid_values = attDef.get( 'values', [] )
                    if valid_values and attValue not in valid_values:
                        errorData.append( "{0}: {1}".format( tr( "Attributo non valido" ), attName ), 
                                          layer=layName, fid=fid, geom=geom )
                    
                    # idFeature checks
                    if attName == partIdField:
                        # check if idFeature is unique
                        if attValue != NULL:
                            lst_fid = featureIdColl.get( attValue, [] )
                            if lst_fid and len(lst_fid) > 1:
                                for other_fid in lst_fid:
                                    duplFeat = partLayer.getFeature( other_fid )
                                    errorData.append( "{0}: {1}".format( tr( "idFeature duplicato" ), attValue ), 
                                                  layer=layName, fid=duplFeat.id(), geom=duplFeat.geometry() )
                                featureIdColl.pop( attValue, None )
                                
                    # check mappale field
                    elif attName == partMappaleField:
                        # check if mappale is unique
                        if attValue != NULL:
                            mappale = get_mappale_key( attValue, attibs.get( partMappaleSubField, '' ) )
                            lst_fid = particelleColl.get( mappale, [] )
                            if lst_fid and len(lst_fid) > 1:
                                for other_fid in lst_fid:
                                    duplFeat = partLayer.getFeature( other_fid )
                                    errorData.append( "{0}: {1}".format( tr( "Numero particella duplicata" ), attValue ), 
                                                  layer=layName, fid=duplFeat.id(), geom=duplFeat.geometry() )
                                particelleColl.pop( mappale, None )
                       
                    # check field "flagSospensione"
                    elif attName == flagSospField:
                        if attValue == flagSospValue:
                            """
                            # check if 'idTipoMotivoSospensione' assigned
                            idTipoMotivoSospensione = attibs.get( flagIdTpSospField, NULL )
                            if not idTipoMotivoSospensione or idTipoMotivoSospensione == NULL:
                                errorData.append( tr( "Motivo sospensione non valorizzato" ), layer=layName, fid=fid, geom=geom )
                            """
                            pass
                         
                    # check field "flagLavorato"
                    elif attName == flagLavField:
                        if attValue != flagLavValue:
                            errorData.append( tr( "Particella non lavorata" ), layer=layName, fid=fid, geom=geom )
                                
                    
            
            # check if found any geometry
            if checkIfEmpty:        
                # count features removed
                totRemFeatures = 0
                for feature in partLayer.getFeatures( fld_cessato_filter ):
                    attValue = feature.attribute( partIdField )
                    if attValue == NULL or not str(attValue).strip():
                        # exclude deleted feature without idFeatue (not from remote DB)
                        pass
                    else:
                        totRemFeatures += 1
                    
                # count suspended work item in working list (no feature)
                cfgPartLav = agriConfig.services.ParticelleLavorazioni
                part_data_rows = self.plugin.controller.getDbTableData( 
                    cfgPartLav.view, 
                    filterExpr = f"{cfgPartLav.statoLavPartField} = {cfgPartLav.statoLavPartSuspendItemValue}" 
                )
                totSuspendItems = len(part_data_rows)
                        
                # check if any Suolo found
                total = totLavFeatures + totRemFeatures + totSuspendItems
                if total == 0:
                    errorData.append( tr( "Nessuna particella lavorata" ), layer=layName )
                
            return True
        
        except Exception as e:
            # handle exception
            logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
            return False
            
            
            
            