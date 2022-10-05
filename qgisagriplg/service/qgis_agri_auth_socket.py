# -*- coding: utf-8 -*-
"""pyUtilclass

Description
-----------

Utility class to operate with Python processes.

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
import re
from re import RegexFlag

from PyQt5.QtCore import pyqtSignal, QObject, QByteArray
from PyQt5.QtNetwork import QLocalServer, QNetworkCookieJar, QNetworkCookie
from qgis.core import QgsNetworkAccessManager

#: Constant value for successful authorization 
__QGIS_AGRI_AUTH_OK__ = b'QGISAGRI:AUTH:OK'

#: Constant name for socket authorization server 
__QGIS_AGRI_AUTH_SOCKETID__ = "C737A0CE-069F-45F4-A249-985B13E946EC"


#
#------------------------------------------------------
class QgisAgriAuthSocket(QObject):
    
    # signals
    authenticated = pyqtSignal()
    
    def __init__(self, parent=None):
        """Constructor"""
        super().__init__(parent)
        self._socketIn = None
        self._socketServer = None
        self._data = ''
        self._msecs = 5000
               
        
    def _onNewConnection(self):
        """New socket connection slot"""  
        if self._socketIn:
            self._socketIn.readyRead.disconnect(self._onReadyRead)
            
        self._socketIn = self._socketServer.nextPendingConnection()
        if not self._socketIn:
            return
        
        self._socketIn.disconnected.connect(self.removeServer)
        
        self._socketIn.write(QByteArray(bytes(self._data,'UTF-8')))
        #if not self._socketIn.waitForBytesWritten(self._msecs):
        #    return #self.onError(f"Invio dati non riuscito entro {(self._msecs / 1000.)}: secondi")
        
        self._socketIn.readyRead.connect(self._onReadyRead)
        
    def _onReadyRead(self):
        """Server socket message slot"""
        while 1:
            message = self._socketIn.readLine()
            if not message:
                break
            
            if message == __QGIS_AGRI_AUTH_OK__:
                self.authenticated.emit() 
                return 
               
            try:
                nam = QgsNetworkAccessManager.instance()
                cookie_jar = nam.cookieJar()
                for cookie in QNetworkCookie.parseCookies(QByteArray(message)):
                    if re.search('piemonte.it$', cookie.domain(), RegexFlag.IGNORECASE):
                        cookie_jar.insertCookie(cookie)
                        
            except TypeError:
                pass
    
    def createServer(self, data):
        """Create Server socket"""
        self._data = data
        self.removeServer()
        self._socketServer = QLocalServer(self)
        if not self._socketServer.listen(__QGIS_AGRI_AUTH_SOCKETID__):
            return False
        self._socketServer.newConnection.connect(self._onNewConnection)
        return True

    
    def removeServer(self):
        """Remove Server socket"""
        socket = self._socketServer
        self._socketServer = None
        if socket:
            socket.close()
            socket.removeServer(__QGIS_AGRI_AUTH_SOCKETID__)
            del socket
    