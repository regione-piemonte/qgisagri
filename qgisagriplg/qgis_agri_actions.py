# -*- coding: utf-8 -*-
"""Classi per la gestione di specifiche azioni del plugin 

Descrizione
-----------

Implementazioni di specifiche classi di azioni per gestire i vari eventi dell'interfaccia del plugin:

- cambio di stato di lavorazione;
- autenticazione;
- scarico e inizio di lavorazione di un foglio;
- salvataggio sul server remoto di un foglio lavorato;
- rilascio e annullamento di un foglio in lavorazione;
- gestione dello stato dei componenti delle toolbar e menù in base al layer corrente;
- gestione dello stato dei componenti delle toolbar e menù in fase di editazione.

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
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.utils import iface

from qgis_agri import tr
from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.qgis_agri_roles import QGISAgriFunctionality


# 
#-----------------------------------------------------------
class QGISAgriActionData():
    def __init__(self, suppress_msg=False):
        self.suppress_msg = suppress_msg

# 
#-----------------------------------------------------------
class QGISAgriActionBase(QAction):
    """Specialized QAction for authentication."""
    
    # signals
    actionIsEnabled = pyqtSignal(bool)
    actionIsVisible = pyqtSignal(bool)
    
    # enumeration
    from enum import Enum
    class action_type(Enum):
        NONE = 0
        STATUS = 1
        AUTHENTICATION = 2
        STARTING = 3
        DOWNLOAD = 4
        UPLOAD = 5
        LAYER = 6
        LAYER_NO_EDIT_MODE = 7
        EDITING = 8
        OFFLINE = 9
        REJECT = 10
        LAYER2 = 666
        
    class enable_type(Enum):
        NONE = 0
        INLINE = 1
        OFFLINE = 2
        OFFLINEFOGLIO = 3
         
    # --------------------------------------
    # 
    # --------------------------------------     
    @staticmethod    
    def factory(action_type, functionality, data, *args):
        
        if action_type == QGISAgriActionBase.action_type.STATUS:
            return QGISAgriStatusAction(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.AUTHENTICATION:
            return QGISAgriAuthAction(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.OFFLINE:
            return QGISAgriOfflineAction(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.STARTING:
            return QGISAgriStartAction(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.DOWNLOAD:
            return QGISAgriDownloadAction(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.UPLOAD:
            return QGISAgriUploadAction(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.REJECT:
            return QGISAgriRejectAction(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.LAYER:
            return QGISAgriLayerAction(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.LAYER2:
            return QGISAgriLayerAction2(functionality, data, *args)
        
        elif action_type == QGISAgriActionBase.action_type.LAYER_NO_EDIT_MODE:
            a = QGISAgriLayerAction(functionality, data, *args)
            a.setEditMode(False)
            return a
        
        elif action_type == QGISAgriActionBase.action_type.EDITING:
            return QGISAgriEditingAction(functionality, data, *args)
        
        else:
            return QGISAgriActionBase(functionality, data, *args)
            
    # --------------------------------------
    # 
    # --------------------------------------         
    @property
    def disabled(self):
        """Returns true if disabled"""
        return self.__disabled
        
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def task(self):
        """Returns associated task"""
        return self.__task
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def offlineEnable(self):
        """Returns associated task"""
        return self.__offlineEnable
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QAction.__init__(self, *args)
        self.__task = None
        self.__functionality = functionality if isinstance( functionality, QGISAgriFunctionality ) else None
        self.__disabled = False
        self.__origtext = self.text()
        self.__visibleOffline = None
        self.__offlineEnable = QGISAgriActionBase.enable_type.NONE
        self.__visibleByLayer = False
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        pass
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def forceDisable(self, disable, add_tip_msg=None):
        self.__disabled = disable
        if disable and add_tip_msg:
            self.setToolTip( f"{self.__origtext}<p style='background-color: yellow'>{add_tip_msg}</p>" )
        else:
            self.setToolTip( self.__origtext )
        self._enable()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setTask(self, task):
        self.__task = task
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def setOfflineEnable(self, enableType):
        self.__offlineEnable = enableType
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def getOfflineEnable(self, offlineLavorazione, offlineFoglio, default=False):
        if self.offlineEnable == QGISAgriActionBase.enable_type.NONE:
            return default
        
        offlineLavorazione = bool(offlineLavorazione)
        offlineFoglio = bool(offlineFoglio)
        if self.offlineEnable == QGISAgriActionBase.enable_type.INLINE:
            return ( not offlineLavorazione and not offlineFoglio )
        elif self.offlineEnable == QGISAgriActionBase.enable_type.OFFLINE:
            return  offlineLavorazione
        elif self.offlineEnable == QGISAgriActionBase.enable_type.OFFLINEFOGLIO:
            return (offlineLavorazione and offlineFoglio)
        else:
            return default
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def setVisibleOffline(self, visible):
        self.__visibleOffline = visible
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def setOfflineVisibility(self, offline):
        if self.__visibleOffline is None:
            self.setVisible( True )
        elif not self.__visibleOffline:
            self.setVisible( not offline )
        else:
            self.setVisible( offline )
            
    # --------------------------------------
    # 
    # --------------------------------------     
    def enableVisibilityByLayer(self, enable):
        self.__visibleByLayer = enable
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def setLayerVisibility(self, visible):
        if self.__visibleByLayer:
            self.setVisible( visible )
            self.actionIsVisible.emit( visible )
            
    # --------------------------------------
    # 
    # --------------------------------------
    def setHidden(self, hidden):
        self.setVisible( not hidden )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        if self.__functionality is None:
            return
        
        self.__disabled = not role.isfunctionalityEnabled( self.__functionality )
        if self.__disabled:
            self.setToolTip( "{0}<p style='background-color: yellow'>{1}</p>".format( self.__origtext, tr( 'Disabilitato per il ruolo attuale' ) ) )
        else:
            self.setToolTip( self.__origtext )
            
    # --------------------------------------
    # 
    # --------------------------------------  
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        pass
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onStart(self, started):
        """Activation slot method."""
        pass
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onLayer(self, layer):
        """Activation on layer slot method."""
        pass
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onDownload(self, enable, task):
        """Activation on download slot method."""
        pass
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onUpload(self, enable):
        """Activation on upload slot method."""
        pass
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onReject(self, reject, task):
        """Activation on reject slot method."""
        pass
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onChecked(self):
        """Checked slot method."""
        pass
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDbRebase(self, database, offlineLavorazione, offlineFoglio):
        """Database rebase slot method."""
        pass
    
# 
#-----------------------------------------------------------
class QGISAgriStatusAction(QGISAgriActionBase):
    """Specialized QAction for authentication."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        pass
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        if authenticated:
            icon_path = ':/plugins/qgis_agri/images/action-auth-valid-icon.png'
        else:
            icon_path = ':/plugins/qgis_agri/images/action-auth-invalid-icon.png'
        self.setIcon( QIcon(icon_path) )

# 
#-----------------------------------------------------------        
class QGISAgriAuthAction(QGISAgriActionBase):
    """Specialized QAction for authentication."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        self.setEnabled( not self.disabled and self.__authenticated )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()


# 
#-----------------------------------------------------------        
class QGISAgriRejectAction(QGISAgriActionBase):
    """Specialized QAction for reject evento lavorazione."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        self.__reject = False
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        self.setEnabled( not self.disabled and self.__authenticated and self.__reject )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onReject(self, reject, task):
        """Activation on reject slot method."""
        if self.task == task:
            self.__reject = reject
        else:
            self.__reject = False
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDbRebase(self, database, offlineLavorazione, offlineFoglio):
        """Database rebase slot method."""
        self.__reject = self.getOfflineEnable( offlineLavorazione, offlineFoglio, self.__reject )
        self.setOfflineVisibility( offlineLavorazione )
        self._enable()
        
# 
#-----------------------------------------------------------        
class QGISAgriOfflineAction(QGISAgriActionBase):
    """Specialized QAction for authentication."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        self.__offline = False
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        self.setEnabled( not self.disabled and self.__authenticated and self.__offline )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDbRebase(self, database, offlineLavorazione, offlineFoglio):
        """Database rebase slot method."""
        self.__offline = offlineLavorazione
        self.setOfflineVisibility( offlineLavorazione )
        self._enable()

# 
#-----------------------------------------------------------
class QGISAgriStartAction(QGISAgriActionBase):
    """Specialized QAction for starting."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        self.__started = False
        self.__checkAuthenticated = False
        self.__layerIndipendent = False
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        if self.disabled:
            self.setEnabled( False )
            return
        #self.setEnabled( self.__authenticated and self.__started ) allow downloading even if not authenticated
        enabled = self.__started
        
        if not self.__layerIndipendent:
            curlayer = iface.activeLayer()
            enabled = (enabled and curlayer is not None)
        else:
            enabled = enabled
        
        if self.__checkAuthenticated:
            enabled = (enabled and self.__authenticated)
        
        # enable
        self.setEnabled( enabled )
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def setCheckAuthenticated(self, value):
        self.__checkAuthenticated = value
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def setLayerIndipendent(self, value):
        self.__layerIndipendent = value
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onStart(self, started):
        """Activation slot method."""
        self.__started = started
        self._enable()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onLayer(self, layer):
        """Activation on layer slot method."""
        self._enable()

# 
#-----------------------------------------------------------        
class QGISAgriDownloadAction(QGISAgriActionBase):
    """Specialized QAction for downloading lista lavorazione."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        self.__download = False
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        #self.setEnabled( self.__authenticated and self.__download ) allow downloading even if not authenticated
        self.setEnabled( not self.disabled and self.__download )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDownload(self, enable, task):
        """Activation on download slot method."""
        if task and self.task != task:
            enable = False
        self.__download = enable
        self._enable()

#-----------------------------------------------------------        
class QGISAgriUploadAction(QGISAgriActionBase):
    """Specialized QAction for uploading lista lavorazione."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        self.__upload = False
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        self.setEnabled( not self.disabled and self.__authenticated and self.__upload )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onUpload(self, enable):
        """Activation on upload slot method."""
        self.__upload = enable
        self._enable()
        
# 
#-----------------------------------------------------------        
class QGISAgriLayerAction(QGISAgriActionBase):
    """Specialized QAction for layer command."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        self.__started = False
        self.__selLayer = None
        self.__layDataSourceUri = data or []
        self.__editmode = True
        self.__stopOnDiffLayer = False
        self.__checkAuthenticated = False
        # update enable status
        self.onLayer( iface.activeLayer() )
        
    # --------------------------------------
    # 
    # --------------------------------------   
    def __del__(self):
        pass  
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _removeMapTool(self):
        # remove map tool
        mapTool = iface.mapCanvas().mapTool()
        if mapTool and mapTool.action() == self:
            if self.__editmode or self.__stopOnDiffLayer:
                iface.actionPan().trigger()
                self.setChecked( False )
            else:
                self.setChecked( True )
                
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _editingStarted(self):
        self._enable()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _editingStopped(self):
        self._enable()
        #if self.__editmode:
        self._removeMapTool()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        enabled = False
        visible = self.__selLayer is not None
        if (not self.disabled and
            self.__selLayer is not None and
            #self.__authenticated and allow editing even if not authenticated
            self.__started):
            
            enabled = True
            
            if self.__checkAuthenticated:
                enabled = self.__authenticated
            
            if self.__editmode:
                enabled = self.__selLayer.isEditable() 
           
        self.setEnabled( enabled )
        self.actionIsEnabled.emit( enabled )
        self.setLayerVisibility( visible )
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def forceDisable(self, disable, add_tip_msg=None):
        super().forceDisable( disable, add_tip_msg )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def setEditMode(self, value):
        self.__editmode = value
    
    # --------------------------------------
    # 
    # --------------------------------------         
    def setStopOnDiffLayer(self, value):
        self.__stopOnDiffLayer = value    
     
    # --------------------------------------
    # 
    # --------------------------------------         
    def setCheckAuthenticated(self, value):
        self.__checkAuthenticated = value
          
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onStart(self, started):
        """Activation slot method."""
        self.__started = started
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDbRebase(self, database, offlineLavorazione, offlineFoglio):
        """Database rebase slot method."""
        for dsUri in self.__layDataSourceUri:
            try:
                dsUri.setDatabase( database )
            except AttributeError:
                pass
                
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onLayer(self, layer):
        """Activation on layer slot method."""
        if layer != self.__selLayer:
            # remove map tool
            self._removeMapTool()
                
            self.__selLayer = None
            if layer is not None:     
                # check data provider uri
                if QGISAgriLayers.is_requested_vectorlayer( layer, self.__layDataSourceUri ):
                    self.__selLayer = layer
                    try:
                        layer.editingStarted.connect( self._editingStarted, Qt.UniqueConnection )
                    except TypeError:
                        pass 
                    try:
                        layer.editingStopped.connect( self._editingStopped, Qt.UniqueConnection )
                    except TypeError:
                        pass  
                    

        self._enable()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def changeRefLayers(self, layers):
        self.__layDataSourceUri = layers or []
        curlayer = iface.activeLayer()
        self.onLayer( curlayer )
# 
#-----------------------------------------------------------        
class QGISAgriLayerAction2(QGISAgriActionBase):
    """Specialized QAction for layer command."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        self.__started = False
        self.__selLayer = None
        self.__layDataSourceUri = data or []
        self.__layEditDataSourceUri = []
        self.__editmode = True
        # update enable status
        self.onLayer( iface.activeLayer() )
        
    # --------------------------------------
    # 
    # --------------------------------------   
    def __del__(self):
        pass  
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _removeMapTool(self):
        # remove map tool
        mapTool = iface.mapCanvas().mapTool()
        if mapTool and mapTool.action() == self:
            if self.__editmode:
                iface.actionPan().trigger()
                self.setChecked( False )  
            else:
                self.setChecked( True )
                
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _editingStarted(self):
        self._enable()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _editingStopped(self):
        self._enable()
        self._removeMapTool()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _connectEditLayers(self):
        lstLays = self.__layDataSourceUri if not self.__layEditDataSourceUri else self.__layEditDataSourceUri
        for layer in QGISAgriLayers.get_vectorlayer( lstLays ):
            try:
                layer.editingStarted.connect( self._editingStarted, Qt.UniqueConnection )
            except TypeError:
                pass 
            try:
                layer.editingStopped.connect( self._editingStopped, Qt.UniqueConnection )
            except TypeError:
                pass  
                
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        enabled = False
        if ( self.disabled or
             self.__selLayer is None or
             #not self.__authenticated and allow editing even if not authenticated
             not self.__started ):
            pass
        
        elif not self.__layEditDataSourceUri:
            # if no edit layer specified, test on declared
            enabled = self.__selLayer.isEditable() if self.__editmode else True
            
        else:
            for layer in QGISAgriLayers.get_vectorlayer( self.__layEditDataSourceUri ):
                if layer.isEditable():
                    enabled = True
                    break
            
        self.setEnabled( enabled )
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def setEditMode(self, value):
        self.__editmode = value
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def setEditLayers(self, layLst):
        if isinstance( layLst, list ):
            self.__layEditDataSourceUri = layLst
          
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onStart(self, started):
        """Activation slot method."""
        self.__started = started
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDbRebase(self, database, offlineLavorazione, offlineFoglio):
        """Database rebase slot method."""
        for dsUri in self.__layDataSourceUri:
            dsUri.setDatabase( database )
            
        for dsUri in self.__layEditDataSourceUri:
            dsUri.setDatabase( database )
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onLayer(self, layer):
        """Activation on layer slot method."""
        if layer != self.__selLayer:
            # remove map tool
            self._removeMapTool()
            
            self.__selLayer = None
            if QGISAgriLayers.is_requested_vectorlayer( layer, self.__layDataSourceUri ):    
                self.__selLayer = layer
                self._connectEditLayers()    
        self._enable()

# 
#-----------------------------------------------------------
class QGISAgriEditingAction(QGISAgriActionBase):
    """Specialized QAction for editing."""
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, functionality, data, *args):
        """Constructor""" 
        QGISAgriActionBase.__init__(self, functionality, data, *args)
        self.__authenticated = False
        self.__started = False
        self.__layDataSourceUri = data or []
        self.__selLayer = None
        # update enable status
        self.onLayer( iface.activeLayer() )
        
    # --------------------------------------
    # 
    # --------------------------------------  
    def __del__(self):
        pass     
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _editingStarted(self):
        self._enable()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _editingStopped(self):
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _checkEditing(self):
        # check if there's a layer on editing
        checked = False
        vlayers = QGISAgriLayers.get_vectorlayer(self.__layDataSourceUri)
        for lay in vlayers:
            if lay.isEditable():
                checked = True
                break
        self.setChecked(checked)
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _enable(self):
        """Private method to enable action"""
        #if (not self.__authenticated or not self.__started): allow editing even if not authenticated
        
        # visibility
        visible = self.__selLayer is not None
        self.setLayerVisibility( visible )
        
        # enable
        if (self.disabled or not self.__started):
            self.setEnabled(False)
            return     
        self.setEnabled(True)
        
        # check if there's a layer on editing
        self._checkEditing()
        
        
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onLayer(self, layer):
        """Activation on layer slot method."""
        self.__selLayer = None
        if QGISAgriLayers.is_requested_vectorlayer( layer, self.__layDataSourceUri ):    
            self.__selLayer = layer
        
        vlayers = QGISAgriLayers.get_vectorlayer(self.__layDataSourceUri)
        for lay in vlayers:
            try:
                lay.editingStarted.connect( self._editingStarted, Qt.UniqueConnection )
            except TypeError:
                pass 
            try:
                lay.editingStopped.connect( self._editingStopped, Qt.UniqueConnection )
            except TypeError:
                pass  
            #lay.editingStarted.connect( self._editingStarted )
            #lay.editingStopped.connect( self._editingStopped )
        self._enable()
        
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onRoleAuthenticated(self, role):
        """Role authentication slot method."""
        super().onRoleAuthenticated( role )
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onAuthenticated(self, authenticated):
        """Authentication slot method."""
        self.__authenticated = authenticated
        self._enable()
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def onStart(self, started):
        """Activation slot method."""
        self.__started = started
        self._enable()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onChecked(self):
        """Checked slot method."""
        self._checkEditing()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onDbRebase(self, database, offlineLavorazione, offlineFoglio):
        """Database rebase slot method."""
        for dsUri in self.__layDataSourceUri:
            dsUri.setDatabase( database )
    

