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
import os.path
import types
# PyQt5 modules
from PyQt5.QtCore import Qt, QTimer
# qgis modules
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, pyqtSlot
# plugin modules
from qgis_agri import __QGIS_AGRI_NAME__, tr
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.html.generate import htmlUtil


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/qgis_agri_documents_dialog.ui'))
 

# QGISAgri documents dialog
#-----------------------------------------------------------
class QGISAgriDocumentsDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog to show feature documents"""
    
    zoomToFeatureByExpression = pyqtSignal(str,object)
    changeParentFeature = pyqtSignal(object, str, int, int, list, str, object, dict)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        """Constructor
        
        :param parent: 
        :type parent: QtWidgets
        """
        super(QGISAgriDocumentsDialog, self).__init__(parent, flags)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.__dataSourceUri = None
        self.__idKeyFieldName = ''
        self.__idKeyFeature = ''
        self.__idFeature = ''
        self.__lstIdFeature = []
        self.__lstErrors = []
        self.__currTabName = ''
        self.__htmlTemplate = 'suolo_documents.html'
        self.__dataLoaderFunc = None
        self.__optionData = {}
        
        
        webView = self.webView
        webView.setContextMenuPolicy( Qt.CustomContextMenu )
        ##webView.setZoomFactor( horizontalDpi / 96.0 )
        webPage = webView.page()
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
    
    def reset(self, idFeature):
        # init
        self.__idKeyFieldName = ''
        servicesData = {
            'idFeature': idFeature,
            'lstIdFeature': [],
            'datiGen': {},
            'datiUsoPart': {},
            'datiUnarPolig': {},
            'datiUnarPart': {},
            'datiUsoPart_summery': {
                'superficie': '0.0000'
            },
            'datiUnarPolig_summery': {
                'superficie': '0.0000'
            },
            'datiUnarPart_summery': {
                'superficie': '0.0000'
            },
            'layerName': 'Scaricamento dei dati dal server...',
            'currentTabName': self.__currTabName
        }
        # load documents web page 
        template = htmlUtil.generateTemplate( self.__htmlTemplate )
        self.webView.setHtml( template.render( [], **servicesData ) ) 
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def loadDocumentData(self, 
                         dataSourceUri: object, 
                         idKeyFieldName: str, 
                         idKeyFeature: int,
                         idFeature: int, 
                         lstIdFeature: list,
                         servicesData: dict,
                         lstErrors: list,
                         htmlTemplate: str,
                         dataLoaderFunc: types.FunctionType,
                         optionData: dict) -> None:
        # init
        self.__dataSourceUri = dataSourceUri
        self.__idKeyFieldName = idKeyFieldName
        self.__idKeyFeature = idKeyFeature
        self.__idFeature = idFeature
        self.__lstIdFeature = lstIdFeature
        self.__lstErrors = list(lstErrors)
        self.__htmlTemplate = htmlTemplate
        self.__dataLoaderFunc = dataLoaderFunc
        self.__optionData = optionData or {}
        
        if not self.isVisible():
            self.__currTabName = ''
        
        servicesData = servicesData or {}
        servicesData['layerName'] = self._getLayerName()
        servicesData['currentTabName'] = self.__currTabName
        
        # set window title
        windowTitle = self.__optionData.get( "windowTitle", "Dati" )
        self.setWindowTitle( f"{__QGIS_AGRI_NAME__} - {windowTitle}" )
        
        # load documents web page 
        template = htmlUtil.generateTemplate( self.__htmlTemplate )
        self.webView.setHtml( template.render( [], **servicesData ) )
        
    
    
    # --------------------------------------
    # 
    # --------------------------------------
    @pyqtSlot(str)
    def change_tab(self, tabName: str) -> None:
        """Store html current tab name"""
        self.__currTabName = tabName
    
    # --------------------------------------
    # 
    # --------------------------------------
    @pyqtSlot(int, result=bool)
    def change_parent_feature(self, idFeature: int) -> bool:
        """Change id to parent feature and reload info"""
        if not idFeature:
            return False
        # emit signal for parent feature changed
        self.changeParentFeature.emit( 
            self.__dataSourceUri, 
            self.__idKeyFieldName, 
            self.__idKeyFeature, 
            idFeature, 
            self.__lstIdFeature,
            self.__htmlTemplate,
            self.__dataLoaderFunc,
            self.__optionData )
        
        return True
        
    # --------------------------------------
    # 
    # --------------------------------------
    @pyqtSlot(result=bool)
    def zoom_to_feature(self):
        """Zoom to feature"""
        if not self.__idKeyFieldName:
            return False
        # emit signal for zoom
        expr = "{0}={1}".format( self.__idKeyFieldName, self.__idKeyFeature )
        self.zoomToFeatureByExpression.emit( expr, self.__dataSourceUri )
        return True