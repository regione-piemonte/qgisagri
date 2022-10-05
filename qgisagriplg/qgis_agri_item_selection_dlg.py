# -*- coding: utf-8 -*-
"""Modulo per la visualizzazione delle foto appezzamenti dei suoli proposti.

Descrizione
-----------

Implementazione della classe che gestisce la selezione di elementi proposti all'utente.

Librerie/Moduli
-----------------
    
Note
-----


TODO
----


Autore
-------

- Creato da Sandro Moretti il 10/12/2021.

Copyright (c) 2019 CSI Piemonte.

Membri
-------
"""
# system modules
import os.path

from PyQt5.QtCore import pyqtSignal

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import Qt

from qgis_agri import agriConfig
from qgis_agri.model.service_sortfilterproxy_model import AgriSortFilterProxyModel
from qgis_agri.model.service_elenco_model import AgriElencoModel, AgriHeaderView

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_item_selection.ui'))

# QGISAgri item selection dialog
#-----------------------------------------------------------
class QGISAgriItemSelectionDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog to show items for user selection"""
    
    # --------------------------------------
    # signals 
    # --------------------------------------  
    itemSelected = pyqtSignal(list)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        """Constructor"""
        super().__init__(parent, flags)
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        # set widgets properties
        self.btnLoad.setDisabled( True )
        
        # set slot for tableview signals
        ##########self.tableView.clicked.connect( self.onTableViewClicked )
        self.tableView.doubleClicked.connect( self.onTableViewDoubleClicked )
        self.btnLoad.clicked.connect( self.onLoadButtonClicked )
    
    def setMultipleSelectionMode(self, multi: bool=True):
        """ """
        self.tableView.setSelectionMode( 
            QtWidgets.QAbstractItemView.ExtendedSelection if multi else
            QtWidgets.QAbstractItemView.SingleSelection )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setData(self, data, service_name):
        # add table view model with data
        table_model = AgriElencoModel( data )
        filter_model = AgriSortFilterProxyModel( self )
        filter_model.setSourceModel( table_model )
        self.tableView.setModel( filter_model )
        
        # set header view (with filters)
        header = AgriHeaderView( Qt.Horizontal, self.tableView ) ##AgriFilterHeader( self.tableView )
        header.setSectionsClickable( True )
        header.setHighlightSections( True )
        header.setSectionsMovable( True )
        header.setStretchLastSection( True )
        header.setSortIndicator( -1,  Qt.AscendingOrder )
        header.setSectionResizeMode( QtWidgets.QHeaderView.Interactive )
        header.setDefaultAlignment( Qt.AlignHCenter | Qt.AlignVCenter | Qt.TextWordWrap )
        self.tableView.setHorizontalHeader( header )
        self.tableView.setEditTriggers( QtWidgets.QAbstractItemView.NoEditTriggers )
        
        # configure columns
        columns_cfg = agriConfig.get_value( f"agri_service/resources/{service_name}/gridColumns", {} )
        header.configureColumns( columns_cfg )

        # apply header view
        header.setVisible( True )
        
        # clear current selection
        selection = self.tableView.selectionModel()
        if selection is not None:
            selection.clearSelection()
            selection.selectionChanged.connect( self.onSelectionChanged )
            
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _getValidSelection(self, index):
        # get item data
        filter_model = index.model()
        table_model = filter_model.sourceModel()
        row = table_model.dataRow( index )
        if row is None:
            return None
        
        # get service config
        service_cfg = agriConfig.get_value( 'agri_service/resources/LeggiValidazioniAzienda', {} )
        data_fields_cfg = service_cfg.get( 'dataFields', {} )
        loaded_field = data_fields_cfg.get( 'loadedField', '__loaded' )
        
        # check if already loaded
        if row.get( loaded_field, False ):
            return None
    
        # return valid data
        return row
        
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onSelectionChanged(self, selected, _):
        # get item data
        indexes = selected.indexes()
        if not indexes:
            self.btnLoad.setDisabled( True )
            return
        
        # check if valid selection
        if self._getValidSelection( indexes[0] ) is None:
            self.btnLoad.setDisabled( True )
            return
            
        # enamble load button   
        self.btnLoad.setDisabled( False )
        
    # --------------------------------------
    # 
    # --------------------------------------      
    def onTableViewDoubleClicked(self, index):
        """Table view double click slot"""
        self.onLoadButtonClicked( )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onLoadButtonClicked(self):
        # get selection model
        selection = self.tableView.selectionModel()
        if selection is None:
            return
        
        # get selected row
        indexes = selection.selectedRows()
        if not indexes:
            return
        
        # loop item selected
        data_list = []
        for index in indexes:
            # get and check if valid selection
            data = self._getValidSelection( index )
            if data:
                data_list.append( data )
                
        # emit signal for selected item
        self.itemSelected.emit( data_list )
        
        # close dialog
        self.close()
        
        