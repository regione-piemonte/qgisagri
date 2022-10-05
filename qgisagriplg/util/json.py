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
import json
import datetime
from qgis_agri import tr


# subclass JSONEncoder
#-----------------------------------------------------------
class JsonDateTimeEncoder(json.JSONEncoder):
    #Override the default method
    def default(self, o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

# 
#-----------------------------------------------------------
class jsonUtil:
    """Utility class to manage JSON objects"""
      
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def numBoolDictionary():
        """
        Get dictionary to convert boolean values as 0 or 1
        """
        return {
            '1': 1,
            '0': 0,
            'true': 1, 
            'false': 0
        }
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @staticmethod
    def strBoolDictionary():
        """
        Get dictionary to convert boolean values as false or true
        """
        return {
            '1': True,
            '0': False,
            'true': True,
            'false': False
        }
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod    
    def concatFldDefDict(d1, d2, *other):
        """
        Concatenates two or more fields definition dictionaries together.
        Field definitions are chosen from the most left dictionary to the right.
        """
        # init
        res = {}
        lstDicts = []
        lstDicts.append( d1 )
        lstDicts.append( d2 )
        lstDicts = lstDicts + list(other)
        
        # loop fields definition dictionaries
        for d in lstDicts:
            # check if dictionary
            if not isinstance( d, dict ):
                continue
            # loop fields definition in dictionary
            for k,v in d.items():
                # check if value is a dictionary
                if not isinstance( v, dict ):
                    continue
                # check ad adjust if field name is renamed
                rename = v.get( 'rename', None )
                if rename is not None:
                    k = str(rename)
                # add field definiton in result dictionary   
                if k in res:
                    continue
                res[k] = v
            
        return res
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def _parseJSON(d, dictProps, boolMapDict):
        """
        Method to convert data type of object literal decoded.
        """
        for propName, propDef in dictProps.items():
            # get property value
            val = d.get( propName, None )
            if val is None:
                continue
                
            # get property type
            tp = propDef.get( 'type', None )
            if tp is None:
                raise Exception( "{0}: '{1}'".format( tr( 'Tipologia campo non definita' ), propName ) )
            tp = tp.lower()
            
            # try to convert
            try:
                if tp == 'str' or tp == 'string':
                    d[propName] = str(val)
                    
                elif tp == 'int' or tp == 'integer':
                    d[propName] = int(val)
                    
                elif tp == 'double':
                    d[propName] = float(val)
                    
                elif tp == 'bool' or tp == 'boolean':
                    d[propName] = boolMapDict[ str(val).lower() ]
                    
                elif tp == 'jsonintarray' and isinstance( val, list ):
                    d[propName] = list( map( lambda x: x if x is None else int(x), val ) )
                    
            except KeyError:
                pass
            
        return d
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def load(fp, dictProps, boolMapDict=None):
        """
        Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
        a JSON document) to a Python object.
        """
        if not isinstance( dictProps, dict ):
            raise Exception( tr( 'jsonUtil.loads - secondo parametro non valido' ) )
        
        boolMapDict = jsonUtil.strBoolDictionary() if boolMapDict is None else boolMapDict
          
        return json.load( fp, object_hook = lambda d: jsonUtil._parseJSON( d, dictProps, boolMapDict ) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def loads(s, dictProps, boolMapDict=None):
        """
        Deserialize s (a str, bytes or bytearray instance 
        containing a JSON document) to a Python object.
        """
        if not isinstance( dictProps, dict ):
            raise Exception( tr( 'jsonUtil.loads - secondo parametro non valido' ) )
        
        boolMapDict = jsonUtil.strBoolDictionary() if boolMapDict is None else boolMapDict
          
        return json.loads( s, object_hook = lambda d: jsonUtil._parseJSON( d, dictProps, boolMapDict ) )
        
