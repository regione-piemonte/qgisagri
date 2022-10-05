# -*- coding: utf-8 -*-
"""Modulo per la gestione e collezione degli errori delle verifiche dei suoli

Descrizione
-----------

Implementazione della classe che gestisce la collezione degli errori e delle
segnalazioni riscontrate dalle verifiche dei suoli; salvati i messaggi di 
errore, la gravità dello stesso, la feature o geometria dell'elemento con
difformità.


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
from qgis.core import (NULL,
                       QgsProject,
                       QgsFeature,
                       QgsVectorLayer,
                       QgsGeometry)

from qgis_agri import __QGIS_AGRI_LAYER_TAG__, agriConfig
from qgis_agri.gui.layer_util import QGISAgriLayers
 
#
#-----------------------------------------------------------
class QGISAgriFeatureErrors:
    """Class to collect features errors"""
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self):
        """Constructor"""
        self.__errorlst = []
        self.__errorNum = 0
        self.__errorWrn = 0
        
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def hasErrors(self):
        """ Returns true if there are errors(readonly) """
        return self.__errorlst and self.__errorNum > 0
        
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def hasWarnings(self):
        """ Returns true if there are warnings(readonly) """
        return self.__errorlst and self.__errorWrn > 0
    
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def numErrors(self):
        """ Returns number of errors(readonly) """
        return self.__errorNum
        
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def numWarnings(self):
        """ Returns number of warnings(readonly) """
        return self.__errorWrn
        
    # --------------------------------------
    # 
    # --------------------------------------    
    @property
    def errors(self):
        """ Returns errors list (readonly) """
        return self.__errorlst
        
    # --------------------------------------
    # 
    # --------------------------------------
    def clear(self):
        """ Method to clear internal errors list """
        self.__errorlst.clear()
        
    # --------------------------------------
    # 
    # --------------------------------------
    def append(self,
               msg, 
               layer='', 
               fid=None, 
               geom=None, 
               isWarning=False,
               isForcedWarning=False, 
               fictitious=False,
               msgCode=None):
        """ Method to append a new error to internal list """
        
        if geom is not None:
            geom = QgsGeometry( geom )
            geom.convertToMultiType()
        
        # append
        self.__errorlst.append({
            'message': str(msg),
            'layer': str(layer),
            'fictitious': fictitious,
            'fid': fid,
            'geom': geom,
            'isWarning': isWarning,
            'isForcedWarning': isForcedWarning,
            'msgCode': msgCode
        })
        if isWarning:
            self.__errorWrn += 1
        else:
            self.__errorNum += 1
     
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def appendFromLayer(self, 
                        srcLayer, 
                        msg, 
                        isWarning=False,
                        isForcedWarning=False,
                        layerAliasName=None, 
                        fictitious=False, 
                        filterWarnExpr=None,
                        msgWarnExpr=None,
                        addCounter=True,
                        addArea=True,
                        minAreaForAppend=None,
                        msgCode=None):
        
        """Method to append errors from a layer feature"""
        # init
        if srcLayer is None:
            return
        
        _layerAliasName = layerAliasName or srcLayer.name()
        
        requestWarn = None
        if filterWarnExpr is not None:
            from qgis.core import QgsFeatureRequest, QgsExpression
            requestWarn = QgsFeatureRequest( QgsExpression( filterWarnExpr ) )
        
        # counter
        totFeatures = srcLayer.featureCount()
        countFeature = 0
        
        # check if minimal layer total area 
        if minAreaForAppend is not None:
            area = 0.0
            totFeatures = 0
            for feature in srcLayer.getFeatures():
                _geom = feature.geometry()
                area = _geom.area()
                if area < minAreaForAppend:
                    continue
                totFeatures += 1
            """
                area += _geom.area()
            if not (area > minAreaForAppend):
                return
            """
        
        # get list of features sorted by area    
        features = sorted(srcLayer.getFeatures(), 
                          key=lambda f: f.geometry().area(), 
                          reverse=True)
        
        # collect error from geometries
        for feature in features:
            # init
            _geom = feature.geometry()
            area = _geom.area()
            if minAreaForAppend is not None:
                if area < minAreaForAppend:
                    continue
            
            #
            _msg = msg
            _isWarning = isWarning
            countFeature += 1
            
            
            # check if filter error as warning
            if requestWarn is None:
                pass
            elif requestWarn.acceptFeature( feature ):
                _isWarning = True
                _msg = msg if msgWarnExpr is None else msgWarnExpr
            
            # area 
            if addArea and _geom:
                _msg = "{} [{:.{prec}f} mq]".format( _msg, area, prec= agriConfig.display_decimals )
               
                
            # add counter in message
            if addCounter:
                _msg = "{} ({}/{})".format( _msg, countFeature, totFeatures )
                
            # append error or warning
            self.append( _msg, 
                         layer =_layerAliasName, 
                         fid = feature.id(), 
                         geom = _geom, 
                         isWarning = _isWarning,
                         isForcedWarning = isForcedWarning,
                         fictitious = fictitious,
                         msgCode = msgCode )
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def getForcedWarnings(self):
        """Return forced warnings"""
        return list( map( lambda e: e.get( 'message' ), 
                          filter( lambda e: e.get( 'isWarning' ) and e.get('isForcedWarning'), 
                                  self.__errorlst  ) ) )
     
    def getUniqueForcedWarnings(self):
        """Return forced warnings: only one for message type"""
        filtered = filter( lambda e: e.get( 'isWarning' ) and e.get('isForcedWarning'), self.__errorlst )
        return list( { str(e.get('msgCode')): e.get( 'message' ) for e in filtered }.values() )  
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def createLayer(self, srcLayer, layerName, tocGrpName=None, wkbType='MultiPolygon', crs='EPSG:3003'):
        """Method to create a layer with errors"""
        
        # init
        project = QgsProject.instance()
        
        # clear older layer
        layers = project.mapLayersByName( layerName )
        for lay in layers:
            project.removeMapLayer( lay )
        layers = None
        
        # create layer
        errLayer = QgsVectorLayer( 
            f"{wkbType}?crs={crs}&field=fid:integer&field=layer:string(250)&field=message:string(250)&field=warning:integer", 
            layerName, "memory" )
        errLayer.setReadOnly( True )
        
        # mark as plugin layer
        errLayer.setProperty( __QGIS_AGRI_LAYER_TAG__, True )
        
        provider = errLayer.dataProvider()
        
        # add freatures
        errFeatures = []
        for err in self.__errorlst:
            # get other geometry
            geom = err.get( 'geom', None )
            if geom is None:
                geom = QgsGeometry()
                
            # fid
            fid = err.get( 'fid', None )
            if fid is None:
                fid = NULL
            
            # create new feature to export
            errFeature = QgsFeature()
            errFeature.setGeometry( geom )
            errFeature.setAttributes( [ 
                err.get( 'fid', -1 ), 
                err.get( 'layer', '' ),
                err.get( 'message', '' ), 
                err.get( 'isWarning', 0 ) 
            ] )
            errFeatures.append( errFeature )
            
        provider.addFeatures( errFeatures )
        
        # get \ create group layer
        root_node = grp_node = project.layerTreeRoot()
        if tocGrpName is not None:  
            _, grp_node = QGISAgriLayers.create_toc_group_path( tocGrpName, root_node, 0 )
        
        # add layer to QGIS layers registry
        project.addMapLayer( errLayer, False )
        
        # load layer in toc
        grp_node.insertLayer( 0, errLayer )
        
        # layer repaint
        errLayer.triggerRepaint()
        
