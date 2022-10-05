# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISAgri
                                 A QGIS plugin
 QGIS Agri Plugin
 Created by Sandro Moretti: sandro.moretti@ngi.it
                              -------------------
        begin                : 2019-06-07
        git sha              : $Format:%H$
        copyright            : (C) 2019 by CSI Piemonte
        email                : qgisagri@csi.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import re
from re import RegexFlag
import urllib.parse
import copy
from threading import Timer

from PyQt5.QtCore import QObject, QUrl, QByteArray
from PyQt5.QtNetwork import (QSslConfiguration,
                             QNetworkDiskCache, 
                             QNetworkRequest,
                             QNetworkReply,
                             QNetworkCookie,
                             QNetworkCookieJar
                             #QNetworkProxy
                             )

from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import Qgis, QgsApplication, QgsNetworkAccessManager

from qgis_agri import agriConfig, tr
from qgis_agri import __PLG_DEBUG__
from builtins import isinstance
from qgis_agri.log.logger import QgisLogger as logger



# 
#-----------------------------------------------------------
class QGISAgriRequestError(Exception):
    """Base class for other exceptions"""

# 
#-----------------------------------------------------------
class QGISAgriReplyTimeout(QObject):
    """
    Simple class to add a timer to control timeout request
    """
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, reply, timeout, msgErr=None):
        '''Constructor'''
        super().__init__(parent=reply)
        
        # create timer as child of reply object
        self.__msgErr = msgErr
        self.__timer = None
        if reply is not None and reply.isRunning():
            self.__timer = Timer( timeout, self._onTimeout )
            self.__timer.start()
            
    # --------------------------------------
    # 
    # --------------------------------------        
    def _onTimeout(self):
        """
        Timer callback.
        """
        
        # check if active timer
        if self.__timer is None:
            return
        
        # cancel reply
        try:
            reply = self.parent()
            if reply.isRunning():
                reply.close()
                # set message error
                if self.__msgErr is not None:
                    reply.setErrorString( str( self.__msgErr ) )
        except:
            pass
            
        # cancel timer
        self.__timer.cancel()
        self.__timer = None
        
# 
#-----------------------------------------------------------
class QGISAgriNetworkAccessManagerCollector(QObject):
    
    finishedAllRequests = pyqtSignal(bool)
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, parent=None):
        '''Constructor'''
        super().__init__(parent= parent)
        
        self.__numReplys = 0
        self.__totReplys = 0
        self.__succReplys = 0
        self.__started = False
        self.__aborted = False
        self.__currentReply = None
        self.__replys = []
        self.__errors = []

#     def __enter__(self): 
#         return self
#  
#     def __exit__(self, type, value, traceback):
#         self.endRequest()

    # --------------------------------------
    # 
    # --------------------------------------
    def __del__(self):
        pass
        
    # --------------------------------------
    # 
    # --------------------------------------
    def _checkFinishedAllRequests(self):
        if not self.__started:
            return
        if self.__aborted:
            return
        if self.__numReplys < self.__totReplys:
            return
        
        successful = self.__succReplys >= self.__numReplys
        self.finishedAllRequests.emit( successful )
        
    # --------------------------------------
    # 
    # --------------------------------------    
    @property
    def isStarted(self):
        """ Returns if requests started"""
        return self.__started
    
    # --------------------------------------
    # 
    # --------------------------------------    
    @property
    def isAborted(self):
        """ Returns if requests aborted"""
        return self.__aborted
    
    # --------------------------------------
    # 
    # --------------------------------------    
    @property
    def Errors(self):
        """ Returns network errors"""
        return self.__errors
    
    
        
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def isPending(self):
        """ Returns if requests started"""
        return ( self.__started and 
                 self.__numReplys < self.__totReplys )
                 
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def isSuccesful(self):
        """ Returns if requests started"""
        return ( self.isStarted and
                 not self.__aborted and
                 self.__numReplys >= self.__totReplys and 
                 self.__succReplys >= self.__numReplys )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def addError(self, msg):
        self.__errors.append( str(msg) )
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def abort(self):
        if not self.__started:
            return
        if self.__aborted:
            return
        
        self.__aborted = True
        for reply in self.__replys:
            try:
                reply.abort()
            except:
                pass
            
        self.finishedAllRequests.emit( False )
        
    # --------------------------------------
    # 
    # --------------------------------------
    def append(self, reply):
        if reply is None:
            return
        reply.finished.connect( self.onFinishedRequest )
        self.__totReplys += 1
        self.__replys.append( reply )
        
    # --------------------------------------
    # 
    # --------------------------------------
    def endRequest(self):
        if self.__started:
            return
        self.__started = True
        self.__numReplys = 0
        self.__succReplys = 0
        self._checkFinishedAllRequests()
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def setSuccessful(self):
        if not self.__started:
            return
        self.__succReplys += 1
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def onFinishedRequest(self):
        """finished request slot"""
        reply = self.sender()
        reply.deleteLater()
        self.__numReplys += 1
        self._checkFinishedAllRequests()

# 
#-----------------------------------------------------------
class QGISAgriNetworkAccessManager(QObject):
    """
    """
    
    # --------------------------------------
    # 
    # --------------------------------------
    def group(self):
        return QGISAgriNetworkAccessManagerCollector( self )

    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, parent=None):
        '''Constructor'''
        super().__init__(parent= parent)
        
        # set of client cookies
        self.__cookieSet = set()
        if Qgis.QGIS_VERSION_INT >= 32200:
            self.networkAccessManager.cookiesChanged.connect(self.collectCookies)
        
        # network config
        netConfig = self.networkAccessManager.configuration()
        self.__defaultTimeout = netConfig.connectTimeout()
        
        # set cache
        self.__diskCache = None
        try:
            service_cfg = agriConfig.get_value( 'agri_service' )
            cache_cfg = service_cfg.get( 'cache', '' )
            if cache_cfg:
                import os
                import tempfile
                # create a network manager disk cache
                sysCacheDir = os.path.join( tempfile.gettempdir(), "qgis_agri_cache" )
                diskCache = QNetworkDiskCache( self )
                diskCache.setCacheDirectory( sysCacheDir )
     
                # assign cache to network manager
                self.networkAccessManager.setCache( diskCache )
                self.__diskCache = diskCache
                
        except:
            pass
            
        
    # --------------------------------------
    # 
    # --------------------------------------    
    @property
    def networkAccessManager(self):
        """ Returns reference to the networkAccessManager (readonly) """
        return QgsNetworkAccessManager.instance()
            
            
    # --------------------------------------
    # 
    # --------------------------------------
    def collectCookies(self, lst_cookies):
        """Slot to collect cookies by name, domain, path"""
        lst_cookies = lst_cookies or []
        for cookie in lst_cookies:
            self.__cookieSet.add( (cookie.name(), cookie.domain(), cookie.path()) )
            
    # --------------------------------------
    # 
    # --------------------------------------    
    def onFinishedRequest(self, cdata=None):
        """finished request slot""" 
        
        # init
        reply = self.sender()
        if reply is None:
            return
        
        cdata = cdata or {}
        
        # manage spinner widget
        spinner = cdata.get( 'spinner', None )
        if spinner is not None:
            spinner.close()
        
        # call callback function
        callbackFn = cdata.get( 'callbackFn', None )
        customData = cdata.get( 'customData', None )
        requestCollector = cdata.get( 'requestCollector', None )
        if callbackFn is not None:
            callbackFn( reply, customData, requestCollector )
            
        reply.deleteLater()
        
    # --------------------------------------
    # 
    # --------------------------------------        
    def setTimeout(self, timeout):
        """Set network configuration timeout"""
        timeout = self.__defaultTimeout if timeout is None else timeout
        netConfig = self.networkAccessManager.configuration()
        netConfig.setConnectTimeout( timeout )
    
    # --------------------------------------
    # 
    # --------------------------------------
    def paramizeQuery(self, params):
        # query parameters
        params = params or {}
        query = ""
        if params is not None and params:
            lst = []
            for k,v in params.items():
                lst.append( "{}={}".format( k, urllib.parse.quote(v) ) )
            query = "&".join(lst)
        return query
        
    # --------------------------------------
    # 
    # --------------------------------------        
    def request(self,
                method, 
                url, 
                headers=None, 
                params=None, 
                postData=None,
                postfile=None, 
                parent=None,
                callbackFn=None,
                customData=None, 
                cache=False,
                timeout=None,
                timeoutError=None,
                requestCollector=None):
        """Send request"""
        
        # init
        headers = headers if isinstance( headers, dict ) else {}
        
        # check custom request timeout
        if timeout is not None:
            try:
                timeout = timeout / 1000.0
            except:
                timeout = None
        
        # query parameters
        query = ""
        if params is not None and params:
            lst = []
            for k,v in params.items():
                lst.append( "{}={}".format( k, urllib.parse.quote(v) ) )
            query = "?" + "&".join(lst)
            
            
        # create spinner widget
        spinner = None
#         if parent is not None:
#             spinner = Spinner(parent)
#             spinner.resize(QSize(50, 50))
       
        if __PLG_DEBUG__:
            logger.log( logger.Level.Info, "Richiesta url: {0}".format( url+query ) )
       
        # create request
        reply = None
        request = QNetworkRequest( QUrl(url+query) )
        request.setPriority( QNetworkRequest.HighPriority )
        request.setAttribute( QNetworkRequest.HttpPipeliningAllowedAttribute, True )
        for name, value in headers.items():
            request.setRawHeader( QByteArray( str(name).encode() ), QByteArray( str(value).encode() ) )
       
        # make request
        if method == 'GET':
            # complete request
            if cache and self.__diskCache is not None:
                request.setAttribute( QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferCache )
                request.setAttribute( QNetworkRequest.CacheSaveControlAttribute, True )
            else:
                request.setAttribute( QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.AlwaysNetwork )
                request.setAttribute( QNetworkRequest.CacheSaveControlAttribute, False )
                
            # send a get request to host 
            reply = self.networkAccessManager.get( request )
            
        elif method == 'POST':
            # format post data to send
            postData = postData or ''
            qbaData = QByteArray( postData ) if isinstance( postData, bytes ) else QByteArray( str( postData ).encode() )
            
            # complete request
            request.setRawHeader( QByteArray( b"Content-Length" ), QByteArray.number( qbaData.size() ) )
            
            
            # send a get request to host 
            reply = self.networkAccessManager.post( request, qbaData )
            
        else:
            raise Exception( "{0}: '{1}'".format( tr("Unsupported HTTP method"), method ) )
        
        # complete reply
        if reply is not None:
            # prepare data
            fncData = {
                "callbackFn": callbackFn, 
                "customData": customData, 
                "spinner": spinner,
                "requestCollector": requestCollector 
            }
            
            # handle finished reply signal
            reply.finished.connect( lambda data=fncData, self=self: self.onFinishedRequest( data ) )
            
            # add a timeout timer with custom message error
            if timeout is not None:
                QGISAgriReplyTimeout( reply, timeout, msgErr=timeoutError )
        
            # show spinner
            if spinner is not None:
                spinner.show()
                
            # add to request collector
            if requestCollector is not None:
                requestCollector.append( reply )
        
        # return reply       
        return reply
                
    # --------------------------------------
    # 
    # -------------------------------------- 
    def requestService(self, 
                       service, 
                       params=None, 
                       callbackFn=None, 
                       parent=None, 
                       customData=None, 
                       cache=False,
                       postData=None,
                       directUrl=None,
                       requestCollector=None):
        """Send request to AGRI service"""
        
        # get agri service config
        service_cfg = agriConfig.get_value('agri_service')
        host_cfg = service_cfg.get('host', '')
        #proxy_cfg = service_cfg.get('proxy')
        
        resources_cfg = service_cfg.get('resources')
        res_cfg = resources_cfg.get(service)
        if res_cfg is None:
            raise Exception( "{0}: {1}".format( tr( 'Servizio non reperito: ' ), service ) )
        
        # check url
        url = directUrl
        if directUrl is None:
            url = res_cfg.get('path', '')
            if not url.startswith('http'):
                url = urllib.parse.urljoin(host_cfg, url)
            
        # make request
        return self.request(
            
            res_cfg.get( 'method', 'GET' ),
            url,
            headers = res_cfg.get( 'headers', {} ), 
            params = params if params is not None else res_cfg.get('params', None),
            parent = parent,
            callbackFn = callbackFn,
            customData = customData,
            cache = cache,
            postData=postData,
            timeout = res_cfg.get( 'timeout', None ),
            timeoutError = res_cfg.get( 'timeoutError', None ),
            requestCollector = requestCollector
        )
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def writeDataToFile(self, data, fileName, asTempFile=True):
        """ Method to write data to a temporary file """
        import os
        import tempfile
        from PyQt5.QtCore import QFile
        
        # init
        fileName = str( fileName )
        tmpFilePath = fileName
        file = None
        try:
            if asTempFile:
                # create a temp file
                fileBase = os.path.basename( fileName )
                fileName, fileExt = os.path.splitext( fileBase )
                
                tmpFilePath = None
                tmp = tempfile.NamedTemporaryFile( mode='w', prefix=fileName+'_', suffix=fileExt, delete=False )
                tmpFilePath = tmp.name
            
            # open temp file
            file = QFile( tmpFilePath )
            if not file.open( QFile.WriteOnly | QFile.Truncate ):
                raise IOError( "Cannot open file: {0}".format( tmpFilePath ) )
                
            # write data
            file.write( data )      
            file.close()
            
            return tmpFilePath
                
        finally:
            if file is not None:
                file.close()

    # --------------------------------------
    # 
    # --------------------------------------
    def clearCookies(self, cookie_domain_filter=""):
        """ 
        Static method  to remove all cookies
        from the instance of NetworkAccessManager
        """
        
        # init
        cookie_domain_filter = str(cookie_domain_filter)
        
        nam = QgsNetworkAccessManager.instance()
        cookie_jar = nam.cookieJar()
        
        if Qgis.QGIS_VERSION_INT >= 32200:
            # loop every cookie identifiers
            for c in self.__cookieSet:
                cookie_name = c[0]
                cookie_domain = c[1]
                cookie_path = c[2]
                # filter cookie identifier by domain 
                if re.search(cookie_domain_filter, cookie_domain, RegexFlag.IGNORECASE):
                    # remove cookie
                    cookie = QNetworkCookie(cookie_name)
                    cookie.setDomain(cookie_domain)
                    cookie.setPath(cookie_path)
                    cookie_jar.deleteCookie(cookie)
        
        else:
            # get and check cookie jar
            nam.setCookieJar(QNetworkCookieJar()) # <===== MAY CRASH!!!
            
            """
            lst_cookies =[]
        
            # collect cookies
            for cookie in cookie_jar.allCookies(): <======= C++ PRIVATE METHOD
                cookie_domain = cookie.domain() or ''
                if re.search(cookie_domain_filter, cookie_domain, RegexFlag.IGNORECASE):
                    lst_cookies.append(cookie)
                    
            # remove cookies
            for cookie in lst_cookies:
                cookie_jar.deleteCookie(cookie)
            """    
            
    # --------------------------------------
    # 
    # --------------------------------------
    def add_client_certificate_to_request(self, auth_method, request):
        """
        Static method to add a client certificate 
        to a request, from qgis authorization manager
        """
        
        # Init
        auth_method = str(auth_method)
        
        # Clear network authentication cache
        QgsNetworkAccessManager.instance().clearAccessCache()
        
        
        # Retrieve 'CSI' authorization config
        # from QGIS Authorization Manager, to
        # get client certification
        auth_man = QgsApplication.authManager()
    
        authm_cfg_lst = [a for _, a in auth_man.availableAuthMethodConfigs().items() if a.name() == auth_method]
        if not authm_cfg_lst:
            raise QGISAgriRequestError( 
                tr( "Metodo di autenticazione '{}' non trovato (autenticazione tramite certificato cliente)".format( auth_method ) ) ) 
        authm_cfg = authm_cfg_lst[0]
        if not authm_cfg.isValid():
            raise QGISAgriRequestError( 
                tr( "Metodo di autenticazione '{}' non valido  (autenticazione tramite certificato cliente)".format( auth_method ) ) ) 
            
        #assert( authm_cfg.method() == 'Identity-Cert' )
        
        # Reload authorization config from the database
        if not auth_man.loadAuthenticationConfig( authm_cfg.method(), authm_cfg, True ):
            raise QGISAgriRequestError( 
                tr( "Impossibile leggere il metodo di autenticazione '{}' (autenticazione tramite certificato cliente)".format( auth_method ) ) )
           
        auth_method = auth_man.authMethod( authm_cfg.method() )
        auth_method.updateNetworkRequest( request, authm_cfg.id() )
        sslConfig_req = request.sslConfiguration()
    
        sslConfig = QSslConfiguration.defaultConfiguration()
        certs = sslConfig.caCertificates()
        localCerts = sslConfig.localCertificateChain()
        localCerts.append( sslConfig_req.localCertificate() )
        #certs = certs + importedCerts
    
        sslConfig.setLocalCertificateChain( localCerts )
        sslConfig.setCaCertificates( certs )
        sslConfig.setPrivateKey( sslConfig_req.privateKey() )
        QSslConfiguration.setDefaultConfiguration(sslConfig)
        #request.setSslConfiguration(sslConfig)

    # --------------------------------------
    # 
    # --------------------------------------
    def getConfigService(self, service):
        #copy.deepcopy(value)
        # get agri service config
        service_cfg = agriConfig.get_value('agri_service')
        host_cfg = service_cfg.get('host', '').strip()
        if not host_cfg.endswith('/'):
            host_cfg = "{}/".format( host_cfg )
        
        #proxy_cfg = service_cfg.get('proxy')
        
        resources_cfg = service_cfg.get('resources')
        res_cfg = resources_cfg.get(service)
        if res_cfg is None:
            return {}
        
        res = copy.deepcopy( res_cfg )
        url = res_cfg.get('path', '')
        if not url.startswith('http'):
            res['path'] = urllib.parse.urljoin( host_cfg, url )
            
        return res