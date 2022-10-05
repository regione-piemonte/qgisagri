# -*- coding: utf-8 -*-
"""Modulo per la visualizzazione delle informazioni di suolo.

Descrizione
-----------

Implementazione della classe che gestisce la visualizzazione dei dati di un suolo
tramite una finestra di dialogo; i dati visualizzati sono:

- informazioni sul suolo;
- utilizzo del suolo;
- UNAR poligono;
- UNAR particella. 

Utilizzata una pagina HTML per La formattazione e la visualizzazione dei dati, tabulati
per le voci sovraelencate.  

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
import json
from os import path
# PyQt5 modules
from PyQt5.QtCore import Qt, QTimer
# qgis modules
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, pyqtSlot
# plugin modules
from qgis_agri import __QGIS_AGRI_NAME__, tr
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.html.generate import htmlUtil
from qgis_agri.gui.layer_util import QGISAgriLayers

FORM_CLASS, _ = uic.loadUiType(path.join(
    path.dirname(__file__), 'ui/qgis_agri_documents_dialog.ui'))
 

# QGISAgri documents dialog
#-----------------------------------------------------------
class QGISAgriPcgInfoDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog to show PCG data"""
    
    zoomToSuoloByExpression = pyqtSignal(str,object,bool)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        """Constructor
        
        :param parent: 
        :type parent: QtWidgets
        """
        super(QGISAgriPcgInfoDialog, self).__init__(parent, flags)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.__dataSourceUri = None
        self.__idKeyFieldName = ''
        self.__idKeyValue = ''
        self.__geoJsonData = {}
        self.__lstErrors = []
        self.__currTabName = ''
        
        self.setWindowTitle( f"{__QGIS_AGRI_NAME__} - Piano Colturale Grafico" )
        
        webView = self.webView
        ##webView.setZoomFactor( horizontalDpi / 96.0 )
        webPage = webView.page()
        webView.setContextMenuPolicy( Qt.CustomContextMenu )
        webPage.mainFrame().javaScriptWindowObjectCleared.connect( self._loadJsPyApi )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __del__(self):
        """Destructor"""

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _loadJsPyApi(self):
        """Add pyapi to javascript window object"""
        frame = self.webView.page().mainFrame()
        frame.addToJavaScriptWindowObject( 'pyroleapi', self )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _getLayerName(self):
        if self.__dataSourceUri is None:
            return None
        
        layName = self.__dataSourceUri.table()
        return layName

    
    # --------------------------------------
    # 
    # --------------------------------------     
    def show(self):
        # call base method
        QtWidgets.QDialog.show(self)
        
        # check if errors
        if self.__lstErrors:
            QTimer.singleShot( 0, lambda: logger.msgbox( 
                logger.Level.Critical, 
                '\n\n'.join( self.__lstErrors ), 
                title=tr('ERRORE') ) )
    
    def reset(self):
        # init
        self.__dataSourceUri = None
        self.__geoJsonData = {}
        self.__lstErrors = []
        self.__currTabName = ''
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def loadPcgData(self,
                    layer,
                    idKeyFieldName: str, 
                    idKeyValue: int) -> None:
        # init
        self.__idKeyFieldName = idKeyFieldName
        self.__idKeyValue = idKeyValue
        
        
        # load GeoJSON file
        uri = QGISAgriLayers.get_data_source_file_path( layer )
        if self.__dataSourceUri != uri or not self.__geoJsonData:
            self.__dataSourceUri = uri
            self.__geoJsonData = {}
            with open( self.__dataSourceUri ) as f:
                self.__geoJsonData = json.load( f )
                
        
        # get selected feature data
        data = {}
        features = self.__geoJsonData.get( 'features', [] )
        feat_data = list(filter(lambda x: x.get( 'properties', {} ).get( idKeyFieldName ) == idKeyValue, features))
        if feat_data:
            data['datoPCG'] = feat_data[0].get( 'properties', {} )
        else:
            return
        
        data['layerName'] = layer.name()
        data['currentTabName'] = self.__currTabName
        
        if not self.isVisible():
            self.__currTabName = ''
        
        # load documents web page 
        template = htmlUtil.generateTemplate( 'pcg_documents.html' )
        self.webView.setHtml( template.render( [], **data ) )
        
       
    # --------------------------------------
    # 
    # --------------------------------------
    @pyqtSlot(str)
    def change_suolo_tab(self, tabName: str) -> None:
        """Store html current tab name"""
        self.__currTabName = tabName
        
    # --------------------------------------
    # 
    # --------------------------------------
    @pyqtSlot(result=bool)
    def zoom_to_suolo(self):
        """Zoom to suolo"""
        if not self.__idKeyFieldName:
            return False
        # emit signal for zoom
        expr = "{0}={1}".format( self.__idKeyFieldName, self.__idKeyValue )
        self.zoomToSuoloByExpression.emit( expr, self.__dataSourceUri, True )
        return True