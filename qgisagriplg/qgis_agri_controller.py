# -*- coding: utf-8 -*-
"""Plugin controller

Description
-----------

Defines the plugin controller class; manages:

- plugin base activities;
- interactions on the data model objects;
- interactions on user editining;
- implements plugin commands;

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
import os.path
import json
import copy

# qgis modules import
###from qgis.PyQt import QtGui, QtWidgets, uic, Qt
###from qgis.PyQt.QtCore import pyqtSignal
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import Qt, QByteArray, QTimer, QUrl
from PyQt5.QtWidgets import QMessageBox

from qgis.core import ( NULL,
                        Qgis,
                        QgsProject,
                        QgsMapLayer,
                        QgsGeometry, 
                        QgsDataSourceUri, 
                        QgsFeatureSource,
                        QgsEditFormConfig,
                        QgsExpression,
                        QgsVectorLayerUtils,
                        QgsFeatureRequest )

# plugin modules import
from qgis_agri import __PLG_DB3__, __PLG_DEBUG__, tr, QGISAgriMessageLevel
from qgis_agri import agriConfig
from qgis_agri.util.signals import signalUtil 
from qgis_agri.util.list import listUtil
from qgis_agri.util.dictionary import dictUtil
from qgis_agri.util.exception import formatException
from qgis_agri.qgis_agri_exceptions import QGISAgriException
from qgis_agri.util.file import fileUtil
from qgis_agri.util.json import jsonUtil
from qgis_agri.util.geojson import geoJsonHelper
from qgis_agri.util.layer import LayerVirtualizer
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.db.db_spatialite_database import SpatialiteDatabase
from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.gui.file_witer_util import QGISAgriVectorFileWrite
from qgis_agri.qgis_agri_errors import QGISAgriFeatureErrors
from qgis_agri.qgis_agri_identify_dlg import QGISAgriIdentifyDialogWrapper
from qgis_agri.service.qgis_agri_networkaccessmanager import ( QGISAgriNetworkAccessManagerCollector, 
                                                               QGISAgriRequestError )
from qgis_agri.qgis_agri_checker import QGISAgriChecker
from qgis_agri.qgis_agri_controller_event import QGISAgriControllerEvent


#
#-----------------------------------------------------------
def formIdentifyOpen(dialog, layer, feature):
    """ Function called when feature attibute form is required """ 
    # Create class to manage Feature Form interaction
    _ = QGISAgriIdentifyDialogWrapper( dialog, layer, feature )


#
#-----------------------------------------------------------
class QGISAgriController:
    """Class to control QGISAgri plugin"""
    
    # constants
    DB_OFFLINE_NAME = "agri_offline.sqlite"
    DB_OFFLINE_PATH_KEY = "offline_db"
    DB_ID_EV_LAVORAZIONE_KEY = "idEventoLavorazione"
    DB_SUOLI_TRIGGER_KEY = "enable_trigger_suoli_bloccati_update"
    MAIN_SUOLO_LAYER_PROP = "agri_main_suolo_layer"
    COMMIT_SUOLO_LAYER_PROP = "agri_main_commit_layer_status"
    SAVING_LAYER_NAME = "SalvaSuoli"
    USER_CANCEL = 0
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, plugin):
        """Constructor"""
        
        # Save reference to the QGIS interface
        self.__plugin = plugin
        self.__odb = None
        self.__odb_path = None
        self.__odb_main_path = None
        self.__odb_ref = 0
        self.__checker = QGISAgriChecker( plugin )
        self.__ev_controller = QGISAgriControllerEvent( self )
        
        # dictionary original geometries
        self.__added_suoli_features = []
        self.__suoli_main_layer_uri = []
        self.__suoli_snap_layer_uri = []
        self.__updateLayerFeatureCountLst = []
        self.__sfondoByAttrib = None
        self.__enableUpdateSuoliFlags = True 
        self.__skipSuoloLavoratoFeatureFid = []
        self.__idEventoLavorazione = None
        self.__isOfflineFoglio = False
        
        self.__srv_last_data = None
        
        # signal\slot
        self.__editingStopped_enabled = True
              
        # initialize suoli attribute dialog
        QGISAgriIdentifyDialogWrapper.initialize( self.__plugin )
        
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
    def plugin(self):
        """ Returns plugin instance (readonly) """
        return self.__plugin
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def checker(self):
        """ Returns agri checker object instance (readonly) """
        return self.__checker 
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def event_controller(self):
        """ Returns agri event controlle object instance (readonly) """
        return self.__ev_controller
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def mainDatabase(self):
        """Returns database (file path)"""
        if self.__odb_main_path is None:
            odb_cfg = agriConfig.get_value('ODB')
            odb_database_cfg = odb_cfg.get( 'database', self.DB_OFFLINE_NAME )
            self.__odb_main_path =  os.path.join( self.plugin.pluginDataPath, odb_database_cfg )
            
        return self.__odb_main_path
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def database(self):
        """Returns offline database (file path)"""
        if self.__odb_path is None:
            self.__odb_path = self.mainDatabase
            # check if present a clone db (that substitute the template one)
            offlineDbPath = self._repair_clone_db()
            if offlineDbPath:
                self.__odb_path = offlineDbPath
                self.plugin.emit_db_rebase()
                
        return self.__odb_path
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def isEditingStoppedSlotEnabled(self):
        """Returns true if editing Stopped is enabled"""
        return self.__editingStopped_enabled
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def isOfflineDb(self):
        """Returns true if cloned offline db"""
        return (self.database is not None and
                self.__odb_main_path is not None and
                self.database.lower() != self.__odb_main_path.lower())
                
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def isOfflineFoglio(self):
        """Returns true if cloned offline db"""
        return ( self.isOfflineDb and self.__isOfflineFoglio )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property            
    def idEventoLavorazione(self):
        """ Returns 'Evento Lavorazione' id, if offline """
        return self._getIdEventoLavorazione()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property            
    def suoliSnapLayerUris(self):
        """ Returns snap reference layer uri """
        return self.__suoli_snap_layer_uri
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property            
    def lastServiceData(self):
        """ Returns last service downloaded data """
        return self.__srv_last_data
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def enable_EditingStoppedSlot(self, enable=True, update_layers=None):
        """Enable\\disable slot for 'editing stopped' signal"""
        update_layers = update_layers or []
        self.__editingStopped_enabled = enable
        # update edited layer
        if update_layers and enable:
            for layer in update_layers:
                self.editingSuoliStopped( layer )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def log_command(self, cmd):
        """Log starting command in QGIS """
        logger.log_info( "--- {0}: {1} ---".format( tr('Avvio comando'), str(cmd) ) )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _set_custom_forms(self, layer):
        # define a custom  layer attribute form
        if QGISAgriLayers.is_requested_vectorlayer(layer, self.__suoli_main_layer_uri):
            file_ui = os.path.join( self.plugin.pluginUiPath, "qgis_agri_attributes_dialog.ui" )
            file_init = os.path.join( self.plugin.pluginPath, "qgis_agri_controller.py" )
            editForm = layer.editFormConfig()
            editForm.setUiForm( file_ui )
            editForm.setInitCodeSource( QgsEditFormConfig.CodeSourceFile )
            editForm.setInitFilePath( file_init )
            editForm.setInitFunction( "formIdentifyOpen" )
            layer.setEditFormConfig( editForm )
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _repair_clone_db(self):
        """Repair clone offline db"""
        
        # get offline db path file from main db settings table
        offlineDBpath = str( self._getDbSetting( self.DB_OFFLINE_PATH_KEY ) ).strip()
        if not offlineDBpath:
            return ''
        
        # check if offline db file exists
        if fileUtil.fileExists( offlineDBpath ):
            return offlineDBpath
        
        # emit error message
        logger.msgbox( 
            logger.Level.Critical, 
            tr( 'Database offline non reperito!\nRipristino delle configurazioni di DB.' ), 
            title=tr('ERRORE') )
        
        # re get offline db path file from main db settings table
        offlineDBpath = str( self._getDbSetting( self.DB_OFFLINE_PATH_KEY ) ).strip()
        if not offlineDBpath:
            return ''
        if fileUtil.fileExists( offlineDBpath ):
            return offlineDBpath
       
        # reset main db settings table
        self._setDbSetting( { 
            self.DB_OFFLINE_PATH_KEY: '', 
            self.DB_ID_EV_LAVORAZIONE_KEY: '' 
        } )
        self.__idEventoLavorazione = None
        
        return ''
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _create_clone_db(self):
        """Create a cloned offline db"""
        # check if db already cloned
        if self.isOfflineDb:
            raise Exception( tr('Database offline già creato') )
        
        # clone db
        dbFile = self.database
        with fileUtil.createTemporaryCopy( dbFile , directory=self.plugin.pluginDataPath, delete=False, suffix='_{}'.format( self.DB_OFFLINE_NAME ) ) as cloneDB:
            # store cloned DB path
            self._setDbSetting( { self.DB_OFFLINE_PATH_KEY: cloneDB.name } )
            
            # reset db refernces
            self._disconnect_db( reset=True )
            self.__odb = None
            self.__odb_path = None
            dbFile = self.database # call to refresh internal members
            self.plugin.emit_db_rebase()
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _removeFile(self, filePath):
        """Remove file with delay"""
        try:
            fileUtil.removeFile( filePath )
        except OSError as e:
            logger.log_warning( formatException(e) )
            
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _disconnect_clone_db(self):
        """Remove cloned offline db"""
        dbCloneFile = None
        
        if self.isOfflineDb and not self.__isOfflineFoglio:
            try:
                # get cloned offline db path
                dbCloneFile = self.database
                # reset cloned DB path
                self._disconnect_db( reset=True )
                self._connect_db( mainDb=True )
                self._setDbSetting( { 
                    self.DB_OFFLINE_PATH_KEY: '', 
                    self.DB_ID_EV_LAVORAZIONE_KEY: '' 
                } )
                self.__isOfflineFoglio = False
                self.__idEventoLavorazione = None
                dbMainFile = self.database # call to refresh internal members
                if not dbMainFile:
                    pass
                self.plugin.emit_db_rebase()
            finally:
                self._disconnect_db( reset=True )
                
        # return db clone file name
        return dbCloneFile
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def _connect_db(self, mainDb=False):
        """ Create connection to offline DB. """
        # connnect always to main db
        if mainDb:
            if self.isOfflineDb:
                self._disconnect_db( reset=True )
            uri = QgsDataSourceUri()
            self.__odb_path = self.mainDatabase
            uri.setDatabase( self.__odb_path )
            self.__odb = SpatialiteDatabase(uri)
        
        # create DB connection
        if self.__odb is None:
            # pylint: disable=E1101
            uri = QgsDataSourceUri()
            uri.setDatabase(self.database)
            self.__odb = SpatialiteDatabase(uri)
         
        # increment db reference counter
        self.__odb_ref = self.__odb_ref + 1
        
        return self.__odb
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _disconnect_db(self, reset=False):
        """ Disconnect offline DB. """
        self.__odb_ref = 0 if reset else (self.__odb_ref -1)
        self.__odb_ref = 0 if self.__odb_ref < 1 else self.__odb_ref
        if self.__odb is None:
            return
        elif self.__odb_ref > 0:
            return    
        try:
            self.__odb.close()
        except Exception as e:
            logger.log_warning( str(e) )
        finally:
            self.__odb = None
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _prepare_db(self, scriptName):
        """Initialize db schema"""
        
        # get script list from config
        scriptLst = agriConfig.get_value( 'ODB/scripts/{0}'.format( scriptName ), [] )
        if not scriptLst:
            return
        
        try:
            # create connection
            conn = self._connect_db().getConnector()
            
            # execute scripts
            sqlPath = self.plugin.pluginSqlPath
            for script in scriptLst:
                scriptPath = os.path.join( sqlPath, str(script) )
                try:
                    conn.executeScript( sqlFile=scriptPath )
                except Exception as e:
                    # handle exception
                    logger.msgbox( 
                        logger.Level.Critical, 
                        "{} '{}': {}".format( tr('Errore nello script'), scriptName, formatException(e) ), 
                        title=tr('ERRORE') )
    
        finally:
            self._disconnect_db()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _getIdEventoLavorazione(self):
        """ Returns 'Evento Lavorazione' id, if offline """
        
        try:
            # check if offline db
            if not self.isOfflineDb:
                return None
            
            # check if already defined
            if self.__idEventoLavorazione is not None:
                return self.__idEventoLavorazione
                
            # get from offline DB
            idEventoLav = self._getDbSetting( self.DB_ID_EV_LAVORAZIONE_KEY )
            if idEventoLav is not None:
                return int(idEventoLav)
                
            # get from 'agenzia' service table
            serviceCfg = agriConfig.services.aziende
            serviceData = self.plugin.controlbox.serviceStoreModel
            rec = serviceData[ serviceCfg.name ].getRow( 0, {} )
            idEventoLav = rec.get( serviceCfg.idEvLavField, None )
            if idEventoLav is not None:
                return int(idEventoLav)
            
            # no 'Evento Lavorazione' id found    
            raise Exception( tr( "Id evento di lavorazione non definito!" ) )
        
        except Exception as e:
            # handle exception
            logger.msgbox( logger.Level.Critical, "Id evento di lavorazione.\n{0}".format( formatException(e) ), title=tr('ERRORE') )
            return None
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def _getIsFoglioLavorazione(self):
        """ Check if there is a working 'foglio' """
        if not self.isOfflineDb:
            return False
        
        try:
            # connect to offline db
            db = self._connect_db()
            conn = db.getConnector()
            # execute query
            serviceCfg = agriConfig.services.fogliAzienda
            sql = f"SELECT count(*) FROM {serviceCfg.name} WHERE {serviceCfg.selectedField} = 1"
            value = conn.executeSingle( sql )
            return ( value == 1 )
        
        finally:
            self._disconnect_db()
            
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _updateFoglioState(self, value, unselect=True):
        """ Update 'foglio' state """
        if not self.isOfflineDb:
            return
        
        try:
            serviceCfg = agriConfig.services.fogliAzienda
            conn = self._connect_db().getConnector()
            
            if value is not None:
                # update foglio state
                sql = f"UPDATE {serviceCfg.name} SET {serviceCfg.statoField} = {value} WHERE {serviceCfg.selectedField} = 1;"
                conn.executeAndCommit( sql )
            
            # reset selecte foglio
            if unselect:
                sql = f"UPDATE {serviceCfg.name} SET {serviceCfg.selectedField} = 0;"
                conn.executeAndCommit( sql )
            
        finally:
            self._disconnect_db()
            
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _updateServiceDataFromDb(self, serviceName, data, field): #field agriConfig.services.fogliAzienda.statoField
        """ Retrieve a value from offline db settings table """
        try:
            # init
            service_cfg = agriConfig.get_value( 'agri_service/resources/{}'.format( serviceName ), {} )
            keyfields = service_cfg.get( 'keyfields', '' )
            if not keyfields:
                return data
            
            fldName = agriConfig.services.fogliAzienda.statoField
            cond = ' AND '.join( [ "{0}=:{0}".format( k.strip() ) for k in str(keyfields).split( ',' ) ] )
            sql = "select {0} FROM {1} WHERE {2};".format( fldName, serviceName, cond )
            
            # connect to offline db
            conn = self._connect_db().getConnector()
            
            # loop row
            for dataRow in data:
                # get value from db table
                value = conn.executeSingle( sql, dataRow )
                # update dictionary
                dataRow[ fldName ] = value
            
            return data
        
        except Exception as e:
            # handle exception
            logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
        
        finally:
            self._disconnect_db()     

            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _getDbSetting(self, key):
        """ Retrieve a value from offline db settings table """
        try:
            # connect to offline db
            db = self._connect_db()
            conn = db.getConnector()
            # execute query
            sql = "SELECT value FROM agri_settings WHERE key='{}'".format( str(key) )
            return conn.executeSingle( sql )
        except Exception as e:
            raise Exception( "{0}: {1}\n{2}".format( tr( "Chiave non presente in db locale" ), str(key), str(e) ) )
        
        finally:
            self._disconnect_db()
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _setDbSetting(self, recs):
        """ Set a value from offline db settings table """
        try:
            # connect to offline db
            db = self._connect_db()
            conn = db.getConnector()
            for key, value in recs.items():
                # execute insert query (if record missing)
                sql = "INSERT OR IGNORE INTO agri_settings (key, value) VALUES ('{0}', '{1}')".format(str(key), str(value))
                conn.executeAndCommit(sql)
                # execute update query
                sql = "UPDATE agri_settings SET value='{1}' WHERE key='{0}'".format(str(key), str(value))
                conn.executeAndCommit(sql)
        
        finally:
            self._disconnect_db()
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _storeModSuoliFeaturesIds(self, fid):
        """Stores new suoli feature Id"""
        self.__added_suoli_features.append( fid )
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _updateModSuoliFeatures(self, layer):
        """Update new suoli features"""
        try:
            if self.__added_suoli_features:
                self._updateSuoliFeaturesFlags( layer, self.__added_suoli_features, chkCommand=False, chkGeom=True )
        finally:
            self.__added_suoli_features.clear()
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _updateSuoliFeaturesFlags(self, layer, fids, chkCommand=True, chkGeom=False):
        """Update/correct suoli flags"""
        
        # chek if procedure is enabled
        if not self.__enableUpdateSuoliFlags:
            return
        
        # check if offline
        if not self.isOfflineDb:
            return
        
        
        # check if layer in editing
        if not layer.isEditable():
            return
        
        # check if there's an active command (trick to skip undo\redo cycle) 
        if chkCommand and not layer.isEditCommandActive():
            return
        
        # get current foglio attributes
        attribs = copy.deepcopy( self.plugin.controlbox.currentFoglioFilterData or {} )

        # get tolerances
        suoliMinArea = agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO

        # get repair suolo config
        uri = QgsDataSourceUri( layer.dataProvider().dataSourceUri() )
        layer_name = uri.table()
        cmd_cfg = self.getCommandConfig( 'updateFlagSuolo', layer_name )
        lay_filter = cmd_cfg.get( 'layFilter', '' ) or ''
        fld_lst = cmd_cfg.get( 'wrkFields', [] ) or []
        
        
        # list of invalid feature geometries
        invalidGeoFeatures = []
        smallGeoFeatures = []
        refValues = {}
        
        # loop features
        for fid in fids:
            # get feature instance
            feature = layer.getFeature( fid )
            
            # check if valid geometry 
            refValues['_flagInvalido'] = 0
            geom = feature.geometry()
            if geom.isEmpty() or not geom.isGeosValid():
                refValues['_flagInvalido'] = 1
                invalidGeoFeatures.append( fid )
                
            elif geom.area() < suoliMinArea:
                refValues['_flagInvalido'] = 1
                smallGeoFeatures.append( fid )
                
            elif geom.isMultipart() and len( geom.asGeometryCollection() ) > 1:
                refValues['_flagInvalido'] = 1
                invalidGeoFeatures.append( fid )
            
            # loop fields from configuration
            featFields = feature.fields()
            for fld_def in fld_lst:
                # get field name
                field_name = fld_def.get( 'name', None )
                if not field_name:
                    continue
                
                # check if key field
                if fid < 0 and fld_def.get( 'keyField', False ):
                    attribs[field_name] = NULL
                    continue
                
                # check if config setValue attribute is defined
                if 'setValue' not in fld_def:
                    continue
                
                # get field value
                field_ndx = featFields.indexFromName( field_name )
                if field_ndx == -1:
                    continue
                
                # get new value
                fld_skippable = fld_def.get( 'skippable', False )
                if self.__skipSuoloLavoratoFeatureFid and \
                   fid in self.__skipSuoloLavoratoFeatureFid and \
                   fld_skippable:
                    continue
                
                # skip valorized field
                fld_skipValorized = fld_def.get( 'skipValorized', False )
                if fld_skipValorized and feature.attribute( field_ndx ) != NULL:
                    continue
                
                # set value
                value = refValues.get( fld_def.get( 'refName', '' ), fld_def.get( 'setValue' ) )
                attribs[field_name] = value
                
            
            # update feature id padre
            fidDict = self._updateSuoliFeatureIdPadre( feature ) #, lay_filter  )
            attribs = {**attribs, **fidDict}
            if attribs:
                # assign attributes to feature
                # loop dictionaty of attributes
                try:
                    self.__enableUpdateSuoliFlags = False 
                    #layer.beginEditCommand( 'updateSuoliFeaturesFlags' )
                    for attr_name, attr_val in attribs.items():
                        field_ndx = featFields.indexFromName( attr_name )
                        if field_ndx == -1:
                            continue
                        
                        val = feature.attribute( field_ndx )
                        if val == attr_val:
                            continue
                        
                        feature.setAttribute( field_ndx, attr_val )
                        layer.changeAttributeValue( feature.id(), field_ndx, attr_val )
                    #layer.endEditCommand()
                finally:
                    self.__enableUpdateSuoliFlags = True
        
        # log message on invalid features
        if chkGeom and invalidGeoFeatures:
            logger.msgbar( logger.Level.Warning, 
                           "'{0}' {1}".format( layer.name(), tr( "Presenti dei suoli con geometrie invalide" ) ),
                           title=self.plugin.name )
            
        if chkGeom and smallGeoFeatures:
            logger.msgbar( logger.Level.Warning, 
                           "'{}' {} {:.3f} mq".format( layer.name(), tr( "Presenti dei suoli con area minore di" ), suoliMinArea ),
                           title=self.plugin.name )
            
    # --------------------------------------
    # 
    # --------------------------------------             
    def _updateSuoliFeatureIdPadre(self, feature, lay_filter=None):
        """ Update 'idFeaturePadre' suolo feature field """
        
        # get tolerances
        suoliMinArea = agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO
        
        # init
        inGeom = feature.geometry()
        ##inGeomArea = inGeom.area()
        maxSearchArea = -1.0
        maxSearchIdFeature = None
        
        
        # get command configuration
        cmd_salva_cfg = self.getCommandConfig( 'salvasuoli' )
        padre_id_cfg = cmd_salva_cfg.get( 'padreRelation', {} )
        padre_id_src_lay = padre_id_cfg.get( 'srcLayer', '' ) or ''
        padre_id_src_fld = padre_id_cfg.get( 'srcField', '' ) or ''
        padre_id_dst_fld = padre_id_cfg.get( 'dstField', '' ) or ''
        check_fld = padre_id_cfg.get( 'chkField', '' ) or ''
        modif_fld = padre_id_cfg.get( 'modField', '' ) or ''
        
        
        # get 'suoli rilevati' vector layer
        vlayers = self.get_suolo_vector_layers( filter_name=padre_id_src_lay )
        if len(vlayers) == 0:
            raise Exception( tr('Nessun layer definito per i suoli rilvati') )
        
        suoliRilLayer = vlayers[0]
        fields = suoliRilLayer.fields()
        fldIdPadreIndex = fields.indexFromName( padre_id_src_fld )
        if fldIdPadreIndex == -1:
            raise Exception( "{0}: {1} (layer: {2})".format( tr('Campo non reperito'), padre_id_src_fld, padre_id_src_lay ) )
         
        # get features that insersect the input feature
        lstFeature_ids = QGISAgriLayers.getFeaturesIdByGeom( suoliRilLayer, inGeom, expression=lay_filter )
        
        # check if modified suolo
        attribs = {}
        attribs[modif_fld] = 1
        if len(lstFeature_ids) == 1:
            fid = lstFeature_ids[0]
            newFeature = suoliRilLayer.getFeature( fid )
            if inGeom.equals( newFeature.geometry() ) and \
               feature.attribute( check_fld ) == newFeature.attribute( check_fld ):
                attribs[modif_fld] = 0
        
        # get feature id from 'suoli rilevati' features
        lstIdFeatures = []
        for fid in lstFeature_ids:
            # get feature
            feat = suoliRilLayer.getFeature( fid )
            
            # get feature geometry
            featGeom = feat.geometry()
            if not featGeom.isGeosValid():
                # repair invalid geometry
                featGeom = featGeom.makeValid()
            
            # check if feature intersect the input one
            intersGeom = inGeom.intersection( featGeom )
            if not intersGeom.isGeosValid():
                continue
            
            # check if intersected feature has valid idFeaturePadre value
            val = feat.attribute( fldIdPadreIndex )
            if val is None or val == NULL:
                continue
            
            # check if intersection valid for area
            intersGeomArea = intersGeom.area()
            if intersGeom.area() < suoliMinArea:
                if intersGeomArea > maxSearchArea:
                    maxSearchArea = intersGeomArea
                    maxSearchIdFeature = val
                continue 
            
            # append idFeaturePadre to search list
            lstIdFeatures.append( val )
        
        # check result
        if not lstIdFeatures and maxSearchIdFeature is not None:
            lstIdFeatures.append( maxSearchIdFeature )
        
        # adjust idFeaturePadre attribute of input feature
        attribs[padre_id_dst_fld] = str(lstIdFeatures)
        
        return attribs
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _clearTOC(self):
        """Reset TOC"""
        QGISAgriLayers.clear_toc( skipRasterLayer=True )
            
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _removeAllMapLayers(self):
        """Remove all map layers in project & clear TOC"""
        QGISAgriLayers.clear_toc( skipRasterLayer=False )
        QGISAgriLayers.removeAllMapLayers()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _newProject(self, prj_filename: str=None):
        """Start a new empty project"""
        self.plugin.iface.newProject()
        """
        project = QgsProject.instance()
        prj_filename = prj_filename or project.fileName()
        if prj_filename:
            self.plugin.iface.newProject()
            project.clear()
            project.read( prj_filename )
            logger.msgbar(
                logger.Level.Info, 
                tr('Ricaricato il progetto corrente.'), 
                title= self.plugin.name)
        else:
            self.plugin.iface.newProject()
        """
        
    # --------------------------------------
    # 
    # --------------------------------------             
    def _resetActivity(self, doneMsg=None, levMsg=logger.Level.Info, unlockEventoLavorazione=True, foglioState=None):
        """Reset job to start new ones"""
        
        # check if offline
        if not self.isOfflineDb:
            return 
        
        # init
        srv_curr_data = {}
        dbCloneFile = None
        
        try:
            # remove all layers to unlock offline db
            canvas = self.plugin.iface.mapCanvas()
            canvas.freeze()
            self._clearTOC() #self._removeAllMapLayers() NO USE: CRASH QGIS
            
            # check if unlock 'Evento di lavorazione'
            if unlockEventoLavorazione:
                # collect offline Agri service data 
                lv_data = self.getDbTableData( agriConfig.services.listaLavorazione.name  ) or [{}]
                az_data = self.getDbTableData( agriConfig.services.Aziende.name  ) or [{}]
                fg_data = self.getDbTableData( agriConfig.services.fogliAzienda.name  ) or [{}]
                srv_curr_data[agriConfig.services.listaLavorazione.name] = {
                    'rows': lv_data,
                    'refData': lv_data[0]
                }
                srv_curr_data[agriConfig.services.Aziende.name] = {
                    'rows': az_data, #[{**lv_data[0], **az_data[0]}],
                    'refData': lv_data[0]
                }
                srv_curr_data[agriConfig.services.fogliAzienda.name] = {
                    'rows': fg_data, #[{**lv_data[0], **az_data[0], **fg_data[0]}],
                    'refData': az_data[0]
                }
                # remove offline db
                self.__isOfflineFoglio = False
                dbCloneFile = self._disconnect_clone_db()
            else:
                # reset offline db
                self._updateFoglioState( foglioState, unselect=True )
                self._prepare_db( scriptName='reset' )
            
            # save last service downloaded data
            self.__srv_last_data = srv_curr_data
            
            #remove offline db
            if dbCloneFile:
                fileUtil.scheduleRemoveFile( dbCloneFile, self._removeFile, delay=2000 )
                
            # Prepare starting a new project
            logger.clear_msgbar()
            logger.suspend_msgbar()
            
            signalUtil.connectOnce( 
                self.plugin.iface.newProjectCreated, 
                
                lambda self=self: (
                    logger.suspend_msgbar( False ), 
                    logger.msgbar_ext( 
                        levMsg, 
                        str(doneMsg), 
                        title=self.plugin.name, 
                        duration=10, 
                        clear=True, 
                        height=60, 
                        icon_path=':/plugins/qgis_agri/images/checked-icon.png' )
                )
            )
            
            # Start a new project
            self._newProject()
            
            # re initialize plugin
            ##self.init( None, initSfondo=True, serviceSavedData=srv_curr_data )
            
            # show done message
            #logger.msgbox( levMsg, str(doneMsg), title=tr('INFO') ) <==== CRASH QGIS!!!!
            
        except Exception as e:
            # handle exception
            logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
        
#         finally:
#             if dbCloneFile:
#                 fileUtil.scheduleRemoveFile( dbCloneFile, self._removeFile, delay=2000 )
                 
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def checkIfPluginLayer(self, layer):
        """Checks if a plugin working layer"""
        if layer.type() != QgsMapLayer.VectorLayer:
            return False
        
        uri = QgsDataSourceUri( layer.dataProvider().dataSourceUri() )
        if os.path.normpath(uri.database()) != self.database:
            return False
        
        lay_cfg = agriConfig.get_value( 'ODB/layers/{0}'.format( layer.name() ), {} )
        if lay_cfg:
            return True
        return False
    
    # --------------------------------------
    # 
    # --------------------------------------             
    def closeEditMode(self, cmdName, buttons=None):
        """Close edit mode for all layers"""
        vlay_list = self.plugin.iface.editableLayers()
        if not QGISAgriLayers.end_editing_ext( vlay_list, buttons=buttons ):
            logger.msgbar( logger.Level.Warning, 
                           "'{0}' {1}".format( cmdName, tr( "annulato perché presenti layer in modifica." ) ),
                           title=self.plugin.name )
            return False
        return True
        
    # --------------------------------------
    # 
    # --------------------------------------  
    def getCommandConfig(self, command, layer=None):
        """ Returns a command config """
        # get command config
        cfg_commands = agriConfig.get_value( 'commands', {} ) or {}
        cmd_cfg = cfg_commands.get( str(command), {} ) or {}
        # correct fields config for layer
        if layer is not None:
            lay_cfg = cmd_cfg.get( 'layers', {} ) or {}
            lay_cfg = lay_cfg.get( str(layer), {} ) or {}
            fld_lay_lst = lay_cfg.get( 'wrkFields', [] ) or []
            fld_lst = cmd_cfg.get( 'wrkFields', [] ) or []
            cmd_cfg['wrkFields'] = fld_lst + fld_lay_lst
            cmd_cfg['layFilter'] = lay_cfg.get( 'layFilter', '' ) or ''
            
        # return config
        return cmd_cfg
        
    # --------------------------------------
    # 
    # --------------------------------------  
    def getDefaultSuoliFeaturesFlags(self, layer, skipFields=False):
        """Returns current foglio field values"""
        
        # get current foglio attributes
        foglioFilterData = self.plugin.controlbox.currentFoglioFilterData
        if foglioFilterData is None:
            logger.msgbox(logger.Level.Critical, tr('Foglio non caricato!'), title=tr('ERRORE'))
        
        attribs = copy.deepcopy( foglioFilterData or {} )

        # get repair suolo config
        uri = QgsDataSourceUri( layer.dataProvider().dataSourceUri() )
        cmd_cfg = self.getCommandConfig( 'updateFlagSuolo', uri.table() )
        fld_lst = cmd_cfg.get( 'wrkFields', [] ) or []
        
        # loop fields from configuration
        for fld_def in fld_lst:
            if not('setValue' in fld_def):
                continue
            
            if skipFields and fld_def.get( 'skippable', False ):
                continue
            
            # get field value
            field_name = fld_def.get( 'name' )
            attribs[field_name] = { 
                'value': fld_def.get( 'setValue' ),
                'skipValorized': fld_def.get( 'skipValorized', False )
            }
            
        # return
        return attribs
        
    # --------------------------------------
    # 
    # --------------------------------------             
    def skipUpdateSuoloFeature(self, fid):
        """Add feature to skip auto update"""
        self.__skipSuoloLavoratoFeatureFid.append( fid )
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def resetUpdateSuoloFeature(self):
        """Add feature to skip auto update"""
        self.__skipSuoloLavoratoFeatureFid = []
                
    # --------------------------------------
    # 
    # --------------------------------------             
    def loadSfondo(self, index, zoom=False, searchByAttrib=None, visible=True, renewTimer=None, renewTimerAuth=True):
        """ Load automatically a sfondo layer """
        
        ##################################################################
        def loadLay(comboData, elapsedRenew=None):
            try:
                if renewTimer is not None and not renewTimer.isActive():
                    return
                         
                # load raster layer and add to toc
                style_file = comboData.get( 'stylefile','' )
                style_file = os.path.join( self.plugin.pluginStylePath, style_file )
                toc_lay_name = comboData.get('tocname')
                rlayer = QGISAgriLayers.add_toc_owslayer( owsUri,
                                                          toc_lay_name = toc_lay_name,
                                                          toc_grp_name = comboData.get('tocgroup'), 
                                                          style_file = style_file,
                                                          allowInvalidSource = True,
                                                          recreateLayer = True )
                if rlayer is None:
                    logger.log( logger.Level.Critical, f"{tr('Impossibile creare layer sfondo')}: {toc_lay_name}" )
                    return
                
                # create timer for reload with renewed authentication
                if elapsedRenew is not None:
                    timer = QTimer( rlayer )
                    timer.timeout.connect( lambda self=self: self.loadSfondo( index, renewTimer=timer ) )
                    self.plugin.pluginAuthenticated.connect( lambda auth,self=self: self.loadSfondo( index, renewTimer=timer, renewTimerAuth=auth ) )
                    rlayer.willBeDeleted.connect( timer.stop )
                    timer.start( elapsedRenew * 1000 ) #msec
                
                # zoom 
                if zoom:
                    QGISAgriLayers.zoom_layers_ext( [rlayer] )
                    
                # vivibility
                if not visible:
                    QGISAgriLayers.hide_layers( [rlayer], hide=True )
                    
                if __PLG_DEBUG__:
                    if renewTimer is not None:
                        logger.log( logger.Level.Info, f"{tr('Rinnovato sfondo')}: {toc_lay_name}" )
                        
            except Exception as e:
                logger.log( logger.Level.Critical, f"{tr('Eccezione durante il rinnovamento sfondo')}: {str(e)}" )
        ##################################################################
        
        # init
        combo = self.plugin.rasterCombo
        if combo is None:
            return
        
        skipOgcProxy = False
        if renewTimer is not None:
            if not self.plugin.authenticated:
                return
            
            elif not renewTimer.isActive():
                return
            
        # search by attrib
        if searchByAttrib is not None:
            index = -1
            searchByAttrib = str(searchByAttrib)
            for i in range( combo.count() ):
                data = combo.itemData( i )
                if data is None:
                    continue
                
                canLoad = data.get( searchByAttrib, False ) or False
                if canLoad:
                    index = i
                    break
            
        # check if data found
        comboData = combo.itemData( index )
        if comboData is None:
            return
        
        # get ows data
        owsUri = comboData.get( 'uri', {} )
        owsUrl = owsUri.get( 'url', '' )
        if not owsUri or not owsUrl:
            return
        
        # check if ogcproxy is needed
        if skipOgcProxy or not comboData.get( 'ogcproxy', False):
            # load raster layer and add to toc     
            return loadLay( comboData )
   
        # start ogcproxy cycle   
        elapsedRenew = agriConfig.get_value( 'WMS/ogcproxyRenewSeconds', None )
        
        ##################################################################
        def callbackFn(error, callbackData):
            if error is not None:
                logger.log( logger.Level.Critical, str(error) )  
                return
            
            #serviceName = callbackData.get( 'serviceName', None )
            serviceData = callbackData.get( 'serviceData', None )
            #servRowSelData = callbackData.get( 'servRowSelData', None )
            
            # compose url
            qPrxUrl = QUrl()
            qPrxUrl.setScheme( qUrl.scheme() )
            qPrxUrl.setAuthority( qUrl.authority() )         
            qPrxUrl.setPath( '/ogcproxy/{0}{1}'.format( serviceData.decode(), qUrl.path() ) )
            if qUrl.hasQuery():
                qPrxUrl.setQuery( qUrl.query() )
               
            # load raster layer and add to toc
            owsUri['url'] = qPrxUrl.toString()  
            loadLay( comboData, elapsedRenew=elapsedRenew )
        ##################################################################
        
        qUrl = None
        prx = comboData.get( 'ogcproxy', False )
        if isinstance( prx, str ):
            qUrl = QUrl( prx )    
        elif prx:
            qUrl = QUrl( owsUrl )
        
        if  qUrl is not None:         
            # call service
            qPrxUrl = QUrl()
            qPrxUrl.setScheme( qUrl.scheme() )
            qPrxUrl.setAuthority( qUrl.authority() )         
            qPrxUrl.setPath( '/ogcproxy/secure/token' )
            qPrxUrl.setQuery( 'feature={0}'.format( owsUri.get( 'layers', '????' ) ) )
            
            self.onServiceRequest( 'Sfondi', 
                                   None, 
                                   None, 
                                   callbackFn, 
                                   directUrl = qPrxUrl.toString(),
                                   createSpinner = False, 
                                   agriResponseFormat = False,
                                   skipDeAuthentication = True,
                                   silentError = True if renewTimer is not None else False )
                
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def executeSqlQuery(self, sql):
        try:
            # execute SQL query
            conn = self._connect_db().getConnector()
            conn.executeAndCommit( sql )
        finally:
            self._disconnect_db()
     
    # --------------------------------------
    # 
    # --------------------------------------     
    def overrideTolerances(self):
        """ Override plugin tolerances """
        try:
            # init
            agriConfig.TOLERANCES = agriConfig.default_tolerances
            if not self.isOfflineDb:
                return
            
            # get config
            service_cfg = agriConfig.get_value( 'agri_service/resources/Parametri', {} )
            override_cfg = service_cfg.get( 'override', {} )
            
            for k,v in override_cfg.items():
                data = self.getDbTableData( 'Parametri', filterExpr = f"codice = '{v}'" )
                if not data:
                    continue
                
                data = data[0]
                
                tipo = data.get( 'tipo', '' )
                if not tipo:
                    continue
                
                elif tipo == 'N':
                    agriConfig.TOLERANCES[k] = float( data.get( 'valoreNumerico' ) )
            
        except:
            pass
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def init(self, foglioData, initSfondo=False, waiting=False, serviceSavedData=None):
        """Initialize controller"""
        
        # init
        self.__editingStopped_enabled = True
        self.__srv_last_data = None
        partController = self.plugin.particelle
        
        self.plugin.iface.mapCanvas().setPreviewJobsEnabled( False )

        
        # hide 
        self.plugin.docsdlg.hide()
        
        # close errors box
        self.plugin.errorsbox.close( )
        
        # check if offline
        isOfflineDb = self.isOfflineDb
        if isOfflineDb:
            self.__isOfflineFoglio = self._getIsFoglioLavorazione()
            self.__idEventoLavorazione = self._getIdEventoLavorazione()
        self.plugin.emit_db_rebase()
            
        # reset suoli attribute dialog
        QGISAgriIdentifyDialogWrapper.reset()
        self.plugin.setEleggibilitaModel()
        
        # set canvas window style
        self.styleCanvasWidget()
        ###self.plugin.set_can_download( self.isOfflineDb, 'search' )
        
        # set plugin panel
        self.plugin.controlbox.setOffLine( 
            isOfflineDb, 
            foglioData, 
            self.idEventoLavorazione, 
            offlineFoglio=self.isOfflineFoglio, 
            waiting=waiting,
            serviceSavedData=serviceSavedData,
            enableParticelleWorking=partController.isParticelleWorkingEnabled )
        
        # load iniatial 'sfondo' layer
        if not initSfondo:
            pass
        
        elif foglioData: # check if no 'foglio' data
            pass
        
        elif QgsProject.instance().count(): # check if toc is empty
            pass
        
        else:
            sfondo_cfg = agriConfig.get_value( 'context/sfondoDefault', {} )
            attrib_cfg = sfondo_cfg.get( 'seachForAttribute', None )
            if attrib_cfg:
                self.loadSfondo( -1, zoom=True, searchByAttrib=attrib_cfg )
        
        # remove old(orphan) files
        if not isOfflineDb:
            # remove old storico files     
            fileUtil.removeFiles( self.plugin.pluginHistoryPath, extension=None, noException=True )
            
            # remove old(orphan) DB files
            fileUtil.removeFilesByFilter( 
                path= self.plugin.pluginDataPath, 
                namefilter= "tmp*_{}".format( self.DB_OFFLINE_NAME ), 
                minfound= 5, 
                noException= True )
         
        # enables\disables action special cases       
        self.post_init(foglioData)
        
        # enables\disables history action
        gpkgFileName = self.plugin.pluginHistoryFileName
        if gpkgFileName is not None:
            # compose Geopackage file full name
            gpkgPath = self.plugin.pluginHistoryPath
            gpkgFile = os.path.join( gpkgPath, gpkgFileName )
            # disable authentication if Geopackage file exists
            self.plugin.StoricoAction.setCheckAuthenticated( not fileUtil.fileExists( gpkgFile ) )
            
        # override tolerances
        self.overrideTolerances()
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def post_init(self, foglioData):
        """Initialize controller"""
        # enables\disables action for browse foglio documentation
        action_disable = False
        if foglioData:
            action_disable = foglioData.get( agriConfig.SERVICES.fogliAzienda.docFlagField, '' ) != 'S'
        self.plugin.BrowseDocAction.forceDisable( action_disable )
        self.plugin.BrowseSuoloPropDocAction.forceDisable( action_disable )
        
        # enables\disables action for download\show suoli proposti photo
        action_disable = False
        if foglioData:
            action_disable = not self.get_suolo_vector_layers( 'browsephotoproposti' )
        self.plugin.BrowsePropostiPhotoAction.forceDisable( action_disable )
        
        # enable\disable PARTICELLE editing action
        partController = self.plugin.particelle
        isPartWorkingEnabled = partController.isParticelleWorkingEnabled
        partController.EditingAction.forceDisable( 
            not isPartWorkingEnabled, 
            tr( "Comando non attivo (Lista di lavorazione Particelle)" ) )
        
        self.plugin.SuoliCondPartAction.forceDisable(
            not isPartWorkingEnabled, 
            tr( "Comando non attivo (Lista di lavorazione Particelle)" ) )
        
        self.plugin.SuoliNoCondPartAction.forceDisable(
            not isPartWorkingEnabled, 
            tr( "Comando non attivo (Lista di lavorazione Particelle)" ) )
        
        self.plugin.CxfAction.forceDisable( 
            not partController.hasCXF, 
            tr( "Nessun file CXF presente (Lista di lavorazione Particelle)" ) )
        
        self.plugin.AllegatiPartAction.forceDisable( 
            not partController.hasAllegati, 
            tr( "Nessun allegato presente (Lista di lavorazione Particelle)" ) )
        
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def getDbTableData(self, table, fields=None, filterExpr=None):
        """Control service request from control box from offline DB"""
        try:
            # create connection
            dbConn = self._connect_db().getConnector()
            
            # dump table records
            data = dbConn.dumpTable( table, fields, filterExpr )
            return data
            
        finally:
            self._disconnect_db()
    
    
    
    # --------------------------------------
    # 
    # --------------------------------------         
    def getProjectSnapping(self):
        """Method to get project snapping."""
        
        snapConfig = QgsProject.instance().snappingConfig()
        return {
            "enabled": snapConfig.enabled(),
            "type": snapConfig.type(),
            "units": snapConfig.units(),
            "tolerance": snapConfig.tolerance(),
            "intersectionSnapping": snapConfig.intersectionSnapping(),
            "mode": snapConfig.mode(),
            "topological": {
                "enable": QgsProject.instance().topologicalEditing()
            }
        }
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setSnappingConfig(self, snap_cfg=None):
        """Method to set snapping by plugin config."""
        
        from qgis.core import QgsSnappingConfig, QgsTolerance
        
        # get snapping config
        if snap_cfg is None:
            snap_cfg = agriConfig.get_value('context/snapping', {})
        
        snapConfig = QgsProject.instance().snappingConfig()
        snapConfig.setEnabled(snap_cfg.get('enabled', True))
        snapConfig.setTolerance(snap_cfg.get('tolerance', 20))
        snapConfig.setIntersectionSnapping(snap_cfg.get('intersectionSnapping', False))
        
        val = snap_cfg.get('type', 'Vertex')
        if isinstance(val, str):
            val = { 
                
              'vertex': QgsSnappingConfig.Vertex,
              'vertexandsegment': QgsSnappingConfig.VertexAndSegment,
              'segment': QgsSnappingConfig.Segment
              
            }.get(val.lower(), QgsSnappingConfig.Vertex)
        snapConfig.setType(val)
        
        val = snap_cfg.get('units', 'Pixels')
        if isinstance(val, str):
            val = { 
                
              'layerunits': QgsTolerance.LayerUnits,
              'pixels': QgsTolerance.Pixels,
              'projectunits': QgsTolerance.ProjectUnits
              
            }.get(val.lower(), QgsTolerance.Pixels)
        snapConfig.setUnits(val)
        
        val = snap_cfg.get('mode', 'AllLayers')
        if isinstance(val, str):
            val = { 
                
              'activelayer': QgsSnappingConfig.ActiveLayer,
              'alllayers': QgsSnappingConfig.AllLayers,
              'advancedconfiguration': QgsSnappingConfig.AdvancedConfiguration
              
            }.get(val.lower(), QgsSnappingConfig.AllLayers)
        snapConfig.setMode(val)
    
        # set snapping
        QgsProject.instance().setSnappingConfig(snapConfig)
    
    
        # set topological snap config
        snap_topo_cfg = snap_cfg.get('topological', {})
        QgsProject.instance().setTopologicalEditing( snap_topo_cfg.get('enable', True) )
        
        
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def get_datasourceuri_layer(self, lay_name):
        """Get a plugin layer"""
        lay_cfg = agriConfig.get_value( 'ODB/layers/{0}'.format( lay_name ), {} )
        if not lay_cfg:
            return None
        
        uri = QgsDataSourceUri()
        uri.setDatabase( self.database )
        uri.setDataSource( ' ', lay_name, lay_cfg.get( 'geometryColumn', 'geometry' ), None )
        return uri  
        
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def get_datasourceuri_suolo_layers(self, filter_cmd=None, sort_attr=None, filter_name=None):
        """Get plugin layers"""
        uri_lst = []
        odb_cfg = agriConfig.get_value('ODB')
        odb_lays_cfg = odb_cfg.get('layers')
        for lay_name, lay_cfg in odb_lays_cfg.items():
            if lay_cfg.get('exclude', False):
                continue
            
            # edit order
            ord_lay = -1
            if sort_attr is not None:
                ord_lay = lay_cfg.get('editorder') or -1
            
            # filter layer on name
            if filter_name is not None:
                if filter_name != lay_name:
                    continue
            
            # filter layer on command
            if filter_cmd is not None:
                filter_cmd = filter_cmd.casefold()
                commands = lay_cfg.get('commands') or []
                if filter_cmd not in map(lambda x: x.casefold(), commands):
                    continue
            
            
            uri = QgsDataSourceUri()
            uri.setDatabase(self.database)
            uri.setDataSource(' ', lay_name, lay_cfg.get( 'geometryColumn', 'geometry' ), None)
            uri_lst.append( (uri, ord_lay) )
            
        # order result
        if sort_attr is not None:
            uri_lst = sorted(uri_lst, key=lambda x: x[1])
            
        return list( map(lambda x: x[0], uri_lst) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def get_suolo_vector_layers(self, filter_cmd=None, sort_attr=None, filter_name=None):
        """Get suoli vector layers"""
        uri_lst = self.get_datasourceuri_suolo_layers( filter_cmd=filter_cmd, sort_attr=sort_attr, filter_name=filter_name )
        return QGISAgriLayers.get_vectorlayer( uri_lst )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def updateLayersFeaturesCount(self, layers):
        """ Update layer features count """
        QGISAgriLayers.update_layers_renderer( layers )
        self.__updateLayerFeatureCountLst = layers
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def intersectSuoli(self, 
                       inFeature, 
                       destLayer, 
                       outLayerLst,
                       cutLayerLst, 
                       overlapLayersLst,
                       inAttrFldList, 
                       setAttrFldList=None, 
                       callBackFnc=None, 
                       layTag=None):
        """Split suoli from Suolo proposto"""
        
        # init
        setAttrFldList = setAttrFldList or []
        msgTag = "{}: ".format( layTag ) if layTag else ''
        addfieldsDict = {}
        dictCalcFeatures = {}
        lstOrdLays = [ destLayer ]
        suoliMinArea = agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO
        
        # check input geometry
        inGeometry = QgsGeometry( inFeature.geometry() )
        if not inGeometry.isGeosValid():
            msg = msgTag + tr( "la geometria del suolo selezionato è invalida" )
            raise QGISAgriException( msg )
        
        #
        snapTolerance = agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE
        suoliSnapLayers = None#QGISAgriLayers.get_vectorlayer( self.__suoli_snap_layer_uri ) TODO - TEST
        
        
        
        # init fields \ attributes to copy
        setAttrFldList = { x["name"] if "name" in x else '' : x for x in setAttrFldList }
        copyAttribList = QGISAgriLayers.get_attribute_values_ext( inFeature, inAttrFldList )
        mergAttribList = { **setAttrFldList, **copyAttribList }
        
        
        
        # get intersections\differences dest layer
        dictCalcFeatures[ destLayer.id() ] =  QGISAgriLayers.get_interserct_feature( inFeature, 
                                                                                     destLayer, 
                                                                                     getDiffGeom=True, 
                                                                                     getMaxIntersGeom=True,
                                                                                     layerFilterExpr=None,
                                                                                     areaTolerance=suoliMinArea,
                                                                                     suoliSnapLayers=suoliSnapLayers,
                                                                                     snapTolerance=snapTolerance )
        
        # check if main intersecting feature found
        featTuple = dictCalcFeatures[ destLayer.id() ]
        maxAreaFeature = featTuple[4]
        if maxAreaFeature is None:
            logger.msgbar( logger.Level.Warning, 
                           tr( "Nessun suolo reperito" ),
                           title = self.plugin.name,
                           clear = True )
            return False
        
        # check if  main intersecting feature geometry
        # in tollerance with input feature one
        intersGeometry = maxAreaFeature.geometry()
        diffGeom = intersGeometry.difference( inGeometry )
        if diffGeom.isEmpty():
            diffGeom = inGeometry.difference( intersGeometry )
        if diffGeom.area() < suoliMinArea:
            # reset results tuple if there are not full overlapping features
            overFeatIdList = list( filter( lambda x: x != maxAreaFeature.id(), featTuple[3] ) )
            if not overFeatIdList:
                dictCalcFeatures[ destLayer.id() ] = ( [maxAreaFeature], [], [], [], maxAreaFeature )
            
                
               
        # cut main intersecting feature found on cutting layers
        featTuple = dictCalcFeatures[ destLayer.id() ]
        intersFeature = featTuple[0][0]
        if intersFeature != maxAreaFeature:
            QGISAgriLayers.cut_interserct_feature( intersFeature, cutLayerLst )
            #
            if overlapLayersLst:
                if not QGISAgriLayers.cut_not_overlapping_feature( 
                            intersFeature, overlapLayersLst, expression="flagConduzione = 'S'" ):
                    return False
        
        # loop other destination layers
        for outLayer in outLayerLst:
            if outLayer == destLayer:
                continue
            
            featTuple =  QGISAgriLayers.get_interserct_feature( inFeature, 
                                                                outLayer, 
                                                                getDiffGeom=True, 
                                                                getIntersGeom=False,
                                                                layerFilterExpr=None,
                                                                areaTolerance=suoliMinArea,
                                                                suoliSnapLayers=suoliSnapLayers,
                                                                snapTolerance=snapTolerance )
            if not featTuple[0] and not featTuple[1]:
                pass
            else: 
                dictCalcFeatures[ outLayer.id() ] = featTuple
                lstOrdLays.append( outLayer )
        
        # callback function
        if callBackFnc is not None:
            if not callBackFnc( dictCalcFeatures, lstOrdLays ):
                return False
        
        # create feature
        for outLayer in lstOrdLays:
            # add new feature and delete old ones
            try:
                # get created features lists
                featTuple = dictCalcFeatures[ outLayer.id() ]
                intersFeatList = featTuple[0]
                diffFeatList = featTuple[1]
                delFeatIdList = featTuple[2]
                maxAreaFeature = featTuple[4]
                if not intersFeatList and not diffFeatList:
                    continue
                
                # open dest layer for editing
                outLayer.startEditing()
            
                # begin edit command
                outLayer.beginEditCommand( 'AgriSuoliIntersect' )
                
                # delete old features
                if delFeatIdList:
                    if not outLayer.deleteFeatures( delFeatIdList ):
                        # reject edit command
                        raise QGISAgriException( tr( 'Impossibile aggiungere nuove feature' ) )
                
                
                # add new features
                if intersFeatList:
                    # check if in feature in tollerance with main intersected feature
                    if maxAreaFeature is not None and \
                       maxAreaFeature == intersFeatList[0]:
                        # ONLY copy source attibutes to new features
                        QGISAgriLayers.change_attribute_values( outLayer, 
                                                                intersFeatList, 
                                                                copyAttribList, 
                                                                add_fields_dic=addfieldsDict )
                        # snap geometries
                        if suoliSnapLayers:
                            for snapFeat in intersFeatList:
                                snapGeom =  QGISAgriLayers.snapFeature( suoliSnapLayers, 
                                                                        snapFeat, 
                                                                        snapTolerance=snapTolerance )
                                outLayer.changeGeometry( snapFeat.id(), snapGeom )
                                
                    else:
                        # copy source attibutes to new features
                        QGISAgriLayers.change_attribute_values( outLayer, 
                                                                intersFeatList, 
                                                                mergAttribList, 
                                                                add_fields_dic=addfieldsDict )
                        
                        # snap geometries
                        if suoliSnapLayers:
                            for snapFeat in intersFeatList:
                                snapGeom =  QGISAgriLayers.snapFeature( suoliSnapLayers, 
                                                                        snapFeat, 
                                                                        snapTolerance=snapTolerance )
                                snapFeat.setGeometry( snapGeom )
                                
                        # add new feature
                        if not outLayer.addFeatures( intersFeatList ):
                            # reject edit command
                            raise QGISAgriException( tr( 'Impossibile aggiungere nuove feature' ) )
                    
                
                # add new features
                if diffFeatList:
                    # copy source attibutes to new features
                    QGISAgriLayers.change_attribute_values( outLayer, 
                                                            diffFeatList, 
                                                            setAttrFldList, 
                                                            add_fields_dic=addfieldsDict )
                    
                    # snap geometries
                    if suoliSnapLayers:
                        for snapFeat in diffFeatList:
                            snapGeom =  QGISAgriLayers.snapFeature( suoliSnapLayers, 
                                                                    snapFeat, 
                                                                    snapTolerance=snapTolerance )
                            snapFeat.setGeometry( snapGeom )
                    
                    # add new feature
                    if not outLayer.addFeatures( diffFeatList ):
                        # reject edit command
                        raise QGISAgriException( tr( 'Impossibile aggiungere nuove feature' ) )
                    
                
                # repair new feature geometries
                editBuffer = outLayer.editBuffer()
                if editBuffer is not None:
                    for fid, feat in editBuffer.addedFeatures().items():
                        QGISAgriLayers.repair_feature(
                            outLayer, 
                            feat, 
                            attr_dict={}, 
                            splitMultiParts=True,
                            autoSnap=True,
                            #suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                            suoliSnapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE,
                            suoliSnapLayerUris=self.suoliSnapLayerUris )
                
                
                # end edit command
                outLayer.endEditCommand()
  
            except Exception as e:
                # reject edit command
                outLayer.destroyEditCommand()
                raise e
        
        # return
        return True
       
    # --------------------------------------
    # 
    # --------------------------------------             
    def load_suoli_layers(self, 
                          check_unfound=True, 
                          except_unfound: QGISAgriMessageLevel = QGISAgriMessageLevel.Exception, 
                          foglio_Filter=True, 
                          filtered=True, 
                          clear_toc=False, 
                          ext_style=False,
                          load_only=False):
        """Load suoli layers from db"""
        
        # init
        currlayer = None
        vlayers = []
        vHidelayers = []
        self.__suoli_main_layer_uri = []
        self.__suoli_snap_layer_uri = []
        particelleController = self.plugin.particelle
        isParticelleWorkingEnabled = particelleController.isParticelleWorkingEnabled
        
        # reset paricelle layers store
        particelleController.storeParticelleLayer( None, reset=True )
        
        
        try:
            # open offline db
            db = self._connect_db()
            
            # remove all layers to unlock offline db
            if clear_toc:
                self._clearTOC()
            
            # get request layer defs
            odb_cfg = agriConfig.get_value('ODB', clone=False)
            odb_crs_cfg =  odb_cfg.get('crs', {})
            odb_lay_crs_cfg = odb_crs_cfg.get('layer')
            odb_map_crs_cfg = odb_crs_cfg.get('map')
            
            
            # set map crs
            QGISAgriLayers.change_map_crs( odb_map_crs_cfg )
            
            # get layer group list
            odb_grp_cfg = odb_cfg.get( 'groups', [] ) or []
            QGISAgriLayers.create_toc_groups( odb_grp_cfg )
            
            # reset layer list config
            odb_lays_cfg = odb_cfg.get('layers')
            for lay_name, lay_cfg in odb_lays_cfg.items():
                lay_cfg['__found'] = False
                lay_cfg['geometryColumn'] = 'geometry'
            
            # load layers to toc
            empty_lays = []
            layOrder = []
            layRefOrder = []
            lst_data_uri = db.getVectorTables()
            for data_uri in lst_data_uri:
                # get layer config
                lay_cfg = odb_lays_cfg.get(data_uri.table())
                if lay_cfg is None:
                    continue
                
                # mark layer config record has found
                lay_cfg['__found'] = True
                lay_cfg['geometryColumn'] = data_uri.geometryColumn()
                
                # get layer coordinate reference system
                odb_lay_crs = lay_cfg.get( 'crs', odb_lay_crs_cfg )
                
                
                # check if layer to exclude
                if lay_cfg.get('exclude', False):
                    continue
                
                # check if layer to exclude
                if lay_cfg.get( 'layerDB3', False ):
                    if not __PLG_DB3__:
                        continue
                    
                # check if PARTICELLE working layer
                if not isParticelleWorkingEnabled and lay_cfg.get( 'particelleWorkOnly', False ):
                    continue
                
                # set filters
                if filtered:
                    # set foglio filter
                    filterExpr = None
                    
                    # add additiona filter from config (always)    
                    fg_filter_cfg = lay_cfg.get( 'baseFilter', None )
                    if not isinstance( fg_filter_cfg, str ):
                        pass
                    elif filterExpr is None or not filterExpr:
                        filterExpr = fg_filter_cfg
                    else:
                        filterExpr = "{0} AND ({1})".format( filterExpr, fg_filter_cfg )
                        
                    # apply filter to source data
                    if filterExpr is not None:
                        data_uri.setSql( filterExpr )
                    
                    
                # update table statistics
                #db.getConnector().updateTableStatistics( data_uri.table() ) - TOO SLOW
           
                # load layer and add to toc
                lay_exclude_ifempty = lay_cfg.get( 'excludeIfEmpty', False )
                lay_ord = lay_cfg.get( 'tocorder', -1 )
                lay_grp = lay_cfg.get( 'tocgroup' )
                style_file = lay_cfg.get( 'stylefile', '' ) or ''
                if ext_style:
                    style_file = lay_cfg.get( 'stylefileExt', style_file ) or ''
                style_file = os.path.join( self.plugin.pluginStylePath, style_file )
                
                # check if layer exists
                vlayer = QGISAgriLayers.get_toc_vectorlayer( data_uri )
                if vlayer is None or not load_only:
                    # create layer
                    vlayer = QGISAgriLayers.add_toc_vectorlayer(data_uri,
                                                                 db.providerName(),
                                                                 crs = odb_lay_crs,
                                                                 toc_lay_name = lay_cfg.get( 'tocname', None ),
                                                                 toc_grp_name = lay_grp,
                                                                 toc_grp_index = listUtil.index( odb_grp_cfg, lay_grp ),
                                                                 toc_lay_order = lay_ord,
                                                                 exclude_empty = lay_exclude_ifempty,
                                                                 style_file = style_file,
                                                                 node_expanded= lay_cfg.get( 'tocexpanded', True ) )
                    
                
                    # check if empty
                    if vlayer.hasFeatures() == QgsFeatureSource.NoFeaturesAvailable:
                        # exclude layer if empty
                        if lay_exclude_ifempty:
                            continue
                        
                        # check if can be empty for PARTICELLE working
                        elif isParticelleWorkingEnabled and lay_cfg.get( 'canBeEmptyForPartLav', False ):
                            pass
                        
                        # collect empty layer to warning
                        elif lay_cfg.get( 'checkIfEmpty', True ): 
                            empty_lays.append( vlayer.name() )
                    
                    # check if set as readonly
                    vlayer.setReadOnly( lay_cfg.get( 'readonly', False ) )
                    
                    # check if set edit form fields as read only
                    readonlyFields = lay_cfg.get( 'readonlyFields', None )
                    if readonlyFields is not None:
                        QGISAgriLayers.layer_editFormFields_setReadOnly( vlayer, readonlyFields, read_only=True )
                    
                    # check if set as visible
                    if not lay_cfg.get( 'visible', True ):
                        vHidelayers.append(vlayer)
                    
                    # check if set as current layer
                    if not isParticelleWorkingEnabled and lay_cfg.get( 'setcurrent', False ):
                        currlayer = vlayer
                        
                    if isParticelleWorkingEnabled and lay_cfg.get( 'setcurrentPart', False ):
                        currlayer = vlayer
                        
                        
                    
                # check if main suolo layer
                if lay_cfg.get( 'connectSuoloSlots', False ):
                    # store source uri 
                    data_provider = vlayer.dataProvider()
                    self.__suoli_main_layer_uri.append( QgsDataSourceUri( data_provider.dataSourceUri() ) )
                    # connect signals to slots
                    self.connectSuoliEditing( vlayer )
                 
                # check if main particelle layer   
                if  lay_cfg.get( 'connectParticelleSlots', False ):
                    partController = self.plugin.particelle
                    # store source uri 
                    partController.storeParticelleLayer( vlayer )
                    # connect signals to slots
                    partController.connectParticelleEditing( vlayer )
                    
                # check if reference suolo for snap
                refLayOrd = lay_cfg.get( 'refSnapLayer', None )
                if refLayOrd is not None:
                    data_provider = vlayer.dataProvider()
                    layRefOrder.append( ( QgsDataSourceUri( data_provider.dataSourceUri() ), refLayOrd) )
                    
                    
                # store layer in collection
                vlayers.append(vlayer)
                layOrder.append( (vlayer, lay_ord) )
                
            # reorder reference snap layers
            layRefOrder.sort( key=lambda e: e[1] )
            self.__suoli_snap_layer_uri = [ l[0] for l in layRefOrder ]
            
           
            # layers load only: set layer added look, no zoom
            if load_only:
                QGISAgriLayers.hide_layers( vHidelayers, True )
                QGISAgriLayers.update_layers( vlayers )
                return vlayers
                
            # reorder layers in toc
            for t in layOrder:
                QGISAgriLayers.reorder_layer(t[0], t[1])
                
                
            # set layers as visible
            QGISAgriLayers.hide_layers( vlayers, False )
            QGISAgriLayers.update_layers( vlayers )
            QGISAgriLayers.zoom_layers_ext( vlayers )
            QGISAgriLayers.hide_layers( vHidelayers, True )
            QGISAgriLayers.update_layers( vlayers )
            if currlayer:
                QGISAgriLayers.set_current_layer( currlayer )

             
            # check if loaded all requested layers
            if check_unfound:
                unfound_lays = []
                for lay_name, lay_cfg in odb_lays_cfg.items():
                    if lay_cfg.get('exclude', False):
                        continue
                    
                    elif not lay_cfg.get( 'checkIfFound', True ):
                        continue
                    
                    elif not lay_cfg.get('__found', False):
                        unfound_lays.append(lay_name)
                    
                
                if unfound_lays:
                    # raise exception for unfounded layers
                    unfound_lays.insert( 0, tr( 'Livelli di lavoro non reperiti:' ) )
                    msg = '\n - '.join( map(str, unfound_lays) )
                    if except_unfound == QGISAgriMessageLevel.Exception:
                        raise Exception( msg )
                    elif except_unfound == QGISAgriMessageLevel.Critical:
                        logger.msgbox( logger.Level.Critical, msg, title=tr('ERRORE') )
                    else:
                        logger.log( logger.Level.Critical, msg )
                
                if empty_lays:
                    # raise exception for empty layers
                    empty_lays.insert( 0, tr( 'Livelli di lavoro non valorizzati:' ) )
                    msg = '\n - '.join( map(str, empty_lays) )
                    if except_unfound == QGISAgriMessageLevel.Exception:
                        raise Exception( msg )
                    elif except_unfound == QGISAgriMessageLevel.Critical:
                        logger.msgbox( logger.Level.Critical, msg, title=tr('ERRORE') )
                    else:
                        logger.log( logger.Level.Critical, msg )
            
  
        finally:
            self._disconnect_db()
            
        return vlayers
    
    # --------------------------------------
    # 
    # --------------------------------------  
    def _checkDeclaredSuoli(self):
        """Check declared suoli with dowloaded ones"""
        
        try:
            # init
            foglioData = None
            controlbox = self.plugin.controlbox
            err_count_lays = {}
            
            # get foglio data
            if controlbox.totFogliToWork == 1:
                foglioData = controlbox.currentFoglioData
                
            if foglioData is None:
                return
            
            # loop layers
            odb_lays_cfg = agriConfig.get_value('ODB/layers')
            for lay_name, lay_cfg in odb_lays_cfg.items():
                # get TOC layer name
                #lay_toc_name =  lay_cfg.get( 'tocname', lay_name )
                
                # get foglio data declared count field
                count_Field = lay_cfg.get( 'numFeatureField', None )
                if count_Field is None:
                    continue
                
                # get declared count
                num_declared = foglioData.get( count_Field, None )
                if num_declared is None:
                    continue
                
                # get vector layer 
                uri = QgsDataSourceUri()
                uri.setDatabase( self.database )
                uri.setDataSource( ' ', lay_name, lay_cfg.get( 'geometryColumn', 'geometry' ), None )
                vlayers = QGISAgriLayers.get_vectorlayer( [uri] )
                if not vlayers:
                    continue
                vlayer = vlayers[0]
                
                # count features
                num_features = 0
                lay_alias = lay_cfg.get( 'numFeatureLayerAlias', lay_name )
                num_FeatureFilter = lay_cfg.get( 'numFeatureFilter', None )
                itFeature = vlayer.getFeatures() if not num_FeatureFilter \
                                    else vlayer.getFeatures( num_FeatureFilter )
                for _ in itFeature:
                    num_features += 1
                
                # store counts
                if count_Field not in err_count_lays:
                    err_count_lays[count_Field] = {
                        'layers': [],
                        'declared': num_declared,
                        'found': 0
                    }
                err = err_count_lays[count_Field]
                err['layers'].append( lay_alias )
                err['found'] = err['found'] + num_features
                    
             
            # check if countings mismatch
            msgTd = ''
            for _, err in err_count_lays.items():
                num_declared = str(err['declared'])
                num_features = str(err['found'])
                if num_declared != num_features:
                    msgTd +=  """<tr>
                                 <td>{}</td>
                                 <td align ="right">{}</td>
                                 <td align ="right">{}</td>
                                 </tr>""".format( 
                                   ",".join(err['layers']), num_declared, num_features ) 
                    
            # emit message box for counting error
            if msgTd:
                msg = """{0}
                         <br>
                         <table border="1" cellspacing="0" cellpadding="5">
                           <tr>
                             <th>{1}</th>
                             <th>{2}</th>
                             <th>{3}</th>
                           </tr>
                           {4}
                         </table>""".format(
                           
                           tr( 'Conteggi entità non congruenti: ' ),
                           tr( 'Layer' ),
                           tr( 'Dichiarati' ),
                           tr( 'Scaricati' ),
                           msgTd )
                
                logger.htmlMsgbox( logger.Level.Critical, msg, title=tr('ERRORE') )
        
        except Exception as e:
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            
        
    # --------------------------------------
    # 
    # --------------------------------------  
    def connectSuoliEditing(self, layer):
        """Connect layer editing signals"""
        
        # check if plugin layer and foglio loaded
        foglioFilterData = self.plugin.controlbox.currentFoglioFilterData
        if foglioFilterData is None and self.checkIfPluginLayer( layer ):
            # disable layer
            layer.setReadOnly( True )
            logger.msgbar( logger.Level.Warning, 
                           "'{0}' {1}".format( layer.name(), tr( " in sola lettura! (Caricare un foglio dal pannello di controllo)" ) ),
                           title=self.plugin.name )
        
        # check if main suolo layer
        if not QGISAgriLayers.is_requested_vectorlayer( layer, self.__suoli_main_layer_uri ):
            return 
        
        # check if already connected
        if layer.property( self.MAIN_SUOLO_LAYER_PROP ):
            return
        layer.setProperty( self.MAIN_SUOLO_LAYER_PROP, True )
        
        ##############################################################
        
        # connect signals
        signalUtil.connectUniqueSignal( layer, layer.beforeEditingStarted, lambda: self.beforeSuoliEditingStarted( layer ) )
        signalUtil.connectUniqueSignal( layer, layer.editingStopped, lambda: self.editingSuoliStopped( layer ) )
        signalUtil.connectUniqueSignal( layer, layer.afterRollBack, lambda: self.editingSuoliStopped( layer ) )
        signalUtil.connectUniqueSignal( layer, layer.beforeCommitChanges, lambda: self.beforeSuoliCommitChanges( layer ) ) 
         
        signalUtil.connectUniqueSignal( layer, layer.featureAdded, self._storeModSuoliFeaturesIds )
        signalUtil.connectUniqueSignal( layer, layer.editCommandStarted, lambda: self.__added_suoli_features.clear() )
        signalUtil.connectUniqueSignal( layer, layer.editCommandEnded, lambda: self._updateModSuoliFeatures( layer ) )
          
        signalUtil.connectUniqueSignal( layer, layer.attributeValueChanged, lambda fid: self._updateSuoliFeaturesFlags( layer, [fid] ) )  
        signalUtil.connectUniqueSignal( layer, layer.geometryChanged, lambda fid: self._updateSuoliFeaturesFlags( layer, [fid] ) )  
        
        if agriConfig.get_value( "context/updateTocCounter", False ):
            signalUtil.connectUniqueSignal( layer, layer.styleChanged, lambda: self.updateLayersFeaturesCount( [ layer ] ) )  
        
        ##############################################################
        
        # define/init custom form
        self._set_custom_forms( layer )
        
        ##############################################################
        
        # collect 'suoli bloccati' feature geometries
        if layer.isEditable():
            self.beforeSuoliEditingStarted( layer )  
            
        
    # --------------------------------------
    # 
    # --------------------------------------          
    def disconnectSuoliEditing(self):
        """Connect layer editing signals"""
        
        vlayers = QGISAgriLayers.get_vectorlayer( self.__suoli_main_layer_uri )
        for layer in vlayers:
            # disconnect signals
            signalUtil.disconnectUniqueSignal( layer, layer.beforeEditingStarted )
            signalUtil.disconnectUniqueSignal( layer, layer.editingStopped )
            signalUtil.disconnectUniqueSignal( layer, layer.afterRollBack )
            signalUtil.disconnectUniqueSignal( layer, layer.beforeCommitChanges)  
            signalUtil.disconnectUniqueSignal( layer, layer.featureAdded )  
            signalUtil.disconnectUniqueSignal( layer, layer.editCommandStarted ) 
            signalUtil.disconnectUniqueSignal( layer, layer.editCommandEnded )  
            signalUtil.disconnectUniqueSignal( layer, layer.attributeValueChanged )  
            signalUtil.disconnectUniqueSignal( layer, layer.geometryChanged )
            if agriConfig.get_value( "context/updateTocCounter", False ):
                signalUtil.disconnectUniqueSignal( layer, layer.styleChanged )  
            # reset the form used to represent this vector layer
            layer.setEditFormConfig( QgsEditFormConfig() )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def beforeSuoliEditingStarted(self, layer):
        """Check layer before editing"""
        # init
        layer.setProperty( self.COMMIT_SUOLO_LAYER_PROP, False )
        self.__updateLayerFeatureCountLst = []
        # hide control panel
        if self.plugin.autoHideControlbox:
            self.plugin.showControlBox( hide=True )
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def editingSuoliStopped(self, layer):
        """Editing stopped"""
        
        # check if slot enabled
        if not self.__editingStopped_enabled:
            return
        
        if layer.property( self.COMMIT_SUOLO_LAYER_PROP ):
            # update controbox
            self.plugin.controlbox.updateOffLineControls() 
        
        # update feature counts in TOC
        if self.__updateLayerFeatureCountLst:    
            QGISAgriLayers.update_layers_renderer( self.__updateLayerFeatureCountLst )
        self.__updateLayerFeatureCountLst = []
        
        # update feature counts in TOC
        QGISAgriLayers.update_layers_renderer( [layer] )
            
        # restore control panel
        if self.plugin.autoHideControlbox:
            self.plugin.showControlBox()
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def beforeSuoliCommitChanges(self, layer):
        """Check layer before commit changes"""
        # init
        layer.setProperty( self.COMMIT_SUOLO_LAYER_PROP, True )

        # emi signal
        self.plugin.emit_check_editing()
            
    # --------------------------------------
    # 
    # --------------------------------------     
    def start(self, emit_msg=True):
        """Start QGIS Agri activity"""
        
        try:
            # start progress bar
            if emit_msg:
                logger.add_progressbar(tr('Caricamento attività; attendere prego...'), only_message=True)
            
            # load suolo layers
            self.load_suoli_layers( except_unfound=QGISAgriMessageLevel.Critical, clear_toc=True )
            
            # set snapping
            cfg = agriConfig.get_value('context', {})
            if cfg.get('snapOnStart'):
                self.setSnappingConfig()
            
            # set flag
            self.plugin.set_started( True, emit_msg )
            
            # exit 
            return True                    
  
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            return False
        
        finally:
            logger.remove_progressbar()
            self._disconnect_db(True)
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def styleCanvasWidget(self, blink=False, reset=False):
        """Set a style for qgis canvas widget"""
        
        # check if offline db or reset canvas window style
        if not self.isOfflineDb or reset:
            mapWidget = self.plugin.iface.mapCanvas()
            mapWidget.setStyleSheet( "" )
            return
        
        # init
        cfg_style = agriConfig.get_value('context/canvas/style', "border: 3px solid lime")
        
        # set bold style
        from qgis_agri.widgets.blinker import Blinker
        def blinkStyle(blinked):
            mapWidget = self.plugin.iface.mapCanvas()
            if blinked:
                style = "QWidget#{0} {{ {1} }}".format( mapWidget.objectName(), cfg_style )
                mapWidget.setStyleSheet( style )
            else:
                mapWidget.setStyleSheet( "" )
            mapWidget.style().polish(mapWidget)
        
        if blink:    
            blinker = Blinker()
            blinker.blinking.connect(blinkStyle)
            blinker.start( max_repeat=5 )
        else:
            blinkStyle(True)
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def zoomToParticellaByExpression(self, featureExpression):
        """ Zoom to Particella feature by expression """
        
        # get PARTICELLE layers
        partController = self.plugin.particelle
        partLayUri = partController.mainLayerUri
        partLayers = QGISAgriLayers.get_vectorlayer( partLayUri )
        if not partLayers:
            return
        
        # try zoom on PARTICELLE layer
        found = self.zoomToFeatureByExpression( featureExpression, partLayUri, activate_layer=True )
        if not found and partController.hasCXF:
            # get CXF layer
            _, lstCxfUri = self.event_controller.get_cxf_layers()
            if not lstCxfUri:
                logger.msgbox( 
                    logger.Level.Warning,
                    tr("Particella non reperita.\nProvare a caricare il file CXF."),
                    title=tr('ERRORE') )
                return
            
            # try zoom on CXF layer
            cfg = agriConfig.services.ParticelleLavorazioni
            cxfFeatureExpression = featureExpression.replace(
                cfg.numParticellaField, cfg.numParticellaCxfField )
            found = self.zoomToFeatureByExpression( 
                cxfFeatureExpression, lstCxfUri, source_other_than_rdbms=True, activate_layer=False )
            if found:            
                # activate PARTICELLE layer
                self.plugin.iface.setActiveLayer( partLayers[0] )
            
        if not found:
            logger.msgbox( 
                logger.Level.Warning,
                tr("Particella non reperita."),
                title=tr('ERRORE') )
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def zoomToFeatureByExpression(self, 
                                featureExpression, 
                                dataSourceUri=None, 
                                source_other_than_rdbms=False,
                                activate_layer=False):
        """ Zoom to Suoli feature by expression """
        # init
        geom = None
        features = []
        suoloLayerFound = None
        extent = None
        featureExpression = str( featureExpression )
        
        # get suoli layers
        suoliLayers = []
        if dataSourceUri is not None:
            dataSourceUri = dataSourceUri if isinstance(dataSourceUri, list) else [ dataSourceUri ]
            suoliLayers = QGISAgriLayers.get_vectorlayer( dataSourceUri, source_other_than_rdbms )
        else:
            suoliLayers = QGISAgriLayers.get_vectorlayer( self.__suoli_main_layer_uri )
        
        # loop all suoli layers
        for suoloLayer in suoliLayers:
            # get features by expression
            for feat in suoloLayer.getFeatures( featureExpression ):
                features.append( feat.id() )
                # get feature bounding box
                geom = feat.geometry()
                if extent is None:
                    extent = geom.boundingBox()
                else:
                    extent.combineExtentWith( geom.boundingBox() )
                    
            # break loop if feature found for current layer
            if extent is not None:
                suoloLayerFound = suoloLayer
                break
              
        # zoom to suoli features      
        if extent is not None:
            extent.grow( 10 )
            canvas = self.plugin.iface.mapCanvas()
            canvas.setExtent( extent )
            canvas.refresh()
            if features is not None:
                canvas = self.plugin.iface.mapCanvas()
                canvas.flashFeatureIds( suoloLayerFound, features, flashes=1, duration=1000 )
                
            if activate_layer:
                self.plugin.iface.setActiveLayer( suoloLayerFound )
                
            return True
        
        else:
            return False     
            
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def checkSuoli(self, 
                   cmdName, 
                   checkFunctionList, 
                   warningAsError=False, 
                   emitResultMessage=True, 
                   cmdOptions=None, 
                   skipPendingChecksOnErrors=False):
        
        """ Check validity of 'Suoli' layer geometries """
        try:
            # init
            cmdName = cmdName or "Verifica geometrie"
        
            # close edit mode
            if not self.closeEditMode( cmdName ):
                return self.USER_CANCEL, False, False
            
            
            # clear error panel
            self.plugin.errorsbox.clear()
            
            # get 'suoli lavorazione' vector layer
            vlayers = QGISAgriLayers.get_vectorlayer( self.__suoli_main_layer_uri )
            if len(vlayers) == 0:
                raise Exception( tr( "Nessun layer associato al comando" ) )
            
            # format cmd options
            cmdOptions = cmdOptions or {}
            options = { 'layerAliasName': cmdName }
            options = { **cmdOptions, **options }
            
            # loop all check functions
            res = True
            checker = self.checker
            errorData = QGISAgriFeatureErrors()
            # loop all suoli layers
            for layer in vlayers:
                # loop all check functions
                for checkFunction in checkFunctionList:
                    nErrors = errorData.numErrors
                    res = res and checkFunction( layer, errorData, options )
                    if not res or (errorData.numErrors - nErrors) > 0:
                        break
                    
            # PARTICELLE working
            partController = self.plugin.particelle
            if partController.isParticelleWorkingEnabled:
                options['isParticelleWorking'] = True
                if not errorData.hasErrors and not errorData.hasWarnings:
                    res = True
                
                partLayers = QGISAgriLayers.get_vectorlayer( partController.mainLayerUri )
                if len(partLayers) == 0:
                    raise Exception( tr( "Nessun layer PARTICELLE associato al comando" ) )
                # loop all PARTICELLE layers
                for layer in partLayers:
                    # loop all check functions
                    for checkFunction in checkFunctionList:
                        nErrors = errorData.numErrors
                        res = res and checkFunction( layer, errorData, options )
                        if not res or (errorData.numErrors - nErrors) > 0:
                            break
                    
            # create error layer
            if errorData.hasErrors or errorData.hasWarnings:
                self.plugin.errorsbox.setErrors( errorData )
                createErrLayer = agriConfig.get_value( 'commands/checkSuoli/addErrorLayer', False )
                if createErrLayer:
                    errorData.createLayer( cmdName, layerName=cmdName, tocGrpName=checker.TOC_ERR_GRP_NAME )
            
            # return processing result    
            return res, errorData.hasErrors, errorData.hasWarnings
         
        except Exception as error:
            # handle exception
            raise error

    # --------------------------------------
    # 
    # -------------------------------------- 
    def onServiceOfflineRequest(self, serviceName, servRowSelData, callbackFn, parent=None):
        """Control service request from control box from offline DB"""
        callbackData = {
            'serviceName': None,
            'serviceData': None,
            'servRowSelData': None
        }
        try:
            # debugger timer
            dbgTimer = logger.createDebugTimer()
            dbgTimer.start( "GET {0}".format( serviceName ) )
        
            # restore cursor
            logger.restoreOverrideCursor()
               
            # get db table config
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            table = res_cfg.get( 'dbName', serviceName )
            fields = res_cfg.get( 'dbFields', '*' )
            
            filterExpr = None
#             fg_filter_cfg = res_cfg.get( 'foglioFilter', False )
#             if fg_filter_cfg:
#                 filterExpr = dictUtil.asStringExpression( self.plugin.controlbox.currentFoglioFilterData )
            
            # import service data from DB
            data = self.getDbTableData( table, 
                                        fields = fields, 
                                        filterExpr = filterExpr )
            
            # callback
            dbgTimer.stop()
            if callbackFn is not None:
                callbackData['serviceName'] = serviceName
                callbackData['serviceData'] = data
                callbackData['servRowSelData'] = servRowSelData
                callbackFn( None, callbackData )
            
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            if callbackFn is not None:
                callbackFn( e, None, None, None )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onServiceRequest(self, 
                         serviceName, 
                         servRowSelData, 
                         genData, 
                         callbackFn,
                         postData=None, 
                         parent=None, 
                         warningCodes=None, 
                         cache=False, 
                         createSpinner=True,
                         directUrl=None,
                         agriResponseFormat=True,
                         skipDeAuthentication=False,
                         followLinkedService=True,
                         requestCollector=None,
                         silentError=False,
                         removeNullParams=False,
                         warningMsgBar=False ):
        """Control service request from control box"""
        
        # debugger timer
        dbgTimer = logger.createDebugTimer()
        
        ##############################################################################################
        def onFinishedRequest( reply, customData, requestCollector=None ):
            createSpinner = False
            agriResponseFormat = True
            callbackData = {
                'serviceName': None,
                'serviceData': None,
                'servRowSelData': None,
                'requestCollector': requestCollector,
                'esitoDTO': 0,
                'headers': {}
            }
            serviceName = '???'
            
            try:
                dbgTimer.stop()
                
                # retrieve custom data attached to this service
                serviceName = customData.get( 'serviceName', '' )
                callbackData['serviceName'] = serviceName
                
                servRowSelData = customData.get( 'servRowSelData', {} )
                appendParams = customData.get( 'appendParams', {} )
                warningCodes = customData.get( 'warningCodes', [] )
                warningMsgBar = customData.get( 'warningMsgBar', [] )
                createSpinner = customData.get( 'createSpinner', [] )
                agriResponseFormat = customData.get( 'agriResponseFormat', True )
                
                
                # destroy spinner
                if createSpinner:
                    self.plugin.controlbox.destroySpinner()
                
                # restore cursor
                logger.restoreOverrideCursor()
                
                # check if error
                statusCode = reply.attribute( QNetworkRequest.HttpStatusCodeAttribute )
                if reply.error():
                    raise Exception( reply.errorString() )
                
                # check if expired authrntication
                header = QByteArray( b'Content-Type' )
                if statusCode == 302 and reply.hasRawHeader( header ):
                    value = reply.rawHeader( header ).data().decode()
                    if 'application/json' not in value:
                        if not skipDeAuthentication:
                            self.plugin.set_authenticated( False, emit_msg=True )
                        raise Exception( 'Autenticazione scaduta' )
                 
                # check i valid http status code
                if statusCode != 200:
                    raise Exception( "'{0}'\nHTTP status code: {1}\n{2}".format( serviceName, statusCode, reply.errorString() ) )
                
                # manage result
                res = {}
                data = None
                errCode = 0
                if agriResponseFormat:
                
                    # read result as json 
                    dbgTimer.start( "Parse JSON" )
                    try:
                        if hasattr( reply, 'readAll' ):
                            res = json.loads( reply.readAll().data() )
                        else:
                            res = json.loads( reply.content() )
                    except ValueError as e:
                        raise Exception(  "'{0}'\n{1}\n{2}".format( serviceName, tr( 'JSON non valido.' ), str(e) ) )
                    dbgTimer.stop()
                    
                    # check
                    if 'esitoDTO' not in res:
                        raise Exception(  "{0} 'esitoDTO' {1} '{2}' ".format( tr( "Manca l'attributo" ),
                                                                              tr( "nella risposta del servizio" ), 
                                                                              serviceName ) )
                    if 'dati' not in res:
                        raise Exception(  "{0} 'dati' {1} '{2}' ".format( tr( "Manca l'attributo" ),
                                                                              tr( "nella risposta del servizio" ), 
                                                                              serviceName ) )
                     
                    esitoDTO = res.get( 'esitoDTO', {} )
                    if not esitoDTO:
                        raise Exception(  "{0} 'esitoDTO' {1} '{2}' ".format( tr( "Attributo" ),
                                                                              tr( "non valorizzato" ), 
                                                                              serviceName ) ) 
                        
                    data = res.get('dati') or {}
                    
                    # check request result 
                    warningCodes = warningCodes or []
                    errCode = esitoDTO.get( 'esito', 0 )
                    if errCode != 0:
                        if errCode not in warningCodes:
                            msg = esitoDTO.get( 'messaggio', tr( 'Errore servizio Agri' ) )
                            raise Exception( "'{0}'\n{1} (cod.: {2})".format( serviceName, msg, errCode ) )
                    
                    # format data
                    if appendParams:
                        # collect fixed params
                        fixedParams = {}
                        for param in appendParams:
                            value = servRowSelData.get( param, None )
                            if value:
                                fixedParams[param] = value
                        # append fixed params to result data
                        if fixedParams:
                            for rec in data:
                                rec.update( fixedParams )
                                
                else:
                    try:
                        if hasattr( reply, 'readAll' ):
                            data = reply.readAll().data()
                        else:
                            data = reply.content()
                    except ValueError as e:
                        raise Exception(  "'{0}'\n{1}\n{2}".format( serviceName, tr( 'Errore lettura contenuto della richiesta.' ), str(e) ) )
                
                # collect headers
                dict_headers = {}
                lst_headers = reply.rawHeaderPairs()
                for h in lst_headers:
                    dict_headers[str(h[0], "UTF-8")] = str(h[1], "UTF-8")
                
                # correct data for offline foglio
                if ( serviceName == agriConfig.services.fogliAzienda.name and
                     self.isOfflineDb and not self.isOfflineFoglio ):
                    self._updateServiceDataFromDb( serviceName, data, agriConfig.services.fogliAzienda.statoField )
                
                # load data to control box grid table
                if callbackFn is not None:
                    callbackData['serviceName'] = serviceName
                    callbackData['serviceData'] = data
                    callbackData['servRowSelData'] = servRowSelData
                    callbackData['esitoDTO'] = errCode
                    callbackData['headers'] = dict_headers
                    callbackFn( None, callbackData )
                    
                
            except Exception as e:
                # destroy spinner
                self.plugin.controlbox.destroySpinner()
                # handle exception
                if not silentError:
                    msg = f'{tr( "Servizio" )}: "{serviceName}"\n\n{formatException(e)}'
                    if requestCollector is not None:
                        requestCollector.addError( msg )
                    #elif warningMsgBar:
                    #    logger.msgbar( logger.Level.Warning, msg, title=self.plugin.name )
                    else:
                        logger.msgbox( logger.Level.Critical, msg, title=tr('ERRORE') )
                            
                if callbackFn is not None: 
                    callbackFn( e, callbackData )
                
            ##############################################################################################
            
            
        try:
            # init
            params = None
            appendParams = None
            
            # get config data
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            #descfld = res_cfg.get('descField', '')
            linkService_cfg = res_cfg.get( 'linkService', {} )
            serviceLinkName = linkService_cfg.get( 'name', None )
            if ( followLinkedService and 
                 serviceLinkName is not None and 
                 servRowSelData is not None ):
                # call linked service with params 
                serviceName = serviceLinkName  
                params = linkService_cfg.get( 'params', {} )
                dictUtil.substituteVariables( params, dictUtil.merge( genData, servRowSelData ) )
                appendParams = linkService_cfg.get( 'appendParams', None )
                warningCodes = linkService_cfg.get( 'warningDtoCodes', [] )
                warningMsgBar = linkService_cfg.get( 'warningMsgBar', False ) 
                
            else:
                # get params
                default_value_params = res_cfg.get( 'default_value_params', {} )
                params = res_cfg.get( 'params', {} )
                dictUtil.substituteVariables( params, dictUtil.merge( default_value_params, genData, servRowSelData ) )   
            
            if removeNullParams and params:
                params = {k:v for k,v in params.items() if v}
                
            # override cursor 
            logger.setOverrideCursor(Qt.WaitCursor)
            
            #
            if createSpinner:
                spinner = self.plugin.controlbox.createSpinner()
                spinner.show()
            
            # custom data
            cData = {
                "serviceName": serviceName,
                "servRowSelData": servRowSelData,
                "appendParams": appendParams,
                "warningCodes": warningCodes,
                "warningMsgBar": warningMsgBar,
                "createSpinner": createSpinner,
                "agriResponseFormat": agriResponseFormat
            }
            
            # make request
            dbgTimer.start( "GET {0}".format( serviceName ) )
            nam = self.plugin.networkAccessManager
            return nam.requestService( serviceName, 
                                       params, 
                                       callbackFn=onFinishedRequest, 
                                       parent=None, # TO REMOVE
                                       customData=cData, 
                                       cache=cache,
                                       postData=postData,
                                       directUrl=directUrl,
                                       requestCollector=requestCollector )
            
        except Exception as e:
            # destroy spinner
            self.plugin.controlbox.destroySpinner()
            # restore cursor
            logger.restoreOverrideCursor()
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            #
            return None
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onConfirmAllSuoliLavorazione(self, layer):
        """ Confirm all 'suoli lavorazione' """
        
        # confirm
        reply = QMessageBox.question(self.plugin.iface.mainWindow(), 
                                     tr('Continuare?'), 
                                     tr('Desideri confermare tutti i suoli in lavorazione?'), 
                                     QMessageBox.Yes, 
                                     QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        #
        dsUri = QgsDataSourceUri( layer.dataProvider().dataSourceUri() )
        layDbName = dsUri.table()
        
        # get 'flagLavorato' config
        ctx_cfg = agriConfig.get_value( 'context/suolo/lavorato', {} )
        flagLavField = ctx_cfg.get( 'fieldValue', '' )
        flagLavValue = ctx_cfg.get( 'fieldAssignValue', 1 )
        flagLavLayTpValues = ctx_cfg.get( 'checkLayers', {} ).get( layDbName, {} )
        flagLavSuoloTpValues = flagLavLayTpValues.get( 'fieldLavValues', [] )
        
        # get 'tipoSuolo' config
        ctx_cfg = agriConfig.get_value( 'context/suolo/type', {} )
        suoloTpField = ctx_cfg.get( 'fieldValue', None )
        
        
        # get attributes index
        fields = layer.fields()
        idxFlag = fields.indexFromName( flagLavField )
        idxTpSuolo = fields.indexFromName( suoloTpField )
        
        # open edit command
        layer.beginEditCommand( 'confirm_all_suoli_lavorazione' )
        try:    
            # search suoli not worked
            exp = QgsExpression( f'{flagLavField} != {flagLavValue}' )
            request = QgsFeatureRequest( exp )
            request.setFlags( QgsFeatureRequest.NoGeometry )
            
            for feature in layer.getFeatures( request ):
                val = feature.attribute( idxTpSuolo )
                if val in flagLavSuoloTpValues:
                    layer.changeAttributeValue( feature.id(), idxFlag, flagLavValue )
                    
            # commit edit command
            layer.endEditCommand()
            
        except Exception as e:
            layer.destroyEditCommand()
            raise e
        
        finally:
            # update layer
            QGISAgriLayers.update_layers( [ layer ] )
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def createSuoliCondParticella(self,
                                  feature,
                                  noCondVectlayers,
                                  destNoCondVectlayer,
                                  destVectlayer,
                                  createOnlyNoCondSuoli=False):
        
        
        # sub function to get field to copy config
        def cmdMapField(layer):
            provider = layer.dataProvider()
            uri = provider.uri()
            layName = uri.table() or layer.name()
            cmd_cfg = self.getCommandConfig( 'suoliCondParticella', layName )
            return cmd_cfg.get( 'wrkFields', [] )
        
        # sub function copy field values
        def copyFieldValues(old_feat, new_feat, cfg_fields):
            old_fields = old_feat.fields()
            new_fields = new_feat.fields()
            for fld_def in cfg_fields:
                fld_name = fld_def.get( 'name' )
                if not fld_name:
                    continue
                index = old_fields.indexFromName( fld_name )
                if index == -1:
                    continue
                value = old_feat.attribute( index )
                if 'setValue' in fld_def:
                    value = fld_def.get( 'setValue' )
                if 'rename' in fld_def:
                    fld_name = fld_def.get( 'rename' )
                    
                index = new_fields.indexFromName( fld_name )
                if index != -1:
                    new_feat.setAttribute( index, value )
        
        # sub function to add features
        def addNewFeature(layer, features, editLayers, repair_geom=True):
            # create new edit command
            if layer not in editLayers:
                layer.startEditing()
                layer.beginEditCommand( 'createSuoliCondParticella' )
                editLayers.append( layer )
            
            # add new features to layer
            layer.addFeatures( features )
            
            if repair_geom:
                # repair new feature geometries
                editBuffer = layer.editBuffer()
                if editBuffer is not None:
                    for fid, feat in editBuffer.addedFeatures().items():
                        QGISAgriLayers.repair_feature(
                            layer, 
                            feat, 
                            attr_dict={}, 
                            splitMultiParts=True,
                            autoSnap=True,
                            #suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                            suoliSnapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE,
                            suoliSnapLayerUris=self.suoliSnapLayerUris )
        
        ###################################################
        
        # init
        suoliMinArea = agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO
        removeFeatIdsDict = {}
        condFeats = []
        noCondFeats = []
        editLayers = []
        editReadOnlyLayers = []
        result = False
        
        # get command config
        cmd_cfg = self.getCommandConfig( 'suoliCondParticella' )
        filter_expr = cmd_cfg.get( 'filterExpression', None )
        filter_lav_expr = cmd_cfg.get( 'filterLavExpression', None )
        if filter_expr is None or  filter_lav_expr is None:
            logger.msgbox(
                    logger.Level.Critical, 
                    tr('Nessun filtro definito per le Particelle in conduzione.'), 
                    title=tr('ERRORE'))
            return False
        
        feature_cond_request = QgsFeatureRequest( 
            QgsExpression( f"{filter_expr} AND {filter_lav_expr}" ) )
        
        feature_nocond_request = QgsFeatureRequest( 
            QgsExpression( f"NOT({filter_expr}) AND {filter_lav_expr}" ) )
        
        # get attributes to copy
        destNoCondMapFields = cmdMapField( destNoCondVectlayer )
        destMapFields = cmdMapField( destVectlayer )
    
        # check if cond particella
        condPartFlg = True
        if feature_cond_request.acceptFeature( feature ):
            if createOnlyNoCondSuoli:
                return False
        
        # check if cond particella    
        elif feature_nocond_request.acceptFeature( feature ):
            condPartFlg = False
            
        else:
            return False
        
        # get geometry
        inGeometry = QgsGeometry( feature.geometry() )

        # loop 'Suoli no conduzione' layers
        for noCondLayer in noCondVectlayers:
            # prepare dict
            layerId = noCondLayer.id()
            if layerId not in removeFeatIdsDict:
                removeFeatIdsDict[layerId] = []
            removeFeatIds = removeFeatIdsDict[layerId]
            
            # get features that insersect the input feature
            outFeats_ids = QGISAgriLayers.getFeaturesIdByGeom( 
                noCondLayer, 
                inGeometry, 
                expression=None )
                
            # loop features for intersection\difference
            for fid in outFeats_ids:
                # get feature geometry
                found = False
                feat = noCondLayer.getFeature( fid )
                featGeom = QgsGeometry( feat.geometry() )
                # check if there are intersections
                if not inGeometry.intersects( featGeom ):
                    continue
                    
                # get difference geometries
                intersGeom = featGeom.intersection( inGeometry )
                # check if valid
                if not intersGeom.isEmpty() and\
                   not intersGeom.isNull() and\
                   not intersGeom.area() < suoliMinArea:
                    
                    # create feature
                    if condPartFlg:
                        newFeature = QgsVectorLayerUtils.createFeature( destVectlayer, intersGeom )
                        copyFieldValues( feat, newFeature, destMapFields )
                        condFeats.append( newFeature )
                    else:
                        newFeature = QgsVectorLayerUtils.createFeature( destNoCondVectlayer, intersGeom )
                        copyFieldValues( feat, newFeature, destNoCondMapFields )
                        noCondFeats.append( newFeature )
                    found = True
                    
                    # get difference geometries
                    diffGeom = featGeom.difference( inGeometry )
                    # check if valid
                    if not diffGeom.isEmpty() and\
                       not diffGeom.isNull() and\
                       not diffGeom.area() < suoliMinArea:
                        # create feature
                        if noCondLayer == destVectlayer:
                            newFeature = QgsVectorLayerUtils.createFeature( destVectlayer, diffGeom )
                            copyFieldValues( feat, newFeature, destMapFields )
                            condFeats.append( newFeature )
                        else:
                            newFeature = QgsVectorLayerUtils.createFeature( destNoCondVectlayer, diffGeom )
                            copyFieldValues( feat, newFeature, destNoCondMapFields )
                            noCondFeats.append( newFeature )
                        found = True
                    
                # collect feature to remove
                if found:
                    removeFeatIds.append( fid )
        
        # check if there are features
        if not condFeats and not noCondFeats:
            return False
        
        # execute edit command
        try: 
            # create 'no cond corrotti Suoli' features
            if noCondFeats:
                addNewFeature( destNoCondVectlayer, noCondFeats, editLayers )
            
            # create 'cond Suoli' features
            if condFeats:
                addNewFeature( destVectlayer, condFeats, editLayers )
                
            # remove 'no cond Suoli' features
            project = QgsProject.instance()
            for layerId, fids in removeFeatIdsDict.items():
                # get layer
                layer = project.mapLayer( layerId )
                # open edit command
                read_only = layer.readOnly()
                if read_only:
                    layer.setReadOnly( False )
                layer.startEditing()
                layer.beginEditCommand( 'createSuoliCondParticella' )
                editLayers.append( layer )
                if read_only:
                    editReadOnlyLayers.append( layer )
                # remove features
                layer.deleteFeatures( fids )
            
            
            # close all edit command
            for layer in editLayers:
                layer.endEditCommand()
                if Qgis.QGIS_VERSION_INT >= 31600:
                    layer.commitChanges( False )
                else:
                    layer.commitChanges()
                
                
            
            # set successful result
            result = True
                 
        except Exception as e:
            # reject all edit command
            for layer in editLayers:
                layer.destroyEditCommand()
            raise e
                
        finally:
            # commit or rollback read only layer
            for layer in editReadOnlyLayers:
                commit_result = True
                if layer.isEditable():
                    if result:
                        commit_result = layer.commitChanges()
                    else:
                        commit_result = layer.rollBack()
                layer.setReadOnly( True )
                if not commit_result:
                    raise Exception( layer.commitErrors() )
        
        return result 

    # --------------------------------------
    # 
    # --------------------------------------
    def onDownloadEventoLavorazione(self, agriControlBox, foglioData, reloadTables=True):
        """Create and populate offline DB"""
        
        # geoJSON collection
        geoJsonColl = {}
        geoJsonTotColl = {}
        
        # debugger timer
        dbgTimerTot = logger.createDebugTimer()
        
        ###########################################################################################
        ###########################################################################################
        def onComplete( isSuccessful=True, initializeDb=True ):
            try:
                # check if offline
                if not self.isOfflineDb:
                    self.init( foglioData )
                    return
                
                # check if successful
                if not isSuccessful:
                    # reject foglio
                    self.onRejectFoglio( ask=False, msgOut=False, foglioData=foglioData, silentError=True )
                    self._updateFoglioState( None, unselect=True )
                    
                    # show error
                    if reqColl.Errors:
                        logger.msgbox( logger.Level.Critical, reqColl.Errors[0], title=tr('ERRORE') )
                    
                    # 
                    self.init( foglioData )
                    return
                
                # set 'evento lavorazione' working flag
                self.__isOfflineFoglio = True
                
                # start debugger timer
                dbgTimer = logger.createDebugTimer()
                dbgTimer.start( "Caricamento layer in TOC" )
                
                # complete offline db schema
                if initializeDb:
                    self._prepare_db( scriptName='initialize' )
                
                # remove all layers
                if self.plugin.controlbox.isNewSelectedFoglioData:
                    self._clearTOC()
                
                # reinitialize plugin
                self.init( foglioData )
                
                # start work
                if self.start():
                    # enables\disables action special cases       
                    self.post_init(foglioData)
                    
                    # reset error box
                    self.plugin.errorsbox.reset()

                    
                    if initializeDb:
                        # check countings
                        self._checkDeclaredSuoli()
                        
                    # load sfondo layer
                    self.loadSfondo( -1, zoom=False, searchByAttrib='loadOnInit' )
                    if self.plugin.authenticated:
                        self.loadSfondo( -1, zoom=False, searchByAttrib='loadOnWork' )
                    else:
                        logger.log_warning( tr( 'Caricamento del livello di Sfondo disabilitato: autenticazione scaduta' ) )
                    
                    # set bold border style for qgis canvas widget
                    self.styleCanvasWidget() 
                      
                    # emit welcome message
                    logger.msgbar(logger.Level.Info, 
                                  tr( 'attività avviata correttamente: buon lavoro.' ), 
                                  title=self.plugin.name)
                
                # stop debugger timer    
                dbgTimer.stop()
                
                # check if downloaded suoli with invalid geometry
                errGeomTag = { 
                    'MultiPoint': tr( 'puntuale' ), 
                    'MultiLineString': tr( 'lineare' )
                }
                errMsgLst = []
                for srvName, geoJsonColl in geoJsonTotColl.items():
                    for geomName, geoJsonData in geoJsonColl.items():
                        featColl = geoJsonData.get( 'features', [] )
                        numFeats = len(featColl)
                        errMsgLst.append( "{0: >3} : {1} {2}".format( numFeats,
                                                                     tr( 'entità di tipo' ),
                                                                     errGeomTag.get( geomName, geomName) ) )
                # show warning message
                if errMsgLst:
                    logger.msgbox( logger.Level.Warning,
                                   '{0}:\n\n{1}'.format( tr( 'Presenti delle geometrie errate dei suoli' ), 
                                                    "\n ".join( errMsgLst ) ),
                                   title=tr('ERRORE') )
                    
                    
            except Exception as e:
                logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
                
            finally:
                # stop total debugger time
                dbgTimerTot.stop()
                # disconnect db
                self._disconnect_db( True )
                # destroy control box spinner
                self.plugin.controlbox.destroySpinner()
        
        
#         def importRemainingService(serviceData):
#             # loop remain service auto import
#             service_cfg = agriConfig.get_value('agri_service', {})
#             resources_cfg = service_cfg.get('resources', {})
#             for serviceName, api_cfg in resources_cfg.items():
#                 isAutoImp = api_cfg.get('autoImport', False)
#                 if isAutoImp:
#                     # import new service
#                     self.onServiceRequest( serviceName, serviceData, None, onFinishedServiceRequest, parent=None, cache=False, createSpinner=False )
#                     yield serviceName
#                     
#             # complete downloading
#             onComplete()
                    
        ################importRemainingServiceGen = importRemainingService({})
        
        def onFinishedServiceRequest( error, callbackData ):
            serviceName = 'ScaricaSuoli'
            requestCollector = None
            geoJsonColl = {}
             
            try:
                # init
                callbackData = callbackData or {}
                requestCollector = callbackData.get( 'requestCollector', None )
                
                # check if offline
                if not self.isOfflineDb:
                    return 
                
                # check service
                if error is not None:
                    raise QGISAgriRequestError(error)
                
                serviceName = callbackData.get( 'serviceName', None )
                serviceData = callbackData.get( 'serviceData', None )
                #servRowSelData = callbackData.get( 'servRowSelData', None )
                
                # debugger timer
                dbgLayTimer = logger.createDebugTimer()
                dbgSrvTimer = logger.createDebugTimer()
                dbgSrvTimer.start( "Importa servizio {0}".format( serviceName ) )
                
                # get service configuration
                service_cfg = agriConfig.get_value( 'agri_service', {} )
                resources_cfg = service_cfg.get( 'resources', {} )
                res_cfg = resources_cfg.get( serviceName, {} )
                hasGeometry = res_cfg.get( 'hasGeometry', False )
                
                # compose db layer configuration
                dbErrLayers_cfg = res_cfg.get( 'dbErrLayers', None )
                dbLayers_cfg = res_cfg.get( 'dbLayers', None )
                if not dbLayers_cfg:
                    layer = str( res_cfg.get( 'dbName', serviceName ) )
                    dbLayers_cfg = {}
                    dbLayers_cfg[ serviceName ] = {
                        'dbName': res_cfg.get( 'dbName', serviceName ),
                        'copy': res_cfg.get( 'copy', None ),
                        'ogrOptions': res_cfg.get( 'ogrOptions', None ),
                        'subsetString': res_cfg.get( 'subsetString', None ),
                        'subData': res_cfg.get( 'subData', {} )
                    }
                else:
                    # check if import all service as copied table
                    cpyLayer = res_cfg.get( 'copy', None )
                    if cpyLayer is not None:
                        dbLayers_cfg[ cpyLayer ] = {
                            'dbName': cpyLayer,
                            'copy': None,
                            'ogrOptions': res_cfg.get( 'ogrOptions', None ),
                            'subsetString': None
                        }
                        
                # check if valid geometries
                if hasGeometry:
                    # slit a GeoJSON on geometry multipat type
                    geojsonHelper = geoJsonHelper()
                    geoJsonColl = geojsonHelper.splitOnGeomType( serviceData, asMultipart=True )
                    serviceData = geoJsonColl['MultiPolygon']
                    del geoJsonColl['MultiPolygon']
                    geoJsonTotColl[serviceName] = geoJsonColl
                    
                    
                # create connection
                dbConn = self._connect_db().getConnector()
                
                # import tables
                for layerKey, layer_cfg in dbLayers_cfg.items():
                    layer = layerKey
                    dbgLayTimer.start()
                    
                    if hasGeometry:
                        # import geometry table
                        layer = layer_cfg.get( 'dbName', layerKey )
                        dbConn.importGeoJsonFromData( layer, 
                                                      serviceData, 
                                                      layerOptions = layer_cfg.get( 'ogrOptions', None ), 
                                                      layerSubsetString = layer_cfg.get( 'subsetString', None ), 
                                                      createSchema = False )
                    else:
                        # import normal table
                        dbConn.importTable( layer, serviceData )
                        
                    # copy/clone imported layer
                    cpyLayer = layer_cfg.get( 'copy', None )
                    if cpyLayer is not None:
                        dbConn.cloneTable( layer, cpyLayer, append=True )
                        
                    # import sub data
                    sub_data_cfg = layer_cfg.get( 'subData', {} )
                    if sub_data_cfg:
                        sub_layer = sub_data_cfg.get( 'dbName', None )
                        sub_data_field = sub_data_cfg.get( 'fieldData', None )
                        copy_layer_fields = sub_data_cfg.get( 'copyLayerFields', {} )
                        sub_fields = sub_data_cfg.get( 'subFields', {} )
                        if sub_layer and sub_data_field:
                            dbConn.importGeoJsonSubData( sub_layer, 
                                                         sub_data_field, 
                                                         copy_layer_fields, 
                                                         sub_fields, 
                                                         serviceData )
                        
                    
                    # stop layer debug timer    
                    dbgLayTimer.stop( "Importa layer {0}".format( layer ) )
                    
                # import geoJSON with wrong geometry type
                if hasGeometry:
                    # import geoJSON with wrong geometry type
                    for geomErrType in ['MultiLineString', 'MultiPoint']:
                        # get GeoJSON with wrong geometry type
                        serviceErrData = geoJsonColl.get( geomErrType, None )
                        if not serviceErrData:
                            continue
                        
                        # get layer from config
                        errLayer_cfg = dbErrLayers_cfg.get( geomErrType, {} )
                        errLayer = errLayer_cfg.get( 'dbName', None )
                        if not errLayer:
                            continue
                        
                        # start loading layer debug timer
                        dbgLayTimer.start()
                        
                        # import GeoJSON
                        dbConn.importGeoJsonFromData( errLayer, 
                                                      serviceErrData, 
                                                      layerOptions = errLayer_cfg.get( 'ogrOptions', None ), 
                                                      layerSubsetString = None, 
                                                      createSchema = False )
                        
                        # stop loading layer debug timer    
                        dbgLayTimer.stop( "Importa layer {0}".format( errLayer ) )
                    
                    
                # stop service debug timer
                dbgSrvTimer.stop()
                
                # update requests collector
                if requestCollector is not None:
                    requestCollector.setSuccessful()
            
            except QGISAgriRequestError as e:
                self._disconnect_db(True)
                # abort requests
                if requestCollector is not None:
                    requestCollector.abort()
                
            except Exception as e:
                self._disconnect_db(True)
                # handle exception
                logger.msgbox( logger.Level.Critical, '{0}: "{1}"\n\n{2}'.format( tr( 'Servizio' ), str(serviceName), formatException(e) ), title=tr('ERRORE') )
                 
#             ######################################################################################    
#             try:
#                 # call next service import
#                 next( importRemainingServiceGen, None )
#             except Exception as e:
#                 self._disconnect_db(True)
#                 # handle exception
#                 logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
                        
        ###########################################################################################
        ###########################################################################################
        
        try:
            # close edit mode
            cmdName = "ScaricaSuoli"
            if not self.closeEditMode( cmdName ):
                return
            
            # log
            self.log_command( cmdName )
            dbgTimerTot.start( "{0} {1}".format( tr( "TOTALE" ), cmdName ) )
            
            # show control box spinner
            spinner = self.plugin.controlbox.createSpinner()
            spinner.show()
            
            # check if offline db
            if self.isOfflineDb:
                # check if there is a foglio loaded
                if self.__isOfflineFoglio:
                    return onComplete( initializeDb=False )
            else:
                # create a clone offline db
                self._create_clone_db()
            
            # create connection
            dbConn = self._connect_db().getConnector()
            
            # service config
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            resources_cfg = service_cfg.get( 'resources', {} )
            
            
            # store servizi selected data
            allData = {}
            for servizio, selModel in agriControlBox.serviceStoreModel.items():
                table = servizio
                selRow = selModel.rowFilter
                rows = {}
                if not selRow:
                    rows = selModel.rows
                    allData = { **allData, **( selModel.getRow( 0, {} ) ) }
                else:
                    rows = [ selRow ]
                    allData = { **allData, **selRow }
                    
                # check if full record import
                service_cfg = resources_cfg.get( servizio, {} )
                key_fields = service_cfg.get( 'keyfields', '' )
                selected_Field = service_cfg.get( 'selectedField', '' )
                if selected_Field and key_fields:
                    rows = selModel.getRowsWithSelectedField( selected_Field )
                    dbConn.importTable( table, rows, dropTable=False, conflictFields=key_fields )
                else:
                    dbConn.importTable( table, rows )
                    
                    
            # get idEventoLavorazione field
            cmd_cfg = agriConfig.get_value( 'commands/scaricasuoli', {} )
            idEventoLavField = cmd_cfg.get( 'idEventoLavField', '' )
            try:
                self.__idEventoLavorazione = int( allData.get( idEventoLavField, None ) )
                self._setDbSetting( { self.DB_ID_EV_LAVORAZIONE_KEY: self.__idEventoLavorazione } )
            except:
                self.__idEventoLavorazione = None
                raise Exception( tr( "Id evento lavorazione non reperito nei dati scaricati dal servizio" ) )
            
            # check if PARTICELLE working
            idTipoLista = cmd_cfg.get( 'idTipoLista', '' )
            idTipoListaParticellaValue = cmd_cfg.get( 'idTipoListaParticella', '-1' )
            idTipoListaCurrValue = allData.get( idTipoLista, None )
            isParticelleWorking = str(idTipoListaCurrValue) == str(idTipoListaParticellaValue)
            
            # collect all remaining service requests 
            reqColl = QGISAgriNetworkAccessManagerCollector()
            reqColl.finishedAllRequests.connect( onComplete )
            
            for serviceName, api_cfg in resources_cfg.items():
                # check if DBE service
                if api_cfg.get( 'serviceDB3', False ):
                    if not __PLG_DB3__:
                        continue
                
                # check if auto import service
                if not api_cfg.get( 'autoImport', False ):
                    # no auto import service
                    pass
                
                elif not isParticelleWorking and api_cfg.get( 'particelleWorking', False ):
                    # exclude PARTICELLE auto import service
                    pass
                
                else:
                    # import auto service
                    self.onServiceRequest( serviceName, 
                                           allData, 
                                           None, 
                                           onFinishedServiceRequest, 
                                           parent=None, 
                                           cache=False, 
                                           createSpinner=False,
                                           requestCollector=reqColl )
            reqColl.endRequest()
            
#             syncronous requests chain            
#             import remaining services
#             importRemainingServiceGen = importRemainingService( allData )
#             next( importRemainingServiceGen, None )


        
        except Exception as e:
            # reject foglio
            self.onRejectFoglio( ask=False, msgOut=False, foglioData=foglioData )
            # disconnect offline db
            self._disconnect_db(True)
            # destroy control box spinner
            self.plugin.controlbox.destroySpinner()
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            
        finally:
            # reinitialize plugin
            if self.isOfflineDb and not self.__isOfflineFoglio:
                self.init( foglioData, waiting=True )
    
           
    # --------------------------------------
    # 
    # --------------------------------------        
    def onRejectListaLav(self, ask=True, msgOut=True, evLavData=None):
        """Reject current job and remove offline db"""
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if error:
                return
            
            # reset current actvity to start a new job
            msg = tr( "Lavorazione annullata con successo" ) if msgOut else None
            if rejectRemoteEvLav:
                # show done message
                if msg is not None:
                    logger.msgbox( logger.Level.Info, msg, title=tr('INFO') )
                # reload service grid
                self.plugin.controlbox.onServiceReload()
            else:
                # reset current actvity to start a new job
                self._resetActivity( 
                    doneMsg=msg, 
                    levMsg=logger.Level.Success, 
                    unlockEventoLavorazione=True )
                    
        ###########################################################################################
        ###########################################################################################
        
        try: 
            # init
            rejectRemoteEvLav = ( not self.isOfflineDb and evLavData is not None )
            
            # confirm
            if ask:
                msg_ask1 = tr("Sei sicuro di voler annullare la lavorazione in corso?")
                msg_ask2 = tr("Tutte le modifiche apportate andranno perse.")
                msg_ask3 = tr("ATTENZIONE:\nassicurati che lavorazione non sia presa in carico da nessuno!")
                
                if self.isOfflineDb:
                    reply = QMessageBox.question(
                       self.plugin.iface.mainWindow(), 
                       tr('Annullare la lavorazione?'), 
                       f"{msg_ask1}\n{msg_ask2}", 
                       QMessageBox.Yes, QMessageBox.No)
                
                else:
                    reply = QMessageBox.warning(
                       self.plugin.iface.mainWindow(), 
                       tr('Annullare la lavorazione?'),
                       f"{msg_ask1}\n{msg_ask2}\n\n{msg_ask3}",
                       QMessageBox.Yes, QMessageBox.No)
                
                if reply != QMessageBox.Yes:
                    return
                
                
            # close edit mode
            serviceName = 'SbloccoForzato'
            if self.isOfflineDb and not self.closeEditMode( serviceName ):
                return
                
            # log
            self.log_command( serviceName )
            
            # get from offline db
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            table = res_cfg.get( 'dbName', serviceName )
            warningCodes = res_cfg.get( 'warningDtoCodes', [] )
                
            # get 'Evento Lavorazione' data 
            data = None
            if rejectRemoteEvLav:
                # from input 'Evento lavorazione' selected row data
                data = evLavData
                
            else:
                data = self.getDbTableData( table )
                if not data:
                    raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
                data = list(data)[0]
            
            # call online agri api to unlock current job
            self.onServiceRequest( serviceName, data, None, callbackServiceFn, parent=self.plugin.controlbox, warningCodes=warningCodes )
        
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            
    # --------------------------------------
    # 
    # --------------------------------------        
    def onRejectFoglio(self, ask=True, msgOut=True, foglioData=None, silentError=False):
        """Reject current job and remove offline db"""
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if error:
                ##self.plugin.controlbox.onServiceReload()
                return
            
            msg = tr( "Foglio sbloccato con successo." )
            levMsg = logger.Level.Success
            unlockEventoLavorazione = True
            errDTO = callbackData.get( 'esitoDTO', None )
            
            # if only foglio unlocked
            if errDTO is not None and errDTO in onlyFoglioUnlockCodes:
                unlockEventoLavorazione = False
                msg = "{0}<br><br><b>Evento di lavorazione da completare.</b>".format( msg )
                levMsg = logger.Level.Warning
            else:
                msg = "{0}<br>Evento di lavorazione sbloccato.".format( msg )
                
            msg = msg if msgOut else None
            
            # reset current actvity to start a new job
            serviceCfg = agriConfig.services.fogliAzienda
            self._resetActivity( 
                doneMsg=msg, 
                levMsg=levMsg, 
                unlockEventoLavorazione=unlockEventoLavorazione, 
                foglioState=serviceCfg.statoFieldReject )
                    
        ###########################################################################################
        ###########################################################################################
        
        try:
            # check if offline
            if not self.isOfflineDb:
                return
            
            # confirm
            if ask:
                msg_ask1 = tr("Sei sicuro di voler sbloccare il foglio in lavorazione?")
                msg_ask2 = tr("Tutte le modifiche apportate andranno perse.")
                reply = QMessageBox.question(
                    self.plugin.iface.mainWindow(), 
                    tr('Annullare la lavorazione del foglio?'),
                    f"{msg_ask1}\n{msg_ask2}",
                    QMessageBox.Yes, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
                
            # close edit mode
            serviceName = 'SbloccoForzatoFoglio'
            if not self.closeEditMode( serviceName ):
                return
                
            # log
            self.log_command( serviceName )
                
            # get 'Evento Lavorazione' data from offline db
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            table = res_cfg.get( 'dbName', serviceName )
            warningCodes = res_cfg.get( 'warningDtoCodes', [200] )
            onlyFoglioUnlockCodes = res_cfg.get( 'onlyFoglioUnlockCodes', [] )
            
            data = {}
            servRowSelData = {}
            if foglioData is None:
                data = self.getDbTableData( table )
                if not data:
                    raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il servizio"), serviceName ) )
                data = list(data)[0]
                
                servRowSelData = self.plugin.controlbox.currentFoglioData
                if not servRowSelData:
                    raise Exception( "{0}: {1}".format( tr("Nessun dato reperito per il foglio corrente"), serviceName ) )
            else:
                servRowSelData = foglioData
            
            # call online agri api to unlock current job
            self.onServiceRequest( 
                serviceName, data, servRowSelData, callbackServiceFn, parent=self.plugin.controlbox, warningCodes=warningCodes, silentError=silentError )
        
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))

    

    # --------------------------------------
    # 
    # --------------------------------------
    def onUploadEventoLavorazione(self, ask=True, warningAsError=False):
        """Upload done work list"""
        
        ###########################################################################################
        ###########################################################################################
        def callbackServiceFn( error, callbackData ):
            
            # check if error
            if error:
                return
            
            # if only foglio unlocked
            msg = tr( "Foglio esportato sul server remoto con successo." )
            levMsg = logger.Level.Success
            unlockEventoLavorazione = True
            errDTO = callbackData.get( 'esitoDTO', None )
            if errDTO is not None and errDTO in onlyFoglioUnlockCodes:
                unlockEventoLavorazione = False
                msg = "{0}<br><br><b>------> Evento di lavorazione da completare !!!!</b>".format( msg )
                levMsg = logger.Level.Warning
            else:
                msg = "{0}<b>------> Evento di lavorazione sbloccato.</b>".format( msg )
            
            # reset current actvity to start a new job
            serviceCfg = agriConfig.services.fogliAzienda
            self._resetActivity(
                doneMsg=msg, 
                levMsg=levMsg, 
                unlockEventoLavorazione=unlockEventoLavorazione, 
                foglioState=serviceCfg.statoFieldDone )
                    
        ###########################################################################################
        ###########################################################################################
        
        # init
        json_file = None
        eraseTempFile = True
        suoliPartLayer = None
        partController = self.plugin.particelle
        checker = self.checker
        isParticelleWorkingEnabled = partController.isParticelleWorkingEnabled
        layerVirtualizer = LayerVirtualizer( startId=1 )
        
        try:
            # log
            serviceName = 'SalvaSuoli'
            self.log_command( serviceName )
            
            # confirm by user
            if ask:
                reply = QMessageBox.question(self.plugin.iface.mainWindow(), tr('Continuare?'), 
                         tr('Sei sicuro di volere salvare la lavorazione?'), QMessageBox.Yes, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return self.USER_CANCEL
                
            # check if any validation disabled
            if not self.checker.can_proceed_if_disabled_checks():
                return self.USER_CANCEL
                
            # close edit mode
            if not self.closeEditMode( serviceName ):
                return self.USER_CANCEL
                
            # init
            errorData = QGISAgriFeatureErrors()
            logger.add_progressbar( tr('Salvataggio evento di lavorazione in rete...'), only_message=True )
            logger.suspend_msgbar( )
            
            # clear error panel
            self.plugin.errorsbox.clear()
                
            # get foglio data
            foglioData = None
            controlbox = self.plugin.controlbox
            if controlbox.totFogliToWork == 1:
                foglioData = controlbox.currentFoglioData
             
            # re initialize plugin
            self.init( foglioData, initSfondo=False )
             
            # load suolo layers
            self.load_suoli_layers( 
                except_unfound=QGISAgriMessageLevel.Debug, filtered=False, clear_toc=True, ext_style=False )
            
            # set activity as started
            self.plugin.set_started( True )
            logger.suspend_msgbar( False )
            
            # get command configuration
            cmd_salva_cfg = self.getCommandConfig( 'salvasuoli' )
            att_check_cfg = cmd_salva_cfg.get( 'checkFields', {} )
            err_lay_cfg = cmd_salva_cfg.get( 'errorLayer', {} )
            part_lay_cfg = cmd_salva_cfg.get( 'suoliParticella', {} )
            eraseTempFile = cmd_salva_cfg.get( 'eraseTempFile', False )
            
            fld_def = att_check_cfg.get( 'cessato', {} )
            fld_cessato_filter = fld_def.get( 'filter', '' ) ## COALESCE(cessato,0) = 1
            
            padre_id_cfg = cmd_salva_cfg.get( 'padreRelation', {} )
            padre_id_src_lay = padre_id_cfg.get( 'srcLayer', '' )
            padre_id_src_fld = padre_id_cfg.get( 'srcField', '' )
            padre_id_dst_fld = padre_id_cfg.get( 'dstField', '' )
            check_fld = padre_id_cfg.get( 'chkField', '' )
            modif_fld = padre_id_cfg.get( 'modField', '' )      
            lavorato_fld = padre_id_cfg.get( 'lavField', '' )
            sospeso_fld = padre_id_cfg.get( 'sspField', '' )
            modif_val = padre_id_cfg.get( 'modValue', 1 )
        
            # get service configuration
            service_cfg = agriConfig.get_value( 'agri_service', {} )
            resources_cfg = service_cfg.get( 'resources', {} )
            res_cfg = resources_cfg.get( serviceName, {} )
            warningCodes = res_cfg.get( 'warningDtoCodes', [] )
            onlyFoglioUnlockCodes = res_cfg.get( 'onlyFoglioUnlockCodes', [] )
            ####table = res_cfg.get( 'dbName', serviceName )
            ####warningCodes = res_cfg.get( 'warningDtoCodes', [200] )
            
            # compose feature filter expression
            featureSelExpr = f"NOT ({fld_cessato_filter})" if fld_cessato_filter else '' ## NOT (COALESCE(cessato,0) = 1)
            featureLavorateExpr = f"{featureSelExpr} AND ({lavorato_fld} = '{modif_val}' OR {sospeso_fld} = '{modif_val}' OR {modif_fld} = '{modif_val}')"
            
            ##########################################################################################################################
            ##########################################################################################################################
            # checks
            
            # get 'suoli lavorazione' vector layer
            suoliLayers = QGISAgriLayers.get_vectorlayer( self.__suoli_main_layer_uri )
            if not suoliLayers:
                raise Exception( tr( "Nessun layer associato al comando SalvaSuoli" ) )
            
            partLayers = QGISAgriLayers.get_vectorlayer( partController.mainLayerUri )
            if not partLayers:
                raise Exception( tr( "Nessun layer PARTICELLE associato al comando SalvaSuoli" ) )
            
            # loop all suoli layers
            options = { 
                'layerAliasName': serviceName,
                'showWrnMessage': False 
            }
            
            # check Suoli (geometry & topology)
            for layer in suoliLayers:
                # geometry validation
                nErrors = errorData.numErrors
                if checker.checkSuoliValidity( layer, errorData, options ) and \
                   (errorData.numErrors - nErrors) <= 0:                
                    # topology validation
                    checker.checkSuoliTopology( layer, errorData, options )
            
            # check PARTICELLE (geometry & topology)
            if isParticelleWorkingEnabled:
                options['isParticelleWorking'] = True
                
                # loop all PARTICELLE layers
                for layer in partLayers:
                    # geometry validation
                    nErrors = errorData.numErrors
                    if checker.checkSuoliValidity( layer, errorData, options ) and \
                       (errorData.numErrors - nErrors) <= 0:                
                        # topology validation
                        checker.checkSuoliTopology( layer, errorData, options )
                
            # check if errors
            hasErrors = errorData.hasErrors or (errorData.hasWarnings if warningAsError else False)
            if hasErrors:
                self.plugin.errorsbox.setErrors( errorData )
                createErrLayer = agriConfig.get_value( 'commands/checkSuoli/addErrorLayer', False )
                if createErrLayer:
                    errorData.createLayer( serviceName, layerName=err_lay_cfg.get( 'name', serviceName ), tocGrpName=checker.TOC_ERR_GRP_NAME )
                    
                raise Exception( '{0}: "{1}"\n\n{2}'.format( 
                                    tr( 'Servizio' ), 
                                    serviceName, 
                                    "Elaborazione interrotta perché riscontrati degli errori." ) )
            
            
            ##########################################################################################################################
            ##########################################################################################################################
            
  
            # 1) create a temporary json file to write to
            suoloLayer = suoliLayers[0]
            ext_rect = suoloLayer.extent()
            for layer in suoliLayers:
                ext_rect.combineExtentWith( layer.extent() )
            
            if isParticelleWorkingEnabled:
                for layer in partLayers:
                    ext_rect.combineExtentWith( layer.extent() )
            
            
            cfg_fields_tot = {}
            json_file = fileUtil.createEmptyTemporaryFile( suffix='.geojson' )
            fileWriter = QGISAgriVectorFileWrite( json_file,
                                                  fileEncoding = "utf-8",
                                                  crs = suoloLayer.sourceCrs(),
                                                  driverName = 'GeoJSON' )
            
            areaFn = lambda feat,value : feat.geometry().area()
            idFeatureFn = lambda feat,value : NULL if ( feat.attribute( modif_fld ) == 1 ) else value
            
            ######################################################################################
            # 1.1) add general user settings
            cfg_fields = {
                'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                'flagDiffAreaSuoli': { 'type': 'Bool' },
                'flagCessatiSuoli': { 'type': 'Bool' },
                'flagAreaMinSuoli': { 'type': 'Bool' },
                'flagDiffPartSuoli': { 'type': 'Bool' },
                'anomalia': { 'type': 'String' },
                'layer': { 'type': 'String', 'value': 'CONFIGURAZIONE' }
            }
            cfg_fields['idEventoLavorazione']['value'] = self.idEventoLavorazione
            cfg_fields['flagDiffAreaSuoli']['value'] = self.plugin.errorsbox.checkDiffAreaSuoli
            cfg_fields['flagCessatiSuoli']['value'] = self.plugin.errorsbox.checkCessatiSuoli
            cfg_fields['flagAreaMinSuoli']['value'] = self.plugin.errorsbox.checkAreaMinSuoli
            cfg_fields['flagDiffPartSuoli']['value'] = self.plugin.errorsbox.checkPartLavorate
            #cfg_fields['anomalia']['value'] = ";".join( errorData.getForcedWarnings()[:1] ) # <----- only first error
            cfg_fields['anomalia']['value'] = ";".join( errorData.getUniqueForcedWarnings() )
            cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
            
            # export feature to temp file
            fileWriter.writeFictitiousFeature( suoloLayer, self.SAVING_LAYER_NAME, cfg_fields, extent=ext_rect )
            
            
            ######################################################################################
            # 1.1) add erased "Suoli no conduzione"
            if isParticelleWorkingEnabled:
                suoliNoCondLayers = self.get_suolo_vector_layers( 'salvasuoli|nocond' ) or []
                for layer in suoliNoCondLayers:
                    # get suolo layer name
                    suoloNoCondLayer = layer.clone()
                    suoloNoCondLayer.setSubsetString( None )
                    
                    # count features removed
                    totRemFeatures = 0
                    for _ in suoloNoCondLayer.getFeatures( fld_cessato_filter ):
                        totRemFeatures += 1
                    
                    # add removed features
                    if totRemFeatures:
                        cfg_fields = {
                            'idFeature': { 'type': 'Int', 'suolo_key_field': True },
                            'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                            'tipoSuolo': { 'type': 'String' },
                            'layer': { 'type': 'String', 'value': 'SUOLI_CESSATI' }
                        }
                        cfg_fields['idEventoLavorazione']['value'] = self.idEventoLavorazione
                        cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
                        
                        # append features to temp file
                        fileWriter.writeLayer( suoloNoCondLayer,
                                               self.SAVING_LAYER_NAME,
                                               cfg_fields,
                                               featureSelExpr = fld_cessato_filter,
                                               skipEmptyGeom = True,
                                               skipNullKeyField = True ) ## COALESCE(cessato,0) = 1
            
            
            # loop suoli layers
            for layer in suoliLayers:
                # get suolo layer name
                suoloLayerId = layerVirtualizer.getVirtualId( layer )
                suoloLayer = layer.clone()
                suoloLayer.setSubsetString( None )
                #suoloLayerName = suoloLayer.name()
                dsUri = QgsDataSourceUri( suoloLayer.dataProvider().dataSourceUri() )
                suoloLayerName = dsUri.table()
                
                # get command configuration for current layer
                cmd_save_cfg = agriConfig.get_value( f'commands/salvasuoli/suoliLavorazione/{suoloLayerName}', {} )
                ##onlyBaseAttribute = cmd_save_cfg.get( 'onlyBaseAttribute', False )
                suoliFilter = cmd_save_cfg.get( 'suoliFilter', '1!=1' )
                particelleFilter = cmd_save_cfg.get( 'particelleFilter', '1!=1' )
                
                # count features removed
                totRemFeatures = 0
                for _ in suoloLayer.getFeatures( fld_cessato_filter ):
                    totRemFeatures += 1
                    
                # count modified features
                totExpFeatures = 0
                for _ in suoloLayer.getFeatures( featureLavorateExpr ):
                    totExpFeatures += 1
            
                ##########################################################################################################################
                ##########################################################################################################################
                # get 'particelle_catastali' vector layer
                suoliPartLayer = None
                particelleLayerId = -1
                if totExpFeatures:
                    vlayers = self.get_suolo_vector_layers( filter_cmd='salvasuoli|particelle' )
                    if not vlayers:
                        raise Exception( tr('Nessun layer definito per le particelle catastali') )
                    particelleLayer = vlayers[0]
                    
                    # process 'suoli lavorazione', 'particelle_catastali' layer intersection
                    suoliPartLayerName = "{0}_{1}".format( part_lay_cfg.get( 'name', 'suoli_particelle' ), suoloLayerName )
                    res = self.checker.run_processing_script( 'suoliParticelle', {
                    
                        'inputLayer': suoloLayer.dataProvider().uri().uri(),
                        'particelleLayer': particelleLayer.dataProvider().uri().uri(),
                        'suoliFilter': suoliFilter,
                        'particelleFilter': particelleFilter,
                        'outputLayer': suoliPartLayerName,
                        'TOLL_AREA_MIN_SUOLO': agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO #agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO
                        
                    },  None, clearResults=True )
                    if not res:
                        raise Exception( tr('Errore nella creazione del layer temporaneo dei suoli particella') )
                    
                    
                    vlayers = QgsProject.instance().mapLayersByName( suoliPartLayerName )
                    if not vlayers:
                        raise Exception( tr('Nessun layer processato per le particelle catastali') ) 
                    else:
                        suoliPartLayer = vlayers[0]
                        particelleLayerId = layerVirtualizer.getVirtualId( particelleLayer )
                                  
                ######################################################################################
                # 2) add removed features
                if totRemFeatures:
                    cfg_fields = {
                        'idFeature': { 'type': 'Int', 'suolo_key_field': True },
                        'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                        'tipoSuolo': { 'type': 'String' },
                        'layer': { 'type': 'String', 'value': 'SUOLI_CESSATI' }
                    }
                    cfg_fields['idEventoLavorazione']['value'] = self.idEventoLavorazione
                    cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
                    
                    # append features to temp file
                    fileWriter.writeLayer( suoloLayer,
                                           self.SAVING_LAYER_NAME,
                                           cfg_fields,
                                           featureSelExpr = fld_cessato_filter,
                                           skipEmptyGeom = True,
                                           skipNullKeyField = True ) ## COALESCE(cessato,0) = 1
                    
                ######################################################################################
                # 3) add removed features for geometry, eleggibilità changes 
                #    Logical erasion: feature is changed for geometry of 'eleggibilità' attribute,
                #    but not erased; in export it will appear as erased and new suolo feature 
                
                ## NOT (COALESCE(cessato,0) = 1) AND (idFeaturePadre IS NOT NULL) AND (modificato= '1')
                featureModifExpr = f"{featureSelExpr} AND ({padre_id_src_fld} IS NOT NULL) AND ({modif_fld} = '{modif_val}')"
                
                
                cfg_fields = {
                    'idFeature': { 'type': 'Int', 'suolo_key_field': True },
                    'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                    'tipoSuolo': { 'type': 'String' },
                    'layer': { 'type': 'String', 'value': 'SUOLI_CESSATI' }
                }
                cfg_fields['idEventoLavorazione']['value'] = self.idEventoLavorazione
                cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
                
                # export features to temp file
                fileWriter.writeLayer( suoloLayer,
                                       self.SAVING_LAYER_NAME,
                                       cfg_fields,
                                       featureSelExpr = featureModifExpr,
                                       skipEmptyGeom = True,
                                       skipNullKeyField = True )
               
                ######################################################################################        
                # 4) add worked features
                
                ## NOT (COALESCE(cessato,0) = 1) AND (flagLavorato = '1' OR flagSospensione = '1' OR modifica = '1')
                featureLavorateExpr = f"{featureSelExpr} AND ({lavorato_fld} = '{modif_val}' OR {sospeso_fld} = '{modif_val}' OR {modif_fld} = '{modif_val}')"
                
                cfg_fields = {    
                    'OGC_FID': { 'type': 'Int' },
                    'OGC_LAYERID': { 'type': 'Int', 'value': 0 },
                    'idFeature': { 'type': 'Int' },
                    'idFeaturePadre': { 'type': 'JsonIntArray' },
                    'flagGeometriaVariata': { 'type': 'Bool', 'value': 0 },
                    'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                    'area':  { 'type': 'Double', 'value': 0.0 },
                    'tipoSuolo': { 'type': 'String' },
                    'layer': { 'type': 'String', 'value': 'SUOLI_LAVORATI' }
                }
                ##if not onlyBaseAttribute:
                cfg_ext_fields = {
                    'codiceNazionale': { 'type': 'String' },
                    'foglio': { 'type': 'String' },
                    'codiceEleggibilitaRilevata': { 'type': 'String' },
                    'flagSospensione': { 'type': 'Bool'  },
                    'descrizioneSospensione': { 'type': 'String' },
                    'noteLavorazione': { 'type': 'String' },
                    'idTipoMotivoSospensione': { 'type': 'Int' }
                }
                cfg_fields = {**cfg_fields, **cfg_ext_fields}
                    
                cfg_fields['idEventoLavorazione']['value'] = self.idEventoLavorazione
                cfg_fields['OGC_LAYERID']['value'] = suoloLayerId
                cfg_fields['area']['value'] = areaFn
                cfg_fields[ padre_id_src_fld ]['value'] = idFeatureFn
                cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
                
                    
                # export features to upload
                fileWriter.writeLayer( suoloLayer,
                                       self.SAVING_LAYER_NAME,
                                       cfg_fields,
                                       featureSelExpr = featureLavorateExpr )
                
                ######################################################################################
                # 5) add particelle-suoli features
                if suoliPartLayer is not None:
                    cfg_fields = {
                        'idFeature': { 'type': 'Int' },
                        'OGC_FID': { 'type': 'Int', 'rename': 'OGC_FID_SUOLO' },
                        'OGC_FID_2': { 'type': 'Int', 'rename': 'OGC_FID_PARTICELLA' },
                        'OGC_LAYERID_SUOLO': { 'type': 'Int', 'value': 0 },
                        'OGC_LAYERID_PARTICELLA': { 'type': 'Int', 'value': 0 },
                        'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                        
                        'codiceNazionale': { 'type': 'String' },
                        'foglio': { 'type': 'String' },
                        'codiceEleggibilitaRilevata': { 'type': 'String' },
                        'numeroParticella': { 'type': 'String' },
                        'subalterno': { 'type': 'String' },
                        
                        'area':  { 'type': 'Double', 'value': 0.0 },
                        'layer': { 'type': 'String', 'value': 'SUOLI_PARTICELLE' }
                    }
                    cfg_fields['idEventoLavorazione']['value'] = self.idEventoLavorazione
                    cfg_fields['OGC_LAYERID_SUOLO']['value'] = suoloLayerId
                    cfg_fields['OGC_LAYERID_PARTICELLA']['value'] = particelleLayerId
                    cfg_fields['area']['value'] = areaFn
                    cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
                    
                    # export features to temp file
                    fileWriter.writeLayer( suoliPartLayer,
                                           self.SAVING_LAYER_NAME,
                                           cfg_fields )
                    
                    # remove particelle-suoli layer
                    QGISAgriLayers.remove_layers( [ suoliPartLayer ] )
                    suoliPartLayer = None
                    
                    
            ######################################################################################
            # 6) add PARTICELLE features (PARTICELLE working)
            if isParticelleWorkingEnabled:
                cfg_fields_tot = partController.onUploadEventoLavorazione( 
                    cfg_fields_tot, self.SAVING_LAYER_NAME, fileWriter, layerVirtualizer )
                
            ######################################################################################
            # 7) call online agri api to upload suoli on remote server
            data = {}
            postData = None
            with open( json_file, "rb" ) as file:
                postData = json.dumps( 
                    jsonUtil.load( file, cfg_fields_tot, boolMapDict=jsonUtil.numBoolDictionary() ) )
            
            if not eraseTempFile:
                # save created GeoJSON file as temporary file
                with open( json_file, 'w' ) as file:
                    file.write( postData )

                # handle exception
                logger.msgbox( 
                    logger.Level.Warning,
                    ("Disabilatata l'esportazione per i test (conf: eraseTempFile).\n\n" 
                     "Salvato file: {}".format( json_file )), 
                    title=tr('ATTENZIONE') )
                
                # reload layers $ filters
                self.start( emit_msg=False )
                # return
                return True
                
            
            self.onServiceRequest( serviceName, data, None, callbackServiceFn, postData=postData, parent=self.plugin.controlbox, warningCodes=warningCodes )             
            return True
            
        except Exception as e:
            # handle exception
            logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
            
            # reload layers & filters
            self.start( emit_msg=False )
            return False
        
        finally:
            logger.suspend_msgbar( False )
            logger.remove_progressbar()
            self._disconnect_db()
            # close temporary GeoJSON file
            if eraseTempFile and json_file is not None:
                fileUtil.removeFile( json_file, noException=True )
            
    
    