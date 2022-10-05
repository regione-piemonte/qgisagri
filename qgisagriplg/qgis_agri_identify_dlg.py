# -*- coding: utf-8 -*-
"""Modulo per la visualizzazione e la modifica degli attributi di un suolo

Descrizione
-----------

Implementazione della classe che gestisce la visualizzazione e la modifica degli attributi 
di un suoli in lavorazione tramite una finetra di dialogo; gli attributi visualizzati e 
modificabili sono:

- codice di eleggibilità rilevata del suolo;
- note della richiesta di lavaorazione (solo lettura);
- stato del suolo (da lavorare, lavorato, sospeso);
- motivo della sospensione del suolo;
- descrizione della sospensione del suolo;
- note aggiuntive da parte dell'utente.


Librerie/Moduli
-----------------
    
Note
-----


TODO
----

Attualmente la procedura funziona per i suoli in conduzione e in lavorazione; verificare se
necessario gestire anche i suoli non in conduzione ma con errori geometrici.

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

# QGIS modules
from qgis.core import QgsDataSourceUri

# Qt modules
from PyQt5.QtCore import Qt, QObject, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QColor, QRegExpValidator
from PyQt5.QtWidgets import QCompleter 

# qgis modules
from qgis.core import NULL
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QRegExp, QTimer
from qgis.utils import iface
#from qgis.gui import QgsAttributeForm

# plugin modules
from qgis_agri import agriConfig, tr
from qgis_agri.gui.layer_util import QGISAgriLayers


# Constants
QGIS_AGRI_ATTR_TEXT_ROLE = Qt.DisplayRole
QGIS_AGRI_ATTR_VALUE_ROLE = Qt.UserRole
QGIS_AGRI_ATTR_ASSIGN_ROLE = Qt.UserRole+1

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_attributes_dialog.ui'))

#
#-----------------------------------------------------------
class QGISAgriIdentifyDialogWrapper(QObject):
    """QGISAgri plugin feature identify dialog"""

    # signals
    validated = pyqtSignal(bool, QObject)
    
    #
    __plugin = None
    __plugin_call = False
    __eleggibilitaModel = None
    __sospensioneModel = None
    
    #
    DIALOG_DONE_PROP = 'QGISAgriIdentifyDialogDone'
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def __init__(self, dialog, layer, feature):
        """Constructor"""
        super().__init__(parent = dialog)
        
        #
        hasDone = dialog.property( self.DIALOG_DONE_PROP )
        if hasDone is not None:
            return
        
        self.__is_dialog = True
        self.__dialog = dialog
        self.__layer = layer
        self.__feature = feature #dialog.feature()#
        self.__valid = False
        self.__init_attribs = {}
        
        #
        self._widgwtWrap([
            'buttonBox',
            'edtCodEleggibilita',
            'cmbDescEleggibilita',
            'cmbSospensione',
            'radioLavorazione',
            'radioLavorato',
            'radioSospensione',
            'chkControllato',
            'txtNoteRichiesta',
            'txtNoteLavorazione',
            'txtNoteSospensione',
            'frmMessage',
            'lblMessage'
        ])
        
        #
        validator = QRegExpValidator( QRegExp("[0-9]*"), self.edtCodEleggibilita )
        self.edtCodEleggibilita.setValidator( validator )
        
        # add a filter model to filter matching items
        comboEleg = self.cmbDescEleggibilita
        comboEleg.setModel( self._getEleggibilitaModel() )
        filterModel = QSortFilterProxyModel( comboEleg )
        filterModel.setFilterCaseSensitivity( Qt.CaseInsensitive )
        filterModel.setSourceModel( comboEleg.model() )
        
        # add a completer, which uses the filter model
        completer = QCompleter( filterModel, comboEleg )
        completer.setCompletionMode( QCompleter.PopupCompletion )
        completer.setCaseSensitivity( Qt.CaseInsensitive )
        completer.setFilterMode( Qt.MatchContains )
        comboEleg.setCompleter( completer )
        
        # set sospensione combo model
        self.cmbSospensione.setModel( self._getSospensioneModel() )
            
        # connect signals    
        self.radioSospensione.toggled.connect( self.onRadioToggle )
        self.edtCodEleggibilita.textEdited.connect( self.onEleggibilitaChange )
        self.cmbDescEleggibilita.currentIndexChanged.connect( self.onEleggibilitaComboChange )
        self.validated.connect( self.onValidated )
        self.__dialog.disconnectButtonBox()
    
        #self.__dialog.parent().accepted.connect( self.accept )
        #self.__dialog.parent().rejected.connect( self.reject )
        self.buttonBox.clicked.connect( self.onButtonBoxClicked )
        
        
        # set read only widgets
        self.chkControllato.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.chkControllato.setFocusPolicy(Qt.NoFocus)
        
        # disable ok button
        btnOk = self.buttonBox.button( QtWidgets.QDialogButtonBox.Ok )
        if btnOk is not None:
            #btnOk.blockSignals( True )
            btnOk.setEnabled( False )
        
        # setup widgets
        self._setupWidgets()
        
        # block signal for OK buton
        if btnOk is not None and not self.__valid:
            btnOk.blockSignals( True )
        
        # set initial focus    
        dialog.setFocusProxy( self.edtCodEleggibilita )
          
        # force modal dialog
        try:
            dialog.parent().setModal( True )
            QTimer.singleShot(200, lambda dlg=dialog: dlg.activateWindow())
        except:
            self.__is_dialog = False
        
        
            
    # --------------------------------------
    # 
    # --------------------------------------
    def __del__(self):
        """Destructor""" 
        if not self.__is_dialog:
            return
        
        try:
            # deselect features
            if self.__layer:
                self.__layer.removeSelection()
        finally:
            # reset members
            self.__layer = None
            self.__feature = None
            self.__dialog = None
            
            
    # --------------------------------------
    # 
    # --------------------------------------
    @classmethod
    def initialize(cls, plugin):
        """Static initialization"""
        cls.__plugin = plugin
        
    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod    
    def reset():
        """Invalidate"""
        if QGISAgriIdentifyDialogWrapper.__eleggibilitaModel is not None:
            QGISAgriIdentifyDialogWrapper.__eleggibilitaModel.deleteLater()
        QGISAgriIdentifyDialogWrapper.__eleggibilitaModel = None
        
        if QGISAgriIdentifyDialogWrapper.__sospensioneModel is not None:
            QGISAgriIdentifyDialogWrapper.__sospensioneModel.deleteLater()
        QGISAgriIdentifyDialogWrapper.__sospensioneModel = None
        
    # --------------------------------------
    # 
    # --------------------------------------    
    @staticmethod
    def initializeCall(pluginCall=False):
        """Static initialization"""
        QGISAgriIdentifyDialogWrapper.__plugin_call = pluginCall
    
    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod
    def isValidEleggibilitaCode(value):
        """ Static metho to check 'codice eleggibilià' attribute """
        if QGISAgriIdentifyDialogWrapper.__eleggibilitaModel is None:
            # instance new model
            QGISAgriIdentifyDialogWrapper.__eleggibilitaModel = \
                QGISAgriIdentifyDialogWrapper.getEleggibilitaModel( parent=QGISAgriIdentifyDialogWrapper.__plugin )
                
        if QGISAgriIdentifyDialogWrapper.__eleggibilitaModel is None:
            return False, False 
            
        # ckeck if value present
        foundItem = None
        model = QGISAgriIdentifyDialogWrapper.__eleggibilitaModel
        for row in range( model.rowCount() ):
            item = model.item( row )
            elegCode = item.data( QGIS_AGRI_ATTR_VALUE_ROLE )
            if elegCode == value:
                foundItem = item
                break
            
        if foundItem is None:
            return False, False
            
        # check if assignable
        assegnable = foundItem.data( QGIS_AGRI_ATTR_ASSIGN_ROLE )
        return True, assegnable
        
    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod
    def getEleggibilitaModel(parent=None, onlyAssignable=False):        
        """Create 'Eleggibilità' item model"""
        
        # instance new model
        plugin = QGISAgriIdentifyDialogWrapper.__plugin
        eleggibilitaModel = QStandardItemModel( parent=parent )
                 
        # get config db table
        eleg_cfg = agriConfig.get_value( 'context/suolo/eleggibilita', {} )
        fld_value = eleg_cfg.get( 'fieldValue', None )
        fld_descr = eleg_cfg.get( 'fieldDesc', '' )
        fld_assign = eleg_cfg.get( 'fieldAssign', None )
        fld_valid = eleg_cfg.get( 'fieldAssignValue', 'S' )
        
        if fld_value is not None:
            # get data from offline db table
            data = plugin.controller.getDbTableData( eleg_cfg.get( 'table', 'ClassiEleggibilita' ) )
        
            # populate model
            for rec in data:
                value = rec.get( fld_value, None )
                if value is None:
                    continue
                
                descr = rec.get( fld_descr, '--- Descrizione mancante ---' )
                assign = fld_valid == rec.get( fld_assign, '' )
                if onlyAssignable and not assign:
                    continue
                
                item = QStandardItem()
                item.setData( "{0} - {1}".format( value, descr ), Qt.DisplayRole )
                item.setData( value, QGIS_AGRI_ATTR_VALUE_ROLE )
                item.setData( assign, QGIS_AGRI_ATTR_ASSIGN_ROLE )
                if not assign:
                    item.setData( QColor( Qt.red ), Qt.BackgroundRole )                  
                eleggibilitaModel.appendRow( item )
                
        return eleggibilitaModel
        
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
    def _widgwtWrap(self, widgetNames):
        """Get widget by name"""
        for widgetName in widgetNames:
            setattr( self, widgetName, self.__dialog.findChild( QObject, widgetName ) )
            
    # --------------------------------------
    # 
    # --------------------------------------        
    def _getAttrName(self, attName):
        """Get attribute name from config file"""
        attName = str(attName)
        return agriConfig.get_value( f"identifydlg/fields/{attName}/name", attName )
        
    # --------------------------------------
    # 
    # --------------------------------------
    def _formatValue(self, value, default=''):
        if value == NULL:
            return default
        return value
        
    # --------------------------------------
    # 
    # --------------------------------------
    def _formatAttribute(self, value, default=NULL, blankAsNull=False):
        if value is None:
            return default
        if blankAsNull and value == '':
            return default
        return value
        
    # --------------------------------------
    # 
    # --------------------------------------
    def _validate(self, value):
        """Validate values"""
        
        # check if layer in edit mode
        self.__valid = True
        if not self.__layer.isEditable():
            return True
        
        # check eleggibilità code
        comboEleg = self.cmbDescEleggibilita
        index = comboEleg.findData( value, QGIS_AGRI_ATTR_VALUE_ROLE )
        if index == -1:
            self.__valid = False
            self.validated.emit( self.__valid, self.edtCodEleggibilita )
            return False

        assegnable = comboEleg.itemData( index, QGIS_AGRI_ATTR_ASSIGN_ROLE )
        if not assegnable:
            self.__valid = False
            self.validated.emit( self.__valid, self.edtCodEleggibilita )
            return False

        self.__valid = True
        self.validated.emit( self.__valid, self.edtCodEleggibilita )
        return True
        
    
        
    # --------------------------------------
    # 
    # --------------------------------------
    def _getEleggibilitaModel(self):
        if QGISAgriIdentifyDialogWrapper.__eleggibilitaModel is None:
            # instance new model
            QGISAgriIdentifyDialogWrapper.__eleggibilitaModel = \
                QGISAgriIdentifyDialogWrapper.getEleggibilitaModel( parent=self.__plugin )
        return QGISAgriIdentifyDialogWrapper.__eleggibilitaModel
        
    # --------------------------------------
    # 
    # --------------------------------------
    def _getSospensioneModel(self):
        if QGISAgriIdentifyDialogWrapper.__sospensioneModel is None:
            # instance new model
            QGISAgriIdentifyDialogWrapper.__sospensioneModel = QStandardItemModel( parent=self.__plugin )
                     
            # get config db table
            eleg_cfg = agriConfig.get_value( 'context/suolo/sospensione', {} )
            fld_value = eleg_cfg.get( 'fieldValue', None )
            fld_descr = eleg_cfg.get( 'fieldDesc', '' )
            
            if fld_value is not None:
                # get data from offline db table
                data = self.__plugin.controller.getDbTableData( eleg_cfg.get( 'table', 'MotivoSospensione' ) )
            
                # populate model
                for rec in data:
                    value = rec.get( fld_value, None )
                    if value is None:
                        continue
                    
                    descr = rec.get( fld_descr, tr( '--- Descrizione mancante ---' ) )
                    
                    item = QStandardItem()
                    item.setData( descr, Qt.DisplayRole )
                    item.setData( value, QGIS_AGRI_ATTR_VALUE_ROLE )
                               
                    self.__sospensioneModel.appendRow( item )
                
        return QGISAgriIdentifyDialogWrapper.__sospensioneModel
        
    # --------------------------------------
    # 
    # --------------------------------------
    def _setupWidgets(self):
        """Setup widgets before showing"""
        
        # init
        self.edtCodEleggibilita.setStyleSheet( "" )                     
        self.cmbDescEleggibilita.setStyleSheet( "" )
        
        # get feature attributes
        self.__init_attribs = attributes = QGISAgriLayers.get_attribute_values( self.__feature )
        
        # select feature
        if QGISAgriIdentifyDialogWrapper.__plugin_call:
            self.__layer.selectByIds( [ self.__feature.id() ] )
            
        QGISAgriIdentifyDialogWrapper.__plugin_call = False
        
        # assign eleggibilità widget
        self.edtCodEleggibilita.setText( self._formatValue( attributes.get( self._getAttrName( 'codiceEleggibilitaRilevata' ), '' ) ) )
        
        # assign note widgets
        self.txtNoteRichiesta.setPlainText( self._formatValue( attributes.get( self._getAttrName( 'note' ), '' ) ) )
        self.txtNoteLavorazione.setPlainText( self._formatValue( attributes.get( self._getAttrName( 'noteLavorazione' ), '' ) ) )
        self.txtNoteSospensione.setPlainText( self._formatValue( attributes.get( self._getAttrName( 'descrizioneSospensione' ), '' ) ) )

        # assign status radio widgets
        if attributes.get( self._getAttrName( 'flagSospensione' ), 0 ) == 1:
            self.radioSospensione.setChecked( True )
            
        elif attributes.get( self._getAttrName( 'flagLavorato' ), 0 ) == 1:
            self.radioLavorato.setChecked( True )
            
        else:
            attributes[ self._getAttrName( 'flagLavorato' ) ] = 0
            self.radioLavorazione.setChecked( True )
            
        # assign tipo motivo sospensione
        index = self.cmbSospensione.findData( attributes.get( self._getAttrName( 'idTipoMotivoSospensione' ), '' ), QGIS_AGRI_ATTR_VALUE_ROLE )
        if index != -1:
            self.cmbSospensione.setCurrentIndex( index )
            
            
        # assign 'Controllato in campo'
        checked = attributes.get( self._getAttrName( 'flagControlloCampo' ), 'N' )  == 'S'
        self.chkControllato.setChecked(checked)
        self.chkControllato.setVisible(checked)
 
                    
        # set widget readonly/editable
        enabled = stateRadioEnabled = self.__layer.isEditable()
        if enabled:
            # check if enable only state radio in edit mode 
            uri = QgsDataSourceUri( self.__layer.dataProvider().dataSourceUri() )
            lay_cfg = agriConfig.get_value( 'ODB/layers/{0}'.format( uri.table() ) )
            if lay_cfg.get( 'editStateOnly', False ):
                # enable only if new feature
                enabled = self._isNewFeature()
        
        # disable if deleted feature 
        self.frmMessage.setVisible( False )
        if attributes.get( self._getAttrName( 'cessato' ), 0 ) == 1:
            enabled = stateRadioEnabled = False
            self.lblMessage.setText( tr( "Suolo rimosso: sola lettura!" ) )
            self.frmMessage.setVisible( True )
         
        # set widgets as  readonly/editable  
        readonly = not enabled
        self.edtCodEleggibilita.setReadOnly( readonly )
        self.cmbDescEleggibilita.setEnabled( enabled )
        self.cmbSospensione.setEnabled( enabled )
        self.txtNoteLavorazione.setReadOnly( readonly )
        self.txtNoteSospensione.setReadOnly( readonly )
        self.radioSospensione.setEnabled( enabled )
        self.radioLavorato.setEnabled( stateRadioEnabled )
        self.radioLavorazione.setEnabled( stateRadioEnabled )
        self.chkControllato.setEnabled( enabled )
        
        # final settings
        self.onEleggibilitaChange()
        self.onRadioToggle()
        
        return True
    
    # --------------------------------------
    # 
    # --------------------------------------
    def _isNewFeature(self):
        """Return True if new added feature, else False"""
        try:
            # check if not editable layer
            if self.__layer.isEditable():
                # check if feature added
                edit_buffer = self.__layer.editBuffer()
                if edit_buffer.isFeatureAdded( self.__feature.id() ):
                    return True
            return False
        except:
            return False
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def onButtonBoxClicked(self, button):
        """On buttonbox clicked slot"""
        if button == self.buttonBox.button( QtWidgets.QDialogButtonBox.Ok ):
            self.onFinished( QtWidgets.QDialog.Accepted )
        else:
            self.onFinished( QtWidgets.QDialog.Rejected )
            
    # --------------------------------------
    # 
    # --------------------------------------
    def onEleggibilitaChange(self):
        """Eleggibilità changed slot"""
        # set combo index
        combo = self.cmbDescEleggibilita
        value = self.edtCodEleggibilita.text()
        index = combo.findData( value, QGIS_AGRI_ATTR_VALUE_ROLE )
        combo.setCurrentIndex( index )
        self._validate( value )
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def onEleggibilitaComboChange(self, index):
        """Eleggibilità combo changed slot"""
        if index == -1:
            return
        
        # check if assignable value
        combo = self.cmbDescEleggibilita
        assegnable = combo.itemData( index, QGIS_AGRI_ATTR_ASSIGN_ROLE )
        combo.setStyleSheet( "" if assegnable else "QComboBox { background-color: rgb(255, 179, 179); }" )
        
        # check if valid value
        value = combo.itemData( index, QGIS_AGRI_ATTR_VALUE_ROLE )
        self.edtCodEleggibilita.setText( value )
        self._validate( value )
        
    # --------------------------------------
    # 
    # --------------------------------------
    def onRadioToggle(self):
        """Suolo status changed slot"""
        radio = self.radioSospensione
        isSuoloSospeso = radio.isChecked()
        self.cmbSospensione.setEnabled( radio.isEnabled() and isSuoloSospeso )
        self.txtNoteSospensione.setEnabled( isSuoloSospeso )
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def onValidated(self, valid, widget):
        """Validation slot"""
        
        # disable ok button
        btn = self.buttonBox.button( QtWidgets.QDialogButtonBox.Ok )
        if btn is not None:
            btn.setEnabled( valid )
            # unblock signal for OK buton
            if btn.signalsBlocked():
                btn.blockSignals( False )
            
        # set widget style
        if widget:
            widget.setStyleSheet( "" if valid else "border: 2px solid red" ) 
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def onFinished(self, result):
        """Finished slot"""
        
        # check if valid call
        if not self.__dialog:
            return
        
        # deselect features
        self.__layer.removeSelection()
        
        #
        self.__dialog.setProperty( self.DIALOG_DONE_PROP, True )
        
        # change feature attribute
        if self.__layer.isEditable() and result == QtWidgets.QDialog.Accepted:
            # prepare attributes
            attributes = {}
            skipFields = False
            
            combo = self.cmbDescEleggibilita
            codEleg = self.edtCodEleggibilita.text()
            index = combo.findData( codEleg, QGIS_AGRI_ATTR_VALUE_ROLE )
            descEleg = combo.itemData( index, Qt.DisplayRole )
            idTpMotivoSospensione = self.cmbSospensione.itemData( self.cmbSospensione.currentIndex(), QGIS_AGRI_ATTR_VALUE_ROLE )
             
            attributes[ self._getAttrName( 'codiceEleggibilitaRilevata' ) ] = codEleg
            attributes[ self._getAttrName( 'noteLavorazione') ] = self._formatAttribute(  
                self.txtNoteLavorazione.toPlainText(), blankAsNull=True )
            attributes[ self._getAttrName( 'descrizioneSospensione' ) ] = self._formatAttribute( 
                self.txtNoteSospensione.toPlainText(), blankAsNull=True )
            
            if self.radioSospensione.isChecked():
                attributes[ self._getAttrName( 'idTipoMotivoSospensione' ) ] = idTpMotivoSospensione
                attributes[ self._getAttrName( 'flagSospensione' ) ] = 1
                attributes[ self._getAttrName( 'flagLavorato' ) ] = 1
                
            elif self.radioLavorato.isChecked():
                attributes[ self._getAttrName( 'idTipoMotivoSospensione' ) ] = NULL
                attributes[ self._getAttrName( 'descrizioneSospensione' ) ] = self._formatAttribute( '', blankAsNull=True )
                attributes[ self._getAttrName( 'flagSospensione' ) ] = 0
                attributes[ self._getAttrName( 'flagLavorato' ) ] = 1
                
            else:
                attributes[ self._getAttrName( 'idTipoMotivoSospensione' ) ] = NULL
                attributes[ self._getAttrName( 'descrizioneSospensione' ) ] = self._formatAttribute( '', blankAsNull=True )
                attributes[ self._getAttrName( 'flagSospensione' ) ] = 0
                attributes[ self._getAttrName( 'flagLavorato' ) ] = 0
                # skip auto update
                flagLav = self.__init_attribs.get( 'flagLavorato' )
                if flagLav != 0:
                    skipFields = True
                    self.__plugin.controller.skipUpdateSuoloFeature( self.__feature.id() )
            
            
            # correct attributes
            defAttribs = self.__plugin.controller.getDefaultSuoliFeaturesFlags( self.__layer, skipFields=skipFields )
            attributes = {**defAttribs, **attributes}
            
            self.__layer.beginEditCommand( 'change_attribute_values' )
            try:
                # assign new attribute values to feature
                if QGISAgriLayers.change_attribute_values( self.__layer, [ self.__feature ], attributes ):
                    # if changes, update dependent attributes
                    pass
                self.__layer.endEditCommand()
                
            except Exception as e:
                self.layer.destroyEditCommand()
                raise e
            
            finally:
                self.__plugin.controller.resetUpdateSuoloFeature()
                    
            iface.mapCanvas().refresh()
            
        else:
            try:
                self.__dialog.parent().close()
            except:
                pass
      
        #
        #self.__dialog.save()
        #self.__dialog.parent().setVisible( False ) 
            
      
        # reset members
        self.__layer = None
        self.__feature = None
        self.__dialog = None

