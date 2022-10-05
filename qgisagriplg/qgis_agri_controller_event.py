# -*- coding: utf-8 -*-
"""Plugin controller event handlers

Description
-----------

Implemets the plugin controller event handlers:

- download 'Suolo' info;
- download 'Foglio' history;
- browse 'Foglio' documentation;
- download 'Foto appezzamenti';

Libraries/Modules
-----------------

- None.
    
Notes
-----

- None.

TODO
----

- None.

Author(s)
---------

- Created by Sandro Moretti on 23/09/2019.
- Modified by Sandro Moretti on 28/10/2020.

Copyright (c) 2019 CSI Piemonte.

Members
-------
"""
# system modules import
import re
import json
from os import path
from typing import Callable

# qgis modules import
from qgis.core import QgsProject, QgsFeatureSource, QgsCoordinateTransform

# Qt modules
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices, QImageReader

# plugin modules import
from qgis_agri import __PLG_DEBUG__, __QGIS_AGRI_NAME__, tr
from qgis_agri import agriConfig
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.util.exception import formatException
from qgis_agri.util.dictionary import dictUtil
from qgis_agri.util.file import fileUtil
from qgis_agri.util.list import listUtil
from qgis_agri.util.json import JsonDateTimeEncoder
from qgis_agri.util.geojson import geoJsonHelper
from qgis_agri.util.object import objUtil
from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.service.qgis_agri_networkaccessmanager import QGISAgriNetworkAccessManagerCollector
from qgis_agri.qgis_agri_history_widget import QgisAgriHistoryWidgetProvider
from qgis_agri.qgis_agri_item_selection_dlg import QGISAgriItemSelectionDialog



#
#-----------------------------------------------------------
class QGISAgriControllerEvent:
    """Class to control QGISAgri plugin"""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, controller):
        """Constructor"""
        self.__controller = controller
        self.__pcgDlg = None
        self.__allSelDlg = None
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def __del__(self):
        """Destructor"""
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def controller(self):
        """ Returns plugin controller (readonly) """
        return self.__controller
    
    
    #---------------------------------------
    #
    #---------------------------------------
    def onDownloadDataSuolo(self, 
                            idKeyFeature: int, 
                            idOrigFeature: int, 
                            lstIdOrigFeature: list, 
                            callbackFn: Callable,
                            optionData: dict) -> None:
        """ Downloads Suolo data from different API """
        
        # init
        optionData = optionData or {}
        
        # get 'anno campagna' from DB
        annoCampagna = ''
        data = self.controller.getDbTableData( agriConfig.services.listaLavorazione.name  )
        if data:
            annoCampagna = data[0].get( agriConfig.services.listaLavorazione.annoField, '' )
            
        paramData = {
            'idSuoloRilevato': idOrigFeature,
            'campagna': annoCampagna
        }
        
        resData = {
            'idSuolo': idOrigFeature,
            'lstIdFeature': lstIdOrigFeature
        }
        
        lst_errors = []
        
        ###################################################################
        #  Callback function
        ###################################################################
        
        def onComplete( successful ):
            
            # show documents dialog
            if callbackFn is not None:
                callbackFn( idKeyFeature, resData, lst_errors )
        
        def onFinishedServiceRequest( error, callbackData ):
            # check if error
            if error is not None:
                lst_errors.append( str(error) )
                return
            
            # store service result data
            serviceName = callbackData.get( 'serviceName', '' )
            serviceData = callbackData.get( 'serviceData', {} )
            serviceRowData = callbackData.get( 'servRowSelData', {} )
            dataKey = serviceRowData.get( 'dataKey', '' )
            resData[dataKey] = serviceData
            
            # check if summary data needed
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            summery_cfg = res_cfg.get( 'summmary', {} )
            summery_fields = summery_cfg.get( 'fields', [] )
            if summery_fields:
                summeries = {}
                
                # execute sum of current field
                for fieldName in summery_fields:
                    fldSum = 0.0
                    for data in serviceData:
                        try:
                            fldSum += data.get( fieldName, 0.0 )
                        except ValueError:
                            pass
                    # store sum
                    summeries[fieldName] = '{0:.4f}'.format(fldSum)
                    
                # store summery
                resData[dataKey + '_summery'] = summeries
            
        ###################################################################
        ###################################################################
        
        # get services config data
        service_cfg = agriConfig.get_value( 'agri_service', {} )
        resources_cfg = service_cfg.get( 'resources', {} )
        
        # get services to load
        cmd_cfg = self.controller.getCommandConfig( 'scaricaDatiSuolo' )
        services = cmd_cfg.get('services', [])
        
        # collect all remaining service requests 
        reqColl = QGISAgriNetworkAccessManagerCollector()
        reqColl.finishedAllRequests.connect( onComplete )
   
        for serviceName in services:
            # initialize result data dictionary
            res_cfg = resources_cfg.get( serviceName, {} )
            warningCodes = res_cfg.get( 'warningDtoCodes', [] )
            datakey_cfg = res_cfg.get( 'dataKey', '' )
            resData[datakey_cfg] = []
            
            # import data service
            self.controller.onServiceRequest( 
                serviceName, 
                { 'dataKey': datakey_cfg },
                paramData, 
                onFinishedServiceRequest, 
                parent=None, 
                warningCodes=warningCodes,
                cache=False, 
                createSpinner=False,
                requestCollector=reqColl,
                silentError=True)
        
        # start all collected service requests    
        reqColl.endRequest()
     
    
    #---------------------------------------
    #
    #---------------------------------------
    def onDownloadDataParticella(self, 
                                 idKeyFeature: int, 
                                 idOrigFeature: int, 
                                 lstIdOrigFeature: list, 
                                 callbackFn: Callable,
                                 optionData: dict) -> None:
        """ Downloads PARTICELLA data from different API """
        
        # init
        plugin = self.controller.plugin
        controlbox = plugin.controlbox
        optionData = optionData or {}
        
        paramData = {
            'annoCampagna': '',
            'codiceNazionale': '',
            'sezione': '',
            'foglio': '',
            'numeroParticella': optionData.get( 'numeroParticella', '' ),
            'subalterno': optionData.get( 'subalterno', '' )
            
        }
        
        resData = {
            'idSuolo': idOrigFeature,
            'lstIdFeature': lstIdOrigFeature
        }
        
        lst_errors = []
        
        # get 'anno campagna' from DB
        data = self.controller.getDbTableData( agriConfig.services.listaLavorazione.name  )
        if data:
            paramData['annoCampagna'] = data[0].get( agriConfig.services.listaLavorazione.annoField, '' )
            
        # get foglio data
        data = controlbox.currentFoglioData
        if data:
            table_cfg = agriConfig.services.fogliAziendaOffline
            paramData['foglio'] = data.get( table_cfg.foglioField, '' )
            paramData['codiceNazionale'] = data.get( table_cfg.codNazionaleField, '' )
            paramData['sezione'] = data.get( table_cfg.sezioneField, '' )
            

        ###################################################################
        #  Callback function
        ###################################################################
        
        def onComplete( successful ):
            # show documents dialog
            if callbackFn is not None:
                callbackFn( idKeyFeature, resData, lst_errors )
        
        def onFinishedServiceRequest( error, callbackData ):
            # check if error
            if error is not None:
                lst_errors.append( str(error) )
                return
            
            # store service result data
            serviceName = callbackData.get( 'serviceName', '' )
            serviceData = callbackData.get( 'serviceData', {} )
            serviceRowData = callbackData.get( 'servRowSelData', {} )
            dataKey = serviceRowData.get( 'dataKey', '' )
            resData[dataKey] = serviceData
            
            # check if summary data needed
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            summery_cfg = res_cfg.get( 'summmary', {} )
            summery_fields = summery_cfg.get( 'fields', [] )
            if summery_fields:
                summeries = {}
                
                # execute sum of current field
                for fieldName in summery_fields:
                    fldSum = 0.0
                    for data in serviceData:
                        try:
                            fldSum += data.get( fieldName, 0.0 )
                        except ValueError:
                            pass
                    # store sum
                    summeries[fieldName] = '{0:.4f}'.format(fldSum)
                    
                # store summery
                resData[dataKey + '_summery'] = summeries
            
        ###################################################################
        ###################################################################
        
        # get services config data
        service_cfg = agriConfig.get_value( 'agri_service', {} )
        resources_cfg = service_cfg.get( 'resources', {} )
        
        # get services to load
        cmd_cfg = self.controller.getCommandConfig( 'scaricaDatiParticella' )
        services = cmd_cfg.get('services', [])
        
        # collect all remaining service requests 
        reqColl = QGISAgriNetworkAccessManagerCollector()
        reqColl.finishedAllRequests.connect( onComplete )
   
        for serviceName in services:
            # initialize result data dictionary
            res_cfg = resources_cfg.get( serviceName, {} )
            warningCodes = res_cfg.get( 'warningDtoCodes', [] )
            datakey_cfg = res_cfg.get( 'dataKey', '' )
            resData[datakey_cfg] = []
            
            # import data service
            self.controller.onServiceRequest( 
                serviceName, 
                { 'dataKey': datakey_cfg },
                paramData, 
                onFinishedServiceRequest, 
                parent=None, 
                warningCodes=warningCodes,
                cache=False, 
                createSpinner=False,
                requestCollector=reqColl,
                silentError=True)
        
        # start all collected service requests    
        reqColl.endRequest()
     
    #---------------------------------------
    #
    #---------------------------------------
    def load_history_layers(self, gpkgFile: str) -> None:
        """ Loads Suoli history layer from Geopackage """ 
        from osgeo import ogr
        
        conn = None
        try:
            # init
            empty_lays = []
            controller = self.controller
            plugin = controller.plugin
            
            # get storico layers config
            storico_cfg = agriConfig.get_value( 'STORICO', clone=False )
            storico_crs_cfg =  storico_cfg.get( 'crs', '' )
            storico_lays_cfg = storico_cfg.get( 'layers' )
            
            # get layer group list
            storico_grp_cfg = storico_cfg.get( 'groups', [] ) or []
            QGISAgriLayers.create_toc_groups( storico_grp_cfg )
            
            # connect to Geopackage and loop layers
            conn = ogr.Open(gpkgFile)
            for lay in conn:
                # get layer config
                layer_cfg = storico_lays_cfg.get( lay.GetName(), {} )
                layer_grp = layer_cfg.get( 'tocgroup' )
                layer_ord = layer_cfg.get( 'tocorder', -1 )
                lay_exclude_ifempty = layer_cfg.get( 'excludeIfEmpty', False )
                style_file = layer_cfg.get( 'stylefile', '' ) or ''
                style_file = path.join( plugin.pluginStylePath, style_file )
                
                data_uri = "{0}|layername={1}".format( gpkgFile, lay.GetName() )
                ############vlayer = iface.addVectorLayer(data_uri, lay.GetName(), 'ogr')
                
                # create layer
                vlayer = QGISAgriLayers.add_toc_vectorlayer(
                    {
                        'path': gpkgFile,
                        'layerName': lay.GetName(),
                        'uri': data_uri
                    },
                    'ogr',
                    crs = storico_crs_cfg,
                    toc_lay_name = layer_cfg.get( 'tocname' ) or lay.GetName(),
                    toc_grp_name = layer_grp,
                    toc_grp_index = listUtil.index( storico_grp_cfg, layer_grp ),
                    toc_lay_order = layer_ord,
                    exclude_empty = lay_exclude_ifempty,
                    style_file = style_file,
                    show_total=False)
                
                if vlayer is None:
                    continue
                
                # check if empty
                if vlayer.hasFeatures() == QgsFeatureSource.NoFeaturesAvailable:
                    # exclude layer if empty
                    if lay_exclude_ifempty:
                        continue
                    
                    # collect empty layer to warning
                    if layer_cfg.get( 'checkIfEmpty', True ): 
                        empty_lays.append( vlayer.name() )
                
                # check if set as readonly
                vlayer.setReadOnly( layer_cfg.get( 'readonly', False ) )
                
                # check if set edit form fields as read only
                readonlyFields = layer_cfg.get( 'readonlyFields', None )
                if readonlyFields is not None:
                    QGISAgriLayers.layer_editFormFields_setReadOnly( vlayer, readonlyFields, read_only=True )
                
                # get 'anno campagna'
                annoCampagna = ''
                data = controller.getDbTableData( agriConfig.services.listaLavorazione.name  )
                if not data:
                    pass
                else:
                    annoCampagna = data[0].get( agriConfig.services.listaLavorazione.annoField, '' )
                
                # add custom widget to layer legend
                QgisAgriHistoryWidgetProvider.annoCampagna = annoCampagna
                QgisAgriHistoryWidgetProvider.addWidgetInstance( vlayer )
        finally:
            conn = None
        
    #---------------------------------------
    #
    #---------------------------------------
    def onDownloadHistory(self, reload: bool = False, callbackFn: Callable = None) -> None:
        """ Download Suoli history Geopackage """
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if not error:
                # check if valid data
                data = callbackData['serviceData']
                if not data:
                    raise ValueError( tr( 'Nessun dato scaricato' ) )
                
                # create history folder
                fileUtil.makedirs( gpkgPath )
                
                # save geopackage to file
                with open( gpkgFile, "wb" ) as f:
                    f.write( data )
                    
                # load geopackage layers
                self.load_history_layers( gpkgFile )
            
            #
            if callbackFn is not None:
                callbackFn( error, callbackData )
            
        ###########################################################################################
        ###########################################################################################
        
        try:
            # init
            serviceName = 'StoricoFoglioGeoPackage'
            controller = self.controller
            plugin = controller.plugin
            controlbox = plugin.controlbox
            data = {}
            servRowSelData = controlbox.currentFoglioData or {}
            
            
            # compose Geopackage full name
            gpkgPath = plugin.pluginHistoryPath
            gpkgFile = path.join( gpkgPath, plugin.pluginHistoryFileName )
            
            # check if geopackage already downloaded
            if fileUtil.fileExists( gpkgFile ):
                # check if reload file from API
                if not reload:
                    # load layers in map and TOC
                    self.load_history_layers( gpkgFile )
                    #
                    if callbackFn is not None:
                        callbackFn( None, data )
                    return
                
                # remove layers from old Geopackage
                lstLayIds = QGISAgriLayers.get_layers_id_by_filesource( gpkgFile )
                QgsProject.instance().removeMapLayers( lstLayIds )
            
            # call API to download history Geopackage
            controller.onServiceRequest( serviceName, 
                                         data, 
                                         servRowSelData, 
                                         callbackServiceFn, 
                                         parent=controlbox,
                                         agriResponseFormat=False )
            
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
    
    
    
    #---------------------------------------
    #
    #---------------------------------------
    def onBrowseDocumentazione(self, check_doc_existance=True, usr_data=None, removeNullParams=False):
        """Call service on external browser"""
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if error:
                return
            
            # get token
            token = str(callbackData.get('serviceData'), 'UTF8')
            
            # get service config
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            host_cfg = service_cfg.get('host', '')
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            browserUrl = res_cfg.get( 'browserUrl', '' )
            
            # compose url
            qHostUrl = QUrl(host_cfg)
            host = "{0}://{1}".format(qHostUrl.scheme(), qHostUrl.authority())
            params = dictUtil.merge( callbackData.get('servRowSelData', {}), { 'host': host, 'token': token } )
            browserUrl = browserUrl.strip().format(**params)
            if __PLG_DEBUG__:
                logger.log( logger.Level.Info, "Browser url: {0}".format( browserUrl ) )
            
            # call extenal browser
            QDesktopServices.openUrl( QUrl(browserUrl) )
                    
        ###########################################################################################
        ###########################################################################################
        
        try:
            
            # init
            usr_data = usr_data or {}
            serviceName = 'BrowseDocumentazione'
            controller = self.controller
            plugin = controller.plugin
            controlbox = plugin.controlbox
            
            #check if exists documentation
            if check_doc_existance:
                servRowSelData = controlbox.currentFoglioData
                if servRowSelData:
                    docFlag = servRowSelData.get( agriConfig.SERVICES.fogliAzienda.docFlagField, "" )
                    if docFlag != 'S':
                        logger.msgbox( logger.Level.Warning, tr( 'Documentazione mancante' ), title=tr('ERRORE') )
                        return
            
            # get azienda data from offline db table
            data = controller.getDbTableData( agriConfig.SERVICES.Aziende.name )
            if not data:
                raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
            data = list(data)[0]
            
            # add "codiceRuolo" data
            currentRole = controlbox.authenticationRole
            data["codiceRuolo"] = currentRole.codice
            
            # add custom data
            data = {**data, **usr_data}
            
            # log
            controller.log_command( serviceName )
            
            # call agri service to get an authentication token
            controller.onServiceRequest( serviceName, 
                                         data, 
                                         None, 
                                         callbackServiceFn, 
                                         parent=controlbox, 
                                         agriResponseFormat=False,
                                         removeNullParams=removeNullParams )
            
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
    
    #---------------------------------------
    #
    #---------------------------------------
    def onBrowseContraddizioni(self):
        """Call 'contraddittori e sopralluoghi' service on external browser"""
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if error:
                return
            
            # get token
            token = str(callbackData.get('serviceData'), 'UTF8')
            
            # get service config
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            host_cfg = service_cfg.get('host', '')
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            browserUrl = res_cfg.get( 'browserUrl', '' )
            
            # compose url
            qHostUrl = QUrl(host_cfg)
            host = "{0}://{1}".format(qHostUrl.scheme(), qHostUrl.authority())
            params = dictUtil.merge( callbackData.get('servRowSelData', {}), { 'host': host, 'token': token } )
            browserUrl = browserUrl.strip().format(**params)
            if __PLG_DEBUG__:
                logger.log( logger.Level.Info, "Browser url: {0}".format( browserUrl ) )
            
            # call extenal browser
            QDesktopServices.openUrl( QUrl(browserUrl) )
                    
        ###########################################################################################
        ###########################################################################################
        
        try:
            
            # init
            serviceName = 'BrowseContraddizioni'
            controller = self.controller
            plugin = controller.plugin
            controlbox = plugin.controlbox
            
            # get azienda data from offline db table
            data = controller.getDbTableData( agriConfig.SERVICES.Aziende.name )
            if not data:
                raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
            data = list(data)[0]
            
            # add "codiceRuolo" data
            currentRole = controlbox.authenticationRole
            data["codiceRuolo"] = currentRole.codice
            
            # log
            controller.log_command( serviceName )
            
            # call agri service to get an authentication token
            controller.onServiceRequest( serviceName, 
                                         data, 
                                         None, 
                                         callbackServiceFn, 
                                         parent=controlbox, 
                                         agriResponseFormat=False )
            
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
    
    #--------------------------------------
    # 
    # --------------------------------------
    def zoomToPhotoAppezzamento(self, photoId ):
        """ Zoom to photo feature """
        # init
        photoId = photoId or ''
        if not photoId:
            return 
        
        # get command config
        cmd_cfg = self.controller.getCommandConfig( 'browsePhotoProposti' )
        id_photo_fld = cmd_cfg.get( 'idField', '' )
        if not id_photo_fld:
            return
        
        # get photo layers
        photo_layers = self.controller.get_suolo_vector_layers( 'browsephotoproposti' )
        if not photo_layers:
            return
        
        #
        extent = None
        features = []
        photo_layer = None
        featureExpression = '"{}"={}'.format( id_photo_fld, photoId )
        
        # loop all photo layers
        for layer in photo_layers:
            # create coordinate transformer 
            p = QgsProject.instance()
            ct = QgsCoordinateTransform( layer.sourceCrs(), p.crs(), p )
            
            # get features by expression
            for feat in layer.getFeatures( featureExpression ):
                features.append( feat.id() )
                # get feature bounding box
                geom = feat.geometry()
                bbox = ct.transformBoundingBox( geom.boundingBox() )  
                if extent is None:
                    extent = bbox
                else:
                    extent.combineExtentWith( bbox )
                    
            # break loop if feature found for current layer
            if extent is not None:
                photo_layer = layer
                break
              
        # zoom to photo features      
        if extent is not None:
            extent.grow( 10 )
            canvas = self.controller.plugin.iface.mapCanvas()
            canvas.setExtent( extent )
            canvas.refresh()
            ##if features is not None:
            ##    canvas.flashFeatureIds( photo_layer, features, flashes=1, duration=1000 )
        
    
    #--------------------------------------
    # 
    # --------------------------------------     
    def onDownloadAppezzamentiPhoto(self, id_photo_fld, lst_photo_ids, use_internal_viewer, clear_tabs=True):
        """ Download suolo proposto photos """ 
        
        ###########################################################################################
        ###########################################################################################
        def callbackDownloadFn( error, callbackData ):
            
            # check if error
            if error:
                return
            
            # write downloaded data to temp file and open doc
            try:          
                # get data
                data = callbackData.get( 'serviceData', None )
                if data is None:
                    return
                
                # get file name from header
                docFile = 'foto.jpg'
                reply_headers = callbackData.get( 'headers', {} )
                replay_content = reply_headers.get( 'Content-Disposition', '' )
                values = replay_content.split( 'filename=' )
                if len(values) > 1:
                    docFile = values[1].strip().split( ';' )[0]
                
                # write dato to temp file
                tmpFilePath = self.controller.plugin.networkAccessManager.writeDataToFile( 
                    data, docFile, asTempFile=True )
                
                # show viewer
                if use_internal_viewer:
                    dlg = self.controller.plugin.photodlg
                    dlg.showImage( clear_tabs= service_data.get('clear_tabs', False) )         
                    dlg.loadImage( tmpFilePath,
                                   docFile,
                                   sorted_tab= True,
                                   orig_img_file= True,
                                   photoId= service_data.get( id_photo_fld ) )

                    #fileUtil.removeFile( tmpFilePath )
                    service_data['clear_tabs'] = False
                
                else: 
                    # open document
                    QDesktopServices.openUrl( QUrl.fromLocalFile(tmpFilePath) )
                    
                    
            except Exception as e:
                logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )

        ###########################################################################################
        ###########################################################################################
        
        # init
        serviceName = 'ScaricaAppezzamentiPhoto'
        service_data = {
            'clear_tabs': True
        }
        lst_photo_ids = lst_photo_ids or []
        
        # loop photo id list
        for photo_id in lst_photo_ids:
            service_data[id_photo_fld] = photo_id
            # call service api
            self.controller.onServiceRequest( serviceName, 
                                              service_data, 
                                              None, 
                                              callbackDownloadFn,
                                              agriResponseFormat=False,
                                              cache=True,
                                              createSpinner=False )

    #---------------------------------------
    #
    #---------------------------------------
    def onDownloadValidationsPCG(self):
        """ Downloads PCG validations """
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if error:
                return
            
            # get data
            data = callbackData.get('serviceData') or []
            
            # get layers already loaded
            _, lst_uri = self.get_pcg_layers()
            lst_id_validation = [ fileUtil.basenameWithoutExt(u).split('_')[-1] for u in lst_uri ] 
           
            # loop items
            for item in data:
                # check if already loaded
                id_validation = str( item.get( id_field, '' ) )
                item[loaded_field] = int( id_validation in lst_id_validation )
                
                # format date as new attribute
                for fld_name, fld_def in conv_date_fields.items(): 
                    new_fld_name = fld_def.get( 'newFieldName', '__data' )
                    formats = fld_def.get( 'formats', '%d/%m/%Y' )
                    item[new_fld_name] = objUtil.datetime_from_str( item.get( fld_name, '' ), formats, no_excption=True )
            
            # sort data
            data = listUtil.multikeysort( data, sort_fields )
            
            # show dialog
            self.__pcgDlg = dlg = QGISAgriItemSelectionDialog( plugin.iface.mainWindow() )
            dlg.setWindowTitle( f"{__QGIS_AGRI_NAME__} - {tr('Validazioni del Piano Colturale Grafico')}" )
            dlg.setModal( True )
            dlg.setData( data, 'LeggiValidazioniAzienda' )
            dlg.resize( 800, 400 )
            dlg.itemSelected.connect( self.onDownloadPCG )
            dlg.show()
            
                    
        ###########################################################################################
        ###########################################################################################
        
        try:
            # init dEventoLavorazione
            serviceName = 'LeggiValidazioniAzienda'
            controller = self.controller
            plugin = controller.plugin
            controlbox = plugin.controlbox
            
            # get service config
            service_cfg = agriConfig.get_value( f'agri_service/resources/{serviceName}', {} )
            sort_fields = service_cfg.get( 'sortByFields', [] )
            conv_date_fields = service_cfg.get( 'convertAsDatetime', {} )
            data_fields_cfg = service_cfg.get( 'dataFields', {} )
            loaded_field = data_fields_cfg.get( 'loadedField', '__loaded' )
            id_field = data_fields_cfg.get( 'id', 'idDichiarazioneConsistenza' )
       
            # get azienda data from offline db table
            data = controller.getDbTableData( agriConfig.SERVICES.Aziende.name )
            if not data:
                raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
            data = list(data)[0]
            
            # call agri service to get list of PCG validations
            controller.onServiceRequest( serviceName, 
                                         data, 
                                         None, 
                                         callbackServiceFn, 
                                         parent=controlbox )
        
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
    
    
    #---------------------------------------
    #
    #---------------------------------------
    def get_pcg_layers(self):
        # init
        pcg_layers_uri = []
        pcg_layers = []
        controller = self.controller
        plugin = controller.plugin
        jsonPath = plugin.pluginHistoryPath
        jsonFileExpr = path.normpath( path.join( jsonPath, 'PCG_' ) )
        rgx = re.compile( '^' + re.escape( jsonFileExpr ) + '.*\.geojson' )
        
        # loop layers
        layers = QgsProject.instance().mapLayers()
        for _, layer in layers.items():
            uri = QGISAgriLayers.get_data_source_file_path( layer )
            if rgx.match( uri ):
                pcg_layers.append( layer )
                pcg_layers_uri.append( uri )
                
        # return pcg layers
        return pcg_layers, pcg_layers_uri
    
    #---------------------------------------
    #
    #---------------------------------------
    def get_cxf_layers(self):
        # init
        pcg_layers_uri = []
        pcg_layers = []
        controller = self.controller
        plugin = controller.plugin
        jsonPath = plugin.pluginHistoryPath
        jsonFileExpr = path.normpath( path.join( jsonPath, 'CXF_' ) )
        rgx = re.compile( '^' + re.escape( jsonFileExpr ) + '.*\.geojson' )
        
        # loop layers
        layers = QgsProject.instance().mapLayers()
        for _, layer in layers.items():
            uri = QGISAgriLayers.get_data_source_file_path( layer )
            if rgx.match( uri ):
                pcg_layers.append( layer )
                pcg_layers_uri.append( uri )
                
        # return pcg layers
        return pcg_layers, pcg_layers_uri
    
    #---------------------------------------
    #
    #---------------------------------------
    def load_geojson_layer(self, 
                           jsonFile: str, 
                           lay_name: str, 
                           cfg_section: str,
                           node_expanded: bool=True,
                           activate_layer: bool=True) -> None:
        """ Loads layer from a GeoJSON file """ 
        
        # init
        lay_name = str(lay_name)
        controller = self.controller
        plugin = controller.plugin
        cfg_section = str(cfg_section)
        curr_layer = plugin.iface.activeLayer()
        
        # load GeoJSON file
        geoJsonData = {}
        with open( jsonFile ) as f:
            geoJsonData = json.load( f )
        if not geoJsonData:
            raise Exception( tr("File GeoJSON non valorizzato") )
        
        # get layer config
        odb_cfg =  agriConfig.get_value( cfg_section.split( '/' )[0], {} )
        layer_crs =  odb_cfg.get( 'crs', 'EPSG:3003' )
        if isinstance( layer_crs, dict ):
            layer_crs =  odb_cfg.get( 'layer', 'EPSG:3003' )
        
        layer_cfg = agriConfig.get_value( cfg_section )
        layer_name = lay_name or layer_cfg.get( 'tocname', 'UNKNOWN' )
        layer_grp = layer_cfg.get( 'tocgroup' )
        layer_ord = layer_cfg.get( 'tocorder' )
        style_file = layer_cfg.get( 'stylefile', '' ) or ''
        style_file = path.join( plugin.pluginStylePath, style_file )
        
        # get layer group list
        layer_group_cfg = odb_cfg.get( 'groups', [] ) or []
        # create layer group
        QGISAgriLayers.create_toc_groups( layer_group_cfg )
        
        # create layer
        vlayer = QGISAgriLayers.add_toc_vectorlayer(
            {
                'path': jsonFile,
                'layerName': layer_name,
                'uri': jsonFile
            },
            'ogr',
            crs = layer_crs,
            toc_lay_name = layer_name,
            toc_grp_name = layer_grp,
            toc_grp_index = listUtil.index( layer_group_cfg, layer_grp ),
            toc_lay_order = layer_ord,
            ##exclude_empty = lay_exclude_ifempty,
            style_file = style_file,
            show_total = False,
            node_expanded = node_expanded )
        
        if vlayer is None:
            raise Exception( f"{tr('Impossibile creare il livello')} {lay_name}" )
        
        # set as readonly
        vlayer.setReadOnly( True )
        readonlyFields = layer_cfg.get( 'readonlyFields', None )
        if readonlyFields is not None:
            QGISAgriLayers.layer_editFormFields_setReadOnly( vlayer, readonlyFields, read_only=True ) 
            
        # update PCG plugin action
        ##_, lst_uri = self.get_pcg_layers()
        ##plugin.PcgAction.changeRefLayers( lst_uri )
        
        # set as active layer
        if activate_layer:
            plugin.iface.setActiveLayer( vlayer )
        elif curr_layer:
            plugin.iface.setActiveLayer( curr_layer )
        
        # check if no geometries
        if vlayer.hasFeatures() == QgsFeatureSource.NoFeaturesAvailable:
            logger.msgbox( 
                logger.Level.Warning, 
                tr( 'Scaricato un livello vettoriale senza geometria' ), 
                title=tr('ERRORE') )
          
    #---------------------------------------
    #
    #---------------------------------------
    def onDownloadPCG(self, pcg_val_data):
        """ Downloads and load PCG """
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if not error:
                # check if valid data
                data = callbackData['serviceData']
                if not data:
                    raise ValueError( tr( 'Nessun dato scaricato' ) )
                
                # slit a GeoJSON on geometry multipat type
                geojsonHelper = geoJsonHelper()
                geoJsonColl = geojsonHelper.splitOnGeomType( data, asMultipart=True )
                data = geoJsonColl['MultiPolygon']
                if not data:
                    raise ValueError( tr( 'Nessun dato scaricato' ) )
                
                # get command config
                cmd_cfg = controller.getCommandConfig( 'scaricaDatiPCG' )
                fid_fld_name = cmd_cfg.get( 'idKeyField', 'OGC_FID' ) 
                
                # add FID attribute
                data = geojsonHelper.addFid( data, fid_fld_name )
                
                # add validation data
                data = geojsonHelper.addProperty( data, 'dati_validazione', pcg_val_data )
                
                # create GeoJSON file folder
                fileUtil.makedirs( jsonPath )
                
                # save GeoJSON file
                with open( jsonFile, "w" ) as f:
                    json.dump( data, f, cls=JsonDateTimeEncoder )
                    
                # load GeoJSON layer
                self.load_geojson_layer( jsonFile, layer_name, cfg_section='PCG/layers/pcg' )
        ###########################################################################################
        ###########################################################################################
        
        try:
            # init
            serviceName = 'LeggiAppezzamentiScheda'
            controller = self.controller
            plugin = controller.plugin
            controlbox = plugin.controlbox
            pcg_val_data = pcg_val_data[0] if pcg_val_data else {}
            data = pcg_val_data
            
            # get service config
            service_cfg = agriConfig.get_value( 'agri_service/resources/LeggiValidazioniAzienda', {} )
            data_fields_cfg = service_cfg.get( 'dataFields', {} )
            id_field = data_fields_cfg.get( 'id', 'idDichiarazioneConsistenza' )
            name_field = data_fields_cfg.get( 'data', '' )
            layer_name = data.get( name_field, '' )
            
            # get azienda data from offline db table
            az_data_rows = controller.getDbTableData( agriConfig.SERVICES.Aziende.name )
            if not az_data_rows:
                raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
           
            data = dictUtil.merge( pcg_val_data, list(az_data_rows)[0] )
            
            # get selected 'foglio' data
            rowSelData = controlbox.currentFoglioData
            if not rowSelData:
                raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il foglio corrente"), serviceName ) )
            
            # get id PCG validation
            id_pcg = data.get( id_field )
            
            # compose GeoJSON full name
            jsonPath = plugin.pluginHistoryPath
            jsonFile = path.join( jsonPath, f'PCG_{id_pcg}.geojson' )
            jsonFilePath = path.normpath( path.join( jsonPath, jsonFile ) )
            
            # check if layer already loaded
            _, lay_uri_lst = self.get_pcg_layers()
            if jsonFilePath in lay_uri_lst:
                return
            
            # check if GeoJSON already downloaded
            if fileUtil.fileExists( jsonFile ):
                # load GeoJSON layer
                self.load_geojson_layer( jsonFile, layer_name, cfg_section='PCG/layers/pcg' )
                return
            
            # call agri service to get list of PCG validations
            controller.onServiceRequest( serviceName, 
                                         data, 
                                         rowSelData, 
                                         callbackServiceFn, 
                                         parent=controlbox )
        
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
        
    
    #---------------------------------------
    #
    #---------------------------------------
    def onDownloadCXF(self) -> None:
        """ Download CXF geometry - PARTICELLE working """
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            # check if error
            if not error:
                # check if valid data
                data = callbackData['serviceData']
                if not data:
                    raise ValueError( tr( 'Nessun dato scaricato' ) )
                
                # slit a GeoJSON on geometry multipat type
                geojsonHelper = geoJsonHelper()
                geoJsonColl = geojsonHelper.splitOnGeomType( data, asMultipart=True )
                data = geoJsonColl['MultiPolygon']
                if not data:
                    raise ValueError( tr( 'Nessun dato scaricato' ) )
                
                # get command config
                cmd_cfg = controller.getCommandConfig( 'scaricaDatiCXF' )
                fid_fld_name = cmd_cfg.get( 'idKeyField', 'OGC_FID' ) 
                
                # add FID attribute
                data = geojsonHelper.addFid( data, fid_fld_name )
                
                # create GeoJSON file folder
                fileUtil.makedirs( cxfPath )
                
                # save GeoJSON file
                with open( cxfFile, "w" ) as f:
                    json.dump( data, f, cls=JsonDateTimeEncoder )
                    
                # load GeoJSON layer
                self.load_geojson_layer( 
                    cxfFile, layer_name, cfg_section=cfg_section, node_expanded=False, activate_layer=False )
            
        ###########################################################################################
        ###########################################################################################
        
        try:
            # init
            serviceName = 'CxfParticelle'
            cfg_section ='ODB/layers/particelle_cxf'
            controller = self.controller
            plugin = controller.plugin
            controlbox = plugin.controlbox
            data = {}
            rowSelData = {}
            
            # get PARTICELLE data from offline db table
            part_data_rows = controller.getDbTableData( agriConfig.SERVICES.ParticelleLavorazioni.name )
            if not part_data_rows:
                raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
           
            data = dictUtil.merge( data, list(part_data_rows)[0] )
            codiceNazionale = data.get( agriConfig.SERVICES.ParticelleLavorazioni.codNazionaleField )
            foglio = data.get( agriConfig.SERVICES.ParticelleLavorazioni.foglioField )
            
            
            # compose GeoJSON full name
            cxfPath = plugin.pluginHistoryPath
            cxfFile = path.join( cxfPath, f'CXF_{foglio}_{codiceNazionale}.geojson' )
            layer_name = 'CXF'
            
            # check if GeoJSON already downloaded
            if fileUtil.fileExists( cxfFile ):
                # load GeoJSON layer
                self.load_geojson_layer( 
                    cxfFile, layer_name, cfg_section=cfg_section, node_expanded=False, activate_layer=False )
                return
            
            # call API to download history Geopackage
            controller.onServiceRequest( serviceName, 
                                         data, 
                                         rowSelData, 
                                         callbackServiceFn, 
                                         parent=controlbox )
            
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            
            
    #---------------------------------------
    #
    #---------------------------------------
    def onDownloadAllegatiParticelle(self):
        """ Downloads download and show PARTICELLE allegati list """
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if error:
                return
            
            # get data
            data = callbackData.get('serviceData') or []
            
            # show dialog
            self.__allSelDlg = dlg = QGISAgriItemSelectionDialog( plugin.iface.mainWindow() )
            dlg.setWindowTitle( f"{__QGIS_AGRI_NAME__} - {tr('Elenco allegati Particelle')}" )
            dlg.setModal( True )
            dlg.resize( 800, 400 )
            dlg.setMultipleSelectionMode( True )
            dlg.setData( data, 'ElencoAllegatiParticella' )
            dlg.itemSelected.connect( self.onShowAllegatoParticella )
            dlg.show()
                    
        ###########################################################################################
        ###########################################################################################
        
        try:
            # init
            serviceName = 'ElencoAllegatiParticella'
            controller = self.controller
            plugin = controller.plugin
            controlbox = plugin.controlbox
            data = {}
            
            # get PARTICELLE data from offline db table
            part_data_rows = controller.getDbTableData( agriConfig.SERVICES.ParticelleLavorazioni.name )
            if not part_data_rows:
                raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
            data = dictUtil.merge( data, list(part_data_rows)[0] )
            
            # call agri service to get list of PCG validations
            controller.onServiceRequest( serviceName, 
                                         data, 
                                         None, 
                                         callbackServiceFn, 
                                         parent=controlbox )
            
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
        
        
    #---------------------------------------
    #
    #---------------------------------------
    def onShowAllegatoParticella(self, allegati_data):
        """ Downloads and show Allegato PARTICELLA """
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if error:
                return
            
            # write downloaded data to temp file and open doc
            try:     
                # get data
                data = callbackData.get( 'serviceData', None )
                if data is None:
                    return
                
                selRowData = callbackData.get( 'servRowSelData', None )
                if selRowData is None:
                    return
                
                # get file name
                imgFile = selRowData.get( file_name_field, '')
                imgName = selRowData.get( logic_name_field, '' )
                imgFile = imgFile or imgName
                imgName = path.basename( imgName or imgFile )
                
                # write data to temp file
                tmpFilePath = self.controller.plugin.networkAccessManager.writeDataToFile( 
                    data, imgFile, asTempFile=True )
                
                # get file extension
                split_tup = path.splitext( str(tmpFilePath) )
                file_extension = split_tup[1].lstrip( '.' ).lower()
                
                # check if image supported format
                if file_extension not in QImageReader.supportedImageFormats():
                    # open document
                    QDesktopServices.openUrl( QUrl.fromLocalFile(tmpFilePath) )
                    
                # show viewer
                elif use_internal_viewer:
                    dlg = plugin.particelle.allegatiDlg
                    dlg.showImage( clear_tabs= service_data.get('clear_tabs', False) )         
                    dlg.loadImage( tmpFilePath,
                                   imgName,
                                   sorted_tab= True,
                                   orig_img_file= True )

                    #fileUtil.removeFile( tmpFilePath )
                    service_data['clear_tabs'] = False
                
                else: 
                    # open document
                    QDesktopServices.openUrl( QUrl.fromLocalFile(tmpFilePath) )
                    
                    
            except Exception as e:
                logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
        ###########################################################################################
        ###########################################################################################
        
        try:
            # init
            serviceName = 'AllegatoParticella'
            controller = self.controller
            plugin = controller.plugin
            controlbox = plugin.controlbox
            allegati_data = allegati_data or []
            service_data = {
                'clear_tabs': True
            }
            
            # get document field
            cmd_cfg = controller.getCommandConfig( 'browseAllegatiParticelle' )
            use_internal_viewer = cmd_cfg.get( 'useInternalViewer', True )
            logic_name_field = str( cmd_cfg.get( 'logicNameField', '' ) ).strip()
            file_name_field = str( cmd_cfg.get( 'fileNameField', '' ) ).strip()
            
            # get PARTICELLE data from offline db table
            part_data_rows = controller.getDbTableData( agriConfig.SERVICES.ParticelleLavorazioni.name )
            if not part_data_rows:
                raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
            part_data = list(part_data_rows)[0]
            
            # loop allegati selected
            for allegato_data in allegati_data:
                data = dictUtil.merge( allegato_data, part_data )
                # call agri service to get Allegato Particella image
                controller.onServiceRequest( serviceName, 
                                             data, 
                                             None, 
                                             callbackServiceFn, 
                                             parent=controlbox,
                                             agriResponseFormat=False,
                                             cache=True,
                                             createSpinner=False )
        
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
    
    