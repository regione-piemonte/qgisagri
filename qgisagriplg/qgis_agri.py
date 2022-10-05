# -*- coding: utf-8 -*-
"""QGIS Agri entry class

Description
-----------

The main working code of the plugin. Contains all the information about 
the actions of the plugin. Defines the user interface.

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

import os.path
import types

# Import PyQt modules
from PyQt5.QtCore import ( Qt,
                           QSize,
                           pyqtSignal, 
                           QObject,    
                           QSettings, 
                           QTranslator, 
                           qVersion,
                           QCoreApplication, 
                           QSortFilterProxyModel )

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import ( QMenu, 
                              QToolButton, 
                              QComboBox, 
                              QLabel, 
                              QCompleter, 
                              QDockWidget, 
                              QMessageBox )

from PyQt5.QtNetwork import QNetworkProxy

# Initialize Qt resources from file resources.py
from qgis_agri.resources import * #@UnusedWildImport

# Import QGIS modules
from qgis.core import ( NULL, 
                        Qgis, 
                        QgsApplication, 
                        QgsProject, 
                        QgsMapLayer, 
                        QgsSettings,
                        QgsFeatureRequest, 
                        QgsDataSourceUri )

from qgis.utils import reloadPlugin
from qgis.gui import QgsGui


# Import plugin modules
from qgis_agri import (tr, 
                       __QGIS_AGRI_NAME__)
                      
from qgis_agri.expressions import * #@UnusedWildImport

from qgis_agri.util.list import listUtil
from qgis_agri.util.object import objUtil
from qgis_agri.util.exception import formatException
from qgis_agri.util.process import ProcessGuard

from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.gui.select_feature_tool import SelectFeatureTool
from qgis_agri.gui.delete_feature_tool import DeleteFeatureTool
from qgis_agri.gui.split_suoli_tool import SplitSuoliTool
from qgis_agri.gui.fill_suoli_tool import FillSuoliTool
from qgis_agri.gui.dissolve_suoli_tool import DissolveSuoliTool
from qgis_agri.gui.difference_suoli_tool import DifferenceSuoliTool

from qgis_agri.plg_processing.provider import Provider
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.service.qgis_agri_networkaccessmanager import QGISAgriNetworkAccessManager

from qgis_agri import agriConfig
from qgis_agri.qgis_agri_exceptions import QGISAgriException
from qgis_agri.qgis_agri_roles import QGISAgriFunctionality
from qgis_agri.qgis_agri_actions import QGISAgriActionBase, QGISAgriActionData
##from qgis_agri.qgis_agri_proxystyle import QGISAgriProxyStyle
from qgis_agri.qgis_agri_history_widget import QgisAgriHistoryWidgetProvider
from qgis_agri.qgis_agri_controller import QGISAgriController
from qgis_agri.qgis_agri_profiles_dlg import QGISAgriProfilesDialog
from qgis_agri.qgis_agri_controlbox import QGISAgriControllerDialog
from qgis_agri.qgis_agri_errorsbox import QGISAgriErrorsDialog 
from qgis_agri.qgis_agri_documents_dlg import QGISAgriDocumentsDialog
from qgis_agri.qgis_agri_pcg_info_dlg import QGISAgriPcgInfoDialog
from qgis_agri.qgis_agri_image_dlg import QGISAgriImageViewer
from qgis_agri.qgis_agri_identify_dlg import ( QGISAgriIdentifyDialogWrapper, 
                                               QGIS_AGRI_ATTR_TEXT_ROLE, 
                                               QGIS_AGRI_ATTR_VALUE_ROLE, 
                                               QGIS_AGRI_ATTR_ASSIGN_ROLE )

from qgis_agri.qgis_agri_search_dlg import QGISAgriFieldExpressionDialog
from qgis_agri.qgis_agri_particelle import QGISAgriParticelle
from qgis_agri.gui.layer_importer import QGISAgriLayerImporter

# 
#-----------------------------------------------------------
class QGISAgri(QObject):
    """QGIS Plugin Implementation."""
   
    # signals
    pluginInitialize = pyqtSignal()
    roleAuthenticated = pyqtSignal(object)
    pluginAuthenticated = pyqtSignal(bool)
    pluginStarted = pyqtSignal(bool)
    pluginCanDownload = pyqtSignal(bool, str)
    pluginCanUpload = pyqtSignal(bool)
    pluginCanReject = pyqtSignal(bool,str)
    currentLayerChanged = pyqtSignal(QgsMapLayer)
    layerWillBeRemoved = pyqtSignal(QgsMapLayer)
    checkEditing = pyqtSignal()
    dbRebase = pyqtSignal(str, bool, bool)
    
    # constants
    PLUGIN_NAME = 'qgis_agri'

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        
        # call parent cunstructor
        QObject.__init__(self)
        
        # Save reference to the QGIS interface
        self.__iface = logger.iface = iface
        
        # plugin version (managed in property)
        self.__version = None
        
        # plugin name
        self.__name = __QGIS_AGRI_NAME__
        
        # initialize plugin directory
        self.__pluginPath = os.path.dirname(__file__)
        
        # initialize locale
        locale = QSettings().value('locale/userLocale')
        if locale:
            locale = locale[0:2]
            locale_path = os.path.join(
                self.pluginPath,
                'i18n',
                'QGISAgri_{}.qm'.format(locale))
    
            if os.path.exists(locale_path):
                self.translator = QTranslator()
                self.translator.load(locale_path)
    
                if qVersion() > '4.3.3':
                    QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.particelle = QGISAgriParticelle( self )
        self.__curr_profile = ''
        self.__actions = []
        self.__toolbars = {}
        self.__menu = None
        self.__optSplitMenu = None
        self.__optFillMenu = None
        self.__splitToolBtn = None
        self.__fillToolBtn = None
        
        # connectorManager
        self.__networkAccessManager = None
        
        # proxy
        self.__networkProxy = None
        
        # authentication
        self.__authenticated = False
        
        # started
        self.__started = False
        
        # freezed
        self.__freezed = False
        
        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        #######################################################self.first_start = None
        self.__pluginIsActive = False
        self.__pluginIsInitialized = False
        self.__pluginIsInitializedMsg = False
        self.__initializationTimer = None
        
        
        #
        self.__url_proxy_exclude_list = []
        
        # plugin processing provider
        self.__provider = None
        
        # Save reference to the QGIS interface
        self.__controller = QGISAgriController(self)
        
        # process guard
        self.__processGuard = ProcessGuard( "QGISAgriProcess", self )
                
        ###self._auth_dlg = None
        self.__profiledlg = None
        self.__controlbox = None
        self.__errorsbox = None
        self.__docsdlg = None
        self.__pcgdlg = None
        self.__photodlg = None
        self.__searchdlg = None
        self.__rastercombo = None
        self.__eleggcombo = None
        self.__eleggcomboAction = None
#         self.__splitCloseAction = None
#         self.__splitAddVxAction = None
#         self.__splitDelVxAction = None
#         self.__splitMoveVxAction = None
        self.__splitMoveAction = None
        self.__fillMoveAction = None
        self.__browseDocAction = None
        self.__browseSuoloPropDocAction = None
        self.__browsePropostiPhotoAction = None
        self.__storicoAction = None
        self.__browseContraddizioni = None
        self.__downloadPcgAction = None
        self.__showPcgAction = None
        self.__downloadCxfAction = None
        self.__downloadAllPartAction = None
        self.__suoliCondPartAction = None
        self.__suoliNoCondPartAction = None
         
        # map tools
        self.__repairSuoloTool = None
        self.__suspendSuoloTool = None
        self.__confirmSuoliPropostiTool = None
        self.__drawPolygonTool = None
        self.__delPolygonTool = None
        self.__identifyTool = None
        self.__splitSuoliTool = None
        self.__fillSuoliTool = None
        self.__dissolveSuoliTool = None
        self.__differenceSuoliTool = None
        self.__scaricaSuoloDocTool = None
        self.__showPcgTool = None
        self.__browsePropostiDocTool = None
        self.__setElegCodeTool = None
        self.__findSuoloTool = None
        self.__browsePropostiPhotoTool = None
        self.__clonePartSuoloTool = None
        self.__suoliCondPartTool = None
        
        # user settings
        self.__auto_hide_controlbox = False
        self.__can_dock_errorsbox = False
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def iface(self):
        """ Returns reference to the QGIS interface (readonly) """
        return self.__iface
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def name(self):
        """ Returns plugin name (readonly) """
        return self.__name
    
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def version(self):
        try:
            if self.__version is None:
                # read version from metadata file
                from configparser import ConfigParser
                config = ConfigParser()
                config.read(os.path.join(os.path.dirname(__file__),'metadata.txt'))
                self.__version = config.get('general', 'version')
                
            # return plugin version
            return self.__version
        
        except Exception as e:
            self.__version = None
            logger.msgbar(
                logger.Level.Critical, 
                f"{tr('Impossibile reperire la versione del plugin')}: {str(e)}", 
                title= self.name)
            return ''
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def menu_tag(self):
        """ Returns plugin menu_tag (readonly) """
        return '&{}'.format( self.__name )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def profile(self):
        """ Returns current plugin profile (readonly) """
        return self.__curr_profile
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def autoHideControlbox(self):
        """ Returns option auto_hide_controlbox (readonly) """
        return self.__auto_hide_controlbox
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pluginPath(self):
        """ Returns plugin path (readonly) """
        return self.__pluginPath
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pluginConfPath(self):
        """Returns plugin config path"""
        return os.path.join( self.__pluginPath, 'conf' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pluginDataPath(self):
        """Returns plugin data path"""
        return os.path.join( self.__pluginPath, 'data' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pluginSqlPath(self):
        """Returns plugin data path"""
        return os.path.join( self.__pluginPath, 'data', 'SQL' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pluginUiPath(self):
        """Returns plugin Ui path"""
        return os.path.join( self.__pluginPath, 'ui' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pluginHistoryPath(self):
        """Returns plugin History path"""
        return os.path.join( self.__pluginPath, 'data', 'storico' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pluginHistoryFileName(self):
        """Returns plugin History file name"""
        
        # check if offline db
        if not self.controller.isOfflineDb:
            return None
        
        # check if selected a foglio
        servRowSelData = self.controlbox.currentFoglioData
        if servRowSelData is None:
            return None
         
        # compose Geopackage full name   
        foglio = servRowSelData.get( agriConfig.services.fogliAziendaOffline.foglioField )
        codiceNazionale = servRowSelData.get( agriConfig.services.fogliAziendaOffline.codNazionaleField )
        return 'history_{0}_{1}.gpkg'.format( foglio, codiceNazionale )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pluginStylePath(self):
        """Returns plugin styles path"""
        return os.path.join( self.__pluginPath, 'styles' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def envPath(self):
        """Returns plugin environment path"""
        return os.path.join( self.__pluginPath, 'env' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def controller(self):
        """ Returns plugin controller (readonly) """
        return self.__controller
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def event_controller(self):
        """ Returns plugin event controller (readonly) """
        return self.__controller.event_controller
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def controlbox(self):
        """ Returns plugin controlbox (readonly) """
        return self.__controlbox
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def errorsbox(self):
        """ Returns plugin errorsbox (readonly) """
        return self.__errorsbox
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def docsdlg(self):
        """ Returns plugin suolo data dialog (readonly) """
        return self.__docsdlg
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def pcgdlg(self):
        """ Returns plugin PCG data dialog (readonly) """
        return self.__pcgdlg
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def photodlg(self):
        """ Returns plugin photo viewer dialog (readonly) """
        return self.__photodlg
    
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def authenticated(self):
        """ Returns authenticated flag (readonly) """
        return self.__authenticated
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def started(self):
        """ Returns started flag (readonly) """
        return self.__started
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def freezed(self):
        """ Returns freezed flag (readonly) """
        return self.__freezed
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def networkAccessManager(self):
        """ Returns networkAccessManager (readonly) """
        return self.__networkAccessManager
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def rasterCombo(self):
        """ Returns raster combo widget (readonly) """
        return self.__rastercombo
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def BrowseDocAction(self):
        """ Returns browse documents action """
        return self.__browseDocAction
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def BrowseSuoloPropDocAction(self):
        """ Returns browse 'suolo proposto' documents action """
        return self.__browseSuoloPropDocAction
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def BrowsePropostiPhotoAction(self):
        """ Returns browse documents action """
        return self.__browsePropostiPhotoAction
    
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def StoricoAction(self):
        """ Returns storico action """
        return self.__storicoAction
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def PcgAction(self):
        """ Returns PCG action """
        return self.__showPcgAction
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def CxfAction(self):
        """ Returns download CXF action """
        return self.__downloadCxfAction
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def AllegatiPartAction(self):
        """ Returns download PARTICELLE ALLEGATO list action """
        return self.__downloadAllPartAction
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def SuoliCondPartAction(self):
        """ Returns Suoli Particelle Conduzione action """
        return self.__suoliCondPartAction
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def SuoliNoCondPartAction(self):
        """ Returns Suoli Particelle No Conduzione action """
        return self.__suoliNoCondPartAction
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setEleggibilitaModel(self):
 
        # set combo model
        self.__eleggcombo.setModel( QGISAgriIdentifyDialogWrapper.getEleggibilitaModel( onlyAssignable=True ) )
        
        # set view model
        lw = self.__eleggcombo.view()
        lw.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
        lw.setWrapping( False )
        
        # set filter model
        filterModel = QSortFilterProxyModel( self.__eleggcombo )
        filterModel.setFilterCaseSensitivity( Qt.CaseInsensitive )
        filterModel.setSourceModel( self.__eleggcombo.model() )
        
        
        # add a completer, which uses the filter model
        completer = QCompleter( filterModel, self.__eleggcombo )
        completer.setCompletionMode( QCompleter.PopupCompletion )
        completer.setCaseSensitivity( Qt.CaseInsensitive )
        completer.setFilterMode( Qt.MatchContains )
        completer.activated.connect( 
            lambda s: ( QtCore.QTimer.singleShot( 0, lambda: ( self.onEleggComboTextChange( s ), 
                                                               self.__eleggcombo.lineEdit().home( True ) )
                      ) ) )
        
        self.__eleggcombo.setCompleter( completer )
        self.__eleggcombo.setCurrentIndex( -1 )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def set_authenticated(self, value, emit_msg=True, only_unauth_msg=True):
        """ Setter method for plugin authentication. """
        
        # check authentication role
        role = self.__controlbox.authenticationRole
        self.roleAuthenticated.emit( role )
        
        self.__authenticated = value
        self.pluginAuthenticated.emit( self.__authenticated )
        
        # if not offline disable download\search service
        if not self.controller.isOfflineDb:
            # disable download action
            self.set_can_download( False, '' )
            
            
        # emit message
        if not emit_msg:
            pass
        
        elif not self.__authenticated:
            # emits message if authentication expired
            logger.msgbar( logger.Level.Critical, 
                           tr( 'Autenticazione scaduta' ), 
                           title=self.name,
                           duration=0 )
        elif not only_unauth_msg:
            # emits message if authorized
            logger.msgbar( logger.Level.Info,
                           tr( 'Autorizzazione con successo' ), 
                           title=self.name,
                           clear=True )
                
    # --------------------------------------
    # 
    # -------------------------------------- 
    def set_started(self, value, emit_msg=True):
        """ Setter method for plugin starting. """
        self.__started = value
        if not self.controller.isOfflineDb:
            self.__started = value and self.__authenticated
        self.pluginStarted.emit( self.__started )
        # emits message if plugin job not started
        if emit_msg and not self.__started:
            logger.msgbar(logger.Level.Warning, 
                          tr( "Caricare un foglio per iniziare l'attività" ) if self.controller.isOfflineDb \
                            else tr( "Scaricare un evento di lavorazione" ),
                          title=self.name)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def set_can_download(self, value, task):
        """ Setter method for plugin downloading. """
        self.pluginCanDownload.emit( value, task )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def set_can_upload(self, value):
        """ Setter method for plugin uploading. """
        self.pluginCanUpload.emit( value )
        if value:
            logger.msgbar(logger.Level.Info, 
                          tr( 'Lavorazione completata: salvare sul server remoto.' ),
                          title=self.name)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def set_can_reject(self, value, task):
        """ Setter method for plugin reject. """
        self.pluginCanReject.emit( value, task )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def emit_check_editing(self):
        """ Setter method for check editing status. """
        self.checkEditing.emit()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def emit_db_rebase(self):
        self.dbRebase.emit( self.controller.database, self.controller.isOfflineDb, self.controller.isOfflineFoglio )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initProcessing(self):
        self.__provider = Provider()
        QgsApplication.processingRegistry().addProvider(self.__provider)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def add_menu(
        self,
        text,
        menu_obj=None,
        position=None):
        """Add new toolbar.
        
        :param text: Menu title.
        :type text: str
        
        :param menu_obj: Parent menu instance.
        :type menu_obj: QMenu (or QMenuBar)
        
        :param position: Sub menu position in parent.
        :type position: int
        
        :returns: The new menu instance that was created or none.
        :rtype: QMenu
        """
        text = text or "???"
        newMenu = None
        if menu_obj:
            # add new menu
            newMenu = QMenu(text, menu_obj)
            lastAction = menu_obj.actions()[position] if position else None
            menu_obj.insertMenu( lastAction, newMenu )
        return newMenu
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def add_toolbar(
        self,
        text=None,
        tooltip=None):
        """Add new toolbar.
        
        :param text: Toolbar title.
        :type text: str
        
        :returns: The new toolbar that was created or defaul plugin toolbar
           if invalid Title.
        :rtype: QToolBar
        """
        
        newToolbar = None
        if not text:
            # invalid title: use defaul plugin toolbar
            newToolbar = self.iface.pluginToolBar()
        elif text in self.__toolbars and not (self.__toolbars[text] is None):
            # toolbar already exists
            newToolbar = self.__toolbars[text]
        else:
            # create new toolbar with the request title
            newToolbar = self.__toolbars[text] = self.iface.addToolBar(text)        
            newToolbar.setToolTip( tooltip or text or '' )
        
        newToolbar.setAttribute( Qt.WA_AlwaysShowToolTips )
        return newToolbar

    # --------------------------------------
    # 
    # -------------------------------------- 
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=False,
        checkable_flag=False,
        add_to_menu=True,
        menu_obj=None,
        add_to_toolbar=True,
        toolbar_obj=None,
        toolbar_fix=False,
        status_tip=None,
        whats_this=None,
        parent=None,
        action_type=QGISAgriActionBase.action_type.STARTING,
        task=None,
        customData=None,
        disallow=False,
        functionality=None,
        text_button=None,
        toolbar_backcolor=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool
        
        :param checkable_flag: A flag indicating if the action should be checked. 
            Defaults to False.
        :type checkable_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool
        
        :param menu_obj: Qgis menu object instance
            where to append new sub menu. Defaults to None (plugin menu).
        :type menu_obj: QMenu
        
        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool
        
        :param toolbar_obj: Qgis toolbar object instance
            where to append action. Defaults to None (plugin toolbar).
        :type toolbar_obj: QToolBar

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
            
        :param toolbar_fix: Flag to adjust toolbar button size. Defaults to False.
        :type toolbar_fix: bool
        
        :param action_type: QGISAgriActionBase enumeration to create a custom plugin action object. 
            Defaults to QGISAgriActionBase.action_type.STARTING.
        :type action_type: enum
        
        :param task: Define a specific task to an action. Defaults to None.
        :type task: str
        
        :param customData: Custom data to join to an action. Defaults to None.
        :type customData: any
        
        :param disallow: Flag to render an action as not allowed for the entire plugin life: needs for beta version
            on untrusted action. Defaults to False.
        :type disallow: bool

        :returns: The action that was created. Note that the action is also
            added to self.__actions list.
        :rtype: QAction
        """
        
        # init
        if disallow:
            text = "{0}<p style='background-color: yellow'>{1}</p>".format( text, tr( 'Funzione non disponibile' ) )
            action_type = QGISAgriActionBase.action_type.NONE
            enabled_flag = False

        # create action object
        icon = QIcon( icon_path )
        action = QGISAgriActionBase.factory( action_type, functionality, customData, icon, text, parent )
        action.setTask( task )
        #action.triggered.connect(callback)
        if callback is not None:
            action.triggered.connect( lambda checked, a=action: callback(checked, a) )
        action.setEnabled( enabled_flag )

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            if toolbar_obj:
                # Adds action to request toolbar
                if text_button is not None:
                    toolButton = QToolButton( toolbar_obj )
                    toolButton.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
                    action.setText( str(text_button) )
                    toolButton.setDefaultAction( action )
                    toolbar_obj.addWidget( toolButton )
                else:
                    toolbar_obj.addAction( action )
                    
                widget = toolbar_obj.widgetForAction( action )
                if widget and toolbar_backcolor:
                    widget.setStyleSheet( f"QToolButton:enabled{{ background: {toolbar_backcolor}; }}" )
                
                # fix toolbar button size
                if toolbar_fix:
                    widget.setFixedSize( toolbar_obj.iconSize() )
                    widget.setIconSize( toolbar_obj.iconSize() )
                    
                # add shadow effect
                tb_cfg = agriConfig.get_value( 'context/toolbarShadow', {} )
                if tb_cfg.get( 'enable', False ):
                    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
                    effect = QGraphicsDropShadowEffect()
                    effect.setBlurRadius(5)
                    effect.setXOffset(3)
                    effect.setYOffset(3)
                    effect.setColor(Qt.gray)
                    widget.setGraphicsEffect(effect)
                
            else:
                # Adds plugin icon to Plugins toolbar
                self.iface.addToolBarIcon( action )
                

        if add_to_menu:
            if menu_obj:
                # Adds action to request menu
                menu_obj.addAction( action )
            else:
                # Adds plugin icon to Plugins toolbar
                self.iface.addPluginToMenu( self.menu_tag, action )
                
        action.setCheckable( checkable_flag )
        
        # connect action to plugin signal
        self.roleAuthenticated.connect( action.onRoleAuthenticated )
        self.pluginAuthenticated.connect( action.onAuthenticated )
        self.pluginStarted.connect( action.onStart )
        self.pluginCanDownload.connect( action.onDownload )
        self.pluginCanUpload.connect( action.onUpload )
        self.pluginCanReject.connect( action.onReject )
        self.checkEditing.connect( action.onChecked )
        self.currentLayerChanged.connect( action.onLayer )
        self.dbRebase.connect( action.onDbRebase )
        
                
        # store action in internal list member
        self.__actions.append(action)

        return action

    # --------------------------------------
    # 
    # -------------------------------------- 
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        
        # check if other instances of QGIS, with this plugin, ae running
        process_guard_cfg = agriConfig.get_value( 'context/enableProcessGuard', True )
        if process_guard_cfg:
            self.__freezed = not self.__processGuard.tryToRun()
        
        
        # set app settings
        s = QgsSettings()
        s.setValue("qgis/enableMacros", "Always")          # enable Python macro always
        s.setValue('Map/identifyAutoFeatureForm','false') # disable Auto Open Form for Identify Results panel
        #s.setValue('Projections/defaultBehavior', '')     # disable CRS selector dialog 
        
        # set qgis CRS transformations
        try:
            # get settings from config
            qgis_prj_cfg = agriConfig.get_value( 'context/qgisProjectionSettings', {} )
            for cfg in qgis_prj_cfg:
                # get setting key name 
                key = cfg.get( 'key' )
                if not key:
                    continue
                
                # complete key name
                key_path = 'Projections/{}'.format( key )
                
                # check if key already exists
                val = s.value( key_path, None )
                if val is not None:
                    continue
                
                # get setting value
                val = cfg.get( 'value' )
                
                # write qgis setting
                s.setValue( key_path, val )
                logger.log( logger.Level.Info, f"{tr('Assegnata impostazione QGIS')}: {key_path}" )
        except:
            pass
        
        # read user settings
        self.readSetting( changeProfile=True )
        
        # set display title
        diplay_title = agriConfig.get_value( 'context/display/plugin_title', default='' )
        if diplay_title:
            self.__name = str(diplay_title)
        
        # initialize plugin processing
        self.initProcessing()
        
        # register layer legend embedded widget
        registry = QgsGui.layerTreeEmbeddedWidgetRegistry()
        self.__storicoWidget = QgisAgriHistoryWidgetProvider()
        registry.addProvider(self.__storicoWidget)
        
        # create 
        self.__profiledlg = QGISAgriProfilesDialog( plugin=self, parent=self.iface.mainWindow() )
        self.__profiledlg.profileChanged.connect( self.onChangeProfile )
        
        # create new instance of networkAccessManager
        self.__networkAccessManager = QGISAgriNetworkAccessManager()
        timeout = agriConfig.get_value( 'agri_service/timeout', None )
        if timeout:
            self.__networkAccessManager.setTimeout( timeout )
        
        # create controller widget
        self.__controlbox = QGISAgriControllerDialog(
            self, 
            parent = QgsApplication.instance().activeWindow(), 
            title = self.name,
            freeze = self.freezed )
        
        # connect to provide cleanup on closing of dockwidget
        self.__controlbox.visibilityChanged.connect( self.onVisibilityChangedControlBox )
        self.__controlbox.closingWidget.connect( self.onCloseControlBox )
        self.__controlbox.serviceRequest.connect( self.onServiceRequest )
        self.__controlbox.serviceOfflineRequest.connect( self.controller.onServiceOfflineRequest )
        self.__controlbox.canDownload.connect( self.set_can_download )
        self.__controlbox.canUpload.connect( self.set_can_upload )
        self.__controlbox.canReject.connect( self.set_can_reject )
        self.__controlbox.downloadListaLav.connect( self.controller.onDownloadEventoLavorazione )
        self.__controlbox.zoomToSuoloByExpression.connect( self.controller.zoomToFeatureByExpression )
        self.__controlbox.zoomToParticellaByExpression.connect( self.controller.zoomToParticellaByExpression )
        self.__controlbox.btnSuoloFinder.clicked.connect( self.onSuoloFind )
        
        
        # show the dockwidget
        # TODO: fix to allow choice of dock location
        self.iface.addDockWidget( Qt.RightDockWidgetArea, self.__controlbox )
        ###self.__controlbox.show()
        
        # create error dialog
        self.__errorsbox = QGISAgriErrorsDialog( plugin=self, parent=QgsApplication.instance().activeWindow() )
        self.__errorsbox.setDockable( self.__can_dock_errorsbox )
        self.__errorsbox.setAllowedAreas( Qt.NoDockWidgetArea )
        self.__errorsbox.close( )
        self.iface.addDockWidget( Qt.BottomDockWidgetArea, self.__errorsbox )
        
        # create suolo info dialog
        self.__docsdlg = QGISAgriDocumentsDialog( parent=self.iface.mainWindow() )
        self.__docsdlg.zoomToFeatureByExpression.connect( self.controller.zoomToFeatureByExpression )
        self.__docsdlg.changeParentFeature.connect( self.downloadFeatureData )
        
        # create PCG info dialog
        self.__pcgdlg = QGISAgriPcgInfoDialog( parent=self.iface.mainWindow() )
        self.__pcgdlg.zoomToSuoloByExpression.connect( self.controller.zoomToFeatureByExpression )
        
        # create photo viewer dialog
        self.__photodlg = QGISAgriImageViewer( 
            parent=self.iface.mainWindow(), 
            flags=Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint,
            enable_zoom_to_feature=True
        )
        self.__photodlg.resize(800, 600)
        self.__photodlg.setWindowTitle( f"{__QGIS_AGRI_NAME__} - {tr('Foto appezzamenti')}" )
        
        self.__photodlg.zoomToPhoto.connect( self.event_controller.zoomToPhotoAppezzamento )
        
        # create search features dialog
        self.__searchdlg = QGISAgriFieldExpressionDialog( parent=QgsApplication.instance().activeWindow() )
        self.__searchdlg.close( )
        self.iface.addDockWidget( Qt.RightDockWidgetArea, self.__searchdlg )
        self.__searchdlg.close( )
        
        # add main menu ###################################
        self.__menu = main_menu = self.add_menu(
            self.menu_tag, 
            self.iface.mainWindow().menuBar(),
            position=-1)
        
        
        # control box toolbar ################
        cbox_tbar = self.__controlbox.cmdToolbar
        
        # add autentication action
        icon_path = ':/plugins/qgis_agri/images/action-auth-invalid-icon.png'
        self.add_action(
            icon_path,
            text=tr( 'Autenticazione' ),
            add_to_menu=False,
            toolbar_obj=cbox_tbar,
            toolbar_fix=True,
            callback=( lambda c, a: self.onClickAuthenticate(c, a, onlyIfNotAuth=False) ),
            parent=self.iface.mainWindow(),
            enabled_flag= not self.freezed,
            action_type=QGISAgriActionBase.action_type.STATUS)
        
        icon_path = ':/plugins/qgis_agri/images/action-search-icon.png'
        self.add_action(
            icon_path,
            text=tr( 'Ricerca lista di lavorazione' ),
            menu_obj=main_menu,
            toolbar_obj=cbox_tbar,
            toolbar_fix=True,
            callback=self.onClickDownload,
            parent=self.iface.mainWindow(),
            task='search',
            action_type=QGISAgriActionBase.action_type.DOWNLOAD)
        
        icon_path = ':/plugins/qgis_agri/images/action-download-icon.png'
        self.add_action(
            icon_path,
            text=tr( 'Scarica foglio da lista di lavorazione' ),
            menu_obj=main_menu,
            toolbar_obj=cbox_tbar,
            toolbar_fix=True,
            callback=self.onClickDownload,
            parent=self.iface.mainWindow(),
            task='download',
            action_type=QGISAgriActionBase.action_type.DOWNLOAD)
        
        icon_path = ':/plugins/qgis_agri/images/action-upload-icon.png'
        self.add_action(
            icon_path,
            text=tr( 'Esporta foglio lavorato' ),
            menu_obj=main_menu,
            toolbar_obj=cbox_tbar,
            toolbar_fix=True,
            callback=self.onClickUpload,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.UPLOAD)
        
        cbox_tbar.addSeparator()
        
        icon_path = ':/plugins/qgis_agri/images/action-reject-foglio-icon.png'
        fgUnlockAction = self.add_action(
            icon_path,
            text=tr( 'Sblocca foglio' ),
            menu_obj=main_menu,
            toolbar_obj=cbox_tbar,
            toolbar_fix=True,
            callback=self.onClickFoglioReject,
            parent=self.iface.mainWindow(),
            task='ElencoFogliAzienda',
            action_type=QGISAgriActionBase.action_type.REJECT)
        fgUnlockAction.setOfflineEnable( QGISAgriActionBase.enable_type.OFFLINEFOGLIO )
        
        icon_path = ':/plugins/qgis_agri/images/action-reject-selected-icon.png'
        selLavUnlockAction = self.add_action(
            icon_path,
            text=tr( 'Sblocca la lavorazione selezionata' ),
            menu_obj=main_menu,
            toolbar_obj=cbox_tbar,
            toolbar_fix=True,
            callback=self.onClickLavReject,
            parent=self.iface.mainWindow(),
            task='ElencoAziende',
            action_type=QGISAgriActionBase.action_type.REJECT,
            functionality= QGISAgriFunctionality( agriConfig.FUNCTIONALITIES.rejectListaLav, defaultEnabled=True ) )
        selLavUnlockAction.setVisibleOffline( False )
        selLavUnlockAction.setOfflineEnable( QGISAgriActionBase.enable_type.INLINE )
        
        icon_path = ':/plugins/qgis_agri/images/action-reject-icon.png'
        lavUnlockAction = self.add_action(
            icon_path,
            text=tr( 'Annulla la lavorazione in corso' ),
            menu_obj=main_menu,
            toolbar_obj=cbox_tbar,
            toolbar_fix=True,
            callback=self.onClickLavReject,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.OFFLINE )
        lavUnlockAction.setVisibleOffline( True )
        
        # add main menu ###################################
        main_menu.addSeparator()
        main_tbar = self.add_toolbar( tr( 'QGIS Agri Servizi' ), tr( 'Barra dei servizi QGIS Agri' ) )
        
        # main panel
        icon_path = ':/plugins/qgis_agri/images/action-show-controls-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Mostra pannello di controllo' ),
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onClickShowControlBox,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            action_type=QGISAgriActionBase.action_type.NONE)
        
        
        ##main_tbar.setStyle( QGISAgriProxyStyle( None ) )
        btn = main_tbar.widgetForAction( action )
        btn.setProperty('iconMinSize',QSize(32,32))
        
        main_tbar.addSeparator()
        
        # main panel
        icon_path = ':/plugins/qgis_agri/images/action-search-suolo-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Ricerca suoli \\ elementi' ),
            menu_obj=main_menu,
            add_to_toolbar=False,
            callback=self.onClickShowSearchBox,
            parent=self.iface.mainWindow(),
            enabled_flag=True,
            action_type=QGISAgriActionBase.action_type.NONE)
        
        # add raster combo label
        label = QLabel()
        label.setStyleSheet( "QLabel { font-weight: bold }" )
        label.setText( tr( "Sfondi: " ) )
        label.setEnabled( False )
        label.setToolTip( tr( "Scelta sfondi" ) )
        self.pluginStarted.connect( label.setEnabled )
        main_tbar.addWidget( label )
        # add combo
        self.__rastercombo = combo = QComboBox()
        combo.setStyleSheet( "QComboBox{ background-color: white; } QAbstractItemView{ background: white } QComboBox:item:selected{ padding-left: 2; color: white; background-color: blue;}" )
        combo.setMinimumWidth( 200 )
        combo.view().setMinimumWidth( 200 )
        combo.setToolTip( label.toolTip() )
        self.pluginAuthenticated.connect( combo.setEnabled )
        ##combo.insertItems(1,["One","Two","Three"])
        main_tbar.addWidget( combo )
        #####combo.lineEdit().setPlaceholderText(translate( 'Seleziona immagine raster' )) NO!
        # load combo data
        wms_cfg = agriConfig.get_value('WMS')
        wms_lays_cfg = wms_cfg.get('layers', {})
        for lay_title, lay_cfg in wms_lays_cfg.items():
            lay_cfg = lay_cfg or {}
            uri_cfg = lay_cfg.get( 'uri', {} )
            url_cfg = uri_cfg.get( 'url', '' ).split('?')[0]
            self.__url_proxy_exclude_list.append( url_cfg )
            combo.addItem( lay_title, lay_cfg )
        combo.setCurrentIndex( -1 )
        combo.setEnabled( False )
        combo.currentIndexChanged.connect( self.onRasterComboChange )
        
        #------------------------------------------------------------------
        main_menu.addSeparator()
        main_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-download-doc-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Info Suoli' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onShowDataSuolo,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            customData=self.controller.get_datasourceuri_suolo_layers('scaricaDatiSuolo'),
            disallow=False)
        
        action.setCheckAuthenticated( True )
        action.setStopOnDiffLayer( True )
        
        
        # -- PARTICELLE
        self.particelle.initGui( main_menu, main_tbar, 'scaricaDatiParticella', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-browse-doc-icon.png'
        self.__browseDocAction = self.add_action(
            icon_path,
            text=tr( 'Accedi alla documentazione del foglio' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onBrowseDocumentazione,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.STARTING,
            disallow=False)
        self.__browseDocAction.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-browse-suolo-doc-icon.png'
        self.__browseSuoloPropDocAction = self.add_action(
            icon_path,
            text=tr( 'Accedi alla documentazione del suolo proposto' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onBrowseDocumentazioneSuoloProposto,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            customData=self.controller.get_datasourceuri_suolo_layers('browsedocproposti'),
            disallow=False)
        self.__browseSuoloPropDocAction.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-browse-contradd-icon.png'
        self.__browseContraddizioni = self.add_action(
            icon_path,
            text=tr( 'Accedi alla gestione dei contraddittori e sopralluoghi' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onBrowseContraddizioni,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.STARTING,
            disallow=False )
        self.__browseContraddizioni.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-show-photo-icon.png'
        self.__browsePropostiPhotoAction = self.add_action(
            icon_path,
            text=tr( 'Visualizza le foto appezzamenti' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onDownloadAppezzamentiPhoto,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            customData=self.controller.get_datasourceuri_suolo_layers('browsephotoproposti|sel'),
            disallow=False)
        self.__browsePropostiPhotoAction.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        main_menu.addSeparator()
        main_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-download-history-icon.png'
        self.__storicoAction = self.add_action(
            icon_path,
            text=tr( 'Scarica lo storico dei suoli' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onDownloadHistory,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.STARTING,
            disallow=False)
        self.__storicoAction.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-download-last-history-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Scarica lo storico dei suoli (aggiornato)' ),
            menu_obj=main_menu,
            add_to_toolbar=False,
            callback=self.onDownloadLastHistory,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.STARTING,
            disallow=False)
        action.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        main_menu.addSeparator()
        main_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-pcg-validation-icon.png'
        self.__downloadPcgAction = self.add_action(
            icon_path,
            text=tr( 'Scarica le validazioni del Piano Colturale Grafico' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onDownloadValidationsPCG,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.STARTING,
            disallow=False)
        self.__downloadPcgAction.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-pcg-info-icon.png'
        self.__showPcgAction = self.add_action(
            icon_path,
            text=tr( 'Visualizza le informazioni del Piano Colturale Grafico' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onShowDatiPCG,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            customData=[],
            disallow=False)
        self.__showPcgAction.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        main_menu.addSeparator()
        main_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-download-cxf-icon.png'
        self.__downloadCxfAction = self.add_action(
            icon_path,
            text=tr( 'Scarica CXF' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onDownloadCXF,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.STARTING,
            #action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            #customData=self.controller.get_datasourceuri_suolo_layers('downloadCXF'),
            toolbar_backcolor=self.particelle.guiColor )
        self.__downloadCxfAction.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-download-raster-icon.png'
        self.__downloadAllPartAction = self.add_action(
            icon_path,
            text=tr( 'Mostra allegati PARTICELLE' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onDownloadAllegatiParticelle,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.STARTING,
            toolbar_backcolor=self.particelle.guiColor )
        self.__downloadAllPartAction.setCheckAuthenticated( True )
        
        #------------------------------------------------------------------
        main_menu.addSeparator()
        main_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-import-layer-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Importa livelli da progetto esterno' ),
            checkable_flag=True,
            menu_obj=main_menu,
            toolbar_obj=main_tbar,
            callback=self.onImportLayersFromProjct,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.STARTING )
        action.setLayerIndipendent( True )
        
        ###############################################################################################################
        # add edit toolbar
        edit_menu = self.add_menu( tr( 'Editazione' ), main_menu )
        edit_tbar = self.add_toolbar( tr( 'QGIS Agri Editazione' ), tr( 'Barra degli strumenti di editazione QGIS Agri' ) )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-start-edit-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Inizia editazione SUOLI' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onStartEditing,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.EDITING,
            customData=self.controller.get_datasourceuri_suolo_layers('editing'))
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'editingParticelle', action )
        
        #------------------------------------------------------------------
        edit_menu.addSeparator()
        edit_tbar.addSeparator()
        
        #------------------------------------------------------------------
        layUris = self.controller.get_datasourceuri_suolo_layers('fillsuoli')    
        icon_path = ':/plugins/qgis_agri/images/action-fill-hole-icon.png'
        fillAction = self.add_action(
            icon_path,
            text=tr( 'Nuovo poligono' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onFillSuoli,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=layUris,
            disallow=False)
        
        # add sub action menu
        self.__fillToolBtn = edit_tbar.widgetForAction( fillAction )
        if self.__fillToolBtn is not None:
            self.__optFillMenu = QMenu( self.__fillToolBtn )
            self.__optFillMenu.addAction( fillAction )
            
            icon_path = ':/plugins/qgis_agri/images/action-split-move-vertex-icon.png'
            self.__fillMoveAction = self.add_action(
                icon_path,
                text=tr( 'Edita spezzata (tasto SHIFT)' ),
                menu_obj= self.__optFillMenu,
                add_to_toolbar=False,
                checkable_flag=True,
                callback=self.onClickMoveFillSuoli,
                parent=self.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=layUris )
            self.__fillMoveAction.forceDisable( True )
            
            self.__fillToolBtn.setPopupMode( QToolButton.MenuButtonPopup )
            self.__fillToolBtn.triggered.connect( self.__fillToolBtn.setDefaultAction )
            self.__fillToolBtn.setMenu( self.__optFillMenu )
            self.__fillToolBtn.setDefaultAction( fillAction )
            
            def setFillCheckedActions(action):
                for a in self.__optFillMenu.actions():
                    if a != action and a!= fillAction:
                        a.setChecked( False )
            
            self.__optFillMenu.triggered.connect( setFillCheckedActions )
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'fillParticelle', fillAction )
        
        #------------------------------------------------------------------
        layUris = self.controller.get_datasourceuri_suolo_layers('splitsuoli')
        icon_path = ':/plugins/qgis_agri/images/action-split-suoli-icon.png'
        splitAction = self.add_action(
            icon_path,
            text=tr( 'Taglia suoli' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onSplitSuoli,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=layUris,
            disallow=False)
        
        # add sub action menu
        self.__splitToolBtn = edit_tbar.widgetForAction( splitAction )
        if self.__splitToolBtn is not None:
            self.__optSplitMenu = QMenu( self.__splitToolBtn )
            self.__optSplitMenu.addAction( splitAction )
            
            #icon_path = ':/plugins/qgis_agri/images/action-split-move-line-icon.png'
            icon_path = ':/plugins/qgis_agri/images/action-split-move-vertex-icon.png'
            self.__splitMoveAction = self.add_action(
                icon_path,
                text=tr( 'Edita spezzata (tasto SHIFT)' ),
                menu_obj= self.__optSplitMenu,
                add_to_toolbar=False,
                checkable_flag=True,
                callback=self.onClickMoveSplitSuoli,
                parent=self.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=layUris )
            self.__splitMoveAction.forceDisable( True )
            
            self.__splitToolBtn.setPopupMode( QToolButton.MenuButtonPopup )
            self.__splitToolBtn.triggered.connect( self.__splitToolBtn.setDefaultAction )
            self.__splitToolBtn.setMenu( self.__optSplitMenu )
            self.__splitToolBtn.setDefaultAction( splitAction )
            
            def setSplitCheckedActions(action):
                for a in self.__optSplitMenu.actions():
                    if a != action and a!= splitAction:
                        a.setChecked( False )
            
            self.__optSplitMenu.triggered.connect( setSplitCheckedActions )
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'splitParticelle', splitAction )    
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-del-polygon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Rimuovi poligono' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickDelPolygon,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('delpolygon'))
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'delParticelle', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-vertex-tool-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Modifica vertici' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickVertexTool,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('vertextool'))
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'vertexParticelle', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-add-hole-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Aggiungi buco poligono' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickAddPolygonHole,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('addpolygonhole'),
            disallow=False)
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'addHoleParticelle', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-delete-hole-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Rimuovi buco poligono' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickDelPolygonHole,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('delpolygonhole'),
            disallow=False)
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'delHoleParticelle', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-dissolve-suoli-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Unisci suoli' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onDissolveSuoli,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('dissolvesuoli'),
            disallow=False)
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'dissolveParticelle', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-difference-suoli-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Ritaglia suolo per differenza' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onDifferenceSuoli,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('diffsuoli'),
            disallow=False)
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'diffParticelle', action )
        
        #------------------------------------------------------------------
        edit_menu.addSeparator()
        edit_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-copy-particella-suolo-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Clona PARTICELLA Suolo' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onCloneParticellaSuolo,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('cloneParticellaSuolo') )
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'cloneParticellaCxf', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-transform-suolo-cond-icon.png'
        self.__suoliCondPartAction = self.add_action(
            icon_path,
            text=tr( 'Taglia suoli non in conduzione su PARTICELLA in conduzione' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onSuoliCondParticella,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('suoliCondParticella|action') )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-transform-suolo-nocond-icon.png'
        self.__suoliNoCondPartAction = self.add_action(
            icon_path,
            text=tr( 'Converti i suoli non in conduzione su PARTICELLA non in conduzione' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onSuoliNoCondParticella,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('suoliCondParticella|action') )
        
        #------------------------------------------------------------------
        edit_menu.addSeparator()
        edit_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-confirm-suoli-proposti.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Conferma suolo proposto' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickConfirmSuoliProposti,
            parent=self.iface.mainWindow(),
            #action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            action_type=QGISAgriActionBase.action_type.LAYER2,
            customData=self.controller.get_datasourceuri_suolo_layers('confirmproposti|action'),
            disallow=False)
        action.setEditLayers( self.controller.get_datasourceuri_suolo_layers('confirmproposti') )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-confirm-suoli-lav.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Conferma tutti i suoli in lavorazione' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickConfirmAllSuoliLavorazione,
            parent=self.iface.mainWindow(),
            #action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('confirmallsuoli'),
            disallow=False)
       
        
        #------------------------------------------------------------------
        edit_menu.addSeparator()
        edit_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-suolo-done-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Ripara suolo' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickRepairSuolo,
            parent=self.iface.mainWindow(),
            #action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('repairsuolo'))
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'repairParticelle', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-multi-to-single-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Converte le geometrie multi parti in singole parti' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickRepairAllSuoli,
            parent=self.iface.mainWindow(),
            #action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('repair-all-suoli'))
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'repairAllParticelle', action )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-identify-icon.png'
        action = self.add_action(
            icon_path,
            text=tr( 'Modifica attributi suolo' ),
            checkable_flag=True,
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickIdentify,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE, #STARTING,
            customData=self.controller.get_datasourceuri_suolo_layers('identitysuolo'))
        
        # -- PARTICELLE
        self.particelle.initGui( edit_menu, edit_tbar, 'identityParticella', action )
        
        #------------------------------------------------------------------
        edit_menu.addSeparator()
        edit_tbar.addSeparator()
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-label-icon.png'
        self.add_action(
            icon_path,
            text=tr( 'Mostra etichette' ),
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickShowLabels,
            parent=self.iface.mainWindow())
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-area-label-icon.png'
        self.add_action(
            icon_path,
            text=tr( 'Mostra etichette area' ),
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickShowAreaLabels,
            parent=self.iface.mainWindow())
        
        #------------------------------------------------------------------
        edit_menu.addSeparator()
        edit_tbar.addSeparator()
        
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-check-topology.png'
        self.add_action(
            icon_path,
            text=tr( 'Verifica geometrica e topologica dei suoli' ),
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickTopoVerify,
            #####action_type=QGISAgriActionBase.action_type.NONE,
            parent=self.iface.mainWindow(),
            text_button='Verifica geometrie e topologia')
        
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/error-list-icon.png'
        self.add_action(
            icon_path,
            text=tr( 'Mostra pannello degli errori' ),
            menu_obj=edit_menu,
            toolbar_obj=edit_tbar,
            callback=self.onClickShowErrorsBox,
            parent=self.iface.mainWindow(),
            disallow=False)
        
        #------------------------------------------------------------------
        edit_menu.addSeparator()
        edit_tbar.addSeparator()
       
        # add combobox to choose new 'Eleggibilità' code
        self.__eleggcombo = combo = QComboBox()
        combo.setStyleSheet( "QComboBox{ background-color: white; } QAbstractItemView{ background: white } QComboBox:item:selected{ color: white; background-color: blue;}" )
        combo.setMinimumWidth( 400 )
        combo.view().setMinimumWidth( 400 )
        combo.setMaximumWidth( 400 )
        combo.view().setMaximumWidth( 400 )
        combo.setToolTip( tr( 'Codice Eleggibilità' ) )
        combo.setEditable( True )
        combo.setInsertPolicy( QComboBox.NoInsert )
        combo.lineEdit().setPlaceholderText(  tr( 'Immetti codice di Eleggibilità' )  )
        combo.view().setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
        combo.view().setWrapping( False )
        
        combo.focusInEvent = objUtil.wrapFunction( combo.focusInEvent, 
                                                   postFunc= lambda e,w=combo: QtCore.QTimer.singleShot( 0, lambda: ( w.lineEdit().end( False ), w.lineEdit().home( True ) ) ) )
       
        
        combo.activated.connect( lambda i: ( self.sender().lineEdit().home( True ) ) )
        combo.currentIndexChanged.connect( self.onEleggComboChange )
        combo.currentTextChanged.connect( self.onEleggComboTextChange )
        combo.lineEdit().editingFinished.connect( self.onEleggComboEditingFinished )
        edit_tbar.addWidget( combo )
        
        #------------------------------------------------------------------
        # add buttun to assign new 'Eleggibilità' code
        icon_path = ':/plugins/qgis_agri/images/action-set-eleggibilita-icon.png'
        actionHiddenElegg = self.add_action(
            icon_path,
            text=tr( 'Assegna codice Eleggibilità' ),
            checkable_flag=True,
            add_to_menu=False,
            toolbar_obj=edit_tbar,
            callback=None,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('seteleggibilita'))
        actionHiddenElegg.setVisible( False )
        
        actionHiddenElegg.actionIsEnabled.connect( self.__eleggcombo.setEnabled )
#         actionHiddenElegg.actionIsEnabled.connect( labelElegg.setEnabled )
        
        #------------------------------------------------------------------
        icon_path = ':/plugins/qgis_agri/images/action-set-eleggibilita-icon.png'
        self.__eleggcomboAction = self.add_action(
            icon_path,
            text=tr( 'Assegna codice Eleggibilità' ),
            checkable_flag=True,
            add_to_menu=False,
            toolbar_obj=edit_tbar,
            callback=self.onClickSetElegCode,
            parent=self.iface.mainWindow(),
            action_type=QGISAgriActionBase.action_type.LAYER,
            customData=self.controller.get_datasourceuri_suolo_layers('seteleggibilita'))
        self.__eleggcomboAction.forceDisable( True )
        
        # add options menu ##########################################################################################
        main_menu.addSeparator()
        opts_menu = self.add_menu( tr( 'Opzioni' ), main_menu )
        
        icon_settings_path = ':/plugins/qgis_agri/images/action-settings-icon.png'
        
        action = opts_menu.addAction( tr( "Rendi agganciabile la finestra di errori" ) )
        action.setIcon( QIcon(icon_settings_path) )
        action.setCheckable( True )
        action.setChecked( self.__can_dock_errorsbox )
        action.triggered.connect( lambda checked, a=action, k='can_dock_errorsbox': self.onChangeUserOption(checked, a, k) )
        
        action = opts_menu.addAction( tr( "Nascondi pannello di controllo in editazione" ) )
        action.setIcon( QIcon(icon_settings_path) )
        action.setCheckable( True )
        action.setChecked( self.__auto_hide_controlbox )
        action.triggered.connect( lambda checked, a=action, k='auto_hide_controlbox': self.onChangeUserOption(checked, a, k) )
        
        opts_menu.addSeparator()
        
        icon_experimental_path = ':/plugins/qgis_agri/images/experimental-icon.png'
        action = opts_menu.addAction( tr( "Installa browser esterno di autenticazione" ) )
        action.setIcon( QIcon(icon_experimental_path) )
        action.triggered.connect( lambda checked, a=action: self.onInstallExtBrowser(checked, a) )
        if os.name != 'nt':
            action.setDisabled(True)
        
        opts_menu.addSeparator()
        
        action = opts_menu.addAction( tr( "Cambia profilo plugin" ) )
        action.setIcon( QIcon(icon_settings_path) )
        action.setCheckable( True )
        ###action.setChecked( self.__auto_hide_controlbox )
        action.triggered.connect( lambda checked, a=action: self.onChooseProfile(checked, a) )
        
        ###############################################################################################################
        # connect project signals
        
        self.pluginAuthenticated.connect( self.__controlbox.setAuthEnabled )
        self.pluginStarted.connect( self.__controlbox.setDownloaded )
        self.pluginInitialize.connect( self.onProjectClearedInit, Qt.QueuedConnection )
        
        ####QgsProject.instance().cleared.connect( self.onProjectCleared )# or self.iface.newProjectCreated
        QgsProject.instance().layerWillBeRemoved.connect( self.onLayerWillBeRemoved )
        QgsProject.instance().layerWasAdded.connect( self.onlayerWasAdded )
        
        #
        self.iface.currentLayerChanged.connect( self.onCurrentLayerChanged )
        self.iface.newProjectCreated.connect( self.onProjectCleared )
        self.iface.projectRead.connect( self.onProjectCleared )
        
        self.__controlbox.authenticated.connect( self.set_authenticated )
        
        # emit message for plugin status
        self.set_started(self.started, emit_msg=False)
        self.set_authenticated( False, emit_msg=False )
        self.__pluginIsActive = True

        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        
        #
        self.__processGuard.release()
        
        #
        self.__photodlg.zoomToPhoto.disconnect( self.event_controller.zoomToPhotoAppezzamento )
        
        #
        self.__docsdlg.zoomToFeatureByExpression.disconnect( self.controller.zoomToFeatureByExpression )
        self.__docsdlg.changeParentFeature.disconnect( self.downloadFeatureData )
        
        #
        #
        self.__pcgdlg.zoomToSuoloByExpression.disconnect( self.controller.zoomToFeatureByExpression )
        
        #
        self.__profiledlg.profileChanged.disconnect( self.onChangeProfile )
        
        # disconnect signal (must be disconnected automatically on object destruction)
        self.__controlbox.btnSuoloFinder.clicked.disconnect( self.onSuoloFind )
        self.__controlbox.zoomToSuoloByExpression.disconnect( self.controller.zoomToFeatureByExpression )
        self.__controlbox.zoomToParticellaByExpression.disconnect( self.controller.zoomToParticellaByExpression )
        self.__controlbox.downloadListaLav.disconnect( self.controller.onDownloadEventoLavorazione )
        self.__controlbox.visibilityChanged.disconnect( self.onVisibilityChangedControlBox )
        self.__controlbox.closingWidget.disconnect( self.onCloseControlBox )
        self.__controlbox.serviceRequest.disconnect( self.onServiceRequest )
        self.__controlbox.serviceOfflineRequest.disconnect( self.controller.onServiceOfflineRequest )
        self.__controlbox.canDownload.disconnect( self.set_can_download )
        self.__controlbox.canUpload.disconnect( self.set_can_upload )
        self.__controlbox.canReject.disconnect( self.set_can_reject )
        self.__controlbox.authenticated.disconnect( self.set_authenticated )
        
        ####QgsProject.instance().cleared.disconnect( self.onProjectCleared )
        QgsProject.instance().layerWasAdded.disconnect( self.onlayerWasAdded )
        QgsProject.instance().layerWillBeRemoved.disconnect( self.onLayerWillBeRemoved )
        ###self._auth_dlg.authenticated.disconnect(self.onAuthenticate)
        
        self.pluginStarted.disconnect( self.__controlbox.setDownloaded )
        self.pluginAuthenticated.disconnect( self.__controlbox.setAuthEnabled )
        self.pluginInitialize.disconnect( self.onProjectClearedInit )
        
        self.iface.currentLayerChanged.disconnect( self.onCurrentLayerChanged )
        self.iface.newProjectCreated.disconnect( self.onProjectCleared )
        self.iface.projectRead.disconnect( self.onProjectCleared )
        
        # disconnect suoli layers signals
        self.__controller.disconnectSuoliEditing()
        
        # disconnect particelle layers signals
        self.particelle.disconnectParticelleEditing()
        
        # unregister plugin processing provider
        QgsApplication.processingRegistry().removeProvider(self.__provider)
        
        # reset canvas window style
        self.__controller.styleCanvasWidget( reset=True )
        logger.clear_msgbar()
        
        # remove search dialog
        self.__searchdlg.close()
        self.iface.removeDockWidget( self.__searchdlg )
        self.__searchdlg.deleteLater()
        self.__searchdlg = None
        
        # remove errors dialog
        self.__errorsbox.close()
        self.iface.removeDockWidget( self.__errorsbox )
        self.__errorsbox.deleteLater()
        self.__errorsbox = None
        
        # remove dialog
        ###self._auth_dlg.close()
        ###del self._auth_dlg
        del self.__controller
        self.__controller = None
        
        self.__controlbox.close()
        self.__controlbox.release()
        self.iface.removeDockWidget( self.__controlbox )
        self.__controlbox.deleteLater()
        self.__controlbox = None
        
        self.__storicoWidget = None
        
        del self.__networkAccessManager
        self.__networkAccessManager = None
        ###self._auth_dlg = None
        self.__rastercombo = None
        self.__eleggcombo = None
        self.__eleggcomboAction = None
        
        # remove actions
        for action in self.__actions:
            self.iface.removePluginMenu( self.menu_tag, action )
            self.iface.removeToolBarIcon( action )
            
        # remove plugin toolbars
        del self.__toolbars
        self.__toolbars = {}
        
        
        # remove plugin menu
        if self.__menu:
            self.__menu.deleteLater()
        self.__menu = None
        
        # reset proxy
        QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.DefaultProxy))
        
        # unregister layer legend embedded widget
        registry = QgsGui.layerTreeEmbeddedWidgetRegistry()
        QgisAgriHistoryWidgetProvider.removeWidgetInstances()
        registry.removeProvider(QgisAgriHistoryWidgetProvider.id())
        self.__storicoWidget = None
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def get_cmd_layers(self, cmdName, err_if_empty=True):
        """Get command layers"""
        vlayers = self.controller.get_suolo_vector_layers( cmdName )
        if not vlayers:
            if err_if_empty:
                logger.msgbox( logger.Level.Critical, tr( 'Nessun layer presente per il comando selezionato' ), title=tr('ERRORE') )
                return None
            else:
                return []
        return vlayers
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def checkable_action(self, checked, action, checkable=False):
        """Check action"""
        if checked:
            pass
        elif checkable:
            pass
        else:
            # disable uncheck action
            action.setChecked( True )
            return False
        
        return True  
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def checkable_tool(self, checked, action, tool, checkable=False, msg=None):
        """Check map tool"""
        
        # get active map tool
        mapTool = self.iface.mapCanvas().mapTool() 
        if mapTool is None:
            pass
        elif mapTool != tool:
            pass
        elif checked:
            pass
        elif checkable:
            # unset tool
            self.iface.mapCanvas().unsetMapTool( tool )
            self.iface.actionPan().trigger()
            return False
        else:
            # disable uncheck action
            action.setChecked( True )
            if msg is not None:
                logger.msgbar( logger.Level.Info, msg, title=self.name, clear=True )
            return False
        
        return True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def run_tool(self, checked, action, tool, msg=None, cmdAction=None, snapping=False, chkLayers=True):
        """Run a map tool"""
        
        # init
        if action is None:
            msg = msg or ''
            action_data = None
        else:
            msg = msg or action.text()
            action_data = action.data()
            
        # check action data
        if isinstance(action_data, QGISAgriActionData):
            if action_data.suppress_msg:
                msg = None
            action.setData(None)
        
        # check layer
        layer = self.iface.layerTreeView().currentLayer()
        if chkLayers and layer is None:
            return
        
        # check if disabled
        if not checked:
            self.iface.mapCanvas().unsetMapTool( tool )
            self.iface.actionPan().trigger()
            return False
        
        canvas = self.iface.mapCanvas()
        oldSnappingConfig = self.controller.getProjectSnapping()
        
        def onMapToolSet(new_tool, old_tool):
            if action is not None:
                try:
                    action.setChecked( new_tool.action() == action )
                except:
                    action.setChecked( False )
            canvas.mapToolSet.disconnect( onMapToolSet )
            self.controller.setSnappingConfig( oldSnappingConfig )
            logger.remove_progressbar()
            
        # active snapping
        if snapping:
            self.controller.setSnappingConfig()
        
        # start activity   
        if cmdAction is not None:
            # activate a base command action, if passed
            cmdAction.trigger()
        
        elif tool is None:
            pass
        
        else:    
            # start tool to select a feature
            tool.setAction( action )
            canvas.setMapTool( tool )
            
        
        canvas.mapToolSet.connect( onMapToolSet )
        if msg is not None:
            logger.msgbar( logger.Level.Info, msg, title=self.name )
            
        return True
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def showControlBox(self, hide=False, currentTabName=None):
        """ Show/Hide pluging control box. """
        if not self.controller.isEditingStoppedSlotEnabled:
            return 
        
        controlBox = self.__controlbox
        if hide:
#             from PyQt5.QtWidgets import QDockWidget
#             wnd = controlBox.window()
#             if wnd == self.iface.mainWindow():
#                 area = wnd.dockWidgetArea( controlBox )
#                 for dock in wnd.findChildren( QDockWidget ):
#                     if dock == controlBox:
#                         pass
#                     elif not dock.isVisible():
#                         pass
#                     elif area == wnd.dockWidgetArea( dock ):
#                         return
            # hide control box
            controlBox.hide()
            return
        
        else:
            
            if controlBox.isVisible():
                return
            
            elif Qgis.QGIS_VERSION_INT >= 31300: # Use native addTabifiedDockWidget
                # add a temporary dock widget
                dock = QDockWidget()
                dock.setFloating( controlBox.isFloating() )
                dock.setAllowedAreas( Qt.AllDockWidgetAreas )
                self.iface.addTabifiedDockWidget( Qt.RightDockWidgetArea, dock )
                
                # need to re add dock widget for bug in Qt
                controlBox.setFloating( controlBox.isFloating() )
                controlBox.setAllowedAreas( Qt.AllDockWidgetAreas )
                self.iface.addDockWidget( Qt.RightDockWidgetArea, controlBox )
                
                # Use native addTabifiedDockWidget
                self.iface.addTabifiedDockWidget( Qt.RightDockWidgetArea, controlBox, [dock.accessibleName()], raiseTab=True )
                
                # remove temporary dock widget
                self.iface.removeDockWidget( dock )
                
            else:
                # need to re add dock widget for bug in Qt
                controlBox.setFloating( controlBox.isFloating() )
                controlBox.setAllowedAreas( Qt.AllDockWidgetAreas )
                self.iface.addDockWidget( Qt.RightDockWidgetArea, controlBox )
                
            # show control box
            controlBox.show()
            controlBox.raise_()
            
            # set current tab
            if currentTabName is not None:
                controlBox.setCurrentTab( currentTabName )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def readSetting(self, changeProfile=False):
        """ Read plugin user settings """
        s = QgsSettings()
        # 
        if changeProfile:
            value = s.value( "{0}/plg_profile".format( self.PLUGIN_NAME ), False )
            self.changeProfile(value)
        # 
        value = s.value( "{0}/auto_hide_controlbox".format( self.PLUGIN_NAME ), False )
        self.__auto_hide_controlbox = str(value).lower() in ("yes", "true", "t", "1")
        #
        value = s.value( "{0}/can_dock_errorsbox".format( self.PLUGIN_NAME ), False )
        self.__can_dock_errorsbox = str(value).lower() in ("yes", "true", "t", "1")
        if self.errorsbox is not None:
            self.errorsbox.setDockable( str(value).lower() in ("yes", "true", "t", "1") )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onChooseProfile(self, checked, action):
        """ Change plugin profile """ 
        # enable action
        action.setChecked( False )
        
        # show profiles dialog
        self.__profiledlg.show()
     
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onChangeProfile(self, profile_name: str):
        """ Change plugin profile slot """ 
        # write setting
        s = QgsSettings()
        s.setValue( "{0}/{1}".format( self.PLUGIN_NAME, 'plg_profile' ), profile_name )
        
        # reload current plugin
        reloadPlugin( self.PLUGIN_NAME )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def changeProfile(self, profile_name: str):
        """ Change plugin profile """ 
        # read plugin profiles config
        cfgObj = agriConfig.loadOtherConfig( agriConfig.CFG_PROFILE_FILE_NAME )
        cfgEntry = cfgObj.get_value( 'plugin', {} )
        cfgProfiles = cfgEntry.get( 'profiles', {} )
        if len(cfgProfiles) < 1:
            logger.msgbox( logger.Level.Critical, 
                           tr('Nessun profilo definito nel file di configurazione'), 
                           title=tr('ERRORE') )
            return
        
        # read default profile
        self.__curr_profile = cfgEntry.get( 'default', '' )
        if profile_name:
            self.__curr_profile = profile_name
            
        elif self.__curr_profile not in cfgProfiles:
            self.__curr_profile = list(cfgProfiles.keys())[0]
        
        # check if valid profile    
        if self.__curr_profile not in cfgProfiles:
            logger.log( logger.Level.Critical, 
                           "{}: '{}'".format( 
                               tr('Profilo non presente nel file di configurazione'), 
                               self.__curr_profile) )
            self.__curr_profile = list(cfgProfiles.keys())[0]
            
        # load config for profile
        cfgCurrProfile = cfgProfiles.get( self.__curr_profile, {} )
        cfgFile = cfgCurrProfile.get( 'config', '' )
        if not cfgFile:
            logger.msgbox( logger.Level.Critical, 
                           "{}: '{}'".format( 
                               tr('Nessun file di configurazione impostato per il profilo'), 
                               self.__curr_profile),
                           title=tr('ERRORE') )
            return
          
        agriConfig.reloadConfig( cfgFile )
        
        ##logger.log( logger.Level.Info, "Impostato profilo: {0}".format( self.__curr_profile ) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onChangeUserOption(self, checked, action, key):
        """"""
        # write setting
        s = QgsSettings()
        s.setValue( "{0}/{1}".format( self.PLUGIN_NAME, key ), checked )
        # read user settings
        self.readSetting()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onProjectClearedInit(self):
        self.onProjectCleared()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onProjectCleared(self):
        """Disables started status on new project"""
        
        # init
        controller = self.controller
        logger.clear_msgbar()
        isActive = self.__controlbox.isVisible()
        self.__pluginIsInitialized = isActive      
        
        # emit message for current profile
        if isActive:
            logger.msgbar( logger.Level.Info,
                           "{}: {}".format( tr( 'Impostato profilo' ), self.__curr_profile ),
                           title=self.name,
                           duration=0 )
        
        # 
        self.set_started( False, emit_msg=isActive )
        if not self.authenticated:
            self.set_authenticated( False, emit_msg=isActive )
            
        # initialize controller
        controller.init( None, initSfondo=isActive, serviceSavedData=controller.lastServiceData )
        if not isActive and not self.__pluginIsInitializedMsg and controller.isOfflineDb:
            #self.__controlbox.show()
            self.__pluginIsInitializedMsg = True
            logger.msgbar( logger.Level.Warning, 
                           tr( "Presente un evento di lavorazione in db offline" ),
                           title=self.name )
            
        if self.freezed and isActive:
            logger.msgbox(
                logger.Level.Critical, 
                tr( 
                    "Presente una o più istanze di QGIS con il plugin 'QGIS Agri' attivo."
                    "\n"
                    "Le funzionalità base del plugin sono state disattivate, sulla presente istanza,"
                    "per evitare conflitti di lavorazione." ), 
                title=tr('ERRORE') )
            
            logger.msgbar(
                logger.Level.Critical,
                tr( "Presente un'altra istanza di QGIS Agri: funzionalità del plugin disabilitate" ), 
                title = self.name,
                duration = 0, 
                clear = True )
        
        # resume message bar 
        logger.suspend_msgbar( False )    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onCurrentLayerChanged(self, layer):
        """Disable/Enable edit tool"""
        self.currentLayerChanged.emit(layer)
        self.adjustMapTool()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onlayerWasAdded(self, layer):
        """Layer added slot"""
        # connect signal commit changes
        self.controller.connectSuoliEditing( layer )
        self.particelle.connectParticelleEditing( layer )
        self.adjustMapTool()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onLayerWillBeRemoved(self, layer):
        """Disable/Enable edit tool"""
        self.layerWillBeRemoved.emit( QgsProject.instance().mapLayer( layer ) )
        self.adjustMapTool()
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def adjustMapTool(self):
        # update PCG plugin action
        vlayers, lst_lay_uri = self.event_controller.get_pcg_layers()
        self.PcgAction.changeRefLayers( lst_lay_uri )
        # update PCG tool
        tool = self.__showPcgTool
        if tool is not None:
            currLayer = self.iface.activeLayer()
            if currLayer in vlayers:
                tool.initialize( [ currLayer ], tool.onSelectFeature )
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onVisibilityChangedControlBox(self, visible):
        """Control box visibility changed slot"""
        if visible and not self.__pluginIsInitialized:
            
            def onTimer():
                if self.__initializationTimer is None:
                    return
                self.__initializationTimer.cancel()
                self.__initializationTimer = None
                if not self.__pluginIsInitialized:
                    self.pluginInitialize.emit()
                    
            from threading import Timer
            self.__initializationTimer = Timer( 1.0, onTimer )
            self.__initializationTimer.start()
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onCloseControlBox(self):
        """Cleanup necessary items here when plugin QGisAgri is closed"""
        
        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onServiceRequest(self, serviceName, dataRow, genData, agriControlBox, followLinkedService, skipIfNoAuth=False):
        """Control service request from control box"""
        if not self.authenticated and skipIfNoAuth:
            return
        
        # get service config
        service_cfg = agriConfig.get_value( 'agri_service', {} )
        resources_cfg = service_cfg.get( 'resources', {} )
        res_cfg = resources_cfg.get( serviceName, {} )
        warningCodes = res_cfg.get( 'warningDtoCodes', [] )
        warningMsgBar = res_cfg.get( 'warningMsgBar', False )
        
        # call service
        self.controller.onServiceRequest( serviceName, 
                                          dataRow, 
                                          genData, 
                                          agriControlBox.setServiceData, 
                                          followLinkedService=followLinkedService,
                                          warningCodes=warningCodes,
                                          warningMsgBar=warningMsgBar )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickAuthenticate(self, checked, action, onlyIfNotAuth=False):
        """Authentication method"""
        # check if authenticated
        if onlyIfNotAuth and self.authenticated:
            return
        
        # show the dialog
        ###self._auth_dlg.show()
        # Run the dialog event loop
        ###result = self._auth_dlg.exec_()
        self.showControlBox( currentTabName='Autenticazione' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRequestDownload(self):
        """Download service request slot"""  
          
        # check if offline db and foglio set
        if self.controller.isOfflineFoglio:
            # download offline DB and start work
            foglioData = self.controlbox.currentFoglioData or self.controlbox.selectedFoglioData
            self.controller.onDownloadEventoLavorazione( self.controlbox, foglioData, reloadTables=False )
        else:
            # download online agri service data
            self.controlbox.onServiziDownload()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickDownload(self, checked, action):
        """Download service click action slot"""
        self.controlbox.setCurrentTab( 'Suoli' )   
        self.onRequestDownload() 
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickUpload(self, checked, action):
        """Upload done worklist and end activity"""
        
        # start activity
        logger.remove_progressbar()
        res = self.controller.onUploadEventoLavorazione()
        if res is self.controller.USER_CANCEL:
            pass
        
        elif res:
            # emit welcome message
            logger.msgbar(logger.Level.Info, 
                          tr( 'salvataggio evento di lavorazione sul server remoto con successo.' ), 
                          title=self.name)
            
        else:
            logger.msgbar(logger.Level.Critical, 
                          tr( 'salvataggio evento di lavorazione sul server remoto con errori' ), 
                          title=self.name)
            
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickLavReject(self, checked, action):
        """Reject worklist activity"""
        logger.remove_progressbar()
        self.controller.onRejectListaLav( evLavData=self.controlbox.selectedEventoLavorazioneData )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickFoglioReject(self, checked, action):
        """Reject current foglio"""
        logger.remove_progressbar()
        self.controller.onRejectFoglio( )
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRasterComboChange(self, index):
        """Raster combo change event handler"""
        
        try:
            # retrieve data
            data = self.__rastercombo.itemData(index)
            if data is None:
                return
            
            # start progress bar
            logger.add_progressbar(tr('Caricamento raster...'), only_message=True)
            
            # load raster layer and add to toc
            self.controller.loadSfondo( index )
            
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            return False
        
        finally:
            logger.remove_progressbar()
            self.__rastercombo.setCurrentIndex(-1)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onEleggComboChange(self, index):
        """Eleggibilità combo change event handler""" 
        if index == -1:
            return
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onEleggComboEditingFinished(self):     
        """Eleggibilità combo text editing finished handler"""
        
        # check if combo has correct value
        combo = self.__eleggcombo
        text = combo.currentText()
        value = combo.itemData( combo.currentIndex(), QGIS_AGRI_ATTR_TEXT_ROLE )
        if text == value:
            return
        
        # find and set currect text, if any
        index = combo.findData( text, QGIS_AGRI_ATTR_TEXT_ROLE )
        if index != -1:
            combo.setCurrentIndex( index )
            self.onEleggComboTextChange( text )
            return
        
        # find and set currect text, if any
        completer = combo.completer()
        if completer is None:
            return
        elif completer.completionCount() != 1:
            return 
        
        text = combo.completer().currentCompletion()
        if not text:
            return 
        
        index = combo.findData( text, QGIS_AGRI_ATTR_TEXT_ROLE )
        if index != -1:
            combo.setCurrentIndex( index )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onEleggComboTextChange(self, value):
        """Eleggibilità combo text change event handler"""
        
        # check if combo has value
        combo = self.__eleggcombo
        if not value:
            combo.setStyleSheet( "QComboBox{ background-color: white; }" )
            self.__eleggcomboAction.forceDisable( True )
            return
       
        # check if combo enabled
        if not combo.isEnabled():
            return
       
        # check if valid value
        valid = False
        index = combo.currentIndex()
        text = combo.itemData( index, QGIS_AGRI_ATTR_TEXT_ROLE )
        if text == value:
            # check if assignable value
            valid = combo.itemData( index, QGIS_AGRI_ATTR_ASSIGN_ROLE ) 
        
        # change combo style
        if valid:
            #combo.setStyleSheet( "QComboBox{ background-color: white; } QAbstractItemView{ background: white } QComboBox:item:selected{ color: white; background-color: blue;}" )
            combo.setStyleSheet( "QComboBox{ background-color: white; }" )
        else:
            combo.setStyleSheet( "QComboBox { background-color: rgb(255, 179, 179); }" )
            
        self.__eleggcomboAction.forceDisable( not valid )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickShowControlBox(self, checked, action):
        """Show control box"""
        # connect to provide cleanup on closing of dockwidget
#         if not self.__controlbox.isVisible():
#             self.__controlbox.closingWidget.connect(self.onCloseControlBox)
#             self.__controlbox.serviceRequest.connect(self.onServiceRequest)
        self.showControlBox()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickShowSearchBox(self, checked, action):
        """Show search box"""
        self.__searchdlg.show()
        self.__searchdlg.raise_()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickShowErrorsBox(self, checked, action):
        """Show errors box"""
        if self.__can_dock_errorsbox:
            # need to re add dock widget for bug in Qt
            self.iface.addDockWidget( Qt.BottomDockWidgetArea, self.errorsbox )
            self.errorsbox.setDockable( self.__can_dock_errorsbox )
        self.errorsbox.show()
        self.errorsbox.raise_()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onStartEditing(self, checked, action):
        """Method to start editing on Agri layers"""
        
        # check if to stop editing
        if not checked:
            self.onEndEditing(checked, action)
            return
        
        # close particelle editing
        if not self.particelle.onParticelleEndEditing(
                        False, 
                        None,
                        buttons=QMessageBox.Save|QMessageBox.Cancel,
                        headerMessage=tr("<b>ATTENZIONE: PARTICELLE APERTE IN EDITING.</b><br>"),
                        msgLevel=Qgis.Warning ):
            action.setChecked( False )
            return
        
        # get list of editable Agri layers
        vlayers = self.controller.get_suolo_vector_layers( 'editing', sort_attr='editorder' )
        if len(vlayers) == 0:
            action.setChecked( False )
            logger.msgbox(logger.Level.Critical, tr( 'Nessun layer di selezione associato al comando' ), title=tr('ERRORE'))
            return
        
        # force only one layer in editing, choosing:
        #  1) current layer in list of editing suoli layers
        #  2) first layer by order of editing suoli layers
        currLayer = self.iface.activeLayer()
        """
        if currLayer in vlayers:
            vlayers = [ currLayer ]
        else:
            vlayers = [ vlayers[ 0 ] ]   
        """
        # start editing
        QGISAgriLayers.start_editing( vlayers )
        
        
        # set current layer
        vlayersEditGrab = self.controller.get_suolo_vector_layers( 'editing|grab' )
        if currLayer not in vlayersEditGrab:
            selLayers = self.controller.get_suolo_vector_layers('editing|select')
            vlayer = selLayers[0] if len(selLayers) > 0 else vlayers[0]
            QGISAgriLayers.set_current_layer( vlayer )
        
        # emit message
        logger.msgbar(logger.Level.Info, tr('Avviata editazione livelli SUOLI'), title=self.name)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onEndEditing(self, checked, action, buttons=None, headerMessage=None, msgLevel=Qgis.Info):
        """Method to terminate editing on Agri layers"""
        
        # get list of editable Agri layers
        vlayers = self.controller.get_suolo_vector_layers('editing', sort_attr='editorder')
        if len(vlayers) == 0:
            logger.msgbox(logger.Level.Critical, tr('Nessun layer di selezione associato al comando'), title=tr('ERRORE'))
            return False
        
        vlayers_ext = self.controller.get_suolo_vector_layers( 'editing|close' ) or []
        vlayers = vlayers + vlayers_ext
              
        # stop editing
        if not QGISAgriLayers.end_editing_ext( 
                    vlayers, buttons=buttons, headerMessage=headerMessage, msgLevel=msgLevel ):
            if action:
                action.setChecked( True )
            return False
        #    
        #QGISAgriLayers.read_only_layers( vlayers_ext )

        # update layers
        QGISAgriLayers.update_layers( vlayers )
        
        return True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickDrawPolygon(self, checked, action):
        """Draw a new polygon"""
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__drawPolygonTool ):
            return
        
        # get current layer
        layer = self.iface.activeLayer()
        provider = layer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or layer.name()
        
        # get config
        attribs = {}
        cmd_cfg = self.controller.getCommandConfig( 'drawpolygon', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
        
        
        # instance tool
        if self.__drawPolygonTool is None:
            from qgis_agri.gui.draw_tools import MapToolDigitizePolygon
            self.__drawPolygonTool = MapToolDigitizePolygon( self.iface, initAttribs=attribs )
            
        # initialize tool and add to canvas
        self.__drawPolygonTool.initialize( layer, initAttribs=attribs )
        self.run_tool( checked, action, self.__drawPolygonTool, msg=tr('Disegna un nuovo poligono'), snapping=True )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickDelPolygon(self, checked, action):
        """Delete an existing polygon"""
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__delPolygonTool ):
            return
        
        # instance tool
        if self.__delPolygonTool is None:
            self.__delPolygonTool = DeleteFeatureTool( self.iface, multiselect=True )
            
        # initialize tool and add to canvas
        self.__delPolygonTool.initialize()
        self.run_tool( checked, action, self.__delPolygonTool, msg=tr( 'Rimuove i poligoni selezionati' ) )
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onCloneParticellaSuolo(self, checked, action):
        """Clone an existing PARTICELLA to suolo layer"""
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__clonePartSuoloTool ):
            return
        
        # get command layers
        selVectlayers = self.controller.get_suolo_vector_layers('cloneParticellaSuolo|sel')
        if not selVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer PARTICELLA presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        
        # get destination layers
        destCondlayers = self.controller.get_suolo_vector_layers('cloneParticellaSuolo|cond')
        if not destCondlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer SUOLO associato al comando.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        destCondlayer = destCondlayers[0]
        
        # get destination layers
        destNoCondlayers = self.controller.get_suolo_vector_layers('cloneParticellaSuolo|nocond')
        if not destNoCondlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer SUOLO associato al comando.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        destNoCondlayer = destNoCondlayers[0]
        
        # show selection layers
        QGISAgriLayers.hide_layers( selVectlayers, hide=False )
        
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # check if left button
            if mouseBtn != Qt.LeftButton:
                # restart action
                action.trigger()
                return
            
            # set action not checked
            action.setChecked( False )
            
            # get feature
            feature = features[0]
            to_layer = destCondlayer
            
            # get copy field definition and destinationlayer
            cmd_cfg = self.controller.getCommandConfig( 'cloneParticellaSuolo' )
            cond_filter = cmd_cfg.get( 'condFilter', '' )
            feature_filter = QgsFeatureRequest( QgsExpression( cond_filter ) )
            if not feature_filter.acceptFeature( feature ):
                to_layer = destNoCondlayer
            
            provider = to_layer.dataProvider()
            uri = provider.uri()
            layName = uri.table() or to_layer.name()
                
            cmd_cfg = self.controller.getCommandConfig( 'cloneParticellaSuolo', to_layer )
            fld_copy_lst = cmd_cfg.get( 'wrkFields', [] )
            defaultAttributes = self.controlbox.currentFoglioFilterData
            
            # clone feature
            to_layer.startEditing()
            to_layer.beginEditCommand( 'clone_particellasuolo' )
            newFeatures = QGISAgriLayers.clone_features(to_layer, [feature], fld_copy_lst, defaultAttributes )
            if newFeatures:
                # show attribute form
                res = self.iface.openFeatureForm( to_layer, newFeatures[0], showModal=True )
                if not res:
                    # rollback for user cancel
                    to_layer.destroyEditCommand()
                else:
                    # commit command
                    to_layer.endEditCommand()
            else:
                # rollback for error
                to_layer.destroyEditCommand()
                    
            # update canvas
            ##QGISAgriLayers.hide_layers( [layer] )
            QGISAgriLayers.update_layers( to_layer )
            
            # restart action
            action.trigger()
        
        
        # instance tool
        if self.__clonePartSuoloTool is None:
            self.__clonePartSuoloTool = SelectFeatureTool( 
                self.iface, selVectlayers, single=True, unsetMapToolOnSelect=True )
            
        # initialize tool and add to canvas
        self.__clonePartSuoloTool.initialize( selVectlayers, onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__clonePartSuoloTool, msg=tr( 'Clona particella come suolo' ) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickAddPolygonHole(self, checked, action):
        """Run action to add new polygon hole"""
        # test if checkable action
        if not self.checkable_action( checked, action ):
            return
        
        # run tool 
        self.run_tool(checked, action, None, msg=tr('Aggiungi buchi poligono'), cmdAction=self.iface.actionAddRing())
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickDelPolygonHole(self, checked, action):
        """Run action to delete a polygon hole"""
        # test if checkable action
        if not self.checkable_action( checked, action ):
            return
        
        # run tool
        self.run_tool(checked, action, None, msg=tr('Rimuovi buchi poligono'), cmdAction=self.iface.actionDeleteRing()) 
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickVertexTool(self, checked, action):
        """Run vertex tool action"""
        # test if checkable action
        if not self.checkable_action( checked, action ):
            return
        
        # run tool
        self.run_tool(checked, action, None, msg=tr('Modifica vertici'), cmdAction=self.iface.actionVertexTool(), snapping=True) 
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickConfirmSuoliProposti(self, checked, action):
        """Confirm Suoli Proposti"""
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__confirmSuoliPropostiTool ):
            return
        
        # get source vector layers
        selVectlayers = self.controller.get_suolo_vector_layers( 'confirmproposti|sel' )
        if len(selVectlayers) == 0:
            logger.msgbox(logger.Level.Critical, tr('Nessun layer di selezione associato al comando'), title=tr('ERRORE'))
            return
        if len(selVectlayers) > 1:
            logger.msgbox(logger.Level.Critical, tr('Definiti più layer di selezione associati al comando'), title=tr('ERRORE'))
            return
        
        # get destination layers 
        #dataSourceUriLst = self.controller.get_datasourceuri_suolo_layers( 'confirmproposti' )
        #if not QGISAgriLayers.is_requested_vectorlayer( currLayer, dataSourceUriLst ):
        #    logger.msgbox(logger.Level.Critical, tr('Nessun layer di destinazione associato al comando'), title=tr('ERRORE'))
        #    return
        suoliVectlayers = self.controller.get_suolo_vector_layers( 'confirmproposti' )
        if len(suoliVectlayers) == 0:
            logger.msgbox(logger.Level.Critical, tr('Nessun layer di destinazione associato al comando'), title=tr('ERRORE'))
            return
        
        
        destVectlayers = self.controller.get_suolo_vector_layers( 'confirmproposti|dest' )
        outLayer = suoliVectlayers[0] if len(destVectlayers) == 0 else destVectlayers[0]
        
        
        # get cutting layers 
        cutVectlayers = self.controller.get_suolo_vector_layers( 'confirmproposti|cut' )
        
        # get overlap layers
        overlapLayers = self.controller.get_suolo_vector_layers( 'confirmproposti|overlap' )
        
        
        # show selection layers
        QGISAgriLayers.hide_layers( selVectlayers, hide=False )
        
        # callback function for checks
        def checkIntersections( dictCalcFeatures, lstOrdLays ):
            try:
                # check there are 'suoli sospesi'
                for outLayer in lstOrdLays:
                    # get 'flagSospensione' field index
                    fields = outLayer.fields()
                    field_ndx = fields.indexFromName( 'flagSospensione' )
                    if field_ndx == -1:
                        continue
                    
                    # get created features lists
                    featTuple = dictCalcFeatures[ outLayer.id() ]
                    intersFeatList = featTuple[0] or []
                    ###diffFeatList = featTuple[1] or [] <--- NO: THIS CONTAINS ESTERNAL CUTTED 'SUOLI'
                    for feat in intersFeatList: ### + diffFeatList:
                        # check if 'suolo sospeso'
                        val = feat.attribute( field_ndx )
                        if val == 1:
                            logger.msgbar( logger.Level.Warning, 
                                           tr( "Presente un suolo sospeso; impossibile accettare il suolo proposto" ),
                                           title = self.name,
                                           clear = True )
                            # return insuccess
                            return False
                # return success
                return True
            except Exception as e:
                logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
                return False
        
        # callback function for selection
        def onSelectFeature(inLayer, inFeatures, mouseBtn):
            try:
                # get selecting feature
                if len(inFeatures) == 0:
                    return
                inFeat = inFeatures[0]
                
                
                # get attributes to copy
                cmd_cfg = self.controller.getCommandConfig( 'confirmproposti' )
                attr_copy_dic = cmd_cfg.get( 'wrkFields', [] )
                attr_set_dic = cmd_cfg.get( 'setFields', [] )
                filter_expr = cmd_cfg.get( 'filterExpression', None )
                
                # for each destination layer, create intersect(difference) features
                layTag = "Suoli proposti"
                if self.controller.intersectSuoli( 
                    inFeat, 
                    outLayer, 
                    suoliVectlayers,
                    cutVectlayers,
                    overlapLayers, 
                    attr_copy_dic,
                    setAttrFldList = attr_set_dic, 
                    callBackFnc = checkIntersections, 
                    layTag = layTag ):
                    
                    # update layer feature count    
                    self.controller.updateLayersFeaturesCount( [inLayer] )
                        
                    # update canvas
                    ##QGISAgriLayers.hide_layers( [inLayer] )
                    QGISAgriLayers.update_layers(  list( set( [inLayer, outLayer] + suoliVectlayers ) ) )
                    
                else:
                    action.setData( QGISAgriActionData(suppress_msg=True) )
                    
                # restart action
                action.trigger()
                
            except QGISAgriException as e:
                # handle exception
                logger.msgbox( logger.Level.Critical, formatException(e), title=tr('ERRORE') )
                
        
        # instance tool to select a feature
        if self.__confirmSuoliPropostiTool is None:
            self.__confirmSuoliPropostiTool = SelectFeatureTool( self.iface, selVectlayers, single=True, unsetMapToolOnSelect=True )
            
        # initialize tool and add to canvas
        self.__confirmSuoliPropostiTool.initialize( selVectlayers, onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__confirmSuoliPropostiTool, msg=tr( 'Conferma suolo proposto' ) )
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickConfirmAllSuoliLavorazione(self, checked, action):
        """ Confirm all 'suoli lavorazione' """
        
        # get command layers
        vlayers = self.get_cmd_layers( 'confirmallsuoli' )
        if not vlayers:
            return
       
        # check if active layer is a command layer
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # confirl all suoli
        self.controller.onConfirmAllSuoliLavorazione( currLayer )
        
        # disable action
        action.setChecked( False )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickRepairSuolo(self, checked, action):
        """ Repair suolo feature """
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__repairSuoloTool ):
            return
        
        # get command layers
        vlayers = self.get_cmd_layers( 'repairsuolo' )
        if not vlayers:
            return
       
        # check if active layer is a command layer
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = self.controller.getCommandConfig( 'repairsuolo', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
                    
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # disable action
            action.setChecked( False )
            
            # run command
            layer.beginEditCommand( 'repairsuolo' )
            res, errMsg, _ = QGISAgriLayers.repair_feature_single( 
                layer, 
                features[0], 
                attr_dict=attribs, 
                splitMultiParts=True,
                autoSnap=True,
                #suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                suoliSnapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE,
                suoliSnapLayerUris=self.controller.suoliSnapLayerUris )
       
            # end command
            layer.endEditCommand()
            
            # show warning
            if errMsg:
                logger.msgbar( logger.Level.Warning, errMsg, title=self.name )
            
            # update layer
            QGISAgriLayers.update_layers( [ layer ] )
            
        
        # instance tool
        if self.__repairSuoloTool is None:
            self.__repairSuoloTool = SelectFeatureTool( self.iface, [currLayer], single=True )
            
        # initialize tool and add to canvas
        self.__repairSuoloTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__repairSuoloTool, msg=tr( 'Ripara suolo' ) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickRepairAllSuoli(self, checked, action):
        """ Repair all suoli features """

        # enable action
        action.setChecked( False )
       
        # get command layers
        vlayers = self.get_cmd_layers( 'repair-all-suoli' )
        if not vlayers:
            return
       
        # check if active layer is a command layer
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = self.controller.getCommandConfig( 'repairsuolo', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
                    
        # show message
        logger.msgbar( logger.Level.Info, tr('Converte le geometrie multi parti in singole parti'), title=self.name )
                    
        # loop layer features
        for feat in currLayer.getFeatures():
            # get feature geometry
            geom = feat.geometry()
            # check if multi parts geometry
            if geom.isMultipart() and len( geom.asGeometryCollection() ) > 1:
                # reapair feature geometry
                QGISAgriLayers.repair_feature( 
                    currLayer, 
                    feat, 
                    attr_dict=attribs, 
                    splitMultiParts=True,
                    autoSnap=True,
                    #suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                    suoliSnapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE,
                    suoliSnapLayerUris=self.controller.suoliSnapLayerUris )
                
        # update layer
        QGISAgriLayers.update_layers( [ currLayer ] ) 
        
        # show warning
        ##if nErr > 0:
        ##    logger.msgbar( logger.Level.Warning, errMsg, title=self.name )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onSuoloFind(self):
        """ Find listed suolo in map """
        # get command layers
        vlayers = self.get_cmd_layers( 'findsuolo' )
        if not vlayers:
            return
        
        # remove filter on grid
        self.controlbox.onRemoveSuoliFilter()
        
        # get suoli type filter
        suoliFilter = agriConfig.services.suoliLavorazioneOffline.suoliInLavorazioneFilter
                    
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # init
            msg = tr( 'Suolo da lavorare non trovato in elenco' )
            
            # check if feature is found
            feat = features[0]
            if feat is None:
                logger.msgbar( logger.Level.Warning, msg, title=self.name )
                return
            
            # get suolo feature id Padre
            featIdField = agriConfig.services.suoliLavorazioneOffline.featureIdField
            featIdPadreField = agriConfig.services.suoliLavorazioneOffline.featureIdFieldPadre
            attribs = QGISAgriLayers.get_attribute_values( feat, attr_list=[ featIdPadreField ] )
            idFeat = attribs.get( featIdPadreField, None )
            if idFeat is None or idFeat == NULL:
                # get suolo feature id 
                attribs = QGISAgriLayers.get_attribute_values( feat, attr_list=[ featIdField ] )
                idFeat = attribs.get( featIdField, None )
            
            # find suolo in control box grid
            if self.controlbox.findSuoloLavByAttib( featIdField, idFeat ):
                
                msg = "{0}: {1}".format( tr( 'Trovato sulo in lavorazione con id' ), idFeat ) 
                logger.msgbar( logger.Level.Info, msg, title=self.name )
                
            else:
                logger.msgbar( logger.Level.Warning, msg, title=self.name )
        
        
        # instance tool
        if self.__findSuoloTool is None:
            self.__findSuoloTool = SelectFeatureTool( self.iface, 
                                                      vlayers, 
                                                      single=True,
                                                      singleClick=True, 
                                                      unsetMapToolOnSelect=True,
                                                      selectionFilter=suoliFilter )
            
        # initialize tool and add to canvas
        self.__findSuoloTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        self.run_tool( True, None, self.__findSuoloTool, msg=tr( 'Ricerca suolo' ), chkLayers=False )
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickIdentify(self, checked, action):
        """Identify Suolo feature"""
        
        # test if tool is checkable
        if not self.checkable_tool( checked, action, self.__identifyTool ):
            return
        
        # get command layers
        vlayers = self.get_cmd_layers( 'identitysuolo' )
        if not vlayers:
            return
                    
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # get single feature
            feature = features[0]
            # show suolo attributes form
            QGISAgriIdentifyDialogWrapper.initializeCall( pluginCall=True )
            self.iface.openFeatureForm( layer, feature, showModal=True )
            #layer.removeSelection()
        
        
        # instance tool to select a feature
        if self.__identifyTool is None:
            self.__identifyTool = SelectFeatureTool( self.iface, vlayers, single=True )
            self.layerWillBeRemoved.connect( self.__identifyTool.onLayerWillBeRemoved )
            
        # initialize tool and add to canvas
        self.__identifyTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__identifyTool, msg=tr( 'Modifica attributi suolo' ) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickShowLabels(self, checked, action):
        """Show / Hide 'suolo lavorazione' labels"""
        # get command layers
        vlayers = self.get_cmd_layers( 'showlabels' )
        if not vlayers:
            return
        
        # show \ hide layer labels
        #QGISAgriLayers.show_layer_labels( vlayers )
        QGISAgriLayers.activate_layer_Labeling( vlayers, '!Area', activeSwitch=True )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickShowAreaLabels(self, checked, action):
        """Show / Hide 'suolo lavorazione' Area labels"""
        # get command layers
        vlayers = self.get_cmd_layers( 'showArealabels' )
        if not vlayers:
            return
        
        # show \ hide layer labels
        res = QGISAgriLayers.activate_layer_Labeling( vlayers, 'Area', activeSwitch=True )
        if res and res.get('hide_min_scale'):
            # notify label not visible for minimum scale
            logger.msgbar(logger.Level.Warning, 
                          tr( "Etichettatura non visibile in base alla scala corrente della mappa" ),
                          title=self.name)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickTopoVerify(self, checked, action):
        """ Checks suoli topology validity. """
        
        # init
        cmdName = 'CheckTopoSuoli'
        
        # check if any validation disabled
        controller = self.controller
        checker = controller.checker
        if not checker.can_proceed_if_disabled_checks():
            return
        
        # close edit mode
        if not controller.closeEditMode( cmdName ):
            return
        
        try:
            # start progress bar
            logger.add_progressbar(
                tr('Verifica geometria e topologia suoli: attendere prego...'), only_message=True)
            
            # run check
            checker = controller.checker
            res, hasErrors, hasWarnings = controller.checkSuoli( 
                cmdName, 
                [ checker.checkSuoliValidity, checker.checkSuoliTopology ], 
                emitResultMessage=False, 
                cmdOptions={ 'layersLoadOnly': True } )
            if res is self.controller.USER_CANCEL:
                return
            
            elif hasErrors:
                logger.msgbox( logger.Level.Critical,
                               tr('Verifica terminata con errori'), 
                               title=self.name )
                
            elif hasWarnings:
                logger.msgbox( logger.Level.Warning,
                               tr('Verifica terminata con segnalazioni'), 
                               title=self.name )
                
            elif res:
                logger.msgbox( logger.Level.Info, 
                               tr('Verifica con successo.'), 
                               title=self.name )
                
            else:
                return
                
            
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
        
        finally:
            logger.remove_progressbar()
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickSetElegCode(self, checked, action):
        """Set 'Eleggibilità' code to Suoli feature"""
        
        # init
        toolMsg = tr( 'Assegna codice Eleggibilità' )
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__setElegCodeTool, msg=toolMsg ):
            return
       
        # get command layers
        vlayers = self.get_cmd_layers( 'seteleggibilita' )
        if not vlayers:
            return
            
        # get 'Eleggibilità' field name from config
        fldElegCode = agriConfig.get_value( 'context/suolo/eleggibilita/fieldValue', '' )               
        
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # get current 'Eleggibilità' code by combo
            index = self.__eleggcombo.currentIndex()
            if index == -1:
                return
            
            # prepare attributes to assign
            attr_dic = {}
            attr_dic[ fldElegCode ] = self.__eleggcombo.itemData( index, QGIS_AGRI_ATTR_VALUE_ROLE )
            
            # begin command
            layer.beginEditCommand( 'seteleggibilita' )
            QGISAgriLayers.change_attribute_values( layer, features, attr_dic )
            layer.endEditCommand()
            
            # update layer
            QGISAgriLayers.update_layers( [ layer ] )
        
        
        # instance tool to select a feature
        if self.__setElegCodeTool is None:
            self.__setElegCodeTool = SelectFeatureTool( self.iface, 
                                                        vlayers, 
                                                        single=False, 
                                                        deselectOnStart=True,
                                                        onSelectFeature=onSelectFeature )
            
        # initialize tool and add to canvas
        self.__setElegCodeTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__setElegCodeTool, msg=toolMsg )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickClearResults(self, checked, action):
        """Clear processing results"""    
        # show controller widget
        self.controller.checker.clear_processing_results()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickMoveSplitSuoli(self, checked, action):
        """Split suoli: cutting line edit"""
        tool = self.__splitSuoliTool
        if tool is None:
            return
        self.checkable_tool( checked, action, tool )
        tool.startOperation( SplitSuoliTool.operation.MOVE )
        logger.msgbar( logger.Level.Info, tr('Edita la linea di taglio'), title=self.name, clear=True )

             
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onSplitSuoli(self, checked, action):
        """Split suoli features dinamically"""
        
        # test if tool is checkable
        tool = self.__splitSuoliTool    
        if not self.checkable_tool( checked, action, tool ):
            # check if default operation
            if tool is not None and tool.currentOperation != tool.operation.DRAW:    
                tool.startOperation( tool.operation.DRAW )
            return
        
        # get source vector layers
        vlayers = self.get_cmd_layers( 'splitsuoli' )
        if not vlayers:
            return
        
        # check if active layer is a command layer
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = self.controller.getCommandConfig( 'splitsuoli', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
        
        # instance tool
        if self.__splitSuoliTool is None:
            self.__splitSuoliTool = SplitSuoliTool( self.iface, 
                                                    currLayer, 
                                                    copyAttribs=attribs,
                                                    snapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE, 
                                                    suoliSnapLayers=self.controller.suoliSnapLayerUris )
            
            self.__splitSuoliTool.deactivated.connect( lambda: ( self.__splitToolBtn.setDefaultAction( self.__splitSuoliTool.action() ),
                                                                 self.__splitMoveAction.forceDisable( True ) ) )
            
            self.__splitSuoliTool.captureChanged.connect( lambda n: ( self.__splitToolBtn.setDefaultAction( self.__splitSuoliTool.action() ) if n < 1 else None,
                                                                      self.__splitMoveAction.forceDisable( n < 2 ) ) )
            
            
            # handle signal for operation changed
            def setToolButton(operation):
                action = None
                tool = self.__splitSuoliTool
                if operation == tool.operation.DRAW:
                    action = tool.action()
                elif operation == tool.operation.MOVE:
                    action = self.__splitMoveAction
                    
                if action is not None:
                    QtCore.QTimer.singleShot( 0, lambda: self.__splitToolBtn.setDefaultAction( action ) )
        
            self.__splitSuoliTool.operationChanged.connect( setToolButton )
              
        # initialize tool and add to canvas
        self.__splitSuoliTool.initialize( currLayer, copyAttribs=attribs )
        self.run_tool( checked, action, self.__splitSuoliTool, msg=tr('Taglia i suoli dinamicamente'), snapping=True )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onClickMoveFillSuoli(self, checked, action):
        """Fill suoli: drawing polyline edit"""
        tool = self.__fillSuoliTool
        if tool is None:
            return
        self.checkable_tool( checked, action, tool )
        tool.startOperation( FillSuoliTool.operation.MOVE )
        logger.msgbar( logger.Level.Info, tr('Edita il tracciato di disegno'), title=self.name, clear=True )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onFillSuoli(self, checked, action):
        """Draws new polygon: fill area and holes with suoli features dynamically"""
        # test if tool is checkable
        tool = self.__fillSuoliTool    
        if not self.checkable_tool( checked, action, tool ):
            # check if default operation
            if tool is not None and tool.currentOperation != tool.operation.DRAW:    
                tool.startOperation( tool.operation.DRAW )
            return
        
        # get dest vector layers
        vDestLayers = self.get_cmd_layers( 'fillsuoli' )
        if not vDestLayers:
            return
        
        # get cutting layers
        vCutLayers = self.get_cmd_layers( 'fillsuoli|cut' )
        vCutLayers = listUtil.concatNoDuplicate( vCutLayers, vDestLayers )
        
        # check if active layer is a command layer
        currLayer = self.iface.activeLayer()
        if currLayer not in vDestLayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = self.controller.getCommandConfig( 'fillsuoli', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
        
        # instance tool
        if self.__fillSuoliTool is None:
            self.__fillSuoliTool = FillSuoliTool( self.iface, 
                                                  currLayer,
                                                  suoliRefLayers=vCutLayers,
                                                  copyAttribs=attribs,
                                                  suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                                                  snapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE, 
                                                  suoliSnapLayers=self.controller.suoliSnapLayerUris )
            
            self.__fillSuoliTool.deactivated.connect( lambda: ( self.__fillToolBtn.setDefaultAction( self.__fillSuoliTool.action() ),
                                                                self.__fillMoveAction.forceDisable( True ) ) )
            
            self.__fillSuoliTool.captureChanged.connect( lambda n: ( self.__fillToolBtn.setDefaultAction( self.__fillSuoliTool.action() ) if n < 1 else None,
                                                                    self.__fillMoveAction.forceDisable( n < 2 ) ) )
            
            # handle signal for operation changed
            def setToolButton(operation):
                action = None
                tool = self.__fillSuoliTool
                if operation == tool.operation.DRAW:
                    action = tool.action()
                elif operation == tool.operation.MOVE:
                    action = self.__fillMoveAction
                    
                if action is not None:
                    QtCore.QTimer.singleShot( 0, lambda: self.__fillToolBtn.setDefaultAction( action ) )
        
            self.__fillSuoliTool.operationChanged.connect( setToolButton )
              
        # initialize tool and add to canvas
        self.__fillSuoliTool.initialize( currLayer, suoliRefLayers=vCutLayers, copyAttribs=attribs )
        self.run_tool( checked, action, self.__fillSuoliTool, msg=tr('Disegna un nuovo suolo'), snapping=True )
 
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onDissolveSuoli(self, checked, action):
        """Dissolve suoli features dinamically"""
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__dissolveSuoliTool ):
            return
        
        # get source vector layers
        vlayers = self.get_cmd_layers( 'dissolvesuoli' )
        if not vlayers:
            return
        
        # check if active layer is a command layer
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = self.controller.getCommandConfig( 'dissolvesuoli', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value

        # instance tool
        if self.__dissolveSuoliTool is None:
            self.__dissolveSuoliTool = DissolveSuoliTool( self.iface, 
                                                          currLayer,
                                                          copyAttribs=attribs,
                                                          holeMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                                                          snapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE, 
                                                          suoliSnapLayers=self.controller.suoliSnapLayerUris,
                                                          msgTitle=self.__name )
            
        # initialize tool and add to canvas
        self.__dissolveSuoliTool.initialize( currLayer, copyAttribs=attribs )
        self.run_tool( checked, action, self.__dissolveSuoliTool, msg=tr( 'Unisci i suoli dinamicamente' ), snapping=False )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onDifferenceSuoli(self, checked, action):
        """ Difference suoli features dinamically """
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__differenceSuoliTool ):
            return
        
        # get source vector layers
        vlayers = self.get_cmd_layers( 'diffsuoli' )
        if not vlayers:
            return
        
        # check if active layer is a command layer
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get diff layers
        vDiffLayers = self.get_cmd_layers( 'diffsuoli|cut', err_if_empty=False )
        vDiffLayers = listUtil.concatNoDuplicate( vDiffLayers, vlayers )

        # instance tool
        if self.__differenceSuoliTool is None:
            self.__differenceSuoliTool = DifferenceSuoliTool( 
                self.iface, 
                currLayer,
                suoliRefLayers=vDiffLayers,
                suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                snapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE, 
                suoliSnapLayers=self.controller.suoliSnapLayerUris,
                msgTitle=self.__name )
            
        # initialize tool and add to canvas
        self.__differenceSuoliTool.initialize( currLayer, suoliRefLayers=vDiffLayers )
        self.run_tool( checked, action, self.__differenceSuoliTool, msg=tr( 'Ritaglia un suolo per differenza con gli altri suoli' ), snapping=False )
    
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def downloadFeatureData(self, 
                            dataSourceUri: object,
                            idKeyFieldName: str, 
                            idKeyFeature: int,
                            idFeature: int,
                            lstIdFeature: list,
                            htmlTemplate: str,
                            dataLoaderFunc: types.FunctionType,
                            optionData: dict) -> None:
        """ Download feature info """
        
        # downloaded data callback function
        def onDownloadFeatureData(idKeyFeature, servicesData, lst_errors):
            # show documents dialog
            self.docsdlg.loadDocumentData( 
                dataSourceUri, 
                idKeyFieldName, 
                idKeyFeature,
                idFeature, 
                lstIdFeature, 
                servicesData,
                lst_errors,
                htmlTemplate,
                dataLoaderFunc,
                optionData
            )
            self.docsdlg.show()
            
        # init
        self.docsdlg.reset( idFeature )   
            
        # download suolo info
        dataLoaderFunc( idKeyFeature, idFeature, lstIdFeature, onDownloadFeatureData, optionData )
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onShowDataSuolo(self, checked, action):
        """ Download suolo info action handler """
        
        # test if tool is checkable
        if not self.checkable_tool( checked, action, self.__scaricaSuoloDocTool ):
            return
        
        # get command layers
        vlayers = self.get_cmd_layers( 'scaricaDatiSuolo|Base' )
        vlayers = vlayers + self.get_cmd_layers( 'scaricaDatiSuolo' )
        if not vlayers:
            return
        
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get document field
        cmd_cfg = self.controller.getCommandConfig( 'scaricaDatiSuolo' )
        idKey_fld = cmd_cfg.get( 'idKeyField', '' ) 
        idSuolo_fld = cmd_cfg.get( 'idField', '' )
        idSuoloPadre_fld = cmd_cfg.get( 'idFieldPadre', '' )
        if not idSuolo_fld or not idSuoloPadre_fld:
            logger.msgbox( logger.Level.Critical, 
                           tr( 'Manca la definizione del campo id nella configurazione del plugin.' ), 
                           title=tr('ERRORE'))
            return
        
        
        ############################################################################################################
        # selection callback function
        def onSelectFeature(layer, features, mouseBtn):
            # get document id
            feature = features[0]
            idKeyFeature = feature.id()
            lstIdSuolo = []
            ##attribs = QGISAgriLayers.get_attribute_values( feature, attr_list=[idSuolo_fld] )
            ##idSuolo = attribs.get( idSuolo_fld, None )
            ##if not idSuolo:
            # try with 'id suolo padre' field
            attribs = QGISAgriLayers.get_attribute_values( feature, attr_list=[idSuoloPadre_fld] )
            idSuolo = attribs.get( idSuoloPadre_fld, None )
            
            # load JSON string as Python object (must be a list)
            if idSuolo:
                import json
                try:
                    idSuolo = json.loads(idSuolo)
                except json.JSONDecodeError:
                    idSuolo = None
                    
            if not idSuolo:
                # try with 'id suolo' field
                attribs = QGISAgriLayers.get_attribute_values( feature, attr_list=[idSuolo_fld] )
                idSuolo = attribs.get( idSuolo_fld, None )
                
            if not idSuolo:
                # id suolo not found 
                logger.msgbar( logger.Level.Warning, 
                               tr( 'Id suolo non valorizzato.' ), 
                               title=self.name )
                return
            
            # check if valid id list
            if isinstance( idSuolo, list ):
                lstIdSuolo = idSuolo
            else:
                lstIdSuolo.append(idSuolo)
                
            if len(lstIdSuolo) == 0:
                logger.msgbar( logger.Level.Warning, 
                               tr( 'Id suolo non valorizzato.' ), 
                               title=self.name )
                return
            
            idSuolo = lstIdSuolo[0]
            
            # download and show suolo info
            provider = layer.dataProvider()
            dataSourceUri = QgsDataSourceUri( provider.dataSourceUri() )
            self.downloadFeatureData( 
                dataSourceUri,
                idKey_fld, 
                idKeyFeature, 
                idSuolo,
                lstIdSuolo,
                'suolo_documents.html',
                self.event_controller.onDownloadDataSuolo,
                {
                    "windowTitle": 'Dati suolo'
                }
            )
        ############################################################################################################
            
        # hide dialog
        self.docsdlg.hide()    
            
        # instance tool
        if self.__scaricaSuoloDocTool is None:
            self.__scaricaSuoloDocTool = SelectFeatureTool( self.iface, vlayers, single=True, unsetMapToolOnSelect=False )
            
        # initialize tool and add to canvas
        self.__scaricaSuoloDocTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__scaricaSuoloDocTool, msg=tr( 'Visualizza le informazioni dei suoli' ) )
        
        
    
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onBrowseDocumentazione(self, checked, action):
        """ Browse suolo document """
        
        # enable action
        action.setChecked( True )
        
        # show documents site on default system browser
        self.event_controller.onBrowseDocumentazione( 
            check_doc_existance=True, usr_data=None, removeNullParams=True )
        
        # disable action
        action.setChecked( False )
            
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onBrowseDocumentazioneSuoloProposto(self, checked, action):
        """ Browse suolo document """
        
        # test if tool is checkable
        if not self.checkable_tool( checked, action, self.__browsePropostiDocTool ):
            return
        
        # get command layers
        vlayers = self.get_cmd_layers( 'browsedocproposti' )
        if not vlayers:
            return
        
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get document field
        #attr_dic = {}
        cmd_cfg = self.controller.getCommandConfig( 'browseDocProposti' )
        idIstanzaRiesame_fld = cmd_cfg.get( 'idField', '' )
        if not idIstanzaRiesame_fld:
            logger.msgbox( logger.Level.Critical, 
                           tr( 'Manca la definizione del campo id Istanza di Riesame nella configurazione del plugin.' ), 
                           title=tr('ERRORE'))
            return
        
       
        # selection callback function
        def onSelectFeature(layer, features, mouseBtn):
            
            # get istanza id 
            attribs = QGISAgriLayers.get_attribute_values( features[0], attr_list=[idIstanzaRiesame_fld] )
            idIstanzaRiesame = attribs.get( idIstanzaRiesame_fld, None )
            if not idIstanzaRiesame:
                logger.msgbar( logger.Level.Warning, 
                               tr( 'Id Istanza di Riesame non valorizzato.' ), 
                               title=self.name )
                return
            
            
            # show documents site on default system browser
            usr_data = {}
            usr_data[idIstanzaRiesame_fld] = idIstanzaRiesame
            self.event_controller.onBrowseDocumentazione( 
                check_doc_existance=False, usr_data=usr_data )
            
        # instance tool
        if self.__browsePropostiDocTool is None:
            self.__browsePropostiDocTool = SelectFeatureTool( self.iface, vlayers, single=True, unsetMapToolOnSelect=False )
            
        # initialize tool and add to canvas
        self.__browsePropostiDocTool.initialize( [ currLayer ], onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__browsePropostiDocTool, msg=tr( 'Accedi alla documentazione dei suoli proposti' ) )
    
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onBrowseContraddizioni(self, checked, action):
        """ Browse suolo 'contraddittori e sopralluoghi' document """
        
        # enable action
        action.setChecked( True )
        
        # show documents site on default system browser
        self.event_controller.onBrowseContraddizioni()
        
        # disable action
        action.setChecked( False )
    
    # --------------------------------------
    # 
    # --------------------------------------   
    def onDownloadHistory(self, checked, action):
        """ Download Suoli history Geopackage """ 
        
        # enable action
        action.setChecked( True )
        
        # emit message
        logger.msgbar( logger.Level.Info, tr('Scarico lo Storico dei Suoli'), title=self.name )
        
        # download geopackage and browse
        self.event_controller.onDownloadHistory( 
            reload= False, callbackFn= lambda e,d,a=action: a.setChecked( False ) )
        
    
    # --------------------------------------
    # 
    # --------------------------------------   
    def onDownloadLastHistory(self, checked, action):
        """ Download Suoli history Geopackage """ 
        
        # emit message
        logger.msgbar( logger.Level.Info, tr('Scarico lo Storico dei Suoli (aggiornato)'), title=self.name )
        
        # download geopackage and browse
        self.event_controller.onDownloadHistory( reload=True )
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDownloadAppezzamentiPhoto(self, checked, action):
        """ Download suolo proposto photos """
        
        # test if tool is checkable
        if not self.checkable_tool( checked, action, self.__browsePropostiPhotoTool ):
            return
        
        # get command layers
        vlayers = self.get_cmd_layers( 'browsephotoproposti' )
        if not vlayers:
            return
        
        
        # get document field
        #attr_dic = {}
        cmd_cfg = self.controller.getCommandConfig( 'browsePhotoProposti' )
        use_internal_viewer = cmd_cfg.get( 'useInternalViewer', True )
        sel_mm_tolerance = cmd_cfg.get( 'selMMTolerance', 5.0 )
        id_photo_fld = cmd_cfg.get( 'idField', '' )
        if not id_photo_fld:
            logger.msgbox( 
                logger.Level.Critical, tr( 'Manca la definizione del campo id foto appezzamenti nella configurazione del plugin.' ), title=tr('ERRORE'))
            return
        
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # get document id 
            lst_photo_ids = []
            for feat in features:
                attribs = QGISAgriLayers.get_attribute_values( feat, attr_list=[id_photo_fld] )
                photoId = attribs.get( id_photo_fld, None )
                if not photoId:
                    logger.msgbar( logger.Level.Warning, 
                                   tr( 'Id foto appezzamenti non reperito.' ), 
                                   title=self.name )
                    return
                lst_photo_ids.append( photoId )
            
            # download photo file and browse
            lst_photo_ids.sort()
            self.event_controller.onDownloadAppezzamentiPhoto( id_photo_fld, lst_photo_ids, use_internal_viewer )
        
        # instance tool
        if self.__browsePropostiPhotoTool is None:
            self.__browsePropostiPhotoTool = SelectFeatureTool( self.iface, 
                                                                vlayers, 
                                                                single=False, 
                                                                unsetMapToolOnSelect=False,
                                                                selMMTolerance=sel_mm_tolerance )
            
        # initialize tool and add to canvas
        self.__browsePropostiPhotoTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__browsePropostiPhotoTool, msg=tr( 'Scarica e visualizza le foto appezzamenti' ) )
    
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDownloadValidationsPCG(self, checked, action):
        """ Download and show 'Piano Colturale Grafico' data """
        # enable action
        action.setChecked( True )
        
        # download and show PCG
        self.event_controller.onDownloadValidationsPCG()
        
        # disable action
        action.setChecked( False )
        
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onShowDatiPCG(self, checked, action):
        """ Download suolo info action handler """
        
        # test if tool is checkable
        if not self.checkable_tool( checked, action, self.__showPcgTool ):
            return
        
        # get command layers
        vlayers, _ = self.event_controller.get_pcg_layers()
        if not vlayers:
            return
        
        currLayer = self.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        vlayers = [ currLayer ]
        
        # get command config
        cmd_cfg = self.controller.getCommandConfig( 'scaricaDatiPCG' )
        fid_fld_name = cmd_cfg.get( 'idKeyField', 'OGC_FID' ) 
        
        ############################################################################################################
        # selection callback function
        def onSelectFeature(layer, features, mouseBtn):
            # get document id
            feature = features[0]
            fields = feature.fields()
            fld_index = fields.indexFromName( fid_fld_name )
            if fld_index == -1:
                return
            fid_value = feature.attribute( fld_index )
            
            # load GeoJSON data and show
            self.pcgdlg.loadPcgData( layer, fid_fld_name, fid_value )
            self.pcgdlg.show()
        ############################################################################################################
            
        # hide dialog
        self.pcgdlg.hide()    
            
        # instance tool
        if self.__showPcgTool is None:
            self.__showPcgTool = SelectFeatureTool( self.iface, vlayers, single=True, unsetMapToolOnSelect=False )
            
        # initialize tool and add to canvas
        self.__showPcgTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        self.run_tool( checked, action, self.__showPcgTool, msg=tr( 'Visualizza le informazioni del Piano Colturale Grafico' ) )
        
        
    # --------------------------------------
    # 
    # --------------------------------------   
    def onDownloadCXF(self, checked, action):
        """ Download CXF geometry - PARTICELLE working """ 
        
        # enable action
        action.setChecked( True )
        
        # download and show PCG
        self.event_controller.onDownloadCXF()
        
        # disable action
        action.setChecked( False )
        
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDownloadAllegatiParticelle(self, checked, action):
        """ Download and show PARTICELLE allegati list """
        # enable action
        action.setChecked( True )
        
        # download and show PARTICELLE allegati list
        self.event_controller.onDownloadAllegatiParticelle()
        
        # disable action
        action.setChecked( False )    
    
    
    # --------------------------------------
    # 
    # --------------------------------------
    def onImportLayersFromProjct(self, checked, action):
        """ Imports layers from external project """
        action.setChecked( True )
        try:
            # init
            s = QgsSettings()
            dir_path = s.value( f"{self.PLUGIN_NAME}/import_prj_dir", '' )
            importer = QGISAgriLayerImporter()
            # select a QGIS project
            prj_file = importer.selectQgisProjectFile( directory=dir_path )
            if not prj_file:
                return
            # save file folder
            dir_path = os.path.dirname(os.path.realpath(prj_file))
            s.setValue( f"{self.PLUGIN_NAME}/import_prj_dir", dir_path )
            # import layers from external project
            if importer.importFromQgisProject( prj_file ):
                # notify user for successfully importation
                logger.msgbar( 
                    logger.Level.Info,
                    tr( 'Livelli importati con successo.' ), 
                    title=self.name,
                    clear=True )
        
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
            
        finally:    
            # disable action
            action.setChecked( False )
            
    
    
    # --------------------------------------
    # 
    # --------------------------------------
    def onRepaierSuoliParticella(self, layer, feature):
        # get config
        attribs = {}
        cmd_cfg = self.controller.getCommandConfig( 'repairsuolo', layer )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
    
        # repair cons uoli over cond particella
        layer.startEditing()
        layer.beginEditCommand( 'repairsuolo' )
        res = QGISAgriLayers.repair_feature_by_geom( 
            layer, 
            feature, 
            attr_dict=attribs, 
            splitMultiParts=True,
            autoSnap=True )
        # end command
        layer.endEditCommand()
        
        return res
            
    # --------------------------------------
    # 
    # --------------------------------------
    def onSuoliCondParticella(self, checked, action):
        """ 
        Generate 'suoli condotti' feature from 'suoli non condotti' 
        ones that overlaps 'Particelle condotte'. 
        """
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__suoliCondPartTool ):
            return
        
        # get command layers
        selVectlayers = self.get_cmd_layers( 'suoliCondParticella|sel' )
        if not selVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer PARTICELLA presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        
        noCondVectlayers = self.get_cmd_layers( 'suoliCondParticella|nocond' )
        if not noCondVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer Suoli non condotti presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        
        destNoCondVectlayers = self.get_cmd_layers( 'suoliCondParticella|nocond|dest' )
        if not destNoCondVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer Suoli non condotti presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        destNoCondVectlayer = destNoCondVectlayers[0]
        
        destVectlayers = self.get_cmd_layers( 'suoliCondParticella|dest' )
        if not destVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer Suoli condotti presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        destVectlayer = destVectlayers[0]
        
        # get command config
        cmd_cfg = self.controller.getCommandConfig( 'suoliCondParticella' )
        filter_expr = cmd_cfg.get( 'filterExpression', None )
        filter_lav_expr = cmd_cfg.get( 'filterLavExpression', None )
        if filter_expr is None or  filter_lav_expr is None:
            logger.msgbox(
                logger.Level.Critical, 
                tr('Nessun filtro definito per le Particelle in conduzione lavorate.'), 
                title=tr('ERRORE') )
            action.setChecked( False )
            return
         
        # create feature filter for 'Particelle in conduzione'    
        feature_filter = QgsFeatureRequest( QgsExpression( f"{filter_expr} AND {filter_lav_expr}" ) )
        
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            try:
                # check if left button
                if mouseBtn != Qt.LeftButton:
                    return
                    
                # check if right feature
                feature = features[0]
                if not feature_filter.acceptFeature( feature ):
                    action.setData( QGISAgriActionData(suppress_msg=True) )
                    logger.msgbar( 
                        logger.Level.Warning, 
                        tr("Selezionare una Particella in conduzione lavorata."), 
                        title=self.name,
                        clear=True )
                    return
                
                res = self.controller.createSuoliCondParticella(
                    feature,
                    noCondVectlayers,
                    destNoCondVectlayer,
                    destVectlayer)
                
                res = res or self.onRepaierSuoliParticella( destVectlayer, feature ) 
                
                if res:
                    # update layer feature count
                    lst_layers = [noCondVectlayers, destNoCondVectlayer, destVectlayer]   
                    self.controller.updateLayersFeaturesCount( lst_layers )
                        
                    # update canvas
                    QGISAgriLayers.update_layers( lst_layers )
                    
                    # show result message
                    action.setData( QGISAgriActionData(suppress_msg=True) )    
                    logger.msgbar( 
                        logger.Level.Info, 
                        tr("Creati i suoli in conduzione."),
                        title=self.name,
                        clear=True )
                    
            finally:
                # restart action
                action.trigger()
        
        # instance tool
        if self.__suoliCondPartTool is None:
            self.__suoliCondPartTool = SelectFeatureTool( 
                self.iface, 
                selVectlayers, 
                single=True, 
                unsetMapToolOnSelect=True )
            
        # initialize tool and add to canvas
        self.__suoliCondPartTool.initialize( selVectlayers, onSelectFeature=onSelectFeature )
        self.run_tool( 
            checked, 
            action, 
            self.__suoliCondPartTool, 
            msg=tr( 'Taglia suoli non in conduzione su PARTICELLA in conduzione lavorata' ) )
        
    
    
    # --------------------------------------
    # 
    # --------------------------------------
    def onSuoliNoCondParticella(self, checked, action):
        """ 
        Generate 'suoli condotti' feature from 'suoli non condotti' 
        ones that overlaps 'Particelle non condotte'. 
        """
        
        # test if tool is checkable        
        if not self.checkable_tool( checked, action, self.__suoliCondPartTool ):
            return
        
        # get command layers
        selVectlayers = self.get_cmd_layers( 'suoliCondParticella|sel' )
        if not selVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer PARTICELLA presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        
        noCondVectlayers = self.get_cmd_layers( 'suoliCondParticella|nocond' )
        if not noCondVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer Suoli non condotti presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        
        destNoCondVectlayers = self.get_cmd_layers( 'suoliCondParticella|nocond|dest' )
        if not destNoCondVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer Suoli non condotti presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        destNoCondVectlayer = destNoCondVectlayers[0]
        
        destVectlayers = self.get_cmd_layers( 'suoliCondParticella|dest' )
        if not destVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer Suoli condotti presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        destVectlayer = destVectlayers[0]
        
        # get command config
        cmd_cfg = self.controller.getCommandConfig( 'suoliCondParticella' )
        filter_expr = cmd_cfg.get( 'filterExpression', None )
        filter_lav_expr = cmd_cfg.get( 'filterLavExpression', None )
        if filter_expr is None or  filter_lav_expr is None:
            logger.msgbox(
                logger.Level.Critical, 
                tr('Nessun filtro definito per le Particelle non in conduzione lavorate.'), 
                title=tr('ERRORE') )
            action.setChecked( False )
            return
         
        # create feature filter for 'Particelle in conduzione'
        filter_expr = str(filter_expr)
        feature_filter = QgsFeatureRequest( 
            QgsExpression( f"NOT({filter_expr}) AND {filter_lav_expr}" ) )
        
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            try:
                # check if left button
                if mouseBtn != Qt.LeftButton:
                    return
                    
                # check if right feature
                feature = features[0]
                if not feature_filter.acceptFeature( feature ):
                    action.setData( QGISAgriActionData(suppress_msg=True) )
                    logger.msgbar( 
                        logger.Level.Warning, 
                        tr("Selezionare una Particella non in conduzione lavorata."), 
                        title=self.name,
                        clear=True )
                    return
                
                res = self.controller.createSuoliCondParticella(
                    feature,
                    noCondVectlayers + [destVectlayer],
                    destNoCondVectlayer,
                    destVectlayer,
                    createOnlyNoCondSuoli=True )
                
                res = res or self.onRepaierSuoliParticella( destNoCondVectlayer, feature ) 
                
                if res:
                    # update layer feature count
                    lst_layers = [noCondVectlayers, destNoCondVectlayer]   
                    self.controller.updateLayersFeaturesCount( lst_layers )
                        
                    # update canvas
                    QGISAgriLayers.update_layers( lst_layers )
                    
                    # show result message
                    action.setData( QGISAgriActionData(suppress_msg=True) )    
                    logger.msgbar( 
                        logger.Level.Info, 
                        tr("Creati i suoli non in conduzione lavorati."),
                        title=self.name,
                        clear=True )
                    
            finally:
                # restart action
                action.trigger()
        
        # instance tool
        if self.__suoliCondPartTool is None:
            self.__suoliCondPartTool = SelectFeatureTool( 
                self.iface, 
                selVectlayers, 
                single=True, 
                unsetMapToolOnSelect=True )
            
        # initialize tool and add to canvas
        self.__suoliCondPartTool.initialize( selVectlayers, onSelectFeature=onSelectFeature )
        self.run_tool( 
            checked, action, 
            self.__suoliCondPartTool, 
            msg=tr( 'Taglia suoli non in conduzione su PARTICELLA non in conduzione lavorata' ) )
        
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onInstallExtBrowser(self, checked, action):
        """Install external browser for authentication""" 
        
        if os.name != 'nt':
            logger.msgbox(
                logger.Level.Warning, 
                tr("Comando disponibile solo per il sistema operativo Windows"), 
                title=tr('ERRORE'))
            return
    
        # Ask if to install
        reply = QMessageBox.question(
            self.iface.mainWindow(), 
            tr('Installazione'),
            tr("Sei sicuro di voler installare il browser esterno di autenticazione?"),
            QMessageBox.Yes, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return 
        
        try:
            from PyQt5.Qt import PYQT_VERSION_STR
            from qgis_agri import __QGIS_AGRI_VENV_NAME__
            from qgis_agri.util.python import pyUtil, PyUtilWarning
            
            logger.msgbar(
                logger.Level.Info, 
                tr('Installazione browser esterno in corso...'), 
                title=self.name, 
                clear=True)
            
            # override cursor 
            logger.setOverrideCursor(Qt.WaitCursor)
            
            # set parameters
            venv_path = os.path.join(self.envPath, __QGIS_AGRI_VENV_NAME__)
            arch_path = os.path.join(self.envPath, f"{__QGIS_AGRI_VENV_NAME__}.zip")
            module_lst = [
                #f"PyQt5=={PYQT_VERSION_STR}",
                #f"PyQtWebEngine=={PYQT_VERSION_STR}"
                "PyQtWebEngine"
            ]
                  
            # crete Python virtual envaironment
            if pyUtil.createVenv(venv_path, module_lst, arch_file=arch_path):
                # update authentication button
                self.controlbox.updateBtnAuthorization()
                
                # show success message
                logger.msgbar(
                    logger.Level.Success, 
                    tr("Browser esterno installato con successo"), 
                    title=self.name,
                    clear=True)
                logger.msgbox(
                    logger.Level.Success, 
                    tr("Browser esterno installato con successo"), 
                    title=tr('INFO'))
        
        except PyUtilWarning as ex:
            logger.msgbox(logger.Level.Warning, str(ex), title=tr('ERRORE'))
            
        except Exception as ex:
            logger.msgbox(logger.Level.Critical, str(ex), title=tr('ERRORE'))
            
        finally:
            # restore cursor
            logger.restoreOverrideCursor()
            
            
    
    