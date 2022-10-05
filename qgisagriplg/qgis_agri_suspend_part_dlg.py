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

# plugin modules
from qgis_agri import agriConfig

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_suspend_part_dialog.ui'))
 

# QGISAgri suspend 'LAVORAZIONE PARTICELLA' dialog
#-----------------------------------------------------------
class QGISAgriSuspendPartDialog(QtWidgets.QDialog, FORM_CLASS): 
    """ Plugin profiles dialog """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, plugin, data, parent=None):
        """Constructor
        
        :param parent: 
        :type parent: QtWidgets
        """
        
        # init
        self.__plugin = plugin
        self.__data = data = data or {}
        
        super().__init__( parent=parent )
        
        
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        # connect signals
        cfg = agriConfig.services.ParticelleLavorazioni
        
        self.btnSave.clicked.connect( self.onButtonSaveClicked )
        self.chkSospesione.stateChanged.connect( self.onCheckSospesioneChanged )
        
        # set controls from data
        self.lblNumPartValue.setText( data.get( cfg.numParticellaField, '' ) )
        self.lblSubPartValue.setText( data.get( cfg.subalternoField, '' ) )
        
        suspended = data.get( cfg.flagSospensioneField, '' ) == cfg.flagFieldTrueValue
        self.chkSospesione.setChecked( suspended )
        self.txtNoteSospensione.setPlainText( data.get( cfg.descSospensioneField, '' ) )
        self.txtNoteSospensione.setEnabled( suspended )
        
        # set dialog properties
        self.setModal( True )
        
    
    # --------------------------------------
    # 
    # --------------------------------------
    def onCheckSospesioneChanged(self):
        """On checkbox suspend changed slot"""
        # disable suspending text edit
        suspended = self.chkSospesione.isChecked()
        self.txtNoteSospensione.setEnabled( suspended )
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def onButtonSaveClicked(self):
        """On Save button clicked slot"""
        try:
            # prepare SQL query
            cfg = agriConfig.services.ParticelleLavorazioni  
            
            checkedValue = ( cfg.flagFieldTrueValue 
                             if self.chkSospesione.isChecked( ) 
                             else cfg.flagFieldFalseValue )
            
            noteValue = self.txtNoteSospensione.toPlainText()
            
            idParticella = self.__data.get( cfg.id, None )
            
            # execute SQL query
            self.__plugin.controller.executeSqlQuery(
                f"UPDATE {cfg.name} SET "\
                f"{cfg.flagSospensioneField}='{checkedValue}',"\
                f"{cfg.descSospensioneField}='{noteValue}' "\
                f"WHERE {cfg.id}='{idParticella}';"
            )     
            
            # update widgets
            self.__plugin.controlbox.updateOffLineControls()
            
        finally:
            # close dialog
            self.close()
        
    