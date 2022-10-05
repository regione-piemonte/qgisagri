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
# Import PyQt modules
from qgis.core import ( NULL,
                        Qgis, 
                        QgsDataSourceUri )

from PyQt5.QtCore import Qt, QTimer, QObject
from PyQt5.QtWidgets import QMenu, QToolButton, QMessageBox

# Import plugin modules
from qgis_agri import __QGIS_AGRI_NAME__, agriConfig, tr
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.qgis_agri_actions import QGISAgriActionBase
from qgis_agri.util.signals import signalUtil
from qgis_agri.util.json import jsonUtil
from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.gui.fill_suoli_tool import FillSuoliTool
from qgis_agri.gui.split_suoli_tool import SplitSuoliTool
from qgis_agri.gui.delete_feature_tool import DeleteFeatureTool
from qgis_agri.gui.dissolve_suoli_tool import DissolveSuoliTool
from qgis_agri.gui.difference_suoli_tool import DifferenceSuoliTool
from qgis_agri.gui.select_feature_tool import SelectFeatureTool
from qgis_agri.qgis_agri_image_dlg import QGISAgriImageViewer


# 
#-----------------------------------------------------------
class QGISAgriParticelle(QObject):
    """QGIS Plugin Implementation for 'Particelle editing'"""

    # constants
    MAIN_PARTICELLE_LAYER_PROP = "agri_main_particelle_layer"
    COMMIT_PARTICELLE_LAYER_PROP = "agri_main_commit_layer_status"

    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, plugin):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        
        # call parent cunstructor
        QObject.__init__(self)
        
        # Particelle Tools
        self.__plugin = plugin
        self.__partFillTool = None
        self.__partFillToolBtn = None
        self.__partOptFillMenu = None
        self.__partSplitTool = None
        self.__partSplitToolBtn = None
        self.__partOptSplitMenu = None
        self.__partCloneToolBtn = None
        self.__partOptCloneMenu = None
        self.__scaricaPartDocTool = None
        self.__partDeleteTool = None
        self.__partDissolveTool = None
        self.__partDifferenceTool = None
        self.__partRepairTool = None
        self.__cloneCxfPartTool = None
        self.__cloneSuoloPartTool = None
        self.__partIdentifyTool = None
        
        # Particelle actions
        self.__partEditingAction = None
        self.__partFillMoveAction = None
        self.__partSplitMoveAction = None
        
        # dictionary original geometries
        self.__edit_part_fids = {}
        self.__part_main_layer_uri = []
        self.__updateLayerFeatureCountLst = []
        self.__added_part_features = {}
        self.__partEnableUpdateFlags = True 
        
        # dialog
        self.__allViewDlg = None
        
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
    def EditingAction(self):
        """ Returns start\stop editing action """
        return self.__partEditingAction
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def isParticelleWorkingEnabled(self):
        """ Return True if PARTICELLE working is enabled (by service data), else False """
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # return if PARTICELLE working is enabled
        data = controller.getDbTableData( agriConfig.services.listaLavorazione.name  )
        idTipoLista = data[0].get( agriConfig.services.listaLavorazione.idTipoLista, None ) if data else None
        return str(idTipoLista) == str(agriConfig.services.listaLavorazione.idTipoListaParticella)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def hasCXF(self):
        """ Return True if PARTICELLE working has CXF file, else False """
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # return if PARTICELLE working is enabled
        data = controller.getDbTableData( agriConfig.services.ParticelleLavorazioni.name  )
        flagCXF = data[0].get( agriConfig.services.ParticelleLavorazioni.flagCxfField, None ) if data else None
        return str(flagCXF) == str(agriConfig.services.ParticelleLavorazioni.flagFieldTrueValue)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def hasAllegati(self):
        """ Return True if PARTICELLE working has allegati files, else False """
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # return if PARTICELLE working is enabled
        data = controller.getDbTableData( agriConfig.services.ParticelleLavorazioni.name  )
        flagAllegati = data[0].get( agriConfig.services.ParticelleLavorazioni.flagAllegatiField, None ) if data else None
        return str(flagAllegati) == str(agriConfig.services.ParticelleLavorazioni.flagFieldTrueValue)
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def mainLayerUri(self):
        """ Return PARTICELLE main layers list """
        return self.__part_main_layer_uri
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def guiColor(self):
        """ Return PARTICELLE tool button background color """
        return agriConfig.get_value( 'context/particella/guiColor', '#FFFACD' )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def allegatiDlg(self):
        """ Returns Allegati viewer dialog (readonly) """
        return self.__allViewDlg
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def storeParticelleLayer(self, layer, reset=False):
        """ """
        if reset:
            self.__part_main_layer_uri.clear()
        if layer:
            data_provider = layer.dataProvider()   
            self.__part_main_layer_uri.append( QgsDataSourceUri( data_provider.dataSourceUri() ) )   
    
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def initGui(self, edit_menu, edit_tbar, action_name: str=None, other_action: QGISAgriActionBase=None) -> list:
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        action_name = action_name or 'all'
        action_lst = []
        
        
        # create photo viewer dialog
        self.__allViewDlg = QGISAgriImageViewer( 
            parent=plugin.iface.mainWindow(), 
            flags=Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint 
        )
        self.__allViewDlg.resize(800, 600)
        self.__allViewDlg.setWindowTitle( f"{__QGIS_AGRI_NAME__} - {tr('Allegati Particelle')}" )
        
        
        #
        def action_required(a):
            return action_name == 'all' or action_name == str(a)
        
        """
        # create new toolbar
        edit_tbar = plugin.add_toolbar( 
            tr( 'QGIS Agri Particelle edit' ), 
            tr( 'Barra degli strumenti di editazione dell paricelle QGIS Agri' ) )
        """
        
        #------------------------------------------------------------------
        if action_required('scaricaDatiParticella'):
            icon_path = ':/plugins/qgis_agri/images/action-download-part-doc-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Info Particelle' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onShowDataParticella,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
                customData=controller.get_datasourceuri_suolo_layers('scaricaDatiParticella'),
                disallow=False)
            
            action.setCheckAuthenticated( True )
            action.enableVisibilityByLayer( True )
            action.setStopOnDiffLayer( True )
            action_lst.append( action )
        
        #------------------------------------------------------------------
        if action_required('editingParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-start-edit-part-icon.png'
            self.__partEditingAction = plugin.add_action(
                icon_path,
                text=tr( 'Inizia editazione PARTICELLE' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleStartEditing,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.EDITING,
                customData=controller.get_datasourceuri_suolo_layers('editingParticelle'),
                toolbar_backcolor=self.guiColor )
            
            self.__partEditingAction.enableVisibilityByLayer( True )
            action_lst.append( self.__partEditingAction )
        
        #------------------------------------------------------------------
        if action_required('all'):
            edit_menu.addSeparator()
            edit_tbar.addSeparator()
        
        #------------------------------------------------------------------
        if action_required('fillParticelle'):
            layUris = plugin.controller.get_datasourceuri_suolo_layers('fillParticelle')    
            icon_path = ':/plugins/qgis_agri/images/action-fill-hole-icon.png'
            fillAction = plugin.add_action(
                icon_path,
                text=tr( 'Nuova PARTICELLA' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleFill,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=layUris,
                toolbar_backcolor=self.guiColor )
            
            fillAction.enableVisibilityByLayer( True )
            action_lst.append( fillAction )
        
            # add sub action menu
            self.__partFillToolBtn = edit_tbar.widgetForAction( fillAction )
            if self.__partFillToolBtn is not None:
                self.__partOptFillMenu = QMenu( self.__partFillToolBtn )
                self.__partOptFillMenu.addAction( fillAction )
                
                icon_path = ':/plugins/qgis_agri/images/action-split-move-vertex-icon.png'
                self.__partFillMoveAction = plugin.add_action(
                    icon_path,
                    text=tr( 'Edita spezzata (tasto SHIFT)' ),
                    menu_obj= self.__partOptFillMenu,
                    add_to_toolbar=False,
                    checkable_flag=True,
                    callback=self.onParticelleClickMoveFill,
                    parent=plugin.iface.mainWindow(),
                    action_type=QGISAgriActionBase.action_type.LAYER,
                    customData=layUris )
                self.__partFillMoveAction.forceDisable( True )
                
                self.__partFillToolBtn.setPopupMode( QToolButton.MenuButtonPopup )
                self.__partFillToolBtn.triggered.connect( self.__partFillToolBtn.setDefaultAction )
                self.__partFillToolBtn.setMenu( self.__partOptFillMenu )
                self.__partFillToolBtn.setDefaultAction( fillAction )
                
                def setFillCheckedActions(action):
                    for a in self.__partOptFillMenu.actions():
                        if a != action and a!= fillAction:
                            a.setChecked( False )
                
                self.__partOptFillMenu.triggered.connect( setFillCheckedActions )
        
        
        #------------------------------------------------------------------
        if action_required('splitParticelle'):
            layUris = controller.get_datasourceuri_suolo_layers('splitParticelle')
            icon_path = ':/plugins/qgis_agri/images/action-split-suoli-icon.png'
            splitAction = plugin.add_action(
                icon_path,
                text=tr( 'Taglia PARTICELLE' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleSplit,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=layUris,
                toolbar_backcolor=self.guiColor )
            
            splitAction.enableVisibilityByLayer( True )
            action_lst.append( splitAction )
            
            # add sub action menu
            self.__partSplitToolBtn = edit_tbar.widgetForAction( splitAction )
            if self.__partSplitToolBtn is not None:
                self.__partOptSplitMenu = QMenu( self.__partSplitToolBtn )
                self.__partOptSplitMenu.addAction( splitAction )
                
                #icon_path = ':/plugins/qgis_agri/images/action-split-move-line-icon.png'
                icon_path = ':/plugins/qgis_agri/images/action-split-move-vertex-icon.png'
                self.__partSplitMoveAction = plugin.add_action(
                    icon_path,
                    text=tr( 'Edita spezzata (tasto SHIFT)' ),
                    menu_obj= self.__partOptSplitMenu,
                    add_to_toolbar=False,
                    checkable_flag=True,
                    callback=self.onParticelleMoveSplit,
                    parent=plugin.iface.mainWindow(),
                    action_type=QGISAgriActionBase.action_type.LAYER,
                    customData=layUris )
                self.__partSplitMoveAction.forceDisable( True )
                
                self.__partSplitToolBtn.setPopupMode( QToolButton.MenuButtonPopup )
                self.__partSplitToolBtn.triggered.connect( self.__partSplitToolBtn.setDefaultAction )
                self.__partSplitToolBtn.setMenu( self.__partOptSplitMenu )
                self.__partSplitToolBtn.setDefaultAction( splitAction )
                
                def setSplitCheckedActions(action):
                    for a in self.__partOptSplitMenu.actions():
                        if a != action and a!= splitAction:
                            a.setChecked( False )
                
                self.__partOptSplitMenu.triggered.connect( setSplitCheckedActions )
           
        
        #------------------------------------------------------------------
        if action_required('delParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-del-polygon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Rimuovi PARTICELLA' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleDelete,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('delParticelle'),
                toolbar_backcolor=self.guiColor )
         
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
        
        #------------------------------------------------------------------
        if action_required('vertexParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-vertex-tool-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Modifica vertici PARTICELLA' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleVertex,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('vertexParticelle'),
                toolbar_backcolor=self.guiColor )
            
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
        
        #------------------------------------------------------------------
        if action_required('addHoleParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-add-hole-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Aggiungi buco PARTICELLA' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleAddHole,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('addHoleParticelle'),
                toolbar_backcolor=self.guiColor )
            
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
        
        #------------------------------------------------------------------
        if action_required('delHoleParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-delete-hole-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Rimuovi buco PARTICELLA' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleDelHole,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('delHoleParticelle'),
                toolbar_backcolor=self.guiColor )
        
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
        
        #------------------------------------------------------------------
        if action_required('dissolveParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-dissolve-suoli-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Unisci PARTICELLE' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleDissolve,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('dissolveParticelle'),
                toolbar_backcolor=self.guiColor )
        
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
        
        #------------------------------------------------------------------
        if action_required('diffParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-difference-suoli-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Ritaglia PARTICELLA per differenza' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleDifference,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('diffParticelle'),
                toolbar_backcolor=self.guiColor )
            
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
        
        #------------------------------------------------------------------
        if action_required('all'):
            edit_menu.addSeparator()
            edit_tbar.addSeparator()
        
        #------------------------------------------------------------------
        if action_required('repairParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-suolo-done-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Ripara PARTICELLA' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleRepair,
                parent=plugin.iface.mainWindow(),
                #action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('repairParticelle'),
                toolbar_backcolor=self.guiColor )
            
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
            
        #------------------------------------------------------------------
        if action_required('repairAllParticelle'):
            icon_path = ':/plugins/qgis_agri/images/action-multi-to-single-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Converte le geometrie delle PARTICELLE da multi parti in singole parti' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleRepairAll,
                parent=plugin.iface.mainWindow(),
                #action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE,
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('repairAllParticelle'),
                toolbar_backcolor=self.guiColor )
            
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
         
         
        #------------------------------------------------------------------
        if action_required('cloneParticellaCxf'):
            icon_path = ':/plugins/qgis_agri/images/action-copy-particella-cxf-icon.png'
            cloneAction = plugin.add_action(
                icon_path,
                text=tr( 'Clona PARTICELLA CXF' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onCloneCxfParticella,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER,
                customData=controller.get_datasourceuri_suolo_layers('cloneParticellaCxf'),
                toolbar_backcolor=self.guiColor )
            
            cloneAction.enableVisibilityByLayer( True )
            action_lst.append( cloneAction )
            
            # add sub action menu
            self.__partCloneToolBtn = edit_tbar.widgetForAction( cloneAction )
            if self.__partSplitToolBtn is not None:
                self.__partOptCloneMenu = QMenu( self.__partCloneToolBtn )
                self.__partOptCloneMenu.addAction( cloneAction )
                
                icon_path = ':/plugins/qgis_agri/images/action-copy-suolo-particella-icon.png'
                cloneSuoloAction = plugin.add_action(
                    icon_path,
                    text=tr( 'Clona PARTICELLA da suolo' ),
                    menu_obj= self.__partOptCloneMenu,
                    add_to_toolbar=False,
                    checkable_flag=True,
                    callback=self.onCloneSuoloParticella,
                    parent=plugin.iface.mainWindow(),
                    action_type=QGISAgriActionBase.action_type.LAYER,
                    customData=controller.get_datasourceuri_suolo_layers('cloneParticellaSuolo|sel'),
                    toolbar_backcolor=self.guiColor )
                
                cloneSuoloAction.enableVisibilityByLayer( True )
                action_lst.append( cloneSuoloAction )
                
                self.__partCloneToolBtn.setPopupMode( QToolButton.MenuButtonPopup )
                self.__partCloneToolBtn.triggered.connect( self.__partCloneToolBtn.setDefaultAction )
                self.__partCloneToolBtn.setMenu( self.__partOptCloneMenu )
                self.__partCloneToolBtn.setDefaultAction( cloneAction )
                
                def setCloneCheckedActions(action):
                    for a in self.__partOptCloneMenu.actions():
                        if a != action and a!= cloneAction:
                            a.setChecked( False )
                
                self.__partOptCloneMenu.triggered.connect( setCloneCheckedActions )
            
        #------------------------------------------------------------------
        if action_required('identityParticella'):
            icon_path = ':/plugins/qgis_agri/images/action-identify-icon.png'
            action = plugin.add_action(
                icon_path,
                text=tr( 'Modifica attributi PARTICELLA' ),
                checkable_flag=True,
                menu_obj=edit_menu,
                toolbar_obj=edit_tbar,
                callback=self.onParticelleIdentify,
                parent=plugin.iface.mainWindow(),
                action_type=QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE, #STARTING,
                customData=controller.get_datasourceuri_suolo_layers('identityParticella'),
                toolbar_backcolor=self.guiColor )
            
            action.enableVisibilityByLayer( True )
            action_lst.append( action )
            
        # assigna other action
        if other_action is not None:
            for a in action_lst:
                a.actionIsVisible.connect( other_action.setHidden )
                
        # return list of created actions
        return action_lst
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onShowDataParticella(self, checked, action):
        """ Download PARTICELLA info action handler """
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # test if tool is checkable
        if not plugin.checkable_tool( checked, action, self.__scaricaPartDocTool ):
            return
        
        # get command layers
        vlayers = plugin.get_cmd_layers( 'scaricaDatiParticella|Base', err_if_empty=False )
        vlayers = vlayers + plugin.get_cmd_layers( 'scaricaDatiParticella' )
        if not vlayers:
            return
        
        currLayer = plugin.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get document field
        cmd_cfg = controller.getCommandConfig( 'scaricaDatiParticella' )
        idKey_fld = cmd_cfg.get( 'idKeyField', '' ) 
        idParticella_fld = cmd_cfg.get( 'idField', '' )
        if not idParticella_fld:
            logger.msgbox( logger.Level.Critical, 
                           tr( 'Manca la definizione del campo id nella configurazione del plugin.' ), 
                           title=tr('ERRORE'))
            return
        
        numero_fld = cmd_cfg.get( 'numero', '' ) 
        subalterno_fld = cmd_cfg.get( 'subalterno', '' )
        
        
        ############################################################################################################
        # selection callback function
        def onSelectFeature(layer, features, mouseBtn):
            # get document id
            feature = features[0]
            idKeyFeature = feature.id()
            lstIdParticella = []
            attribs = QGISAgriLayers.get_attribute_values( feature, attr_list=[idParticella_fld, numero_fld, subalterno_fld] )
            numero = attribs.get( numero_fld, '' ) 
            subalterno = attribs.get( subalterno_fld, '' ) 
            idParticella = attribs.get( idParticella_fld, None )     
            if not idParticella:
                # id suolo not found 
                #logger.msgbar( logger.Level.Warning, 
                #               tr( 'Id particella non valorizzato.' ), 
                #               title=plugin.name )
                #return
                pass
            else:
                lstIdParticella.append( idParticella )
            
            # download and show suolo info
            provider = layer.dataProvider()
            dataSourceUri = QgsDataSourceUri( provider.dataSourceUri() )
            plugin.downloadFeatureData( 
                dataSourceUri,
                idKey_fld, 
                idKeyFeature, 
                idParticella,
                lstIdParticella,
                'particella_documents.html',
                plugin.event_controller.onDownloadDataParticella,
                {
                    "numeroParticella": numero,
                    "subalterno": subalterno,
                    "windowTitle": 'Dati particella'
                }
            )
        ############################################################################################################
            
        # hide dialog
        plugin.docsdlg.hide()    
            
        # instance tool
        if self.__scaricaPartDocTool is None:
            self.__scaricaPartDocTool = SelectFeatureTool( plugin.iface, vlayers, single=True, unsetMapToolOnSelect=False )
            
        # initialize tool and add to canvas
        self.__scaricaPartDocTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        plugin.run_tool( checked, action, self.__scaricaPartDocTool, msg=tr( 'Visualizza le informazioni delle PARTICELLE' ) )    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleStartEditing(self, checked, action):
        """Method to start editing on Agri PARTICELLE layer"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # check if to stop editing
        if not checked:
            self.onParticelleEndEditing(checked, action)
            return
        
        # close suoli editing
        if not plugin.onEndEditing(
                        False, 
                        None,
                        buttons=QMessageBox.Save|QMessageBox.Cancel,
                        headerMessage=tr("<b>ATTENZIONE: SUOLI APERTI IN EDITING.</b><br>"),
                        msgLevel=Qgis.Warning ):
            action.setChecked( False )
            return
            
        # check if PARTICELLE working is enabled
        if not self.isParticelleWorkingEnabled:
            action.setChecked( False )
            logger.msgbox(
                logger.Level.Warning,
                tr( "Lista di lavorazione per i soli suoli: le particelle non sono lavorabili." ),
                title = plugin.name )
            return
        
        # get list of editable Agri layers
        vlayers = controller.get_suolo_vector_layers( 'editingParticelle', sort_attr='editorder' )
        if len(vlayers) == 0:
            logger.msgbox(logger.Level.Critical, tr( 'Nessun layer di selezione associato al comando' ), title=tr('ERRORE'))
            return
        
        # force only one layer in editing, choosing:
        #  1) current layer in list of editing suoli layers
        #  2) first layer by order of editing suoli layers
        currLayer = plugin.iface.activeLayer()
        if currLayer in vlayers:
            vlayers = [ currLayer ]
        else:
            vlayers = [ vlayers[ 0 ] ]   
        
        # start editing
        QGISAgriLayers.start_editing( vlayers, force_edit=True )
        
        # set as active layer
        plugin.iface.setActiveLayer( vlayers[ 0 ] )
        
        # emit message
        logger.msgbar(logger.Level.Info, tr('Avviata editazione livelli PARTICELLE'), title=plugin.name)
        

    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleEndEditing(self, checked, action, buttons=None, headerMessage=None, msgLevel=Qgis.Info):
        """Method to terminate editing on Agri PARTICELLE layers"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # get list of editable Agri PARTICELLE layers
        vlayers = controller.get_suolo_vector_layers('editingParticelle', sort_attr='editorder')
        if len(vlayers) == 0:
            logger.msgbox(logger.Level.Critical, tr('Nessun layer di selezione associato al comando'), title=tr('ERRORE'))
            return False
        
        # get layer config
        odb_lays_cfg = agriConfig.get_value( 'ODB/layers', {} )
        
        # define callback function
        def callback(layer, oper, init):
            if init:
                # set wait cursor
                logger.setOverrideCursor()
                
            else:
                uri = QgsDataSourceUri( layer.dataProvider().dataSourceUri() )
                layer_cfg = odb_lays_cfg.get( uri.table(), {} )
                layer.setReadOnly( layer_cfg.get( 'readonly', False ) )
        
        try:
            # stop editing
            res = QGISAgriLayers.end_editing_ext(
                        vlayers, 
                        callback=callback, 
                        buttons=buttons, 
                        headerMessage=headerMessage, 
                        msgLevel=msgLevel )
            if not res:
                if action:
                    action.setChecked( True )
                return False
            
            return True
        finally:
            logger.restoreOverrideCursor()
        
        # update layers
        QGISAgriLayers.update_layers( vlayers )
   
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleClickMoveFill(self, checked, action):
        """Fill PARTICELLE: drawing polyline edit"""
        # init
        plugin = self.plugin
        
        #
        tool = self.__partFillTool
        if tool is None:
            return
        plugin.checkable_tool( checked, action, tool )
        tool.startOperation( FillSuoliTool.operation.MOVE )
        logger.msgbar( logger.Level.Info, tr('Edita il tracciato di disegno'), title=plugin.name, clear=True )
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleFill(self, checked, action):
        """Draws new PARTICELLA: fill area and holes with features dynamically"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # test if tool is checkable
        tool = self.__partFillTool    
        if not plugin.checkable_tool( checked, action, tool ):
            # check if default operation
            if tool is not None and tool.currentOperation != tool.operation.DRAW:    
                tool.startOperation( tool.operation.DRAW )
            return
        
        # get dest vector layers
        vDestLayers = plugin.get_cmd_layers( 'fillParticelle' )
        if not vDestLayers:
            return
        
        # get cutting layers
        vCutLayers = []
        # TODO: CONTROL OR REMOVE!!!
        """
        vCutLayers = plugin.get_cmd_layers( 'fillParticelle|cut' )
        vCutLayers = listUtil.concatNoDuplicate( vCutLayers, vDestLayers )
        """
        
        # check if active layer is a command layer
        currLayer = plugin.iface.activeLayer()
        if currLayer not in vDestLayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = controller.getCommandConfig( 'fillParticelle', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
        
        #####################################################################    
        def checkAttributes(layer, feature):
            # init
            nullAttribs = []
            assignAttribs = {}
            
            # get feature attributes
            attribs = QGISAgriLayers.get_attribute_values( feature )
            for fld_def in fld_lst:
                fld_name = fld_def.get( 'name', '' )
                if fld_name not in attribs:
                    continue
                
                # get fiel value
                fld_value = attribs.get( fld_name )
                
                # check not null fields
                if fld_def.get( 'notNull', False ):
                    if not fld_value or fld_value == NULL:
                        nullAttribs.append( fld_name )
                        continue
                        
                # get fiel value
                fld_zero_fill = fld_def.get( 'zeroFill', 0 )
                if fld_zero_fill:
                    try:
                        assignAttribs[ fld_name ] = str( fld_value ).zfill( fld_zero_fill )         
                    except TypeError:
                        pass
            
            if nullAttribs:
                # show message err message and return false
                logger.htmlMsgbox( 
                    logger.Level.Warning,
                    "{}<br><ul>{}</ul>".format(
                        tr('Attributi non assegnati:\n'),
                        "".join( map(lambda s: f"<li><b> {s}</b></li>", nullAttribs ) )
                    ), 
                    title=plugin.name )
                return False
            
            elif assignAttribs:
                # assign new attribute value
                QGISAgriLayers.change_attribute_values( layer, [ feature ], assignAttribs )
            
            return True
        ##################################################################### 
        
        # instance tool
        if self.__partFillTool is None:
            self.__partFillTool = FillSuoliTool( plugin.iface, 
                                                 currLayer,
                                                 suoliRefLayers=vCutLayers,
                                                 copyAttribs=attribs,
                                                 suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                                                 snapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE, 
                                                 suoliSnapLayers=vDestLayers,
                                                 attribCallbackFn=checkAttributes )
            
            self.__partFillTool.deactivated.connect( lambda: ( self.__partFillToolBtn.setDefaultAction( self.__partFillTool.action() ),
                                                               self.__partFillMoveAction.forceDisable( True ) ) )
            
            self.__partFillTool.captureChanged.connect( lambda n: ( self.__partFillToolBtn.setDefaultAction( self.__partFillTool.action() ) if n < 1 else None,
                                                                    self.__partFillMoveAction.forceDisable( n < 2 ) ) )
            
            # handle signal for operation changed
            def setToolButton(operation):
                action = None
                tool = self.__partFillTool
                if operation == tool.operation.DRAW:
                    action = tool.action()
                elif operation == tool.operation.MOVE:
                    action = self.__partFillMoveAction
                    
                if action is not None:
                    QTimer.singleShot( 0, lambda: self.__partFillToolBtn.setDefaultAction( action ) )
        
            self.__partFillTool.operationChanged.connect( setToolButton )
              
        # initialize tool and add to canvas
        self.__partFillTool.initialize( currLayer, suoliRefLayers=vCutLayers, copyAttribs=attribs )
        plugin.run_tool( checked, action, self.__partFillTool, msg=tr('Disegna una nuova PARTICELLA'), snapping=True )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleMoveSplit(self, checked, action):
        """Split PARTICELLE: cutting line edit"""
        # init
        plugin = self.plugin
        
        #
        tool = self.__partSplitTool
        if tool is None:
            return
        plugin.checkable_tool( checked, action, tool )
        tool.startOperation( SplitSuoliTool.operation.MOVE )
        logger.msgbar( logger.Level.Info, tr('Edita la linea di taglio'), title=plugin.name, clear=True )

             
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleSplit(self, checked, action):
        """Split PARTICELLE features dinamically"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # test if tool is checkable
        tool = self.__partSplitTool    
        if not plugin.checkable_tool( checked, action, tool ):
            # check if default operation
            if tool is not None and tool.currentOperation != tool.operation.DRAW:    
                tool.startOperation( tool.operation.DRAW )
            return
        
        # get source vector layers
        vlayers = plugin.get_cmd_layers( 'splitParticelle' )
        if not vlayers:
            return
        
        # check if active layer is a command layer
        currLayer = plugin.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = controller.getCommandConfig( 'splitParticelle', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
        
        # instance tool
        if self.__partSplitTool is None:
            self.__partSplitTool = SplitSuoliTool( plugin.iface, 
                                                   currLayer, 
                                                   copyAttribs=attribs,
                                                   snapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE, 
                                                   suoliSnapLayers=vlayers )
            
            self.__partSplitTool.deactivated.connect( lambda: ( self.__partSplitToolBtn.setDefaultAction( self.__partSplitTool.action() ),
                                                                 self.__partSplitMoveAction.forceDisable( True ) ) )
            
            self.__partSplitTool.captureChanged.connect( lambda n: ( self.__partSplitToolBtn.setDefaultAction( self.__partSplitTool.action() ) if n < 1 else None,
                                                                      self.__partSplitMoveAction.forceDisable( n < 2 ) ) )
            
            
            # handle signal for operation changed
            def setToolButton(operation):
                action = None
                tool = self.__partSplitTool
                if operation == tool.operation.DRAW:
                    action = tool.action()
                elif operation == tool.operation.MOVE:
                    action = self.__partSplitMoveAction
                    
                if action is not None:
                    QTimer.singleShot( 0, lambda: self.__partSplitToolBtn.setDefaultAction( action ) )
        
            self.__partSplitTool.operationChanged.connect( setToolButton )
              
        # initialize tool and add to canvas
        self.__partSplitTool.initialize( currLayer, copyAttribs=attribs )
        plugin.run_tool( checked, action, self.__partSplitTool, msg=tr('Taglia le PARTICELLE dinamicamente'), snapping=True )
        

    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleDelete(self, checked, action):
        """Delete an existing PARTICELLA"""
        
        # init
        plugin = self.plugin
        
        # test if tool is checkable        
        if not plugin.checkable_tool( checked, action, self.__partDeleteTool ):
            return
        
        # instance tool
        if self.__partDeleteTool is None:
            self.__partDeleteTool = DeleteFeatureTool( plugin.iface, multiselect=True )
            
        # initialize tool and add to canvas
        self.__partDeleteTool.initialize()
        plugin.run_tool( checked, action, self.__partDeleteTool, msg=tr( 'Rimuove le PARTICELLE selezionate' ) )
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleVertex(self, checked, action):
        """Run vertex tool action for PARTICELLE"""
        
        # init
        plugin = self.plugin
        
        # test if checkable action
        if not plugin.checkable_action( checked, action ):
            return
        
        # run tool
        plugin.run_tool(checked, action, None, msg=tr('Modifica vertici PARTICELLE'), cmdAction=plugin.iface.actionVertexTool(), snapping=True)
 

    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleAddHole(self, checked, action):
        """Run action to add new PARTICELLA hole"""
        
        # init
        plugin = self.plugin
        
        # test if checkable action
        if not plugin.checkable_action( checked, action ):
            return
        
        # run tool 
        plugin.run_tool(checked, action, None, msg=tr('Aggiungi buco PARTICELLA'), cmdAction=plugin.iface.actionAddRing())
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleDelHole(self, checked, action):
        """Run action to delete a PARTICELLA hole"""
        
        # init
        plugin = self.plugin
    
        """Run action to delete a polygon hole"""
        # test if checkable action
        if not plugin.checkable_action( checked, action ):
            return
        
        # run tool
        plugin.run_tool(checked, action, None, msg=tr('Rimuovi buco PARTICELLA'), cmdAction=plugin.iface.actionDeleteRing()) 
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleDissolve(self, checked, action):
        """Dissolve PARTICELLE features dinamically"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # test if tool is checkable        
        if not plugin.checkable_tool( checked, action, self.__partDissolveTool ):
            return
        
        # get source vector layers
        vlayers = plugin.get_cmd_layers( 'dissolveParticelle' )
        if not vlayers:
            return
        
        # check if active layer is a command layer
        currLayer = plugin.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = controller.getCommandConfig( 'dissolveParticelle', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value

        # instance tool
        if self.__partDissolveTool is None:
            self.__partDissolveTool = DissolveSuoliTool( plugin.iface, 
                                                         currLayer,
                                                         copyAttribs=attribs,
                                                         holeMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                                                         snapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE, 
                                                         suoliSnapLayers=vlayers,
                                                         msgTitle=plugin.name )
            
        # initialize tool and add to canvas
        self.__partDissolveTool.initialize( currLayer, copyAttribs=attribs )
        plugin.run_tool( checked, action, self.__partDissolveTool, msg=tr( 'Unisci le PARTICELLE' ), snapping=False )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleDifference(self, checked, action):
        """ Difference PARTICELLE features dinamically """
        
        # init
        plugin = self.plugin
        
        # test if tool is checkable        
        if not plugin.checkable_tool( checked, action, self.__partDifferenceTool ):
            return
        
        # get source vector layers
        vlayers = plugin.get_cmd_layers( 'diffParticelle' )
        if not vlayers:
            return
        
        # check if active layer is a command layer
        currLayer = plugin.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get diff layers
        vDiffLayers = []
        
        # instance tool
        if self.__partDifferenceTool is None:
            self.__partDifferenceTool = DifferenceSuoliTool( 
                plugin.iface, 
                currLayer,
                suoliRefLayers=vDiffLayers,
                suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                snapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE, 
                suoliSnapLayers=QGISAgriLayers.get_data_source_uri( vlayers ),
                msgTitle=plugin.name )
            
        # initialize tool and add to canvas
        self.__partDifferenceTool.initialize( currLayer, suoliRefLayers=vDiffLayers )
        plugin.run_tool( checked, action, self.__partDifferenceTool, msg=tr( 'Ritaglia una PARTICELLA per differenza con le altre' ), snapping=False )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleRepair(self, checked, action):
        """ Repair PARTICELLA feature """
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # test if tool is checkable        
        if not plugin.checkable_tool( checked, action, self.__partRepairTool ):
            return
        
        # get command layers
        vlayers = plugin.get_cmd_layers( 'repairParticelle' )
        if not vlayers:
            return
       
        # check if active layer is a command layer
        currLayer = plugin.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = controller.getCommandConfig( 'repairParticelle', layName )
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
            layer.beginEditCommand( 'repairParticelle' )
            res, errMsg, _ = QGISAgriLayers.repair_feature_single( 
                layer, 
                features[0], 
                attr_dict=attribs, 
                splitMultiParts=True,
                autoSnap=True,
                #suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO,
                suoliSnapTolerance=agriConfig.TOLERANCES.AUTO_SNAP_TOLERANCE,
                suoliSnapLayerUris=QGISAgriLayers.get_data_source_uri( vlayers ) )
       
            # end command
            layer.endEditCommand()
            
            # show warning
            if errMsg:
                logger.msgbar( logger.Level.Warning, errMsg, title=plugin.name )
            
            # update layer
            QGISAgriLayers.update_layers( [ layer ] )
            
        
        # instance tool
        if self.__partRepairTool is None:
            self.__partRepairTool = SelectFeatureTool( plugin.iface, [currLayer], single=True )
            
        # initialize tool and add to canvas
        self.__partRepairTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        plugin.run_tool( checked, action, self.__partRepairTool, msg=tr( 'Ripara PARTICELLA' ) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleRepairAll(self, checked, action):
        """ Repair all PARTICELLE features """

        # init
        plugin = self.plugin
        controller = plugin.controller

        # enable action
        action.setChecked( False )
       
        # get command layers
        vlayers = plugin.get_cmd_layers( 'repairAllParticelle' )
        if not vlayers:
            return
       
        # check if active layer is a command layer
        currLayer = plugin.iface.activeLayer()
        if currLayer not in vlayers:
            return
        
        # get layer name
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        # get config
        attribs = {}
        cmd_cfg = controller.getCommandConfig( 'repairParticelle', layName )
        fld_lst = cmd_cfg.get( 'wrkFields', [] )
        for fld_def in fld_lst:
            if 'setValue' not in fld_def:
                continue
            fld_name = fld_def.get( 'name', '' )
            fld_value = fld_def.get( 'setValue', None )
            attribs[fld_name] = fld_value
                    
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
                    suoliSnapLayerUris=QGISAgriLayers.get_data_source_uri( vlayers ) )
                
        # update layer
        QGISAgriLayers.update_layers( [ currLayer ] )
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onCloneCxfParticella(self, checked, action):
        """Clone an existing CXF feature to PARTICELLE layer"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # test if tool is checkable        
        if not plugin.checkable_tool( checked, action, self.__cloneCxfPartTool ):
            return
        
        # get command layers
        selVectlayers, _ = plugin.event_controller.get_cxf_layers()
        if not selVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer CXF presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        
        # get destination layers
        destVectlayers = controller.get_suolo_vector_layers('cloneParticellaCxf')
        if not destVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer SUOLO associato al comando.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
            
        # check if active layer is a command layer
        currLayer = plugin.iface.activeLayer()
        if currLayer not in destVectlayers:
            action.setChecked( False )
            return
        
        # get copy field definition and destinationlayer
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        cmd_cfg = controller.getCommandConfig( 'cloneParticellaCxf', layName )
        fld_copy_lst = cmd_cfg.get( 'wrkFields', [] )
        
        # show selection layers
        QGISAgriLayers.hide_layers( selVectlayers, hide=False )
        
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # check if left button
            if mouseBtn == Qt.LeftButton:
                # clone feature
                action.setChecked( False )
                currLayer.beginEditCommand( 'clone_particellacxf' )
                defaultAttributes = None #controlbox.currentFoglioFilterData
                QGISAgriLayers.clone_features( currLayer, features, fld_copy_lst, defaultAttributes )
                currLayer.endEditCommand()
                # update canvas
                ##QGISAgriLayers.hide_layers( [layer] )
                QGISAgriLayers.update_layers( destVectlayers )
            # restart action
            action.trigger()
        
        
        # instance tool
        if self.__cloneCxfPartTool is None:
            self.__cloneCxfPartTool = SelectFeatureTool( 
                plugin.iface, selVectlayers, single=True, unsetMapToolOnSelect=True )
            
        # initialize tool and add to canvas
        self.__cloneCxfPartTool.initialize( selVectlayers, onSelectFeature=onSelectFeature )
        plugin.run_tool( checked, action, self.__cloneCxfPartTool, msg=tr( 'Clona Particella CXF' ) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onCloneSuoloParticella(self, checked, action):
        """Clone an existing Suolo feature to PARTICELLE layer"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # test if tool is checkable        
        if not plugin.checkable_tool( checked, action, self.__cloneSuoloPartTool ):
            return
        
        # get command layers
        selVectlayers = controller.get_suolo_vector_layers('cloneSuoloParticella|sel')
        if not selVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer Suolo presente in mappa.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
        
        # get destination layers
        destVectlayers = QGISAgriLayers.get_vectorlayer( self.mainLayerUri )
        if not destVectlayers:
            logger.msgbox(
                logger.Level.Critical, tr('Nessun layer SUOLO associato al comando.'), title=tr('ERRORE'))
            action.setChecked( False )
            return
            
        # check if active layer is a command layer
        currLayer = plugin.iface.activeLayer()
        if currLayer not in destVectlayers:
            action.setChecked( False )
            return
        
        # get copy field definition and destinationlayer
        provider = currLayer.dataProvider()
        uri = provider.uri()
        layName = uri.table() or currLayer.name()
        
        cmd_cfg = controller.getCommandConfig( 'cloneSuoloParticella', layName )
        fld_copy_lst = cmd_cfg.get( 'wrkFields', [] )
        
        # show selection layers
        QGISAgriLayers.hide_layers( selVectlayers, hide=False )
        
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # check if left button
            if mouseBtn == Qt.LeftButton:
                # get feature
                feature = features[0]
                # clone feature
                action.setChecked( False )
                currLayer.beginEditCommand( 'clone_suoloParticella' )
                defaultAttributes = None
                newFeatures = QGISAgriLayers.clone_features( currLayer, [feature], fld_copy_lst, defaultAttributes )
                if newFeatures:
                    # show attribute form
                    res = plugin.iface.openFeatureForm( currLayer, newFeatures[0], showModal=True )
                    if not res:
                        # rollback for user cancel
                        currLayer.destroyEditCommand()
                    else:
                        # commit command
                        currLayer.endEditCommand()
                else:
                    # rollback for error
                    currLayer.destroyEditCommand()
                # update canvas
                QGISAgriLayers.update_layers( destVectlayers )
            # restart action
            action.trigger()
        
        
        # instance tool
        if self.__cloneSuoloPartTool is None:
            self.__cloneSuoloPartTool = SelectFeatureTool( 
                plugin.iface, selVectlayers, single=True, unsetMapToolOnSelect=True )
            
        # initialize tool and add to canvas
        self.__cloneSuoloPartTool.initialize( selVectlayers, onSelectFeature=onSelectFeature )
        plugin.run_tool( checked, action, self.__cloneSuoloPartTool, msg=tr( 'Clona Particella da geometria Suolo' ) )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onParticelleIdentify(self, checked, action):
        """Identify PARTICELLLA feature"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # test if tool is checkable
        if not plugin.checkable_tool( checked, action, self.__partIdentifyTool ):
            return
        
        # get command layers
        vlayers = plugin.get_cmd_layers( 'identityParticella' )
        if not vlayers:
            return
                    
        # callback function
        def onSelectFeature(layer, features, mouseBtn):
            # get single feature
            feature = features[0]
            # show suolo attributes form
            plugin.iface.openFeatureForm( layer, feature, showModal=True )
            #layer.removeSelection()
        
        
        # instance tool to select a feature
        if self.__partIdentifyTool is None:
            self.__partIdentifyTool = SelectFeatureTool( plugin.iface, vlayers, single=True )
            plugin.layerWillBeRemoved.connect( self.__partIdentifyTool.onLayerWillBeRemoved )
            
        # initialize tool and add to canvas
        self.__partIdentifyTool.initialize( vlayers, onSelectFeature=onSelectFeature )
        plugin.run_tool( checked, action, self.__partIdentifyTool, msg=tr( 'Modifica attributi PARTICELLA' ) )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def beforeParticelleEditingStarted(self, layer):
        """Check layer before editing"""
        # init
        layer.setProperty( self.COMMIT_PARTICELLE_LAYER_PROP, False )
        self.__updateLayerFeatureCountLst = []
        # hide control panel
        if self.plugin.autoHideControlbox:
            self.plugin.showControlBox( hide=True )
            
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def beforeParticelleCommitChanges(self, layer):
        """Check layer before commit changes"""
        # init
        layer.setProperty( self.COMMIT_PARTICELLE_LAYER_PROP, True )
        
        # collect modified feature id
        editBuffer = layer.editBuffer()
        if editBuffer is not None:
            editPartFids = []
            
            for fid, _ in editBuffer.changedGeometries().items():
                editPartFids.append( fid )
                
            for fid, _ in editBuffer.addedFeatures().items():
                editPartFids.append( fid )
                
            for fid, _ in editBuffer.changedAttributeValues().items():
                editPartFids.append( fid )
               
            editPartFids = list( dict.fromkeys( editPartFids ) )
            
            layerId = layer.id()
            self.__edit_part_fids[layerId] = [layer.getFeature(fid) for fid in editPartFids]
        
        # emi signal
        self.plugin.emit_check_editing()
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def afterParticelleCommitChanges(self, layer):
        """Check layer after commit changes"""
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # get particelle layers
        vlayers = controller.get_suolo_vector_layers('editingParticelle', sort_attr='editorder')
        
        # check if all layer committed
        for layer in vlayers:
            if layer.isEditable():
                return 
            
        # create 'suoli no cond corrotti' over worked 'particella no cond'
        def callbackFn():
            # create suoli from edited particelle
            layerId = layer.id()
            features = self.__edit_part_fids.get( layerId, [] )
            self.createSuoliOverWorkedParticella( layer, features, createOnlyNoCondSuoli=False )
            if features: 
                del self.__edit_part_fids[layerId]
        
        QTimer.singleShot( 500, callbackFn )
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def editingParticelleStopped(self, layer):
        """Editing stopped"""
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # check if edit commit
        if layer.property( self.COMMIT_PARTICELLE_LAYER_PROP ):
            # update controbox
            plugin.controlbox.updateOffLineControls() 
        
        # update feature counts in TOC
        if self.__updateLayerFeatureCountLst:    
            QGISAgriLayers.update_layers_renderer( self.__updateLayerFeatureCountLst )
        self.__updateLayerFeatureCountLst = []
        
        # update feature counts in TOC
        QGISAgriLayers.update_layers_renderer( [layer] )
            
        # restore control panel
        if plugin.autoHideControlbox:
            plugin.showControlBox()
            
        if Qgis.QGIS_VERSION_INT < 31600:
            if layer.property( self.COMMIT_PARTICELLE_LAYER_PROP ):
                self.afterParticelleCommitChanges( layer )
            
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _storeModParticelleFeaturesIds(self, layer, fid):
        """Stores new suoli feature Id"""
        layerId =  layer.id()
        if layerId not in self.__added_part_features:
            self.__added_part_features[layerId] = []
        self.__added_part_features[layerId].append( fid )
        
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def _clearModParticelleFeaturesIds(self, layer):
        """Stores new suoli feature Id"""
        layerId =  layer.id()
        try:
            self.__added_part_features[layerId].clear()
        except KeyError:
            pass
        
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _updateModParticelleFeatures(self, layer):
        """Update new suoli features"""
        fids = None
        try:
            layerId =  layer.id()
            fids = self.__added_part_features.get( layerId, None )
            if fids:
                self._updateParticelleFeaturesFlags( layer, fids, chkCommand=False, chkGeom=True )
        finally:
            self._clearModParticelleFeaturesIds( layer )
            
    # --------------------------------------
    # 
    # --------------------------------------         
    def _updateParticelleFeaturesFlags(self, layer, fids, chkCommand=True, chkGeom=False):
        """Update/correct suoli flags"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # chek if procedure is enabled
        if not self.__partEnableUpdateFlags:
            return
        
        # check if offline
        if not controller.isOfflineDb:
            return
        
        
        # check if layer in editing
        if not layer.isEditable():
            return
        
        # check if there's an active command (trick to skip undo\redo cycle) 
        if chkCommand and not layer.isEditCommandActive():
            return
        
        # feature attributes to set
        attribs = {}
        
        # get tolerances
        particellaMinArea = agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO
        
        # get repair suolo config
        uri = QgsDataSourceUri( layer.dataProvider().dataSourceUri() )
        cmd_cfg = controller.getCommandConfig( 'updateFlagParticella', uri.table() )
        #lay_filter = cmd_cfg.get( 'layFilter', '' ) or ''
        fld_lst = cmd_cfg.get( 'wrkFields', [] ) or []
        
        # list of invalid feature geometries
        invalidGeoFeatures = []
        smallGeoFeatures = []
        refValues = {}
        
        # loop features
        for fid in fids:
            # get feature instance
            feature = layer.getFeature( fid )
            
            #TODO - replace withe checker method
            # check if valid geometry 
            refValues['_flagInvalido'] = 0
            geom = feature.geometry()
            if geom.isEmpty() or not geom.isGeosValid():
                refValues['_flagInvalido'] = 1
                invalidGeoFeatures.append( fid )
                
            elif geom.area() < particellaMinArea:
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
                
                """
                # get new value
                fld_skippable = fld_def.get( 'skippable', False )
                if self.__skipPartLavoratoFeatureFid and \
                   fid in self.__skipPartLavoratoFeatureFid and \
                   fld_skippable:
                    continue
                """
                
                # skip valorized field
                fld_skipValorized = fld_def.get( 'skipValorized', False )
                if fld_skipValorized and feature.attribute( field_ndx ) != NULL:
                    continue
                
                # set value
                value = refValues.get( fld_def.get( 'refName', '' ), fld_def.get( 'setValue' ) )
                attribs[field_name] = value
        
            # update feature attributes
            if attribs:
                # assign attributes to feature
                # loop dictionaty of attributes
                try:
                    self.__partEnableUpdateFlags = False 
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
                    self.__partEnableUpdateFlags = True
        
        # log message on invalid features
        if chkGeom and invalidGeoFeatures:
            logger.msgbar( logger.Level.Warning, 
                           "'{0}' {1}".format( layer.name(), tr( "Presenti delle particelle con geometrie invalide" ) ),
                           title=plugin.name )
            
        if chkGeom and smallGeoFeatures:
            logger.msgbar( logger.Level.Warning, 
                           "'{}' {} {:.3f} mq".format( layer.name(), tr( "Presenti delle particelle con area minore di" ), particellaMinArea ),
                           title=plugin.name )
        
    # --------------------------------------
    # 
    # --------------------------------------  
    def connectParticelleEditing(self, layer):
        """Connect layer editing signals"""
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        
        # check if plugin layer and foglio loaded
        foglioFilterData = plugin.controlbox.currentFoglioFilterData
        if foglioFilterData is None and controller.checkIfPluginLayer( layer ):
            # disable layer
            layer.setReadOnly( True )
            logger.msgbar( logger.Level.Warning, 
                           "'{0}' {1}".format( layer.name(), tr( " in sola lettura! (Caricare un foglio dal pannello di controllo)" ) ),
                           title=plugin.name )
        
        # check if PARTICELLE working is enabled
        ###if not self.isParticelleWorkingEnabled:
        ###    return
        
        # check if main suolo layer
        if not QGISAgriLayers.is_requested_vectorlayer( layer, self.__part_main_layer_uri ):
            return
        
        # check if already connected
        if layer.property( self.MAIN_PARTICELLE_LAYER_PROP ):
            return
        layer.setProperty( self.MAIN_PARTICELLE_LAYER_PROP, True )
        
        ##############################################################
        
        # connect signals
        signalUtil.connectUniqueSignal( layer, layer.beforeEditingStarted, lambda: self.beforeParticelleEditingStarted( layer ) )
        signalUtil.connectUniqueSignal( layer, layer.editingStopped, lambda: self.editingParticelleStopped( layer ) )
        signalUtil.connectUniqueSignal( layer, layer.afterRollBack, lambda: self.editingParticelleStopped( layer ) )
        signalUtil.connectUniqueSignal( layer, layer.beforeCommitChanges, lambda: self.beforeParticelleCommitChanges( layer ) )
        if Qgis.QGIS_VERSION_INT >= 31600:
            signalUtil.connectUniqueSignal( layer, layer.afterCommitChanges, lambda: self.afterParticelleCommitChanges( layer ) ) 
         
        signalUtil.connectUniqueSignal( layer, layer.featureAdded, lambda fid: self._storeModParticelleFeaturesIds( layer, fid ) )
        signalUtil.connectUniqueSignal( layer, layer.editCommandStarted, lambda: self._clearModParticelleFeaturesIds( layer ) )
        signalUtil.connectUniqueSignal( layer, layer.editCommandEnded, lambda: self._updateModParticelleFeatures( layer ) )
          
        signalUtil.connectUniqueSignal( layer, layer.attributeValueChanged, lambda fid: self._updateParticelleFeaturesFlags( layer, [fid] ) )  
        signalUtil.connectUniqueSignal( layer, layer.geometryChanged, lambda fid: self._updateParticelleFeaturesFlags( layer, [fid] ) )  
        
        ##############################################################
        
        # define/init custom form
        ####self._set_custom_forms( layer )
        
        ##############################################################
        
        # collect 'suoli bloccati' feature geometries
        if layer.isEditable():
            self.beforeParticelleEditingStarted( layer )  
        
        
    # --------------------------------------
    # 
    # --------------------------------------          
    def disconnectParticelleEditing(self):
        """Disconnect layer editing signals"""
        
        vlayers = QGISAgriLayers.get_vectorlayer( self.__part_main_layer_uri )
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
            if Qgis.QGIS_VERSION_INT >= 31600:
                signalUtil.disconnectUniqueSignal( layer, layer.afterCommitChanges)  
            # reset the form used to represent this vector layer
            #####layer.setEditFormConfig( QgsEditFormConfig() )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def createSuoliOverWorkedParticella(self, layer, features, createOnlyNoCondSuoli=False):
        """
        Method to create 'suoli no cond corrotti' from 'suoli no cond' 
        that ovelaps worked 'particelle no cond'. 
        """
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        if not features:
            return False
            
        try:
            lst_close_edit_lays = []
            
            # get 'Particelle' layer
            selVectlayers = plugin.get_cmd_layers( 'suoliCondParticella|sel' )
            if not selVectlayers:
                logger.msgbox(
                    logger.Level.Critical, 
                    tr('Nessun layer PARTICELLA presente in mappa.'), 
                    title=tr('ERRORE') )
                return False
            partVectLayer = selVectlayers[0]
            
            # get "Suoli no cond" layers
            noCondVectlayers = plugin.get_cmd_layers( 'suoliCondParticella|nocond' )
            if not noCondVectlayers:
                logger.msgbox(
                    logger.Level.Critical, 
                    tr('Nessun layer Suoli non condotti presente in mappa.'), 
                    title=tr('ERRORE') )
                return False
            
            # get "Suoli no cond corrotti" layer
            destNoCondVectlayers = plugin.get_cmd_layers( 'suoliCondParticella|nocond|dest' )
            if not destNoCondVectlayers:
                logger.msgbox(
                    logger.Level.Critical, 
                    tr('Nessun layer Suoli non condotti presente in mappa.'), 
                    title=tr('ERRORE') )
                return False
            
            destNoCondVectlayer = destNoCondVectlayers[0]
            if not destNoCondVectlayer.isEditable():
                lst_close_edit_lays.append( destNoCondVectlayer )
            
            # get "Suoli cond" layer
            destVectlayers = plugin.get_cmd_layers( 'suoliCondParticella|dest' )
            if not destVectlayers:
                logger.msgbox(
                    logger.Level.Critical, 
                    tr('Nessun layer Suoli condotti presente in mappa.'), 
                    title=tr('ERRORE') )
                return False
            
            destVectlayer = destVectlayers[0]
            if not destVectlayer.isEditable():
                lst_close_edit_lays.append( destVectlayer )
            
            # show result message
            logger.msgbar( 
                logger.Level.Info, 
                tr("Sistemazione dei suoli su particelle lavorate; attendere..."),
                title=plugin.name,
                clear=True )
            
            # override cursor 
            logger.setOverrideCursor( Qt.WaitCursor )
            
            # disable suoli 'Editing Stopped' Slot
            controller.enable_EditingStoppedSlot( enable=False )
            
            # create 'suoli no cond corrotti'
            res = False
            for feature in features:
                if controller.createSuoliCondParticella(
                        feature,
                        noCondVectlayers,
                        destNoCondVectlayer,
                        destVectlayer,
                        createOnlyNoCondSuoli=createOnlyNoCondSuoli ):
                    res = res or True
            
            # close layers
            if lst_close_edit_lays:
                QGISAgriLayers.end_editing_ext( lst_close_edit_lays, noMessage=True )
            
            if res:
                # show result message
                logger.msgbar( 
                    logger.Level.Warning, 
                    tr("Creati suoli su particelle lavorate da entità non condotte."),
                    title=plugin.name,
                    clear=True )
                
            # enable suoli 'Editing Stopped' Slot
            controller.enable_EditingStoppedSlot( enable=True, update_layers=[destVectlayer, destNoCondVectlayer] )
                
            return res
        
        except Exception as e:
            logger.msgbar( 
                logger.Level.Critical, 
                str(e), 
                title=tr('ERRORE'),
                clear=True )
            return False
        
        finally:
            # restore cursor
            logger.restoreOverrideCursor()
            # enable editing stopped slot
            controller.enable_EditingStoppedSlot()

    
        
    # --------------------------------------
    # 
    # --------------------------------------
    def onUploadEventoLavorazione(self, cfg_fields_tot, out_layer_name, fileWriter, layerVirtualizer) -> bool:
        """ Upload done work list """
        
        # init
        plugin = self.plugin
        controller = plugin.controller
        controlbox = plugin.controlbox
        cfgPartLav = agriConfig.services.ParticelleLavorazioni
        cfgFogliAzienda = agriConfig.services.fogliAziendaOffline
        cfg_fields_tot = cfg_fields_tot or {}
        if not self.isParticelleWorkingEnabled:
            return cfg_fields_tot
        
        # define function to calculate output attributes
        areaFn = lambda feat,value : feat.geometry().area()
        
        # get command configuration
        cmd_salva_cfg = controller.getCommandConfig( 'salvasuoli' )
        att_check_cfg = cmd_salva_cfg.get( 'checkParticelleFields', {} )
        fld_def = att_check_cfg.get( 'flagCessato', {} )
        fld_cessato_filter = fld_def.get( 'filter', '' ) ## COALESCE(flagCessato,0) = 1
        featureSelExpr = f"NOT ({fld_cessato_filter})" if fld_cessato_filter else '' ## NOT (COALESCE(flagCessato,0) = 1)
        padre_id_cfg = cmd_salva_cfg.get( 'padreRelation', {} )
        lavorato_fld = padre_id_cfg.get( 'lavField', '' )
        sospeso_fld = padre_id_cfg.get( 'sspField', '' )
        modif_val = padre_id_cfg.get( 'modValue', 1 )
        idFeature_fld = padre_id_cfg.get( 'srcField', '' )
            
        # get PARTICELLE layers
        partLayers = QGISAgriLayers.get_vectorlayer( self.mainLayerUri )
        if not partLayers:
            raise Exception( tr( "Nessun layer PARTICELLE associato al comando SalvaSuoli" ) )
        
        # loop PARTICELLE layers
        for layer in partLayers:
            # get suolo layer name
            partLayerId = layerVirtualizer.getVirtualId( layer )
            partLayer = layer.clone()
            partLayer.setSubsetString( None )
                        
            # count features removed
            totRemFeatures = 0
            for _ in partLayer.getFeatures( fld_cessato_filter ):
                totRemFeatures += 1            
                        
            ######################################################################################
            # 1) add removed features
            if totRemFeatures:
                cfg_fields = {
                    'idFeature': { 'type': 'Int', 'suolo_key_field': True },
                    'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                    'layer': { 'type': 'String', 'value': 'PARTICELLE_CESSATE' }
                }
                cfg_fields['idEventoLavorazione']['value'] = controller.idEventoLavorazione
                cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
                
                # export features to temp file
                fileWriter.writeLayer( partLayer,
                                       out_layer_name,
                                       cfg_fields,
                                       featureSelExpr = fld_cessato_filter,
                                       skipEmptyGeom = True,
                                       skipNullKeyField = True ) ## COALESCE(cessato,0) = 1
                                       
                                       
            ######################################################################################        
            # 2) add worked features
            
            ## NOT (COALESCE(cessato,0) = 1) AND (flagLavorato = '1' OR flagSospensione = '1')
            featureLavorateExpr = f"{featureSelExpr} AND ({lavorato_fld} = '{modif_val}' OR {sospeso_fld} = '{modif_val}')"
            featureModifiedExpr = f"{featureLavorateExpr} AND {idFeature_fld} IS NOT NULL"
            
            # 2.1)  add worked modified existing features
            cfg_fields = {
                'idFeature': { 'type': 'Int', 'suolo_key_field': True },
                'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                'layer': { 'type': 'String', 'value': 'PARTICELLE_CESSATE' }
            }
            cfg_fields['idEventoLavorazione']['value'] = controller.idEventoLavorazione
            cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
            
            # export features to file
            fileWriter.writeLayer( partLayer,
                                   out_layer_name,
                                   cfg_fields,
                                   featureSelExpr = featureModifiedExpr,
                                   skipEmptyGeom = True,
                                   skipNullKeyField = True )
            
            # 2.2)  add worked new features
            cfg_fields = {    
                'OGC_FID': { 'type': 'Int' },
                'OGC_LAYERID': { 'type': 'Int', 'value': 0 },
                'idFeature': { 'type': 'Int', 'value': NULL }, # <===== Set always NULL: if valorized, emitted as 'PARTICELLE_CESSATE'
                'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                'codiceNazionale': { 'type': 'String' },
                'foglio': { 'type': 'String' },
                'numeroParticella': { 'type': 'String' },
                'subalterno': { 'type': 'String' },
                'area':  { 'type': 'Double', 'value': 0.0 },
                'flagConduzione': { 'type': 'String' },
                'flagSospensione': { 'type': 'Bool'  },
                'descrizioneSospensione': { 'type': 'String' },
                'noteLavorazione': { 'type': 'String', 'value': '' },
                'idTipoMotivoSospensione': { 'type': 'Int' },
                'layer': { 'type': 'String', 'value': 'PARTICELLE_LAVORATE' }
            }
            
            cfg_fields['idEventoLavorazione']['value'] = controller.idEventoLavorazione
            cfg_fields['OGC_LAYERID']['value'] = partLayerId
            cfg_fields['codiceNazionale']['value'] = controlbox.currentFoglioData.get( cfgFogliAzienda.codNazionaleField, '' )
            cfg_fields['foglio']['value'] = controlbox.currentFoglioData.get( cfgFogliAzienda.foglioField, '' )
            cfg_fields['area']['value'] = areaFn
            cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
            
            
            # export features to upload
            fileWriter.writeLayer( partLayer,
                                   out_layer_name,
                                   cfg_fields,
                                   featureSelExpr = featureLavorateExpr )
            
        ######################################################################################        
        # 3) add single suspended PARTICELLE work items (no features)
        
        part_data_rows = controller.getDbTableData( 
            cfgPartLav.view, 
            filterExpr = f"{cfgPartLav.statoLavPartField} = {cfgPartLav.statoLavPartSuspendItemValue}" 
        )
        if part_data_rows:
            # create a fictitious geometry
            partLayer = partLayers[0]
            ext_rect = partLayer.extent()
            for layer in partLayers:
                ext_rect.combineExtentWith( layer.extent() )
            
            # define output attributes
            cfg_fields = {    
                'OGC_FID': { 'type': 'Int' },
                'idFeature': { 'type': 'Int' },
                'idEventoLavorazione':  { 'type': 'Int', 'value': 0 },
                'idParticellaLavorazione':  { 'type': 'Int', 'value': 0 },
                'codiceNazionale': { 'type': 'String' },
                'foglio': { 'type': 'String' },
                'numeroParticella': { 'type': 'String' },
                'subalterno': { 'type': 'String' },
                'area':  { 'type': 'Double', 'value': 0.0 },
                'flagConduzione': { 'type': 'String', 'value': 'S' },
                'flagSospensione': { 'type': 'Bool'  },
                'descrizioneSospensione': { 'type': 'String' },
                'noteLavorazione': { 'type': 'String', 'value': '' },
                'idTipoMotivoSospensione': { 'type': 'Int' },
                'layer': { 'type': 'String', 'value': 'PARTICELLE_SOSPESE' }
            }
            cfg_fields['idEventoLavorazione']['value'] = controller.idEventoLavorazione
            cfg_fields['codiceNazionale']['value'] = controlbox.currentFoglioData.get( cfgFogliAzienda.codNazionaleField, '' )
            cfg_fields['foglio']['value'] = controlbox.currentFoglioData.get( cfgFogliAzienda.foglioField, '' )
            cfg_fields['area']['value'] = ext_rect.area()
            cfg_fields_tot = jsonUtil.concatFldDefDict( cfg_fields_tot, cfg_fields )
            
            # loop rows
            for row in part_data_rows:
                # valorize output attributes
                cfg_fields['numeroParticella']['value'] = row.get( cfgPartLav.numParticellaField, None )
                cfg_fields['subalterno']['value'] = row.get( cfgPartLav.subalternoField, None )
                cfg_fields['flagSospensione']['value'] = 1
                cfg_fields['descrizioneSospensione']['value'] = row.get( cfgPartLav.descSospensioneField, None )
                cfg_fields['idParticellaLavorazione']['value'] = row.get( cfgPartLav.idParticellaLavorazione, None )
                
                # export feature to upload
                fileWriter.writeFictitiousFeature( partLayer, out_layer_name, cfg_fields, extent=ext_rect )
                
        
        return cfg_fields_tot
        
    
        