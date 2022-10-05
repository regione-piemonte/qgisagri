# -*- coding: utf-8 -*-
"""Modulo per la selezione dei profili di configurazione del plugin.

Descrizione
-----------

Implementazione della classe che permette di selezionare un profilo di
configurazione del plugin tramite finetra di dialogo; richiamato da specifica
voce del sottomenù delle opzioni del plugin. 

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
# system modules
import os.path

# qgis modules
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

# Import plugin modules
from qgis_agri import agriConfig, tr
from qgis_agri.log.logger import QgisLogger as logger


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_profiles_dialog.ui'))
 

# QGISAgri error dialog
#-----------------------------------------------------------
class QGISAgriProfilesDialog(QtWidgets.QDialog, FORM_CLASS): 
    """ Plugin profiles dialog """
    
    # --------------------------------------
    # signals 
    # --------------------------------------  
    profileChanged = pyqtSignal(str)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, plugin, parent=None):
        """Constructor
        
        :param parent: 
        :type parent: QtWidgets
        """
        self.plugin = plugin
        self.profileName = ''
        
        #
        super().__init__( parent=parent )
        
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        # set dialog properties
        self.setModal( True )
        
        # connect signals
        self.buttonBox.clicked.connect( self.onButtonBoxClicked )
        
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def show(self):
        """"""
        # read profiles config
        cfgProfiles, cfgDefProfile = self.get_profile_config()
        self.profileName = self.plugin.profile or cfgDefProfile
        
        # set profiles combo
        self.cmbProfiles.clear()
        self.cmbProfiles.addItems( list(cfgProfiles.keys()) )
        index = self.cmbProfiles.findText( self.profileName )
        self.cmbProfiles.setCurrentIndex( index )
        
        #
        super().show()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def get_profile_config(self):
        """ Get profile from config file """
        # read plugin profiles config
        cfgObj = agriConfig.loadOtherConfig( agriConfig.CFG_PROFILE_FILE_NAME )
        cfgEntry = cfgObj.get_value( 'plugin', {} )
        cfgProfiles = cfgEntry.get( 'profiles', {} )
        if len(cfgProfiles) < 1:
            logger.msgbox( logger.Level.Critical, 
                           tr('Nessun profilo definito nel file di configurazione'), 
                           title=tr('ERRORE') )
            return
        
        # get default profile
        cfgDefaultProfile = cfgEntry.get( 'default', '' )
        if cfgDefaultProfile not in cfgProfiles:
            cfgDefaultProfile = list(cfgProfiles.keys())[0]
            
        # return profiles dictionary and default profile key
        return cfgProfiles, cfgDefaultProfile
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __del__(self):
        """Destructor"""
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def onButtonBoxClicked(self, button):
        """On buttonbox clicked slot"""
        if button == self.buttonBox.button( QtWidgets.QDialogButtonBox.Ok ):
            selProfile = self.cmbProfiles.currentText()
            if selProfile != self.profileName or\
               self.plugin.freezed:
                self.profileName = selProfile
                self.profileChanged.emit( self.profileName )
        
        
    