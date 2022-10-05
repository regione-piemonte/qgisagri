# -*- coding: utf-8 -*-
"""Modulo per gestione del pannello principale del plugin.

Descrizione
-----------

Implementazione della classe che gestisce il pannello principale di controllo del
plugin; il pannello consiste in una finestra agganciabile con tutti i controlli
necessari per la scelta, lo scarico, la gestione e il salvataggio di un foglio 
di lavorazione.


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
import os.path
import json
from sys import platform

from PyQt5.QtCore import Qt, QObject, QUrl, QUrlQuery, QSize, QThread
from PyQt5.QtGui import QStandardItem, QClipboard
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWidgets import (QMessageBox, 
                             QWidget, 
                             QMenu, 
                             QAction, 
                             QAbstractItemView)
##from PyQt5.QtWebKit import QWebSettings

# qgis modules import
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsApplication, QgsSettings

# plugin modules
from qgis_agri import (tr, 
                       __PLG_DEBUG__, 
                       __QGIS_AGRI_CERT_METHOD__, 
                       __QGIS_AGRI_VENV_NAME__,
                       __QGIS_AGRI_COOKIE_DOMAIN_FILTER__)

from qgis_agri import agriConfig
from qgis_agri.util.exception import formatException
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.html.generate import htmlUtil
from qgis_agri.util.dictionary import dictUtil
from qgis_agri.widgets.spinner import Spinner
from qgis_agri.model.service_sortfilterproxy_model import AgriSortFilterProxyModel
from qgis_agri.model.service_elenco_model import AgriSelectionModel, AgriElencoModel, AgriFilterHeader
from qgis_agri.service.qgis_agri_networkaccessmanager import (QGISAgriRequestError,
                                                              QGISAgriNetworkAccessManager)
from qgis_agri.qgis_agri_roles import QGISAgriRoleManager
from qgis_agri.qgis_agri_proxystyle import QGISAgriProxyStyle
from qgis_agri.qgis_agri_suspend_part_dlg import QGISAgriSuspendPartDialog
from qgis_agri.service.qgis_agri_auth_socket import QgisAgriAuthSocket

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_controller_widget.ui'))
 
 
#: Constant name of script\executable for external browser
__QGIS_AGRI_EXT_BROWSER_FILE__ = 'qgis_agri_ext_browser_script'

"""
#: Constant name of folder containing the executable
__QGIS_AGRI_EXT_BROWSER_DIR__ = 'qgis_agri_ext_browser'
"""

# QGISAgri control dialog
#-----------------------------------------------------------
class QGISAgriControllerDialog(QtWidgets.QDockWidget, FORM_CLASS):
    """Control dock widget for QGISAgri plugin"""
     
    # signals
    closingWidget = pyqtSignal()
    canDownload = pyqtSignal(bool, str)
    canUpload = pyqtSignal(bool)
    canReject = pyqtSignal(bool,str)
    serviceRequest = pyqtSignal(str, object, object, QObject, bool, bool)
    serviceOfflineRequest = pyqtSignal(str, object, object, QObject)
    downloadListaLav = pyqtSignal(QObject, dict)
    authenticated = pyqtSignal(bool,bool,bool)
    zoomToSuoloByExpression = pyqtSignal(str)
    zoomToParticellaByExpression = pyqtSignal(str)
    
    # constant members
    SERVIZIO_AGRI_PROPERTY = 'servizioAgri'
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, plugin, parent=None, title=None, freeze=False):
        """Constructor
        
        :param parent: 
        :type parent: QtWidgets
        """
        super().__init__( parent=parent )
        
        # flags
        self.__plugin = plugin
        self.__authUrl = QUrl()
        self.__offlineFoglio = False
        self.__offlineEvLavorazione = False
        self.__enabled = False
        self.__freezed = freeze
        self.__downloaded = False
        self.__currentFoglioData = None
        self.__selectedFoglioData = None
        self.__selectedEvLavRow = None
        self.__totFogliToWork = 0 
        # service selected data
        self.__serviceStoreModel = {}
        self.__serviceGenData = {
            'cuaa': '',
            'escludiLavorate': 'S',
            'escludiBloccate': 'S',
            'escludiSospese': 'S'
        }
        # initialize pages
        self.__pagecfg = {}
        #
        self.__spinner = None
        self.__authError = None
        
        # create role selection object
        self.__roleManager = QGISAgriRoleManager( parent=self )
        self.__roleManager.selectedRole.connect( self._setAuthenticatedRole )
        
        # create an authorization socket for external browser
        self.__authSocket = QgisAgriAuthSocket(self)
        self.__authSocket.authenticated.connect(self.loadAuthPage)
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
#         curFont = self.font()
#         curFont.setBold( True )
#         self.setFont( curFont )
        
        # toolbar
        self.cmdToolbar.setStyle( QGISAgriProxyStyle( self, self.cmdToolbar.iconSize() ) )
        #self.cmdToolbar.setMinimumHeight(64)
        #self.cmdToolbar.setIconSize(QSize(50,50))
        
        # buttons
        self.btnBack.setText( '' )
        self.btnForward.setText( '' )
        self.btnReload.setText( '' )
        self.btnSuoloZoom.setText( '' )
        self.btnParticellaZoom.setText( '' )
        self.btnSuoloFinder.setText( '' )
        self.btnRemoveFilter.setText( '' )
        self.btnBack.setEnabled( False )
        self.btnForward.setEnabled( False )
        self.btnSuoloZoom.setEnabled( False )
        self.btnParticellaZoom.setEnabled( False )
        self.btnParticellaSosp.setEnabled( False )
        self.btnParticellaSosp.setVisible( False )
        
        self.btnBack.clicked.connect( self.onServiceBack )
        self.btnForward.clicked.connect( self.onServiceForward )
        self.btnReload.clicked.connect( self.onServiceReload )
        self.btnSuoloZoom.clicked.connect( self.onZoomSuolo )
        self.btnParticellaZoom.clicked.connect( self.onZoomParticella )
        self.btnParticellaSosp.clicked.connect( self.onSuspendParticella )
        self.btnRemoveFilter.clicked.connect( self.onRemoveSuoliFilter )
        
        # filter combo
        self.cmbAnnoInit = False
        self.cmbAnno.setEnabled( False )
        self.cmbLista.setEnabled( False )
        self.edtCuaa.setEnabled( False )
        
        self.cmbAnno.currentIndexChanged.connect( self.onAnnoFilterSelectionchange )
        self.cmbLista.currentIndexChanged.connect( self.onListaFilterSelectionchange )
        self.edtCuaa.editingFinished.connect( self.onCuaaEditingFinished )
        self.edtCuaa.textChanged.connect( self.onCuaaTextChanged )
        
        # filter on 'evnto lavorazione' state
        self.filterUpdating = False
        self.chkLavorate.stateChanged.connect( lambda state, self=self: self.onFiltroStatoLavorazioneChange( state, 'escludiLavorate' ) )
        self.chkBloccate.stateChanged.connect( lambda state, self=self: self.onFiltroStatoLavorazioneChange( state, 'escludiBloccate' ) )
        self.chkSospese.stateChanged.connect( lambda state, self=self: self.onFiltroStatoLavorazioneChange( state, 'escludiSospese' ) )
        
        self.chkLavorateAz.stateChanged.connect( lambda state, self=self: self.onFiltroStatoLavorazioneChange( state, 'escludiLavorate', reloadService=True ) )
        self.chkBloccateAz.stateChanged.connect( lambda state, self=self: self.onFiltroStatoLavorazioneChange( state, 'escludiBloccate', reloadService=True ) )
        self.chkSospeseAz.stateChanged.connect( lambda state, self=self: self.onFiltroStatoLavorazioneChange( state, 'escludiSospese', reloadService=True ) )

        # grid signals
        self.grid_ListaLavorazione.customContextMenuRequested.connect( self.onCustomContextMenuRequested )
        self.grid_ElencoAziende.customContextMenuRequested.connect( self.onCustomContextMenuRequested )
        self.grid_ElencoFogliAzienda.customContextMenuRequested.connect( self.onCustomContextMenuRequested )
        self.grid_ElencoFogliScaricati.customContextMenuRequested.connect( self.onCustomContextMenuRequested )
        self.grid_SuoliInLavorazione.customContextMenuRequested.connect( self.onCustomContextMenuRequested )
        self.grid_ElencoLavorazioniParticelle.customContextMenuRequested.connect( self.onCustomContextMenuRequested )
        
        self.grid_ElencoLavorazioniParticelle.doubleClicked.connect( self.onLavParticelleDoubleClicked )
        
        # initialize pages
        self._initPageFilters( agriConfig.services.listaLavorazione.name, 'tipoLista' )
        self._initPageFiltersByWidget( self.cmbAnno, 'anno' )
        self._initPageFiltersByWidget( self.cmbLista, 'lista' )
        self._initPageFiltersByWidget( self.edtCuaa, 'cuaa' )
          
        # connect current page changed signal
        self.serviziPagine.currentChanged.connect( self.onServicePageChanged )
        self.ListaLavorazioneScaricata.currentChanged.connect( self.onScaricoPageChanged )
        
        # set tab appearance
        ##self.tabWidget.removeTab ( self.tabWidget.indexOf( self.Particelle ) )
        """
        particelle_tab_index = self.tabWidget.indexOf( self.Particelle )
        self.tabWidget.setTabEnabled( particelle_tab_index, False )
        self.tabWidget.setStyleSheet( "QTabBar::tab::disabled {width: 1; height: 0; margin: 0; padding: 0; border: none;} " )
        """
        self.Suoli.setEnabled( False )
        self.tabWidget.currentChanged.connect( self.onTabChanged )
        
        # configure NetworkAccessManager
        nam = self.__plugin.networkAccessManager
        nam.clearCookies(__QGIS_AGRI_COOKIE_DOMAIN_FILTER__)
        
        # authentication tab
        try:
            # get authentication url page
            cfg = nam.getConfigService( 'Autenticazione' )
            self.__authUrl = QUrl( cfg.get( 'path', '' ) )
            
            # add url params
            plugin_version = self.__plugin.version
            if plugin_version:
                params = cfg.get( 'params', {} )
                dictUtil.substituteVariables( 
                    params, { "versionePlugin": self.__plugin.version } 
                )
                paramStr = nam.paramizeQuery( params )
                if paramStr:
                    self.__authUrl.setQuery( paramStr )
            
            # save url   
            self.__authOrigUrl = self.__authUrl
            
            # manage url redirection
            redirectUrl = cfg.get( 'redirectPath', None )
            if redirectUrl:
                # get url redirection
                self.__authUrl = QUrl( redirectUrl )
                # add params
                if plugin_version: 
                    param_key = cfg.get( 'redirectParam', 'target' )
                    url_query = QUrlQuery( self.__authUrl.query() )
                    url_param = url_query.queryItemValue( param_key )
                    if url_param:
                        url = QUrl( url_param )
                        url.setQuery( paramStr )
                        url_query.removeAllQueryItems( param_key )
                        url_query.addQueryItem( param_key, url.toString() )
                        self.__authUrl.setQuery( url_query )
            
        except Exception:
            pass
         
        # hide notification frame 
        self.titleFrame.setVisible( False )
        
        # set labels selectable
        labels = self.findChildren( QtWidgets.QLabel )
        for label in labels:
            label.setTextInteractionFlags( Qt.TextSelectableByMouse )
        
        # 'evento lavorazione' state             
        self.chkLavorate.setChecked( False )
        self.chkBloccate.setChecked( False )
        self.chkSospese.setChecked( False )
        
        # get real application DPI 
        window = QgsApplication.desktop().screen()
        horizontalDpi = window.logicalDpiX()
        
        # set webView
        webView = self.webView
        webView.setContextMenuPolicy( Qt.CustomContextMenu )
        webView.setZoomFactor( horizontalDpi / 96.0 )
        webPage = webView.page()
        webPage.setNetworkAccessManager( nam.networkAccessManager )
        ####self.webView.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        webView.loadStarted.connect( self.onWebLoadStarted )
        webView.loadFinished.connect( self.onWebLoadFinished )
        webPage.networkAccessManager().finished.connect( self.onFinishedAuthRequest ) 
        # get the main frame of the view so that we can load the api each time
        # the window object is cleared
        webPage.mainFrame().javaScriptWindowObjectCleared.connect( self._loadJsPyApi )
        
        templateFile = 'disabled.html' if self.__freezed else 'authentication.html'
        template = htmlUtil.generateTemplate( templateFile )
        webView.setHtml( template.render() )
        
        # set winwow title
        if title:
            self.setWindowTitle(title)
            
        # set authentication button
        self.updateBtnAuthorization()
        
        # load login page
        if self.__freezed:
            self.btnAuthentication.setDisabled(True)
        else:
            self.loadAuthPage()
    
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __del__(self):
        """Destructor"""
        self.release()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def release(self):
        """Destructor"""
        try:
            self.webView.page().networkAccessManager().finished.disconnect( self.onFinishedAuthRequest )
        except:
            pass
        # restore cursor
        logger.restoreOverrideCursor()
        # destroy spinner
        if self.__spinner is not None:
            self.__spinner.close()
        self.__spinner = None
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def updateBtnAuthorization(self):
        """Authentication button setting"""
        
        # init
        if os.name == 'nt':
            venv_path = os.path.join(self.__plugin.envPath, __QGIS_AGRI_VENV_NAME__)
            use_ext_browser = os.path.isdir(venv_path)
            """
            venv_path = os.path.join(
                self.__plugin.envPath, __QGIS_AGRI_EXT_BROWSER_DIR__, f"{__QGIS_AGRI_EXT_BROWSER_FILE__}.exe"
            )
            use_ext_browser = os.path.exists(venv_path)
            """
        else:
            use_ext_browser = True
        
        # create button menu
        authMenu = QMenu(self.btnAuthentication)
        self.__authAction = authMenu.addAction(tr("Autenticazione standard"))
        self.__authAction.triggered.connect(self.reauthenticate)
        
        if use_ext_browser:
            self.__authExtAction = authMenu.addAction(tr("Autenticazione browser esterno"))
            self.__authExtAction.triggered.connect(self.reauthenticateExtBrowser)
            
            s = QgsSettings()
            value = s.value( f"{self.__plugin.PLUGIN_NAME}/plg_auth_mode", 'standard' )
            if (value == 'standard'):
                authMenu.setDefaultAction(self.__authAction)
                self.btnAuthentication.setDefaultAction(self.__authAction)
            else:
                authMenu.setDefaultAction(self.__authExtAction)
                self.btnAuthentication.setDefaultAction(self.__authExtAction)
 
        else:
            self.__authExtAction = None
            authMenu.setDefaultAction(self.__authAction)
            self.btnAuthentication.setDefaultAction(self.__authAction)
        
        self.btnAuthentication.triggered.connect(self.btnAuthentication.setDefaultAction)
        self.btnAuthentication.setMenu(authMenu)
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def authUrl(self):
        """Returns authorization url method"""
        return self.__authUrl
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def isOfflineFoglio(self):
        """ Returns true if offline foglio"""
        return self.__offlineFoglio
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def selectedEventoLavorazioneData(self):
        """ Returns selected 'Evento lavorazione' data"""
        return self.__selectedEvLavRow
        
    # --------------------------------------
    # 
    # --------------------------------------  
    @property
    def currentFoglioData(self):
        """ Returns current foglio data"""
        return self.__currentFoglioData
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def selectedFoglioData(self):
        """ Returns foglio data to load in QGIS"""
        return self.__selectedFoglioData
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def currentFoglioFilterData(self):
        """ Returns current foglio filter data"""
        return self.getFoglioData( self.__currentFoglioData )
        
#     # --------------------------------------
#     # 
#     # -------------------------------------- 
#     @property
#     def selectedFoglioFilterData(self):
#         """ Returns foglio filter data to load in QGIS"""
#         return self.getFoglioData( self.__selectedFoglioData )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def isNewSelectedFoglioData(self):
        """ Returns foglio data to load in QGIS"""
        return self.__currentFoglioData != self.__selectedFoglioData
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def totFogliToWork(self):
        """ Returns total number of fogli to work"""
        return self.__totFogliToWork
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def authenticationRole(self):
        """ Returns selected authentication role """
        return self.__roleManager.getSelectedRole()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def serviceStoreModel(self):
        """ Returns service store model dictionry"""
        return self.__serviceStoreModel
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _loadJsPyApi(self):
        """Add pyapi to javascript window object"""
        frame = self.webView.page().mainFrame()
        frame.addToJavaScriptWindowObject( 'pyroleapi', self.__roleManager )
        
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _getServicePage(self, stackedWidget, serviceName):
        # check if current page is requested service
        stackedWidget = stackedWidget or self.serviziPagine
        page = stackedWidget.currentWidget()
        if page is not None and page.property(self.SERVIZIO_AGRI_PROPERTY) == serviceName:
            return page
        # find page for requested service
        pages = (stackedWidget.widget(i) for i in range(stackedWidget.count()))
        for page in pages:
            if page.property( self.SERVIZIO_AGRI_PROPERTY ) == serviceName:
                return page
        return None
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _getServiceName(self, stackedWidget, page=None):
        # check if valid page
        stackedWidget = stackedWidget or self.serviziPagine
        page = stackedWidget.currentWidget() if page is None else page
        serviceName = page.property( self.SERVIZIO_AGRI_PROPERTY )
        return serviceName
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _getServiceTable(self, stackedWidget, page=None):
        # check if valid page
        stackedWidget = stackedWidget or self.serviziPagine
        page = stackedWidget.currentWidget() if page is None else page
        serviceName = self._getServiceName( stackedWidget, page )
        if serviceName is None:
            return None
        # get service table grid
        tabViewLst = page.findChildren( QtWidgets.QTableView )
        for tabView in tabViewLst:
            if tabView.property( self.SERVIZIO_AGRI_PROPERTY ) == serviceName:
                return tabView
            
        return None
        
    # --------------------------------------
    # 
    # --------------------------------------   
    def _clearTables(self, startIndex=0):
        """Clear grid tables"""
        for pages in [self.serviziPagine, self.serviziPagineParticelle]:
            for index in range(startIndex, pages.count()):
                page = pages.widget( index )
                grid = self._getServiceTable( self.serviziPagine, page )
                if grid is None:
                    continue
                
                filterModel = grid.model()
                if filterModel is None:
                    continue
                
                filterModel.sourceModel().clear() 
                
                # remove relative service store data model
                serviceName = page.property( self.SERVIZIO_AGRI_PROPERTY )
                self._removeServiceStoreModel( serviceName )
       
            
    # --------------------------------------
    # 
    # --------------------------------------       
    def _populateFilterCombo(self, combo, dictValues):
        """Private method to populate a filter combo"""
        combo.setEnabled(True)
        combo.clear()
        
        cmbModel = combo.model()
        item = QStandardItem()
        item.setData( tr('') , Qt.DisplayRole )
        item.setData( None, Qt.UserRole )
        cmbModel.appendRow( item )
            
        for tup in sorted(dictValues.items()):
            item = QStandardItem()
            item.setData( tup[1], Qt.DisplayRole )
            item.setData( tup[0], Qt.UserRole )
            cmbModel.appendRow( item )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def _initPageFilters(self, serviceName, filterName):
        """Initializes page filter config"""
        
        # init page config dictionary
        serviceCfg = self.__pagecfg.get( serviceName, None )
        if serviceCfg is None:
            serviceCfg = self.__pagecfg[serviceName] = {}
        
        # init grid filters config dictionary    
        filters = serviceCfg.get( 'gridfilters', None )
        if filters is None:
            filters = serviceCfg['gridfilters'] = {}
            
        # init single grid filter config  
        filterCfg = filters.get( filterName, None )
        if filterCfg is None:
            filterCfg = filters[filterName] = {}
            # set field name for value and display
            service_cfg = agriConfig.get_value('agri_service', {})
            resources_cfg = service_cfg.get('resources', {})
            res_cfg = resources_cfg.get(serviceName, {})
            filters_cfg = res_cfg.get('gridFilters', {})
            filterCfg['filterFn'] = None
            filterCfg['field'] = fieldCfg = filters_cfg.get( filterName,  { 'valueField': '', 'displayField': None } )
            if fieldCfg.get('displayField', None) is None:
                fieldCfg['displayField'] = fieldCfg['valueField']
                
            # create filter on field fixed value
            fix_val_cfg = fieldCfg.get( 'fixValue', None )
            if fix_val_cfg is not None:
                fldName = fieldCfg['valueField']
                filterCfg['filterFn'] = lambda r, s: fix_val_cfg == r[fldName]
        
        return filterCfg
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _initPageFiltersByWidget(self, widget, filterName):
        """Initializes page filter config"""
        
        # init page config dictionary
        serviceName = widget.property(self.SERVIZIO_AGRI_PROPERTY) 
        return self._initPageFilters( serviceName, filterName )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _getServiceGridData(self, grid):
        # get service table grid
        if grid is None:
            return None
        
        filterModel = grid.model()
        tableModel = filterModel.sourceModel()
        return tableModel.rows()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _selectedServiceGridData(self, grid):
        # get service table grid
        if grid is None:
            return None
        
        # service data from selected row
        selection = grid.selectionModel()
        if selection is None:
            return None
        
        indexes = selection.selectedRows()
        if not indexes:
            return None
        
        filterModel = grid.model()
        index = filterModel.mapToSource( indexes[0] )
        dataRow = filterModel.sourceModel().dataRow( index )
        return dataRow
    
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _setGridData(self, serviceName, grid, data):
        """Set table/grid data model"""
        
        # set model data
        tableModel = AgriElencoModel(data)
        filterModel = AgriSortFilterProxyModel(self)
        filterModel.setSourceModel( tableModel )
        #filterModel.setSortRole( Qt.InitialSortOrderRole )   
        grid.setModel( filterModel )
        
        #self.disconnect( grid.selectionModel().selectionChanged )
        grid.selectionModel().selectionChanged.connect( 
            lambda: self.onServiceSelectionChanged( grid ) )
        
        if grid == self.grid_ElencoLavorazioniParticelle:
            grid.selectionModel().selectionChanged.connect( self.onTableViewSelectParticella )
            self.onTableViewSelectParticella()
        
        # set header view (with filters)
        header = AgriFilterHeader( grid )
        header.setSectionsClickable( True )
        header.setHighlightSections( True )
        header.setSectionsMovable( True )
        header.setStretchLastSection( True )
        header.setSortIndicator( -1,  Qt.AscendingOrder )
        header.setSectionResizeMode( QtWidgets.QHeaderView.Interactive )
        header.setDefaultAlignment( Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextWordWrap )
        grid.setHorizontalHeader( header )
        
        # configure columns
        columns_cfg = agriConfig.get_value( f"agri_service/resources/{serviceName}/gridColumns", {} )
        header.configureColumns( columns_cfg )
        
        # apply header view
        header.setVisible( True )
        header.setFilterBoxes( )
        header.filterActivated.connect( self.handleFilterActivated )
        
        # grid sorting type
        #grid.sortByColumn( 0, Qt.AscendingOrder )
        
    def _isServiceLocked(self, serviceName, dataRow):
        """Private method to check if locked service"""
        try:
            service_cfg = agriConfig.get_value( 'agri_service/resources/{0}'.format( serviceName ) , {} )
            lock_fld_cfg = service_cfg.get( 'lockFieldExpression', {} )
            for fld, expr in lock_fld_cfg.items():
                value = expr.get( 'value', None )
                if value == dataRow.get( fld, None ):
                    return True
        except:
            return True
            
        return False
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _isRejectable(self, serviceName, dataRow):
        """Private method to check if rejectable 'Evento Lavorazione'"""
        try:
            # init
            dataRow = dataRow or {}
            if serviceName != agriConfig.SERVICES.Aziende.name:
                return False
            
            # check if service locked by current user (role)
            curRole = self.__roleManager.currentRole
            if curRole is None:
                return False
            
            # check if current role has functionality to reject event
            if curRole.isfunctionalityEnabled( agriConfig.FUNCTIONALITIES.rejectListaLav, defaultEnabled=False ):
                return True
            
            """
            # if same role, can reject
            service_cfg = agriConfig.get_value( 'agri_service/resources/{0}'.format( serviceName ) , {} )
            idUtente_fld_cfg = service_cfg.get( 'idUtenteBloccoField', '' )
            if not idUtente_fld_cfg:
                return False
            if curRole.id == dataRow.get( idUtente_fld_cfg, '' ):
                return True
            """
            return False
            
        except:
            return False
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _setAuthenticatedRole(self, role=None):
        """Private method to set plugin authentication"""
        
        """
        lst = []
        cs = self.webView.page().networkAccessManager().cookieJar()
        for c in cs.allCookies():
            lst.append("{}={}".format( c.name().data().decode('utf8'), 
                                       c.value().data().decode('utf8') ))
        s = ";".join( lst )
        with open("D:/Output.txt", "w") as text_file:
            text_file.write(s)
        """
        
        # store role code as genneral data (for ulr request parameters)
        self.__serviceGenData["codiceRuolo"] = "" if not role else role.codice
        
        # load QGIS font settings
        s = QgsSettings()
        fontFamily = s.value("qgis/stylesheet/fontFamily", "Arial")
        fontPointSize = s.value("qgis/stylesheet/fontPointSize", 12)
        
        # set authentication page content
        template = htmlUtil.generateTemplate( 'authenticated.html' )
        self.webView.setHtml( template.render(
            font_family = fontFamily,
            font_point_size = fontPointSize,
            img = htmlUtil.imgToBase64( ':/plugins/qgis_agri/images/authenticated.png' ),
            cf = "" if not role else role.cod_fiscale,
            ruolo = "" if not role else role.descrizione
        ) )
        
        # emit authentication signal
        self.authenticated.emit( True, True, False )  
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _getServiceStoreModel(self, serviceName):
        """ Returns a service store model """
        return self.__serviceStoreModel.get( serviceName, None )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _createServiceStoreModel(self, serviceName: str):
        """ Creates and returns a service store model """
        model = self.__serviceStoreModel.get( serviceName, None )
        if model is None:
            self.__serviceStoreModel[serviceName] = model = AgriSelectionModel()
        return model
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _removeServiceStoreModel(self, serviceName: str):
        """ Removes a service store model """
        try:
            del self.__serviceStoreModel[ serviceName ]
        except:
            pass
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _loadServiceStoreModel(self, serviceData: dict):
        """ Load service store models """
        if not dict:
            return 
        
        # 'anno campagna' filter
        annoFilterCfg = self._initPageFiltersByWidget( self.cmbAnno, 'anno' )
        annoFilterFieldCfg = annoFilterCfg.get('field', {})
        annoFilterField = annoFilterFieldCfg.get( 'valueField', '' )
        annoFilterValue = ''
         
        # set service selected data
        for serviceName, data in serviceData.items():
            rows = list(data.get( 'rows', [] ))
            refData = data.get( 'refData', {} )
            if rows:
                storeModel = self._createServiceStoreModel( serviceName )
                storeModel.setRows( rows )
                storeModel.setRefData( refData )
            # get 'anno campagna'
            if not annoFilterValue:
                annoFilterValue = refData.get( annoFilterField, '' )
                
        # set filter widget
        if annoFilterValue:
            index = self.cmbAnno.findText( annoFilterValue )
            if index != -1:
                self.cmbAnno.setCurrentIndex( index )
            
    # --------------------------------------
    # 
    # --------------------------------------     
    def _copyGridRowToClipboard(self, grid, rowNum):
        """ Copy row data to clipboard """
        
        # retrieve row data
        filterModel = grid.model()
        index = filterModel.mapToSource( filterModel.index( rowNum, 0 ) )
        rowData = filterModel.sourceModel().dataRow( index )
        jsonRowData = json.dumps( rowData )
        
        # copy to clipboard
        clipboard = QgsApplication.clipboard()
        clipboard.setText( str(jsonRowData), QClipboard.Clipboard )
        if clipboard.supportsSelection():
            clipboard.setText( str(jsonRowData), QClipboard.Selection )
        if platform == "linux" or platform == "linux2":
            QThread.msleep(1) # workaround for os Linux
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _exportGridAsCsv(self, grid):
        """ Export service grid data to CSV file """
        
        # init
        serviceName = grid.property( self.SERVIZIO_AGRI_PROPERTY )
        if serviceName is None:
            serviceName = 'ServizioAgri'
            
        csvFile = "{0}.csv".format( serviceName )
        
        # select file name, path
        from PyQt5.QtWidgets import QFileDialog
        path, filter_doc = QFileDialog.getSaveFileName( self, tr( 'Esporta come file CSV' ), csvFile, 'CSV(*.csv)' )
        if not path:
            return
        
        filterModel = grid.model()
        sourceModel = filterModel.sourceModel()
        rowCount = filterModel.rowCount()

        import csv
        with open( str(path), 'w', newline='\n', encoding='utf-8' ) as stream:
            writer = csv.writer( stream, delimiter=';', lineterminator='\n' )
            if rowCount:
                # write fields
                index = filterModel.mapToSource( filterModel.index( 0, 0 ) )
                row = sourceModel.dataRow( index )
                rowdata = list(map( lambda x: '' if x is None else str(x), row.keys() ))
                writer.writerow( rowdata )
                    
                # write data
                for rowNum in range( rowCount ):
                    index = filterModel.mapToSource( filterModel.index( rowNum, 0 ) )
                    row = sourceModel.dataRow( index )
                    rowdata = list(map( lambda x: '' if x is None else str(x), row.values() ))
                    writer.writerow( rowdata )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onCustomContextMenuRequested(self, pos):
        """ Grid custom menu request slot """
        # init
        if pos is None:
            return
        
        grid = self.sender()
        filterModel = grid.model()
        rowNum = grid.rowAt( pos.y() )
        if rowNum < 0:
            return
        
        # create a popup menu
        menu = QMenu( grid )
        
        # add copy to clipboard action
        action = QAction( tr( 'Copia riga negli appunti' ), grid )
        action.triggered.connect( lambda: self._copyGridRowToClipboard( grid, rowNum ) )
        menu.addAction( action )
        
        # add export action
        export_cfg = agriConfig.get_value( 'context/controlbox/exportGrid', False )
        if export_cfg and filterModel.rowCount():
            menu.addSeparator()
            
            action = QAction( tr( 'Esporta tabella in file CSV' ), grid )
            action.triggered.connect( lambda: self._exportGridAsCsv( grid ) )
            menu.addAction( action )
            
        # add suspend PARTICELLA work item action
        if grid == self.grid_ElencoLavorazioniParticelle and\
           self.btnParticellaSosp.isVisible() and\
           self.btnParticellaSosp.isEnabled():
            # add action
            menu.addSeparator()
            action = QAction( self.btnParticellaSosp.text(), grid )
            action.triggered.connect( self.onSuspendParticella )
            menu.addAction( action )
        
        # show popup menu
        menuPos = grid.viewport().mapToGlobal( pos )
        menu.popup( menuPos )    
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onFinishedAuthRequest(self, reply):
        """finished request slot"""
        # check if method authenticated
        statusCode = reply.attribute( QNetworkRequest.HttpStatusCodeAttribute )
        if reply.error() or statusCode != 200:
            self.__authError = { 
                "code": statusCode, 
                "message": reply.errorString() 
            }
            
    # --------------------------------------
    # 
    # --------------------------------------          
    def onWebLoadStarted(self):
        """Web load started slot"""
        
        # destroy spinner
        self.destroySpinner()
        
        if self.isVisible():
            # show spinner
            spinner = self.createSpinner()
            spinner.show()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onWebLoadFinished(self, ok):
        try:
            # destroy spinner
            self.destroySpinner()
                
            # Check if method authenticated
            current_url = self.webView.url().toString()
            if self.__authOrigUrl.toString() in current_url:
                
                if __PLG_DEBUG__:
                    logger.log( logger.Level.Info, "Autenticazione url: {0}".format( self.__authUrl.toString() ) )
                
                try:
                    # check if json result
                    res = json.loads( self.webView.page().mainFrame().toPlainText() )
                except ValueError as e:
                    #raise Exception( tr( 'Errore servizio Agri' ) )
                    return
                
                # check if DTO error from server
                err = res.get( 'esitoDTO', {} )
                errCode = err.get( 'esito', 0 )
                if errCode != 0:
                    msg = err.get( 'messaggio', tr( 'Errore servizio Agri' ) )
                    raise Exception( "'{0}'\n{1}".format( tr( 'Autenticazione' ), msg ) )
                
                # get roles data
                roles = res.get( 'dati', [] )
                self.__roleManager.setRoles( roles )
                if self.__roleManager.count() < 2:
                    # set plugin as authenticated immediately
                    self.__roleManager.set_selected_role( None )
                    return
                
                # load QGIS font settings
                s = QgsSettings()
                fontFamily = s.value("qgis/stylesheet/fontFamily", "Arial")
                fontPointSize = s.value("qgis/stylesheet/fontPointSize", 12)
                
                # load web page for role selection
                template = htmlUtil.generateTemplate( 'roles.html' )
                self.webView.setHtml( template.render(
                    font_family = fontFamily,
                    font_point_size = fontPointSize, 
                    roles = roles
                ) )
                    
            else:
                self.webView.page().mainFrame().evaluateJavaScript('var a=document.querySelectorAll(\"input[type=\'password\']\");if (a.length > 0 && !!a[0].form) a[0].form.parentElement.scrollIntoView();')
        
        except Exception as e:
            # handle exception
            logger.msgbox(logger.Level.Critical, formatException(e), title=tr('ERRORE'))
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onTabChanged(self, index):
        """Tab changed"""
        tab = self.tabWidget.currentWidget()
        if not tab:
            self.canDownload.emit( False, '' )
            #self.canReject.emit( False, '' )
            
        elif tab == self.Suoli:
            if self.__offlineFoglio:
                self.onScaricoPageChanged()
            else:
                self.onServicePageChanged()
                
        elif tab == self.Particelle:
            if self.__offlineFoglio:
                self.canDownload.emit( True, 'download'  )
            else:
                self.canDownload.emit( False, '' )
            
        elif self.__enabled:    
            self.canDownload.emit( False, '' )
            #self.canReject.emit( False, '' )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onServicePageChanged(self):
        """Page/service changed."""
        grid = self._getServiceTable( self.serviziPagine )
        self.onServiceSelectionChanged( grid )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onScaricoPageChanged(self):
        """Page/service changed."""
        grid = self._getServiceTable( self.ListaLavorazioneScaricata )
        self.onServiceSelectionChanged( grid )
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onServiceSelectionChanged(self, gridTable):
        """Check service table selection changing"""
        # init
        self.__selectedEvLavRow = None
        
        # check if offline db
        if self.__offlineFoglio:
            # set widgets
            curIdx = self.ListaLavorazioneScaricata.currentIndex()
            numPag = self.ListaLavorazioneScaricata.count() -1
            self.btnBack.setEnabled( curIdx > 0 )
            self.btnForward.setEnabled( curIdx < numPag )
            if not gridTable:
                return 
            
            # settings on grid selection
            pageService = self._getServiceName( self.ListaLavorazioneScaricata )
            gridService = gridTable.property( self.SERVIZIO_AGRI_PROPERTY )
            isFogliPage = ( gridService == agriConfig.services.fogliAziendaOffline.name )
            
            self.lblFoglioRp.setVisible( isFogliPage )
            self.lblFoglioValueRp.setVisible( isFogliPage )
            
            dataRow = self._selectedServiceGridData( gridTable )
            
            if isFogliPage:
                # get selected foglio data
                self.__selectedFoglioData = dataRow #self.__selectedFoglioData = self.__currentFoglioData = dataRow
                self.updateWidgets( agriConfig.services.fogliAziendaOffline.name )
                # emit signal ready to downloas
                self.canDownload.emit( True, 'download' )
                
            elif gridService == pageService:
                # only if grid on current page
                self.canDownload.emit( False, ''  )
             
            # if grid of 'suoli foglio offline', enable zoom button   
            if gridTable == self.grid_SuoliInLavorazione:
                self.btnSuoloZoom.setEnabled( self.__downloaded and dataRow is not None )
                
            # exit
            return
        
        
        # get page indexes
        curIdx = self.serviziPagine.currentIndex()
        lastIdx = self.serviziPagine.indexOf( self.ElencoFogliAzienda )
        offIdx = self.serviziPagine.indexOf( self.OfflinePage )
        # return if offline page
        if curIdx == offIdx:
            return
         
        # enable / disable navigation buttons
        btnBackEnabled = ( curIdx != 0 )
        btnForwardEnabled = False
                
        # check if select row can access next service
        canReject = False
        lockedService = False
        serviceName = self._getServiceName( self.serviziPagine )
        dataRow = self._selectedServiceGridData( gridTable )
        if dataRow is not None:
            lockedService = self._isServiceLocked( serviceName, dataRow )
            btnForwardEnabled = curIdx < lastIdx and not lockedService
            # check if rejectable
            if lockedService and self._isRejectable( serviceName, dataRow ):
                self.__selectedEvLavRow = dataRow
                canReject = True
            
        # disable navigation buttons if db offline but no foglio choosen
        if self.__offlineEvLavorazione and not self.__offlineFoglio:
            btnBackEnabled = btnForwardEnabled = False
        
        # enable / disable navigation buttons
        self.btnBack.setEnabled( btnBackEnabled )
        self.btnForward.setEnabled( btnForwardEnabled )
   
   
        # get selected foglio data
        dataRow = self._selectedServiceGridData( gridTable )
        self.__selectedFoglioData = dataRow
   
        
        # emit signal can download
        if self.tabWidget.currentWidget() != self.Suoli:
            self.canDownload.emit( False, ''  )
        elif curIdx == 0:
            self.canDownload.emit( True, 'search' )
        elif curIdx == lastIdx and dataRow is not None and not lockedService:
            self.canDownload.emit( True, 'download'  )
        else:
            self.canDownload.emit( False, ''  )
            
        # emit signal can reject
        self.canReject.emit( canReject, serviceName )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRemoveSuoliFilter(self):
        """ Remove column filters on suoli grid """
        grid = self.grid_SuoliInLavorazione
        h = grid.horizontalHeader()
        h.clearFilters()
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onTableViewSelectParticella(self):
        """ Selected particella slot """
        
        # init
        enable = False
        suspended = False
        hasGeometry = False
        cfg = agriConfig.services.ParticelleLavorazioni
        
        # get selected row
        grid = self.grid_ElencoLavorazioniParticelle
        selection = grid.selectionModel()
        if selection is not None:
            indexes = selection.selectedRows()
            if indexes:
                enable = True
                
                # check if suspended item
                index = indexes[0]
                filterModel = grid.model()
                tableModel = filterModel.sourceModel()
                data = tableModel.row( index.row() ) or {}
                suspended = ( data.get( cfg.flagSospensioneField, '' ) 
                              == 
                              cfg.flagFieldTrueValue )
                hasGeometry = data.get( cfg.hasGeometryField, 0 ) 
        
        # enable\disable buttons
        self.btnParticellaZoom.setEnabled( enable )
        self.btnParticellaSosp.setEnabled( enable )
        self.btnParticellaSosp.setVisible( enable and not hasGeometry )
 
        # update buttons
        if suspended:
            self.btnParticellaSosp.setText( tr("Riprendi lavorazione") )
        else:
            self.btnParticellaSosp.setText( tr("Sospendi lavorazione") )
 
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onZoomParticella(self):
        """ Zoom to selected particella """
        
        # get selected row
        grid = self.grid_ElencoLavorazioniParticelle
        selection = grid.selectionModel()
        if selection is None:
            return None
        
        indexes = selection.selectedRows()
        if not indexes:
            return None
        
        return self.onLavParticelleDoubleClicked( indexes[0] )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onSuspendParticella(self):
        """ Show suspend particella item dialog """
        
        # get selected row
        grid = self.grid_ElencoLavorazioniParticelle
        selection = grid.selectionModel()
        if selection is None:
            return None
        
        indexes = selection.selectedRows()
        if not indexes:
            return None
        
        index = indexes[0]
       
        # get item from index
        filterModel = self.grid_ElencoLavorazioniParticelle.model()
        index = filterModel.mapToSource( index )
        dataRow = filterModel.sourceModel().dataRow( index )
        
        # show dialog
        dlg = QGISAgriSuspendPartDialog( self.__plugin, dataRow, parent=self )
        dlg.setModal( True )
        dlg.show()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onZoomSuolo(self):
        """ Zoom to selected suolo (offline grid) """
         
        # get selected row
        grid = self.grid_SuoliInLavorazione
        selection = grid.selectionModel()
        if selection is None:
            return None
        
        indexes = selection.selectedRows()
        if not indexes:
            return None
        
        # get data row
        filterModel = grid.model()
        index = filterModel.mapToSource( indexes[0] )
        dataRow = filterModel.sourceModel().dataRow( index )
        
        # get featureId
        featureIdField = agriConfig.services.suoliLavorazioneOffline.featureIdField
        featureId = dataRow.get( featureIdField, None )
        if featureId is None:
            return 
        
        # create filter expression
        expr = "{0}={1}".format( featureIdField, featureId )
        
        featureIdFieldPadre = agriConfig.services.suoliLavorazioneOffline.featureIdFieldPadre
        expr2 = " or array_find( string_to_array( regexp_substr({0}, '[0-9 ,]+' ) ), {1} ) != -1".format( featureIdFieldPadre, featureId )
        expr += expr2 
        
        # emit signal for zoom
        self.zoomToSuoloByExpression.emit( expr )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onServiceReload(self, step=0):
        """Prepares loading of an Agri service: current, next or previous"""
        # init
        if step > 1:
            return
    
        # check if offline db
        if self.__offlineFoglio:
            pages = self.ListaLavorazioneScaricata
            index = pages.currentIndex() + step
            pages.setCurrentIndex( index )
            return
    
        # prepare service page
        pages = self.serviziPagine
        if step > 0:
            self.onServiziDownload()
        else:
            index = pages.currentIndex() + step
            prevPage = pages.widget( index )
            ##self._clearTables( index  )
            ##pages.setCurrentIndex( index + step )
            self.onServiziDownload( reloadServicePage=prevPage )
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onServiceBack(self):
        self.onServiceReload( step=-1 )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onServiceForward(self):
        """Go to Agri parent service."""
        self.onServiceReload( step=+1 )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onServiziDownload(self, reloadServicePage=None):
        """Load selected service data"""
        
        # get service table grid
        grid = self._getServiceTable( self.serviziPagine, reloadServicePage )
        if grid is None:
            return 
        
        serviceName = self._getServiceName( self.serviziPagine, reloadServicePage )
        
                        
        # default params
        dataRow = None
        genData = self.__serviceGenData
        followLinkedService = True
        
        if reloadServicePage is not None:
            dataRow = None
            selModel = self._getServiceStoreModel( serviceName )
            if selModel is not None:
                dataRow = selModel.refData
            followLinkedService = False
            # clear current selection
            selection = grid.selectionModel()
            if selection is not None:
                selection.clearSelection()
            
        else:
            # retrieve current selected service data
            dataRow = self._selectedServiceGridData( grid ) #self.__selectedServiceData( self.serviziPagine )
            if dataRow is not None:
                # check if download action
                if serviceName == agriConfig.services.fogliAzienda.name:
                    # store service data recors
                    rows = self._getServiceGridData( grid )
                    self._createServiceStoreModel( serviceName ).setRows( rows, dataRow )
                    # emit signal to run donwload 'Evento lavorazione'
                    self.downloadListaLav.emit( self, dataRow )
                    return
                
                # store service selected data
                self._createServiceStoreModel( serviceName ).setRows( [dataRow] )        
        
          
        self.updateWidgets( serviceName )
        self.onServiceSelectionChanged( grid )
            
        # emit signal for service load
        self.serviceRequest.emit( serviceName, dataRow, genData, self, followLinkedService, self.__offlineEvLavorazione )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onAnnoFilterSelectionchange(self, i):
        """Filter on combo 'anno campagna'"""
        
        # reset other filter combo
        self.cmbLista.setCurrentIndex( -1 )
        
        # init page filter config
        filterCfg = self._initPageFiltersByWidget( self.cmbAnno, 'anno' )
        
        # create 'anno campagna' filter function
        anno = self.cmbAnno.currentData()
        filterField = filterCfg.get('field')
        valueField = filterField['valueField']
        filterCfg['filterFn'] = None if not anno else lambda r, s: anno == str(r[valueField])
        
        # recreate filters
        self.handleFilterActivated()
        
        # set lista combo
        gridTable = self._getServiceTable( self.serviziPagine )
        filterModel = gridTable.model()
        tableModel = filterModel.sourceModel()
        filterCfg = self._initPageFiltersByWidget( self.cmbLista, 'lista' )
        filterField = filterCfg.get('field')
        idfldValue = tableModel.indexColumn( filterField['valueField'] )
        idfldDesc = tableModel.indexColumn( filterField['displayField'] )
        dictValues = filterModel.getUniqueValues( idfldValue, idfldDesc )
        self._populateFilterCombo( self.cmbLista, dictValues )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onListaFilterSelectionchange(self, i):
        """Filter on combo 'lista di lavorazione'"""
        
        # init page filter config
        filterCfg = self._initPageFiltersByWidget( self.cmbLista, 'lista' )
            
        # create 'lista di lavorazione' filter function
        lista = self.cmbLista.currentData()
        filterField = filterCfg.get('field')
        valueField = filterField['valueField']
        filterCfg['filterFn'] = None if not lista else lambda r, s: lista == str(r[valueField])
        
        # recreate filters
        self.handleFilterActivated()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onCuaaEditingFinished(self):
        """Filter on edit 'CUAAA'"""
        
        # init page filter config
        filterCfg = self._initPageFiltersByWidget( self.edtCuaa, 'cuaa' )
        # create 'CUAA' filter function
        self.__serviceGenData["cuaa"] = cuaa = self.edtCuaa.text().strip()
        noCuaa = not cuaa
        filterField = filterCfg.get('field')
        valueField = filterField['valueField']
        filterCfg['filterFn'] = None if noCuaa else lambda r, s: cuaa in str(r[valueField])
        # recreate filters
        self.handleFilterActivated()
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def onCuaaTextChanged(self, text):
        """TextChanged handler for edit 'CUAAA'"""
        # disable filter checkboxes
        noCuaa = not text.strip()
        self.chkLavorate.setEnabled(noCuaa)
        self.chkBloccate.setEnabled(noCuaa)
        self.chkSospese.setEnabled(noCuaa)
        self.chkLavorateAz.setEnabled(noCuaa)
        self.chkBloccateAz.setEnabled(noCuaa)
        self.chkSospeseAz.setEnabled(noCuaa)
     
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onFiltroStatoLavorazioneChange(self, state, excludeKey, reloadService=False):
        """ Filter on 'evento lavorazione' state """
        
        # check if in updating mode
        if self.filterUpdating:
            return
       
        try: 
            # set updatin filter plag
            self.filterUpdating = True
            
            # store exclude value for service params 
            chkbox = self.sender()
            isCheked = chkbox.isChecked()
            state = 'N' if isCheked else 'S'
            oldState = self.__serviceGenData.get( excludeKey, 'S' )
            
            self.__serviceGenData['escludiLavorate'] = 'S'
            self.__serviceGenData['escludiBloccate'] = 'S'
            self.__serviceGenData['escludiSospese'] = 'S'
            self.__serviceGenData[excludeKey] = state
            
            # update all checkboxes
            self.updateFilterWidgets()
            
            if oldState == state:
                return
            
            # reload service
            if reloadService:
                self.onServiceReload()
            
        finally:
            self.filterUpdating = False
            
                
    # --------------------------------------
    # 
    # --------------------------------------      
    def onLavParticelleDoubleClicked(self, index):
        """Table view 'LavorazioniParticelle' double click slot"""
        # get item from index
        filterModel = self.grid_ElencoLavorazioniParticelle.model()
        index = filterModel.mapToSource( index )
        dataRow = filterModel.sourceModel().dataRow( index )
        
        # get PARTICELLA number
        numParticellaField = agriConfig.services.ParticelleLavorazioni.numParticellaField
        numParticella = dataRow.get( numParticellaField, None )
        if numParticella is None:
            return
        
        # get PARTICELLA subalterno
        subalternoField = agriConfig.services.ParticelleLavorazioni.subalternoField
        subalterno = dataRow.get( subalternoField, None ) or ''
        
        # create filter expression
        expr = "regexp_match( trim({0}), '^0*{1}$' ) AND trim({2})='{3}'".format( 
            numParticellaField, str( numParticella ).strip().lstrip('0'), 
            subalternoField, str( subalterno ).strip() )
         
        # emit signal for zoom
        self.zoomToParticellaByExpression.emit( expr )
     
    # --------------------------------------
    # 
    # --------------------------------------      
    def closeEvent(self, event):
        self.closingWidget.emit()
        event.accept()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def isServiceStoreModelEmpty(self):
        """ Returns true if service store model empty """
        return not self.__serviceStoreModel
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def getFoglioData(self, dataRow):
        """ """
        if not dataRow:
            return dataRow
        service_cfg = agriConfig.get_value( 'agri_service', {} )
        resources_cfg = service_cfg.get( 'resources', {} )
        res_cfg = resources_cfg.get( agriConfig.services.fogliAziendaOffline.name, {} )
        selection_cfg = res_cfg.get( 'selectionFilterFields', {} )
        return dictUtil.subset( dataRow, selection_cfg, asString=True )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def destroySpinner(self):
        """ Destroy spinner """
        if self.__spinner is not None:
            self.__spinner.close()
        #del self.__spinner
        #self.__spinner = None
        self.setEnabled( True )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def createSpinner(self, disableBox=True):
        """ Create new spinner """
        self.destroySpinner()
        
        if self.__spinner is None:
            self.__spinner = Spinner( self )
            #self.__spinner.setAttribute( Qt.WA_DeleteOnClose )
            self.__spinner.resize( QSize(50, 50) )
            
        if disableBox:
            self.setEnabled( False )
            
        return self.__spinner
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setCurrentTab(self, tabName):
        """Set current tab by name"""
        tab = self.tabWidget.findChild(QWidget, tabName)
        if tab is not None:
            self.tabWidget.setCurrentWidget( tab )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setAuthEnabled(self, enabled):
        """Enable / disable control panel"""
        # if offline set always true
        self.__enabled = ( enabled or self.__offlineFoglio or self.__offlineEvLavorazione )
        self.Suoli.setEnabled( self.__enabled )
        if enabled:
            self.onServiceReload()   
        else:
            self.tabWidget.setCurrentWidget( self.Autenticazione )
            self.loadAuthPage()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setDownloaded(self, downloaded):
        """Set downloaded member """        
        self.__downloaded = downloaded
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def setServiceData(self, error, callbackData):
        # check service
        #if error is not None:
        #    return
        
        serviceName = callbackData.get( 'serviceName', None )
        serviceData = callbackData.get( 'serviceData', None )
        servRowParentData = callbackData.get( 'servRowSelData', None )
        
        # find widget form service name
        servicePage = self._getServicePage( self.serviziPagine, serviceName )
        if servicePage is None:
            return
        
        # get service table grid
        grid = self._getServiceTable( self.serviziPagine, servicePage )
        if grid is None:
            return
        
        # handle service error
        if error is not None:
            # check if same 
            currService = self._getServiceName( self.serviziPagine )
            if currService == serviceName:
                # filter all records
                filterModel = grid.model()
                filterModel.addFilterFunction( 'filter_all', lambda x,s: False)
                self.serviziPagine.setCurrentWidget( servicePage )
            # exit
            return
        
        # store servRowParentData
        self._createServiceStoreModel( serviceName ).setRefData( servRowParentData )
        
        # set model data
        self._setGridData( serviceName, grid, serviceData )
        filterModel = grid.model()
        tableModel = filterModel.sourceModel()
        
        # set current page
        self.serviziPagine.setCurrentWidget( servicePage )
        
        # set filter combo
        if serviceName == self.cmbAnno.property( self.SERVIZIO_AGRI_PROPERTY ): 
            # set anno combo
            currValue = self.cmbAnno.itemText( self.cmbAnno.currentIndex() )
            filterCfg = self._initPageFiltersByWidget( self.cmbAnno, 'anno' )
            filterField = filterCfg.get( 'field' )
            dictValues = tableModel.getUniqueValues( filterField['valueField'], filterField['displayField'] )
            self._populateFilterCombo( self.cmbAnno, dictValues )
            index = self.cmbAnno.findText( currValue ) if self.cmbAnnoInit else self.cmbAnno.count() -1
            self.cmbAnno.setCurrentIndex( index )
            self.cmbAnnoInit = True
            # enable other filter combo
            self.cmbLista.setEnabled( True )
            self.edtCuaa.setEnabled( True )
            
        # recreate filters
        self.handleFilterActivated()
    
        # try to set previous selection
        selModel = self._getServiceStoreModel( serviceName )
        if selModel:
            rows = selModel.rows or []
            if len(rows) == 1:
                selRow = rows[0]
                service_cfg = agriConfig.get_value('agri_service', {})
                resources_cfg = service_cfg.get('resources', {})
                res_cfg = resources_cfg.get(serviceName, {})
                key_fields = res_cfg.get('keyfields', '')
                key_fields = [ k.strip() for k in key_fields.split( ',' ) ]

                index = tableModel.findIndexByFunction( lambda row : dictUtil.equal_values( row, selRow, key_fields ) )
                if index.isValid():
                    column_index = grid.horizontalHeader().logicalIndexAt(0)
                    filter_index = filterModel.mapFromSource( tableModel.index( index.row(), column_index ) )
                    grid.setCurrentIndex( filter_index )
                    grid.scrollTo( filter_index, QAbstractItemView.EnsureVisible )
                    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def reauthenticateExtBrowser(self):
        """Re-authentication method with external browser"""
        
        # init
        s = QgsSettings()
        s.setValue( f"{self.__plugin.PLUGIN_NAME}/plg_auth_mode", 'external' )
        
        # confirm if reauthenticate
        if self.__enabled:
            reply = QMessageBox.question( self, tr('Autentizazione'), 
                     tr('Desideri riautenticarti?'), QMessageBox.Yes, QMessageBox.No )
            if reply != QMessageBox.Yes:
                return
        
        try:    
            from qgis_agri.util.python import pyUtil
            
            data = json.dumps({
                'authOrigUrl': self.__authOrigUrl.toString(), 
                'authUrl': self.__authUrl.toString()
            })
            
            # start authorization server socket
            if not self.__authSocket.createServer(data):
                logger.msgbox(
                    logger.Level.Critical, 
                    tr("Impossibile aprire il socket locale di autenticazione."), 
                    title=tr('ERRORE'))
                return
            
            # clear all cookies to invalidate authentication
            nam = self.__plugin.networkAccessManager
            nam.clearCookies(__QGIS_AGRI_COOKIE_DOMAIN_FILTER__)
            
            # set parameters
            envPath = self.__plugin.envPath
            script_file = os.path.join(envPath, f"{__QGIS_AGRI_EXT_BROWSER_FILE__}.py")
            if os.name == 'nt':
                python_bin = os.path.join(envPath, __QGIS_AGRI_VENV_NAME__, pyUtil.getPlatformPythonExe(for_venv=True))
            else:
                python_bin = pyUtil.getPlatformPythonExe()
        
            # run external browser
            pyUtil.runScript(script_file, python_bin=python_bin, for_venv=True, check_result=False)
            
            # emit deauthentication signal
            self.authenticated.emit( False, False, False )
            
        except Exception as ex:
            logger.msgbox(logger.Level.Critical, str(ex), title=tr('ERRORE'))
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def reauthenticate(self):
        """Re-authentication method"""  
        
        # init
        s = QgsSettings()
        s.setValue( f"{self.__plugin.PLUGIN_NAME}/plg_auth_mode", 'standard' )  
        
        # confirm if reauthenticate
        if self.__enabled:
            reply = QMessageBox.question( self, tr('Autentizazione'), 
                     tr('Desideri riautenticarti?'), QMessageBox.Yes, QMessageBox.No )
            if reply != QMessageBox.Yes:
                return
       
        # clear all cookies to invalidate authentication
        nam = self.__plugin.networkAccessManager
        nam.clearCookies(__QGIS_AGRI_COOKIE_DOMAIN_FILTER__)
            
        # emit deauthentication signal
        self.authenticated.emit( False, False, False )
        
        # reload authentication page
        self.loadAuthPage()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def loadAuthPage(self):
        """Load authorization page"""
        
        # init
        if self.__freezed:
            return
        
        # Create a network request
        request = QNetworkRequest()
        request.setUrl( self.__authUrl )
        
        try:
            # Check if use client authorization certificate
            use_client_cent_auth = agriConfig.get_value( "context/useClientCentificate", True )
            if use_client_cent_auth:
                # Add the client authorization certificate
                nam = self.__plugin.networkAccessManager
                nam.add_client_certificate_to_request( __QGIS_AGRI_CERT_METHOD__, request )
        except QGISAgriRequestError as ex:
            logger.log( logger.Level.Warning, str(ex) )
        
        # Load the request
        self.webView.load( request )
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def updateFilterWidgets(self):
        self.chkLavorate.setChecked( False )
        self.chkLavorateAz.setChecked( False )
        self.chkBloccate.setChecked( False )
        self.chkBloccateAz.setChecked( False )
        self.chkSospese.setChecked( False )
        self.chkSospeseAz.setChecked( False )
        
        # update 'evento lavorazione' filter checkbox
        checked = self.__serviceGenData.get( 'escludiLavorate', 'S' ) == 'N'
        self.chkLavorate.setChecked( checked )
        self.chkLavorateAz.setChecked( checked )
        
        checked = self.__serviceGenData.get( 'escludiBloccate', 'S' ) == 'N'
        self.chkBloccate.setChecked( checked )
        self.chkBloccateAz.setChecked( checked )
        
        checked = self.__serviceGenData.get( 'escludiSospese', 'S' ) == 'N'
        self.chkSospese.setChecked( checked )
        self.chkSospeseAz.setChecked( checked )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def updateWidgets(self, serviceName):
        # init
        xstr = lambda s: '' if s is None else str(s)
        
        # update anno widgets
        filterCfg = self._initPageFiltersByWidget( self.cmbAnno, 'anno' )
        filterField = filterCfg.get('field')
        
        selModel = self._getServiceStoreModel( agriConfig.services.listaLavorazione.name )
        data = selModel.getRow( 0, {} ) if selModel is not None else {}
        anno = xstr(data.get(filterField['displayField'], ''))
        
        self.lblAnnValueAz.setText( anno )
        self.lblAnnoValueFg.setText( anno )
        self.lblAnnoValueRp.setText( anno )
        
        # update lista widgets
        filterCfg = self._initPageFiltersByWidget( self.cmbLista, 'lista' )
        filterField = filterCfg.get('field')
        lista = xstr(data.get(filterField['valueField'], ''))
        self.lblListaIdValueAz.setText( lista )
        self.lblListaIdValueFg.setText( lista )
        self.lblListaIdValueRp.setText( lista )
        
        lista = xstr(data.get(filterField['displayField'], ''))
        self.lblListaDescValueAz.setText( lista )
        self.lblListaDescValueFg.setText( lista )
        self.lblListaDescValueRp.setText( lista )
        
        selModel = self._getServiceStoreModel( 'ListaLavorazione' )
        data = selModel.getRow( 0, {} ) if selModel is not None else {}
        filterCfg = self._initPageFilters( 'ListaLavorazione', 'tipoLista' )
        filterField = filterCfg.get('field')
        tpLista = xstr(data.get(filterField['displayField'], ''))
        self.lblListaTipoValueRp.setText( tpLista ) 
        
        
        # update cuaa widgets
        selModel = self._getServiceStoreModel( 'ElencoAziende' )
        data = selModel.getRow( 0, {} ) if selModel is not None else {}
        filterCfg = self._initPageFiltersByWidget( self.edtCuaa, 'cuaa' )
        filterField = filterCfg.get('field')
        cuaa = xstr(data.get(filterField['valueField'], ''))
        self.lblCuaaIdValueFg.setText( cuaa )
        self.lblCuaaIdValueRp.setText( cuaa )
        self.lblCuaaIdValuePart.setText( cuaa )
        
        cuaa = xstr(data.get(filterField['displayField'], ''))
        self.lblCuaaDescValueFg.setText( cuaa )
        self.lblCuaaDescValueRp.setText( cuaa )
        self.lblCuaaDescValuePart.setText( cuaa )
        
        # update 'Foglio', 'Comune' labels
        self.lblComValueRp.setText( '' )
        self.lblFoglioValueRp.setText( '' )
        if self.__offlineFoglio and self.currentFoglioData:
            # 'Comune'
            com = self.currentFoglioData.get( agriConfig.services.fogliAziendaOffline.comuneField, '' )
            self.lblComValueRp.setText( str(com) )
            # 'Foglio'
            fg = self.currentFoglioData.get( agriConfig.services.fogliAziendaOffline.foglioField, '' )
            self.lblFoglioValueRp.setText( str(fg) )
            
            
            # update PARTICELLE widgets
            selModel = self._getServiceStoreModel( 'ParticelleLavorazioniOffline' )
            data = selModel.getRow( 0, {} ) if selModel is not None else {}
            codNaz = data.get( agriConfig.services.ParticelleLavorazioni.codNazionaleField, '' )
            self.lblCodNazValuePart.setText( str(codNaz) )
            fg = data.get( agriConfig.services.ParticelleLavorazioni.foglioField, '' )
            self.lblFoglioValuePart.setText( str(fg) )
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def handleFilterActivated(self):
        """Handle grid table filters"""
        
        # get current service table
        lstPages = [self.ListaLavorazioneScaricata, self.serviziPagineParticelle] if self.__offlineFoglio else [self.serviziPagine]
        for pages in lstPages:
            gridTable = self._getServiceTable( pages )
            if gridTable is None:
                return
            
            # remove previous filters
            filterModel = gridTable.model()
            if filterModel is None:
                return
            
            filterModel.removeFilterFunctions()
            model = filterModel.sourceModel()
        
            # add control grid filters
            serviceName = self._getServiceName( pages )
            serviceCfg = self.__pagecfg.get( serviceName, {} )
            filterCfg = serviceCfg.get( 'gridfilters', {} )
            for k, cfg in filterCfg.items():
                if cfg is not None:
                    filterModel.addFilterFunction( k, cfg['filterFn'], invalidate=False )
            
            # add header filters
            def filterFn(r,_):
                h = gridTable.horizontalHeader()
                for i in range(h.count()):
                    col = model.headerField(i)
                    fltr = str( h.filterText(i) ).lower()
                    if not fltr:
                        continue
                    
                    colVal = str( r[col] ).lower()
                    if fltr in colVal:
                        continue
                    
                    # check if filter is a list of values
                    try:
                        if list(filter(lambda x, v=colVal: str(x) == v, json.loads( fltr ))):
                            continue
                    except (json.decoder.JSONDecodeError, TypeError):
                        pass
                    
                    return False
                   
                return True
            
            filterModel.addFilterFunction( 'headerFilter', filterFn, invalidate=True )
            
            # select row if there is only one
            if filterModel.rowCount() == 1:
                gridTable.setCurrentIndex( filterModel.index(0, 0) )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def setOffLine(self, 
                   offlineEvLavorazione, 
                   foglioData, 
                   idEventoLavorazione, 
                   offlineFoglio=False, 
                   waiting=False, 
                   serviceSavedData=None,
                   enableParticelleWorking=False):
        """Method to set offline mode"""
        
        ###########################################################################################
        ###########################################################################################
        def callbackOfflineServiceFn( error, callbackData, stackedPages ):
            if error:
                return
            
            serviceName = callbackData.get( 'serviceName', None )
            serviceData = callbackData.get( 'serviceData', None )
            servRowSelData = callbackData.get( 'servRowSelData', None )
            if serviceData is None:
                return
            
            storeModel = self._createServiceStoreModel( serviceName )
            storeModel.setRows( list(serviceData) )
            storeModel.setRefData( servRowSelData )
            self.updateWidgets( serviceName )
                
            # find widget form service name
            servicePage = self._getServicePage( stackedPages, serviceName )
            if servicePage is None:
                return
            
            # get service table grid
            grid = self._getServiceTable( stackedPages, servicePage )
            if grid is None:
                return
            
            # set model data
            self._setGridData( serviceName, grid, serviceData )
        ###########################################################################################
        ###########################################################################################
        
        # init
        self.__offlineEvLavorazione = offlineEvLavorazione
        self.__offlineFoglio = offlineEvLavorazione and offlineFoglio
        if waiting:
            self.setEnabled( False )
        else:
            self.setEnabled( True )
            self.Suoli.setEnabled( self.__enabled or self.__offlineEvLavorazione or self.__offlineFoglio )
            self.destroySpinner()
        # clear tables
        self._clearTables()
       
       
        # set tab text
        suoli_tab_index = self.tabWidget.indexOf( self.Suoli )
        if self.__offlineEvLavorazione and not self.__offlineFoglio:
            self.tabWidget.setTabText( suoli_tab_index, tr("Lavorazione fogli") )
        else:
            self.tabWidget.setTabText( suoli_tab_index, tr("Lavorazione suoli") )
        
       
        #
        if self.__offlineFoglio:
            # set 'Evento lavorazione' label
            text = "{0}: {1}".format( tr("Evento di lavorazione"), idEventoLavorazione )
            self.lblTitle.setText( text )
            self.lblTitlePart.setText( text )
            self.titleFrame.setVisible( True )
            
            # set foglia data (for filters)
            self.__currentFoglioData = self.__selectedFoglioData = foglioData
                
            # set first page
            #self.barComandi.setVisible( False )
            self.serviziPagine.setCurrentWidget( self.OfflinePage )
            self.ListaLavorazioneScaricata.setCurrentWidget( self.ElencoFogliScaricati )
            ######self.onScaricoPageChanged()
            if enableParticelleWorking:
                self.tabWidget.setCurrentWidget( self.Particelle )
            else:
                self.tabWidget.setCurrentWidget( self.Suoli )    
            
            # load service data from db
            pages = self.serviziPagine
            for index in range( pages.count() ):
                page = pages.widget( index )
                serviceName = self._getServiceName( pages, page )
                if serviceName: 
                    self.serviceOfflineRequest.emit( serviceName, None, lambda e,d,p=pages: callbackOfflineServiceFn(e,d,p), self )
                    
            # load PARTICELLE service data from db
            pages = self.serviziPagineParticelle
            for index in range( pages.count() ):
                page = pages.widget( index )
                serviceName = self._getServiceName( pages, page )
                if serviceName: 
                    self.serviceOfflineRequest.emit( serviceName, None, lambda e,d,p=pages: callbackOfflineServiceFn(e,d,p), self )
                
            # load service data from db (Offline page)
            self.updateOffLineControls()
            pages.setCurrentWidget( self.ElencoFogliScaricati )
            
        elif self.__offlineEvLavorazione:
            # set 'Evento lavorazione' label
            self.lblTitle.setText( "{0}: {1}".format( tr("Evento di lavorazione"), idEventoLavorazione ) )
            self.titleFrame.setVisible( True )
            
            # emit signal cannot upload
            self.canUpload.emit( False )
                
            # set first page
            self.__currentFoglioData = None
            self.__selectedFoglioData = None
            self.barComandi.setVisible( True )
            
            # load service data from db
            selRow = None
            for page in [ self.ListaLavorazione, self.ElencoAziende, self.ElencoFogliAzienda ]:
                serviceName = self._getServiceName( self.serviziPagine, page )
                if serviceName: 
                    self.serviceOfflineRequest.emit( serviceName, None, lambda e,d,p=self.serviziPagine: callbackOfflineServiceFn(e,d,p), self )
                    storeModel = self._getServiceStoreModel( serviceName )
                    if page == self.ElencoAziende:
                        selRow = storeModel.getRow( 0, default={} )
       
            serviceFogliAziendaName = self._getServiceName( self.serviziPagine, self.ElencoFogliAzienda )
            self._createServiceStoreModel( serviceFogliAziendaName ).setRefData( selRow )
                    
            # set current page
            self.serviziPagine.setCurrentWidget( self.ElencoFogliAzienda )
            self.onServicePageChanged()
               
        else:
            # hide 'Evento lavorazione' label
            self.titleFrame.setVisible( False )
            
            # emit signal cannot upload
            self.canUpload.emit( False )
                
            # set service page
            self.__currentFoglioData = None
            self.__selectedFoglioData = None
            self.barComandi.setVisible( True )
            if serviceSavedData:
                # Remove CUAA filter
                self.edtCuaa.setText('')
                self.onCuaaEditingFinished()
                # Reload services with previous selections
                self._loadServiceStoreModel( serviceSavedData )
                self.serviziPagine.setCurrentWidget( self.ElencoAziende )
            else:
                self.serviziPagine.setCurrentWidget( self.ListaLavorazione )
            self.onServicePageChanged()
        
        # PARTICELLE working settings
        particelle_tab_enable = False
        if self.__offlineFoglio:
            if enableParticelleWorking:
                gui_color = agriConfig.get_value( 'context/particella/guiColor', '#FFFACD' )
                self.lblListaTipoValueRp.setStyleSheet( f"QLabel {{ background-color: {gui_color}; }}" )
                particelle_tab_enable = True
        else:
            self.lblListaTipoValueRp.setStyleSheet( "" )
            
        # show\hide PARTICELLE tab
        particelle_tab_index = self.tabWidget.indexOf( self.Particelle )
        self.tabWidget.setTabEnabled( particelle_tab_index, particelle_tab_enable )
        self.tabWidget.setStyleSheet( 
            "QTabBar {font-weight: bold;}"
            "QTabBar::tab:!last {font-weight: normal;}"
            "QTabBar::tab::disabled {width: 1; height: 0; margin: 0; padding: 0; border: none;} " )
        
        # check if controbox enabled    
        if not self.__enabled:
            # show authentication tab
            self.tabWidget.setCurrentWidget( self.Autenticazione )
            
        elif enableParticelleWorking and particelle_tab_enable:
            # show particelle tab
            self.tabWidget.setCurrentWidget( self.Particelle )
            # reload service
            self.onServiceReload()
            
        else:
            # show suoli tab
            self.tabWidget.setCurrentWidget( self.Suoli )
            # reload service
            self.onServiceReload()
            
        #if self.__enabled and not self.__offlineEvLavorazione:
        #    # reload service
        #    self.onServiceReload()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getSuoliLavorazioneValues(self, attName):
        """Method to find a suolo by an attribute"""
        # init
        if not attName:
            return []
        
        lstValues = []
        
        # get suoli grid model
        grid = self.grid_SuoliInLavorazione
        filterModel = grid.model()
        model = filterModel.sourceModel()
        ##ndx = model.indexColumn( attName )
        for row in model.rows():
            value = row.get( attName, None )
            if value is not None:
                lstValues.append( value )
        
        return lstValues
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def findSuoloLavByAttib(self, attName, attValue):
        """Method to find a suolo by an attribute"""
        # init
        if not attName:
            return False
        
        # get suoli grid model
        grid = self.grid_SuoliInLavorazione
        filterModel = grid.model()
        model = filterModel.sourceModel()
        
        """
        # find data row
        index = model.findIndexByFunction( lambda row : attName in row and row.get( attName, None ) == attValue )
        if not index.isValid():
            grid.clearSelection()
            return False
        
        # set current index for found suolo
        grid.setCurrentIndex( filterModel.mapFromSource( index ) )
        """
        # set column filter
        ndx = model.indexColumn( attName )
        h = grid.horizontalHeader()
        h.setFilterText( ndx, str(attValue) )
        
        return True
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def updateOffLineControls(self):
        """Method to update cotrolbox in offline mode"""
        
        # init
        self.__totFogliToWork = 0
        
        # check if offline db
        if not self.__offlineFoglio:
            return
        
        ###########################################################################################
        ###########################################################################################
        def callbackScaricoFn( error, callbackData, stackedPages ):
            if error:
                return
            
            serviceName = callbackData.get( 'serviceName', None )
            serviceData = callbackData.get( 'serviceData', None )
            #servRowSelData = callbackData.get( 'servRowSelData', None )
            
            #if not data:
            #    return 
            
            # find widget form service name
            servicePage = self._getServicePage( stackedPages, serviceName )
            if servicePage is None:
                return
            
            # get service table grid
            grid = self._getServiceTable( stackedPages, servicePage )
            if grid is None:
                return
            
            # set model data
            self._setGridData( serviceName, grid, serviceData )
            
            # initial settings
            if serviceName == agriConfig.services.fogliAziendaOffline.name:
                #
                serviceCfg = agriConfig.services.fogliAziendaOffline
                
                # selected foglio settings
                filterModel = grid.model()
                tableModel = filterModel.sourceModel()
                lstIndeces = filterModel.getSelectableRowIndeces()
                self.__totFogliToWork = len( lstIndeces )
                
                #############self.__totFogliToWork = filterModel.rowCount() 
                if self.__totFogliToWork == 1:
                    index = lstIndeces[0]
                    self.__currentFoglioData = tableModel.row( index )
                    grid.setCurrentIndex( filterModel.index( index, 0 ) )
                    
                
                hasFoglioDone = False
                if self.currentFoglioData:
                    # check if this setting is required
                    service_cfg = agriConfig.get_value( 'agri_service', {} )
                    resources_cfg = service_cfg.get( 'resources', {} )
                    res_cfg = resources_cfg.get( serviceName, {} )
                    fg_sel_cfg = res_cfg.get( 'highlightFoglio', False )
                    if fg_sel_cfg:
                        # get foglio record index
                        tableModel.resetRowInfo()
                        index = tableModel.findIndexByFunction( lambda row : dictUtil.isSubset( self.currentFoglioFilterData, row ) )
                        if index.isValid():
                            # get row background color
                            rows_cfg = res_cfg.get( 'gridRows', {} )
                            bg_color_cfg = rows_cfg.get( 'foglioSelBgColor', '#e6ffcc' )
                            # set row background color
                            grid.setCurrentIndex( filterModel.mapFromSource( index ) )
                            tableModel.setData( index, bg_color_cfg, Qt.BackgroundRole )
                            
                    # check foglio done
                    foglioSuoliState = self.currentFoglioData.get( serviceCfg.statoFieldEdit, None )
                    foglioPartState = self.currentFoglioData.get( serviceCfg.statoPartFieldEdit, None )
                    hasFoglioDone = ( 
                        foglioSuoliState == serviceCfg.statoFieldEditDone
                        and
                        foglioPartState == serviceCfg.statoFieldEditDone 
                    )
                        
                # emit signal ready to upload
                self.canUpload.emit( hasFoglioDone )
                
                
        ###########################################################################################
        ###########################################################################################
        
        # load service data from DB (Offline page)
        pages = self.ListaLavorazioneScaricata
        for index in range( pages.count() ):
            page = pages.widget( index )
            serviceName = self._getServiceName( pages, page )
            if serviceName: 
                self.serviceOfflineRequest.emit( serviceName, None, lambda e,d,p=pages,self=self: callbackScaricoFn(e,d,p), self )
                
        # load PARTICELLE working data from DB
        pages = self.serviziPagineParticelle
        for index in range( pages.count() ):
            page = pages.widget( index )
            serviceName = self._getServiceName( pages, page )
            if serviceName: 
                self.serviceOfflineRequest.emit( serviceName, None, lambda e,d,p=pages,self=self: callbackScaricoFn(e,d,p), self )
        