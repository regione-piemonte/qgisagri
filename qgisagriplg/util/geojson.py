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
import copy
from enum import Enum


#
#---------------------------------------------
class geoJsonHelper:
    
    
    # --------------------------------------
    # 
    # --------------------------------------
    class GeomtryType(Enum):
        Unknown            = { 'value': 0, 'multipart': 'Unknown' }
        Point              = { 'value': 1, 'multipart': 'MultiPoint' }
        LineString         = { 'value': 2, 'multipart': 'MultiLineString' }
        Polygon            = { 'value': 3, 'multipart': 'MultiPolygon' }
        MultiPoint         = { 'value': 4, 'multipart': 'MultiPoint' }
        MultiLineString    = { 'value': 5, 'multipart': 'MultiLineString' }
        MultiPolygon       = { 'value': 6, 'multipart': 'MultiPolygon' }
        GeometryCollection = { 'value': 7, 'multipart': 'GeometryCollection' }
        
        @classmethod
        def get(cls, name, asMultipart=False):
            try:
                return cls[name] if not asMultipart \
                        else cls[cls[name].value.get('multipart')]
            except:
                return cls.Unknown
                
        def multipart(self, asMultipart=True):
            try:
                # pylint: disable=E1101
                return self.get( self.value.get('multipart') ) \
                        if asMultipart else self
            except:
                return geoJsonHelper.GeomtryType.Unknown
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self):
        self.tpFeatDict = {}
    
    # --------------------------------------
    # 
    # --------------------------------------
    def collectFeature(self, feat, geom, asMultipart=False):
        # get type
        geomEnum = geoJsonHelper.GeomtryType.get( geom.get( 'type', '' ), asMultipart )
        geomName = geomEnum.name
       
        # check geometry type
        if geomName == "GeometryCollection":
            # loop all geometries in collection
            geomColl = geom.get( 'geometries', [] )
            for g in geomColl:
                self.collectFeature( feat, g, asMultipart )
            return
                
        # clone feature
        newFeat = copy.deepcopy(feat)
        newFeat['geometry'] = geom
        # collect feature
        if geomName not in self.tpFeatDict:
            self.tpFeatDict[geomName] = []
        self.tpFeatDict[geomName].append( newFeat )
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def splitOnGeomType(self, geoJsonData, asMultipart=False):
        # init
        self.tpFeatDict = {}
        
        # loop features collection
        featColl = geoJsonData.get( 'features', [] )
        for feature in featColl:
            # get geometry
            geometry = feature.get( 'geometry', {} )
            # collect feature on geometry type
            self.collectFeature( feature, geometry, asMultipart )
        
        # loop feature collection types
        featCollDict = {
            'MultiPolygon': {
                "type": "FeatureCollection",
                "features": []
            }
        }
        
        for k,v in self.tpFeatDict.items():
            featCollDict[k] = {
                "type": "FeatureCollection",
                "features": v
            }
            
        # return feature collection dict
        return featCollDict
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def countFeatures(self, geoJsonData):
        """ Returns number of features """
        return len( geoJsonData.get( 'features', [] ) )
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def addFid(self, geoJsonData, fid_fld_name='OGC_FID'):
        """ Add FID to features """
        
        # loop features collection
        featColl = geoJsonData.get( 'features', [] )
        for fid, feature in enumerate(featColl, start=1):
            properties = feature.get( 'properties', {} )
            properties[fid_fld_name] = fid
            
        # return GeoJSON data
        return geoJsonData
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def addProperty(self, geoJsonData, property_name, property_value):
        """ Add FID to features """
        # init
        if not property_name:
            return
        # loop features collection
        featColl = geoJsonData.get( 'features', [] )
        for fid, feature in enumerate(featColl, start=1):
            properties = feature.get( 'properties', {} )
            properties[property_name] = property_value
            
        # return GeoJSON data
        return geoJsonData
    
    
        
        