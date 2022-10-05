# -*- coding: utf-8 -*-
"""QGIS Agri external browser

Description
-----------

Python script to show authentication external browser.

Libraries/Modules
-----------------

- None.
    
Notes
-----

- None.

TODO
----

- None.

Author(s)
---------

- Created by Sandro Moretti on 12/06/2022.

Copyright (c) 2019 CSI Piemonte.

Members
-------
"""
#: Constant value for successful authorization 
__QGIS_AGRI_AUTH_OK__ = b'QGISAGRI:AUTH:OK'

#: Constant name for socket authorization server 
__QGIS_AGRI_AUTH_SOCKETID__ = "C737A0CE-069F-45F4-A249-985B13E946EC"


import sys
import json

# Import necessary libraries
from PyQt5.QtCore import QSize, QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView
from PyQt5.QtNetwork import QLocalSocket

#
#-----------------------------------------------------------
class MainWindow(QMainWindow):

    # Constructor of this class
    def __init__(self):
        """Constructor"""
        
        # Init
        super(MainWindow, self).__init__()
        self._msecs = 5000
        self._running = False
        self._authOrigUrl = ''
        self._authUrl = ''
        
        # Settings
        self.setWindowTitle("QGIS Agri- Autenticazione")
        ##dw = QDesktopWidget()
        ##self.resize(dw.width()*0.7,dw.height()*0.7)
        
        # Create client socket
        self._socketOut = QLocalSocket(self)
        
        # Create web view widget
        self.browser = QWebEngineView()
        self.browser.loadFinished.connect(self.onLoadFinished)
        self.setCentralWidget(self.browser)
 
        # Load initial page 
        #self.browser.setHtml(self.getInfoPageContent("Collegamento al plugin"))
 
        # Show
        self.show() #self.showMaximized() #self.show() #self.showMaximized()
        
    def sizeHint(self):
        return QSize(1000, 800)

    def getInfoPageContent(self, message):
        """Returns a defaul info HTML content"""
        
        return """
        
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            body {
                background: #595BD4;
            }
            .loading {
                position: absolute;
                left: 0;
                right: 0;
                top: 30%;
                width: 200px;
                color: #FFF;
                margin: auto;
                transform: translateY(-30%);
            }
            .loading span {
                position: absolute;
                height: 10px;
                width: 180px;
                top: 50px;
                overflow: hidden;
            }
            .loading span > i {
                position: absolute;
                height: 4px;
                width: 4px;
                border-radius: 50%;
                animation: wait 4s infinite;
            }
            .loading span > i:nth-of-type(1) {
                left: -128px;
                background: yellow;
            }
            .loading span > i:nth-of-type(2) {
                left: -121px;
                animation-delay: 0.8s;
                background: lightgreen;
            }
            @keyframes wait {
                0%   { left: -7px  }
                30%  { left: 132px  }
                60%  { left: 72px  }
                100% { left: 200px }
            } 
            </style>  

            </head>
            <body>
                <div class="loading">
                    <h3>__message__</h3>
                    <span><i></i><i></i></span>
                </div>
            </body>
            </html>
        
        """.replace("__message__", message)
        
    
    def showEvent(self, event):
        """Override show event"""
        QMainWindow.showEvent(self, event)
        QTimer.singleShot(200, self.connectToQgisAgri)
        
    
    def closeEvent(self, event):
        """Override close event"""      
        self._running = False
        # close and dispose 
        self.browser.close()
        del self.browser
        self._socketOut.close()
        del self._socketOut
        QMainWindow.closeEvent(self, event)
        
        
    def quitApplication(self, msec=200):
        """Quit main application aftee an elapsed time"""
        self.close()
        QTimer.singleShot(msec, lambda: QApplication.instance().exit())
    
    
    def connectToQgisAgri(self):
        """Connect client/server sockets"""
        # create client socket
        self._socketOut.connectToServer(__QGIS_AGRI_AUTH_SOCKETID__)
        self._socketOut.error.connect(self.onSocketError)
        self._running = self._socketOut.waitForConnected()
        if not self._running:
            self.onError("Impossibile collegarsi al plugin QgisAgri.")
            return
        
        # connect signal
        self._socketOut.disconnected.connect(self.onDisconnected)
        
            
        if not self._socketOut.waitForReadyRead(self._msecs):
            self.onError("Impossibile collegarsi al plugin QgisAgri.")
            return
       
        try:
            # read data from server
            data = self._socketOut.readAll().data()
            data = json.loads(str(data, 'UTF8'))
            self._authOrigUrl = data.get("authOrigUrl", '')
            self._authUrl = data.get("authUrl", '')
            
        except Exception as ex:
            self.onError(str(ex))
            self.onError("Impossibile collegarsi al plugin QgisAgri.")
            return
            
        # load authentication page
        cookie_store = QWebEngineProfile.defaultProfile().cookieStore()
        cookie_store.cookieAdded.connect(self.onCookieAdd)
        self.browser.setUrl(QUrl(self._authUrl))
        
    
    def onDisconnected(self):
        """Disconnected slot"""
        if not self._running:
            return
        self.onError("Persa la connessione al plugin QgisAgri", quit_app=False)
            
    def onError(self, message, quit_app=True):
        """Handle errors"""  
        self._running = False
        if message:
            QMessageBox.critical(self, "QgisAgri", message)
        if quit_app:
            self.quitApplication()
            
            
    def onSocketError(self, message):
        """Handle socket errors"""
        print(f"Errore sul collegamento al plugin QgisAgri:\n{message}")
    
    
    def onCookieAdd(self, cookie):
        """
        :param cookie: QNetworkCookie
        """
        if not self._running:
            return
            
        # send coockie to plugin
        self._socketOut.write(cookie.toRawForm())
        if not self._socketOut.waitForBytesWritten(self._msecs):
            self.onError(f"Invio dati non riuscito entro {(self._msecs / 1000.)}: secondi")


    def onLoadFinished(self, ok):
        """On page loaded signal slot"""
        if not self._running:
            return
            
        # Check if authentication page
        current_url = self.browser.url().toString()
        url = QUrl(self._authOrigUrl)
        url.setQuery('')
        if self._authOrigUrl in current_url or url.toString() in current_url:
            self.browser.page().toPlainText(self._checkAutenticated)

        
            
    def _checkAutenticated(self, page_content):
        """Check if authenticate page content"""
        
        # Check if method authenticated
        try:
            # check if json result
            _ = json.loads(str(page_content))
        except json.JSONDecodeError:
            return
        
        # disconnect signal
        self._socketOut.disconnected.disconnect(self.onDisconnected)
        
        # set authentication page
        self.browser.setHtml(self.getInfoPageContent("Invio autenticazione al plugin"))
        
        # send authorized message
        self._socketOut.write(__QGIS_AGRI_AUTH_OK__)
        if not self._socketOut.waitForBytesWritten(self._msecs):
            self.onError(f"Invio dati non riuscito entro {(self._msecs / 1000.)}: secondi")
            return
        
        # close and exit application
        self.quitApplication(msec=1000)
        

if __name__ == "__main__":
    # Create application
    app = QApplication(sys.argv)
    # Specify application name
    QApplication.setApplicationName("QGIS_Agri_Ext_Browser")
    # Create main window
    window = MainWindow()
    window.show()
    # Run application event loop
    app.exec()
    