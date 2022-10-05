# system modules
import os.path

# qgis modules
from qgis.utils import iface
from qgis.gui import QgsAttributeTableModel, QgsAttributeTableFilterModel # QgsAttributeTableView
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsExpression, QgsVectorLayer, QgsVectorLayerCache, QgsFeatureRequest
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtGui import QKeySequence

from qgis_agri import tr
 
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_search_dialog.ui'))
    
# 
#-----------------------------------------------------------
class QGISAgriFieldExpressionDialog(QtWidgets.QDockWidget, FORM_CLASS):
    """Field expression dialog"""
    
    LAYER_SEARCH_EXPRESSION = "QGIS_AGRI_SEARCH_EXPRESSION"
    
    # --------------------------------------
    # signals 
    # --------------------------------------
    closingWidget = pyqtSignal()
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, parent = None):
        """Constructor
        
        :param title: 
        :type title: str
        
        :param parent: 
        :type parent: QtWidgets
        """
        super().__init__( parent )
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        # member data
        self._vector_layer_cache = None
        self._attr_model = None
        self._attr_filter_model = None
        
        # set attributes table read only
        self.tabAttributes.setEditTriggers( QAbstractItemView.NoEditTriggers )
        self.tabAttributes.willShowContextMenu.connect( self.onWillShowContextMenu )
        # add event filter on attributes table
        verticalHeader = self.tabAttributes.verticalHeader()
        if verticalHeader is not None:
            verticalHeader.sectionClicked.connect( self.onSelectionChanged )
            
        #
        self.wdFieldExpression.clearButtonEnable( True )
  
        ##self.setObjectName( "Espressione ricerca suoli" )
        self.setFloating( True )
        
        # set current layer
        self.setLayer( iface.activeLayer() )
        
        # connect signals to slots
        self.wdFieldExpression.fieldChanged.connect( self.checkExpr )
        self.wdFieldExpression.editingFinished.connect( self.onEditingFinished )
        self.btnSearch.clicked.connect( self.onClickedSearch ) 
        iface.currentLayerChanged.connect( self.setLayer )
        
        """
        w = QtWidgets.QLabel( "Espressione ricerca suoli", self )
        w.setObjectName( "bespin_docktitle_dummy" )
        self.setTitleBarWidget(w)
        """
    
    # --------------------------------------
    # 
    # --------------------------------------      
    def closeEvent(self, event):
        self.closingWidget.emit()
        event.accept()
    
    # --------------------------------------
    # 
    # --------------------------------------
    def onEditingFinished(self):
        # when expression editing is finished do search if valid
        self.onClickedSearch()
            
            
    # --------------------------------------
    # 
    # --------------------------------------
    def onClickedSearch(self):
        
        # check if valid layer
        layer = self.wdFieldExpression.layer()
        if layer is None:
            return
        
        # check if valid
        featureExpression = str(self.wdFieldExpression.asExpression()).strip()
            
        # store expression as layer property
        layer.setProperty( QGISAgriFieldExpressionDialog.LAYER_SEARCH_EXPRESSION, featureExpression )
        
        # clear current selection
        self.clearSelection()
            
        # get features ids
        fids = []
        if self.checkExpr( featureExpression ):
            fids = [ f.id() for f in layer.getFeatures( featureExpression ) ]
        
        # populate grid
        self._populateGrid( fids )
        
        # zoom to features
        self.zoomToFeatures( fids )
            
        # select features
        ##layer.selectByExpression( featureExpression )
        
        #
        self.updateStatus()
    
    # --------------------------------------
    # 
    # --------------------------------------
    def onTriggeredContextMenu(self, action):
        if action.shortcut() == QKeySequence.SelectAll:
            # call selection changed slot
            QTimer.singleShot( 200, lambda self=self: self.onSelectionChanged() )
            
        elif action.shortcut == QKeySequence.Deselect:
            # called clear selection slot
            pass
    
    # --------------------------------------
    # 
    # --------------------------------------
    def onWillShowContextMenu(self, menu, atIndex):
        # add deselect all action
        deselectAllAction = menu.addAction( tr( "Deseleziona tutto" ) )
        deselectAllAction.setShortcut( QKeySequence.Deselect )
        deselectAllAction.triggered.connect( self.clearSelection )
        # add separator
        menu.addSeparator()
        # add filter action
        filterAction = menu.addAction( tr( "Filtra" ) )
        filterAction.triggered.connect( lambda: self.onFilterTabble( atIndex ) )
        # connect slot to menu triggered signal
        menu.triggered.connect( self.onTriggeredContextMenu )
    
    
    def onFilterTabble(self, atIndex):
        # get layer
        exprWidget =  self.wdFieldExpression
        layer = exprWidget.layer()
        if layer is None:
            return
        
        # get field name and value
        model = atIndex.model()
        att_value = model.data( atIndex, Qt.DisplayRole )
        fld_index = model.data( atIndex, QgsAttributeTableModel.FieldIndexRole )
        fid = model.data( atIndex, QgsAttributeTableModel.FeatureIdRole )
        feat = layer.getFeature( fid )
        fld_value = feat.attribute( fld_index ) 
        fld_object = feat.fields().field( fld_index )
        fld_name = fld_object.name()
        
        filter_expr = QgsExpression.createFieldEqualityExpression( fld_name, fld_value )
        
        # apply filter search
        expr = exprWidget.currentText().strip()
        exprWidget.setExpression( f"{expr} AND {filter_expr}" if expr else filter_expr )
        self.onClickedSearch()
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def onSelectionChanged(self):
        # zoom to features
        self.zoomToFeatures( self.tabAttributes.selectedFeaturesIds() )
        self.updateStatus()
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def updateStatus(self):
        # init
        nFound, nMapSel, nSel, layName = '', '', '', ''
        
        try:
            # try to get status info
            layer = self.wdFieldExpression.layer()
            layName = layer.name() if layer else ''
                 
            model = self.tabAttributes.model()
            if model is not None:
                found_fids = set(model.filteredFeatures())
                selec_fids = set(self.tabAttributes.selectedFeaturesIds())
                selec_map_fids = set(layer.selectedFeatureIds ())
                selec_fids = selec_fids - ( selec_fids - selec_map_fids )
                
                nFound = len(found_fids)
                nMapSel = len(selec_map_fids)
                nSel = len(selec_fids)
        except:
            pass
         
        # update status info 
        self.lblStat_3.setText( f"Layer: <b>{layName}</b>" )
        self.lblStat_1.setText( f"Trovati: <b>{nFound}</b>" )
        if nMapSel == nSel:
            self.lblStat_2.setText( f"Selezionati: <b>{nSel}</b>" )
        else:
            self.lblStat_2.setText( f"Selezionati: <b>{nSel}</b> (Selezionati in mappa: <b>{nMapSel}</b>)" )
         
        
    # --------------------------------------
    # 
    # --------------------------------------
    def setLayer(self, layer):
        # update field expression widget
        cur_layer = self.wdFieldExpression.layer()
        if cur_layer == layer and layer is not None:
            return
        
        if isinstance( cur_layer, QgsVectorLayer ):
            cur_layer.selectionChanged.disconnect( self.updateStatus )
        
        lay_expr = ''
        if isinstance( layer, QgsVectorLayer ):
            layer.selectionChanged.connect( self.updateStatus )
            lay_expr = layer.property( QGISAgriFieldExpressionDialog.LAYER_SEARCH_EXPRESSION )
            
        self.wdFieldExpression.setExpression( lay_expr or '' )     
        self.wdFieldExpression.setLayer( layer )
        self.wdFieldExpression.isExpressionValid_ext( self.wdFieldExpression.asExpression() )
        
        # update title
        title = f"{tr( 'Espressione di ricerca per')} '{layer.name() if layer else 'suoli'}'"
        self.setWindowTitle( title )
        self.wdFieldExpression.setExpressionDialogTitle( title )
        self._populateGrid( [] )
        
        # update status bar
        self.updateStatus()
        
            
    # --------------------------------------
    # 
    # --------------------------------------        
    def checkExpr(self, expr: str) -> bool:
        if not self.wdFieldExpression.isExpressionValid( expr ):
            return False
        return self.wdFieldExpression.isExpressionValid_ext( expr )
    
    # --------------------------------------
    # 
    # --------------------------------------
    def clearSelection(self):
        # clear current selection
        layer = self.wdFieldExpression.layer()
        if layer is not None:
            layer.removeSelection()
        self.updateStatus()
    
    # --------------------------------------
    # 
    # --------------------------------------        
    def _populateGrid(self, fids):
        # get current layer
        layer = self.wdFieldExpression.layer()
        if layer is None:
            self.tabAttributes.setModel( None )
            self._attr_filter_model = None
            self._attr_model = None
            self._vector_layer_cache = None
            return
        
        # create feature attributes model
        self._vector_layer_cache = QgsVectorLayerCache( layer, 10000 )
        self._attr_model = QgsAttributeTableModel( self._vector_layer_cache )
        self._attr_model.setRequest( QgsFeatureRequest( fids ) )
        self._attr_model.loadLayer()
        
        canvas = iface.mapCanvas()
        self._attr_filter_model = QgsAttributeTableFilterModel( canvas, self._attr_model )
        
        # apply model to view
        self.tabAttributes.setModel( self._attr_filter_model )
        self.tabAttributes.setEditTriggers( QAbstractItemView.NoEditTriggers )
        
    # --------------------------------------
    # 
    # --------------------------------------
    def zoomToFeatures(self, fids):
        # check if feature founds
        if not fids:
            return
        
        # get associated layer
        layer = self.wdFieldExpression.layer()
        if layer is None:
            return
        
        # get features extent
        extent = None
        for feat in layer.getFeatures( fids ):
            # get feature bounding box
            geom = feat.geometry()
            if extent is None:
                extent = geom.boundingBox()
            else:
                extent.combineExtentWith( geom.boundingBox() )
            
        # zoom to features
        extent.grow( 10 )
        canvas = iface.mapCanvas()
        canvas.setExtent( extent )
        canvas.refresh() 
        
        # highlight featurs
        canvas = iface.mapCanvas()
        canvas.flashFeatureIds( layer, fids, flashes=1, duration=1000 )     
        
    

