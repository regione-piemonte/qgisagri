# -*- coding: utf-8 -*-
"""Modulo per la visualizzazione degli errori delle verifiche dei suoli

Descrizione
-----------

Implementazione della classe che gestisce la visualizzazione degli errori e delle
segnalazioni riscontrate dalle verifiche dei suoli; utilizzata una gliglia dati 
in un pannello agganciabile, per mostrare i messaggi e permettere all'utente di
eseguire uno zoom sull'anomalia selezionata.


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

# PyQt5 modules
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QColor, QIcon

# qgis modules
from qgis.utils import iface
from qgis.core import QgsGeometry, QgsRectangle
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

# plugin modules
from qgis_agri import tr
from qgis_agri.qgis_agri_errors import QGISAgriFeatureErrors

# COSTANTS
GEOM_DATA_ROLE = Qt.UserRole + 100
VISITED_DATA_ROLE = Qt.UserRole + 101

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_errors_dialog.ui'))


# QGISAgri error dialog
#-----------------------------------------------------------
class QGISAgriErrorsOptionMenu(QtWidgets.QMenu):
    def setVisible(self, visible):
        # Don't hide the menu if action choosen
        if not visible and self.activeAction():
            return

        super().setVisible( visible ) 

# QGISAgri error dialog
#-----------------------------------------------------------
class QGISAgriErrorsDialog(QtWidgets.QDockWidget, FORM_CLASS): 
    """Control dock widget for QGISAgri plugin"""
    
    # --------------------------------------
    # 
    # --------------------------------------  
    class QGISAgriErrorsItemModel(QStandardItemModel):
        def data(self, index, role):
            if not index.isValid():
                return None
            
            if role == Qt.TextAlignmentRole:
                if index.column() == 0:
                    return Qt.AlignRight | Qt.AlignVCenter
            
            if role == Qt.BackgroundRole:
                # get item from index
                item = index.model().item( index.row() )
                # get visited flag
                visited = item.data( VISITED_DATA_ROLE )
                if visited:
                    return QColor( 'DarkSeaGreen' )
                # get geometry
                geom = item.data( GEOM_DATA_ROLE )
                if geom is None:
                    return QColor( 'LightGray' )
                
            return super().data(index, role)
    
    # --------------------------------------
    # signals 
    # --------------------------------------  
    closingWidget = pyqtSignal()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, plugin, parent=None):
        """Constructor
        
        :param parent: 
        :type parent: QtWidgets
        """
        self.plugin = plugin
        
        self.actionChkDiffAreaSuoli = None
        self.actionChkCessatiSuoli = None
        self.actionChkAreaMinSuoli = None
        self.actionChkPartSep = None
        self.actionChkPartLavorate = None
        
        super().__init__( parent=parent )
        
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        # set error tab
        self.dockErrWidgetContents.layout().removeWidget(self.panCommands)
        self.tabErrors.setCornerWidget(self.panCommands, Qt.TopRightCorner)
        
        # set errors table model
        errModel = QGISAgriErrorsDialog.QGISAgriErrorsItemModel(0, 3)
        errModel.setHeaderData(0, Qt.Horizontal, tr("OGC_FID"), Qt.DisplayRole)
        errModel.setHeaderData(1, Qt.Horizontal, tr("Errore"), Qt.DisplayRole)
        errModel.setHeaderData(2, Qt.Horizontal, tr("layer"), Qt.DisplayRole)
        
        # set error table model
        self.errorsGrid.setModel(errModel)
        
        # set warnings table model
        wrnModel = QGISAgriErrorsDialog.QGISAgriErrorsItemModel(0, 3)
        wrnModel.setHeaderData(0, Qt.Horizontal, tr("OGC_FID"), Qt.DisplayRole)
        wrnModel.setHeaderData(1, Qt.Horizontal, tr("Segnalazione"), Qt.DisplayRole)
        wrnModel.setHeaderData(2, Qt.Horizontal, tr("layer"), Qt.DisplayRole)
        
        # set error table model
        self.warningsGrid.setModel(wrnModel)
        
        # set tabs
        self.tabErrors.setTabIcon( self.tabErrors.indexOf( self.errorsPage ), QIcon(':/plugins/qgis_agri/images/error-icon.png') )
        self.tabErrors.setTabIcon( self.tabErrors.indexOf( self.warningsPage ), QIcon(':/plugins/qgis_agri/images/warning-icon.png') )   
        
        # set slot for tableview signals
        self.errorsGrid.doubleClicked.connect( self.onTableViewDoubleClicked )
        self.warningsGrid.doubleClicked.connect( self.onTableViewDoubleClicked )
        
        
        # populate menu options
        self.menu_options = QGISAgriErrorsOptionMenu(self)
        self.menu_options.triggered.connect(self.onOptionsTriggered)
        
        self.actionChkDiffAreaSuoli =\
        action = self.menu_options.addAction("Verifica 'Differenza area suoli'")
        #action.setToolTip(r"Abilita\disabilita la verifica sulla 'Differenza area suoli'")
        action.setCheckable(True)
        action.setChecked(True)
        
        self.actionChkCessatiSuoli =\
        action = self.menu_options.addAction("Verifica 'Suoli cessati'")
        #action.setToolTip(r"Abilita\disabilita la verifica sui 'Suoli cessati'")
        action.setCheckable(True)
        action.setChecked(True)
        
        self.actionChkAreaMinSuoli =\
        action = self.menu_options.addAction("Verifica 'Superficie minima suoli'")
        #action.setToolTip(r"Abilita\disabilita la verifica 'Superficie minima dei suoli'")
        action.setCheckable(True)
        action.setChecked(True)
        
        # PARTICELLE actions
        self.actionChkPartSep = self.menu_options.addSeparator()
        
         
        self.actionChkPartLavorate =\
        action = self.menu_options.addAction("Verifica 'Particelle lavorate-Suoli'")
        #action.setToolTip(r"Abilita\disabilita la verifica 'Particelle lavorate-Suoli'")
        action.setCheckable(True)
        action.setChecked(True)
            
        self.tbOptions.setMenu(self.menu_options)
        self.tbOptions.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        
        self.chkZoom.setCheckState(Qt.Checked)
        self.spinGeomBuffer.setValue(1)
        
        
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
    def checkDiffAreaSuoli(self):
        """ Returns flag for 'Differenza Area Suoli' check """
        if self.actionChkDiffAreaSuoli is None:
            return True
        return self.actionChkDiffAreaSuoli.isChecked()
    
    @checkDiffAreaSuoli.setter
    def checkDiffAreaSuoli(self, value):
        if self.actionChkDiffAreaSuoli is None:
            return
        flag = True if value else False
        self.actionChkDiffAreaSuoli.setChecked( flag )
        
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def checkCessatiSuoli(self):
        """ Returns flag for 'Suoli cessati' check """
        if self.actionChkCessatiSuoli is None:
            return True
        return self.actionChkCessatiSuoli.isChecked()
    
    @checkCessatiSuoli.setter
    def checkCessatiSuoli(self, value):
        if self.actionChkCessatiSuoli is None:
            return
        flag = True if value else False
        self.actionChkCessatiSuoli.setChecked( flag ) 
        
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def checkAreaMinSuoli(self):
        """ Returns flag for 'Superficie minima suoli' check """
        if self.actionChkAreaMinSuoli is None:
            return True
        return self.actionChkAreaMinSuoli.isChecked()
    
    @checkAreaMinSuoli.setter
    def checkAreaMinSuoli(self, value):
        if self.actionChkAreaMinSuoli is None:
            return
        flag = True if value else False
        self.actionChkAreaMinSuoli.setChecked( flag ) 
        
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def checkPartLavorate(self):
        """ Returns flag for 'Superficie minima suoli' check """
        if self.actionChkPartLavorate is None:
            return True
        return self.actionChkPartLavorate.isChecked()
    
    @checkPartLavorate.setter
    def checkPartLavorate(self, value):
        if self.actionChkPartLavorate is None:
            return
        flag = True if value else False
        self.actionChkPartLavorate.setChecked( flag )
        
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def onOptionsTriggered(self, action):
        ##self.menu_options.setVisible(True)
        # check if 'Differenza area suoli' option
        if action == self.actionChkDiffAreaSuoli:
            pass
        
    # --------------------------------------
    # 
    # --------------------------------------      
    def onTableViewDoubleClicked(self, index):
        """Table view double click slot"""
        # get item from index
        item = index.model().item( index.row() )
        # get geometry
        geom = item.data( GEOM_DATA_ROLE )
        if geom is None:
            return 
        
        # set visited flag
        item.setData( True, VISITED_DATA_ROLE )
        
        # get geometry bounding box
        bbox = None
        if not self.chkZoom.isChecked():
            try:
                poGeom = geom.pointOnSurface()
                errQgsPointXY = poGeom.asPoint()
                bbox = QgsRectangle(errQgsPointXY, errQgsPointXY)
            except:
                pass
        
        if bbox is None:
            bbox = geom.boundingBox()
            bbox.grow( 10 )
        
        # zoom to geometry bounding box
        canvas = iface.mapCanvas()
        canvas.setExtent( bbox )
        canvas.refresh()
        
        # create a buffered geometry for a valid distance
        buffGeom = geom
        dist = self.spinGeomBuffer.value()
        if dist > 0:
            try:
                buffGeom = geom.buffer( dist, 20 )
            except:
                pass
        
        # flash geometry on canvas  
        canvas.flashGeometries( [buffGeom],
                                canvas.mapSettings().destinationCrs(), 
                                flashes= 1, 
                                duration= 1000 )
        
        
    # --------------------------------------
    # 
    # --------------------------------------      
    def closeEvent(self, event):
        self.closingWidget.emit()
        event.accept()
        
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def show(self):
        # enable\disable PARTICELLE actions
        enable_part_actions = self.plugin.particelle.isParticelleWorkingEnabled
        self.actionChkPartSep.setEnabled( enable_part_actions )
        self.actionChkPartLavorate.setEnabled( enable_part_actions )
            
        # call base method
        QtWidgets.QDialog.show(self)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def resizeColumnToContents(self, tableview, column):
        tableview.resizeColumnToContents( column )
        tableview.setColumnWidth( column, tableview.columnWidth( column ) + 10 )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setDockable(self, dock):
        self.setFloating(True)
        if not dock:
            self.setAllowedAreas( Qt.NoDockWidgetArea )
        else:
            self.setAllowedAreas( Qt.AllDockWidgetAreas )
           
    
    # --------------------------------------
    # 
    # --------------------------------------        
    def _updateTabLabels(self, nErrs=0, nWrns=0):
        # set tab widgets
        self.tabErrors.setTabText( self.tabErrors.indexOf( self.errorsPage ), 
                                   "{} ({})".format( tr("Errori"), nErrs ) )
        
        self.tabErrors.setTabText( self.tabErrors.indexOf( self.warningsPage ), 
                                   "{} ({})".format( tr("Segnalazioni"), nWrns ) )
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def clear(self):
        """Method to empty table view models"""
        # init
        errModel = self.errorsGrid.model()
        wrnModel = self.warningsGrid.model()
        
        # clear models
        errModel.removeRows(0, errModel.rowCount())
        wrnModel.removeRows(0, wrnModel.rowCount())
        
        # set tab widgets
        self._updateTabLabels()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def reset(self):
        """Method to reset this panel"""
        # init
        enable_part_actions = self.plugin.particelle.isParticelleWorkingEnabled
        # clear results
        self.clear()
        self.checkDiffAreaSuoli = True #not enable_part_actions
        self.checkCessatiSuoli = True
        self.checkAreaMinSuoli = True
        #---
        self.checkPartLavorate = enable_part_actions
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setErrors(self, errorData: QGISAgriFeatureErrors):
        """Method to load table view models by error class"""
        # init
        nErrs = 0
        nWrns = 0
        errModel = self.errorsGrid.model()
        wrnModel = self.warningsGrid.model()
        
        # Clear models
        errModel.removeRows(0, errModel.rowCount())
        wrnModel.removeRows(0, wrnModel.rowCount())
        
        # populate models
        for err in errorData.errors:
            # get moded ref
            if err.get( 'isWarning', 0 ) == 0:
                nErrs += 1
                model = errModel
            else:
                nWrns += 1
                model = wrnModel
             
            # get geomtry   
            geom = err.get( 'geom', None )
            if geom is not None:
                geom = QgsGeometry( geom )
                
            # append a new row of items to model
            fictitious = err.get( 'fictitious', False )
            fid = str( err.get( 'fid', '' ) or '' ) 
            if fictitious:
                fid = "({})".format( fid )
            
            fidItem = QStandardItem( fid )
            fidItem.setData( geom, GEOM_DATA_ROLE )
            fidItem.setData( False, VISITED_DATA_ROLE )
            
            msgItem = QStandardItem( err.get( 'message', '' ) )
            
            layItem = QStandardItem( err.get( 'layer', '' ) )
            
            model.appendRow( [ fidItem, msgItem, layItem ] )
            ##model.appendRow( [ msgItem, layItem ] )
     
        # set tab widgets
        self._updateTabLabels( nErrs, nWrns )
        
        if nErrs > 0:
            self.resizeColumnToContents( self.errorsGrid, 0 )
            self.resizeColumnToContents( self.errorsGrid, 1 )
            
        if nWrns > 0:
            self.resizeColumnToContents( self.warningsGrid, 0 )
            self.resizeColumnToContents( self.warningsGrid, 1 )
            
        if nWrns > 0 and nErrs == 0:
            self.tabErrors.setCurrentIndex( self.tabErrors.indexOf( self.warningsPage ) )
        else:
            self.tabErrors.setCurrentIndex( self.tabErrors.indexOf( self.errorsPage ) )
        
    
        # show dialog
        if nErrs > 0 or nWrns > 0:
            self.show()#QTimer.singleShot( 200, lambda self=self: self.show() )
            self.raise_()
    