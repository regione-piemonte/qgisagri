# -*- coding: utf-8 -*-
"""Modulo per la gestione della visualizzazione dello storico dei suoli

Descrizione
-----------

Implementazione del widget della TOC personalizzato per la la visualizzazione dello storico 
dei suoli per il foglio in lavorazione; permette di specificare una data tramite una combo
oppure tamite uno slider. Widget associato al layer di storicizzazione.


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
# Import python modules
import os
##import time
##from functools import partial
from osgeo import ogr
from datetime import datetime


# Import PyQt5 modules
##from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QDate
from PyQt5.QtWidgets import QApplication, QGridLayout
from PyQt5.QtGui import QTextDocument, QAbstractTextDocumentLayout
 
# Import QGIS modules
from qgis.PyQt import QtWidgets, uic
from qgis.core import QgsProject, QgsMapLayer, QgsProviderRegistry
from qgis.gui import QgsLayerTreeEmbeddedWidgetProvider 
from qgis.utils import iface

# Import plugin modules
from qgis_agri import agriConfig
##from qgis_agri.util.file import fileUtil
from qgis_agri.widgets.calendar import CalendarExt
from qgis_agri.gui.layer_util import QGISAgriLayers

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_history_widget.ui'))


#
#-----------------------------------------------------------
class QgisAgriHistoryCalendarPopup(QtWidgets.QWidget):
    
    selectedDate = pyqtSignal(QDate)
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, parent = None, widget=None, selDate=None, dates=None):    
        QtWidgets. QWidget.__init__(self, parent)
        layout = QGridLayout( self )
        calendar = CalendarExt()
        if dates is not None and len(dates) > 0:
            calendar.selectDates( dates )
            calendar.setDateRange( dates[0], dates[-1] )
        if selDate is not None:
            calendar.setSelectedDate( selDate )
        ##button = QPushButton("Very Interesting Text Popup. Here's an arrow   ^")
        layout.addWidget( calendar )
        
        calendar.clicked.connect( self.onCalendarClicked )

        # adjust the margins or you will get an invisible, unintended border
        layout.setContentsMargins( 0, 0, 0, 0 )

        # need to set the layout
        self.setLayout( layout )
        self.adjustSize()

        # tag this widget as a popup
        self.setWindowFlags( Qt.Popup )

        # calculate the botoom right point from the parents rectangle
        point = widget.rect().bottomLeft()

        # map that point as a global position
        global_point = widget.mapToGlobal( point )

        # correct widget position for visibility on screen
        screenRect = QApplication.desktop().screenGeometry()
        
        
        rel_point = global_point + QPoint( 0, self.height() )
        if rel_point.y() > screenRect.height():
            global_point = global_point - QPoint( 0, self.height() + widget.height() )
        
        rel_point = global_point + QPoint( self.width(), 0 )
        if rel_point.x() > screenRect.width():
            global_point = global_point - QPoint( self.width()-widget.width(), 0 )
        
        self.move( global_point )

    # --------------------------------------
    # 
    # --------------------------------------
    def onCalendarClicked(self, date):
        self.selectedDate.emit( date )
        
#
#-----------------------------------------------------------
class QgisAgriHistoryLabel(object):
    """Suoli History date label"""
    
    PLACEMENTS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    DEFAULT_FONT_SIZE = 25
    font = "Arial"
    size = DEFAULT_FONT_SIZE
    fmt = "%d/%m/%Y"
    placement = 'SE'
    color = 'black'
    bgcolor = 'white'
    type = "dt"

    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self):
        pass

    # --------------------------------------
    # 
    # --------------------------------------
    def getLabel(self, dt):
        return dt

#
#-----------------------------------------------------------
class QgisAgriHistoryWidget(QtWidgets.QWidget, FORM_CLASS):
    """Suoli History layer embedded widget"""
    
    # --------------------------------------
    # 
    # --------------------------------------
    def getDateSqlScript(self):
        return """
            WITH formatDates AS (
    
            -- format dates as IS0-8601
            SELECT
                 annoCampagna
                 
               , substr(dataInizioValidita, 7) 
                 ||'-'||
                 substr(dataInizioValidita, 4, 2)
                 ||'-'||
                 substr(dataInizioValidita, 1, 2) 
                 AS isoDate
                 
            FROM SUOLO 
            WHERE dataInizioValidita IS NOT NULL
           
        ), pastYearDates AS (
    
            -- select past year dates
            SELECT
               annoCampagna
              
               , LAST_VALUE ( isoDate ) OVER (
                    PARTITION BY annoCampagna
                    ORDER BY annoCampagna, isoDate
                    RANGE BETWEEN UNBOUNDED PRECEDING AND 
                    UNBOUNDED FOLLOWING    
                  ) AS isoDate
                
            FROM formatDates 
            
        ), currYearDates AS (
    
            -- select current year date
            SELECT 
                annoCampagna
                , isoDate
               
            FROM formatDates
            WHERE annoCampagna = '{0}'
            
        ), extractDates AS (
    
            -- collect dates
            SELECT * FROM pastYearDates
               UNION
            SELECT * FROM currYearDates
    
        )
        SELECT
             annoCampagna
             --, isoDate
             , strftime('%d/%m/%Y', date(isoDate)) AS dataInizioValidita
             
          FROM extractDates
          --GROUP BY isoDate
        ORDER BY annoCampagna,isoDate;
        """.format( self.annoCampagna )
        
    
    # --------------------------------------
    # 
    # --------------------------------------
    def getDateExprFilter(self, dateValue):
        # foramat date as IS0-8601
        dateVal = datetime.strptime(dateValue, self.dateFieldFormat).date()
        dateIso = dateVal.strftime("%Y-%m-%d")
       
        # return layer filter expression
        return """
        {0} <= '{3}'
        AND 
        '{4}' BETWEEN
        substr({1}, 7)||'-'||substr({1}, 4, 2)||'-'||substr({1}, 1, 2)
        AND 
        substr({2}, 7)||'-'||substr({2}, 4, 2)||'-'||substr({2}, 1, 2)
        """.format( self.yearFieldName, 
                    self.dateFieldName,
                    self.dateEndFieldName,
                    self.annoSelected, 
                    dateIso )
    
    # --------------------------------------
    # 
    # --------------------------------------
    def getFilterDates(self):
        # init
        dateDict = {}
        conn = None
        recSet = None
         
        try:
            # check if ogr layer
            source_provider = self.layer.dataProvider().name()
            if source_provider != 'ogr':
                return dateDict
            
            source_parts = QgsProviderRegistry.instance().decodeUri( source_provider, self.layer.source() )
            source_path = source_parts.get( 'path', '' )
            if not source_path:
                return dateDict
            
            # get config
            ##storico_cfg = agriConfig.get_value('commands/storico')
            ##scriptFile = storico_cfg.get( 'dateScript', '' )
            
            # execute SQL script
            conn = ogr.Open(source_path)
            recSet = conn.ExecuteSQL( self.getDateSqlScript(), dialect = "SQLITE" )
            if recSet is None:
                return dateDict
            
            for row in recSet:
                year = row.GetField(0)
                date = row.GetField(1)
                if not year or not date:
                    continue
                
                if year not in dateDict:
                    dateDict[year] = []
                    
                dateDict[year].append( date )
            
        except Exception:
            pass
        
        finally:
            # destroy the result set
            conn.ReleaseResultSet( recSet )
            # release connection
            conn = None
        
        return dateDict
        
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, layer, annoCampagna, *args, **kwargs):
        super(QgisAgriHistoryWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)
        
        # init
        self.layer = layer
        self.annoCampagna = str(annoCampagna)
        self.annoSelected = None
        self.dateSelected = None
        self.showLabel = True
        self.labelOptions = QgisAgriHistoryLabel()
        
        storico_cfg = agriConfig.get_value('commands/storico')
        dateField_cfg = storico_cfg.get( 'yearField', {} )
        self.yearFieldName = dateField_cfg.get( 'name', 'annoCampagna' )
        
        dateField_cfg = storico_cfg.get( 'dateField', {} )
        self.dateFieldName = dateField_cfg.get( 'name', 'dataInizioValidita' )
        self.dateFieldFormat =dateField_cfg.get( 'format', '%d/%m/%Y' )
        
        dateField_cfg = storico_cfg.get( 'dateEndField', {} )
        self.dateEndFieldName = dateField_cfg.get( 'name', 'dataFineValidita' )
        ##self.dateFieldFormat =dateField_cfg.get( 'format', '%d/%m/%Y' )

        # get filter dates
        self.layer.setSubsetString( '' )
        self.dateDict = self.getFilterDates()
        
        # 'anno campagna' combo
        self.comboAnno.addItems( self.dateDict.keys() )
        self.comboAnno.setCurrentIndex( -1 )
        self.comboAnno.currentIndexChanged.connect( self.annoCampagnaChange )
        
        # date label
        self.lblDate.setText('')
        
        # date slider
        self.sliderDate.setDisabled( True )
        self.sliderDate.valueChanged.connect( self.sliderDateChange )
        
        # reset date button
        self.btnReset.setText( '' )
        self.btnReset.clicked.connect( self.btnResetClicked )
        
        # set start date (and year)
        self.resetDateFiler()
        
        
        """
        # get unique dates from layer
        provider = self.layer.dataProvider()
        idx = provider.fieldNameIndex( self.dateFieldName ) 
        uv = [i for i in provider.uniqueValues( idx ) if i] 
        uv = list(map(lambda x: datetime.strptime(x, self.dateFieldFormat), uv))
        # sort dates
        uv = map(lambda x: x.strftime(self.dateFieldFormat), sorted(uv))
        
        # create date filter combo
        #############################self.combo = QtWidgets.QComboBox(parent=self)
        self.dateCombo.addItems( uv )
        self.dateCombo.setCurrentIndex( -1 )
        self.dateCombo.currentIndexChanged.connect(self.selectionchange)
        
        # calendar popup
        self.calendar_popup = None
        self.btnCalendar.setText( '' )
        self.btnCalendar.clicked.connect( self.onBtnCalendarClicked )
        """
        
        # this signal is responsible for rendering the label
        iface.mapCanvas().renderComplete.connect( self.renderLabel )
        iface.mapCanvas().currentLayerChanged.connect( self.onCurrentLayerChanged )

    
    # --------------------------------------
    # 
    # --------------------------------------
    def annoCampagnaChange(self, i):
        # set widget layer as current
        view = iface.layerTreeView()
        view.setCurrentLayer( None ) 
        view.setCurrentLayer( self.layer )
        
        # init
        self.annoSelected = None
        self.dateSelected = None
        
        # check if selected a year
        if i == -1:
            self.layer.setSubsetString( '' )
            return
        
        self.annoSelected = self.comboAnno.currentText()
        
        # get dates for select year
        dates = self.dateDict.get( self.annoSelected, [] )
        if not dates:
            return
        
        
        # set slider
        numDates = len(dates)
        if numDates == 1:
            ####self.dateSelected = dates[0]
            self.sliderDate.setDisabled( True )
            self.sliderDateChange( 0 )
        else:
            self.sliderDate.setRange( 0, numDates-1 )
            ##self.sliderDate.setFocusPolicy( Qt.NoFocus )
            self.sliderDate.setPageStep( 1 )
            self.sliderDate.setValue( numDates-1 )
            self.sliderDate.setDisabled( False )
            self.sliderDateChange( self.sliderDate.value() )
            
        
    
    # --------------------------------------
    # 
    # --------------------------------------
    def sliderDateChange(self, i):
        # set widget layer as current
        view = iface.layerTreeView()
        view.setCurrentLayer( None ) 
        view.setCurrentLayer( self.layer )
        
        # get dates for select year
        dates = self.dateDict.get( self.annoSelected, [] )
        if not dates:
            return
        
        self.dateSelected = dates[i]
        
        # date label
        self.lblDate.setText( self.dateSelected )
        
        # filter layer on selected date
        self.layer.setSubsetString( self.getDateExprFilter( self.dateSelected ) )
        
        # zoom to layer extent
        QGISAgriLayers.zoom_layers_ext([ self.layer ])
    
    
    # --------------------------------------
    # 
    # --------------------------------------
    def btnResetClicked(self):
        self.resetDateFiler()
    
    # --------------------------------------
    # 
    # --------------------------------------
    """
    def selectionchange(self,i):
        # set widget layer as current
        view = iface.layerTreeView()
        view.setCurrentLayer( None ) 
        view.setCurrentLayer( self.layer )

        # check if selected a date
        if i == -1:
            self.layer.setSubsetString( '' )
            self.dateSelected = None
            return
        
        # filter layer on selected date
        self.dateSelected = self.dateCombo.currentText()
        self.layer.setSubsetString( "{0}='{1}'".format(self.dateFieldName, self.dateSelected) )
        #logger("selected value {0}".format(value))
    """
    
    # --------------------------------------
    # 
    # --------------------------------------
    """
    def onBtnCalendarClicked(self):
        # get list of dates
        model = self.dateCombo.model()   
        dates = [model.data(model.index(i,0)) for i in range(model.rowCount())]
        dates = list(map(lambda x: datetime.strptime(x, self.dateFieldFormat), dates))
        
        # get selected date
        selDate = None
        if self.dateCombo.currentIndex() != -1:
            selDate = datetime.strptime(self.dateCombo.currentText(), self.dateFieldFormat)
        
        # show calendar popup
        self.calendar_popup = QgisAgriHistoryCalendarPopup(parent= self, 
                                                           widget= self.dateCombo,
                                                           selDate= selDate, 
                                                           dates= dates)
        self.calendar_popup.selectedDate.connect( self.onCalendarClicked )
        self.calendar_popup.show()
    """
        
    # --------------------------------------
    # 
    # --------------------------------------
    """
    def onCalendarClicked(self, date):
        if self.calendar_popup is not None:
            self.calendar_popup.close()
            self.calendar_popup = None
        
        if date is None:
            return 
        
        index = self.dateCombo.findText( date.toString( 'dd/MM/yyyy' ) )
        if index != -1:
            self.dateCombo.setCurrentIndex( index )
            self.dateCombo.setFocus( Qt.PopupFocusReason )
    """
        
    # --------------------------------------
    # 
    # --------------------------------------
    def onCurrentLayerChanged(self, currLayer):
        iface.mapCanvas().refresh()
        
        
    # --------------------------------------
    # 
    # --------------------------------------
    def resetDateFiler(self):
        """ Reset start date """
        index = self.comboAnno.findText( self.annoCampagna )
        if index == -1:
            index = self.comboAnno.count() -1
            
        self.comboAnno.setCurrentIndex( index )
    
    # --------------------------------------
    # 
    # --------------------------------------
    def renderLabel(self, painter):
        """Render the current timestamp on the map canvas"""
        if not self.showLabel: # or not self.model.hasLayers() or not self.dock.pushButtonToggleTime.isChecked():
            return
        
        if iface.mapCanvas().currentLayer() != self.layer:
            return

        if not self.dateSelected:
            return

        # compose label text
        dt = ''
        treeLayer = QgsProject.instance().layerTreeRoot().findLayer( self.layer )
        if treeLayer is not None:
            dt = "{0} in data {1}".format( treeLayer.name(), self.dateSelected )

        labelString = self.labelOptions.getLabel(dt)

        # Determine placement of label given cardinal directions
        flags = 0
        for direction, flag in ('N', Qt.AlignTop), ('S', Qt.AlignBottom), ('E', Qt.AlignRight), ('W', Qt.AlignLeft):
            if direction in self.labelOptions.placement:
                flags |= flag

        # Get canvas dimensions
        pixelRatio = painter.device().devicePixelRatio()
        width = painter.device().width() / pixelRatio
        height = painter.device().height() / pixelRatio

        painter.setRenderHint(painter.Antialiasing, True)
        txt = QTextDocument()
        html = """<span style="background-color:%s; padding: 5px; font-size: %spx;">
                    <font face="%s" color="%s">&nbsp;%s</font>
                  </span> """\
               % (self.labelOptions.bgcolor, self.labelOptions.size, self.labelOptions.font,
                  self.labelOptions.color, labelString)
        txt.setHtml(html)
        layout = txt.documentLayout()
        size = layout.documentSize()

        if flags & Qt.AlignRight:
            x = width - 5 - size.width()
        elif flags & Qt.AlignLeft:
            x = 5
        else:
            x = width / 2 - size.width() / 2

        if flags & Qt.AlignBottom:
            y = height - 5 - size.height()
        elif flags & Qt.AlignTop:
            y = 5
        else:
            y = height / 2 - size.height() / 2

        painter.translate(x, y)
        layout.draw(painter, QAbstractTextDocumentLayout.PaintContext())
        painter.translate(-x, -y)  # translate back

#
#-----------------------------------------------------------
class QgisAgriHistoryWidgetProvider(QgsLayerTreeEmbeddedWidgetProvider):

    SUPPORTED_DATA_PROVIDERS = [
        "ogr",
    ]
    
    annoCampagna = ''

    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, *args, **kwargs):
        ##logger("Instantiating provider...")
        super().__init__(*args, **kwargs)
        ##self.creation_timestamp = int(time.time())
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def __del__(self):
        """Destructor"""
        pass
            

    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod
    def id() -> str:
        ##logger("id called")
        return "QgisAgriStorico"#"{}_{}".format(self.__class__.__name__, self.creation_timestamp)

    # --------------------------------------
    # 
    # --------------------------------------
    def name(self) -> str:
        ##logger("name called")
        return "QgisAgri Storico"

    # --------------------------------------
    # 
    # --------------------------------------
    def createWidget(self, map_layer: QgsMapLayer, widget_index: int) -> QtWidgets.QWidget:
        ##logger("createWidget called")
        ##widget = QtWidgets.QLabel("hi world!")
        ##widget.setAutoFillBackground(True)
        widget = QgisAgriHistoryWidget(map_layer, self.annoCampagna)
        return widget

    # --------------------------------------
    # 
    # --------------------------------------
    def supportsLayer(self, map_layer: QgsMapLayer) -> bool:
        ##logger("supportsLayer called")
        provider = map_layer.dataProvider()
        name = provider.name()
        result = True if name in self.SUPPORTED_DATA_PROVIDERS else False
        ##logger("supportsLayer: {}".format(result))
        return result
      
    # --------------------------------------
    # 
    # --------------------------------------  
    @staticmethod
    def addWidgetInstance(layer: QgsMapLayer) -> None:
        if (layer.customProperty("embeddedWidgets/count") != 1 or 
            layer.customProperty("embeddedWidgets/0/id") != u'QgisAgriStorico'):
            
            layer.setCustomProperty("embeddedWidgets/count", 1)
            layer.setCustomProperty("embeddedWidgets/0/id", "QgisAgriStorico")         
        else:
            pass
        iface.layerTreeView().refreshLayerSymbology(layer.id())
            
    # --------------------------------------
    # 
    # --------------------------------------  
    @staticmethod
    def removeWidgetInstances() -> None:
        for layer in QgsProject.instance().mapLayers().values():
            layer.setCustomProperty("embeddedWidgets/count", 0)
            iface.layerTreeView().refreshLayerSymbology(layer.id())
            
            