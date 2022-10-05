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
import collections

from PyQt5.QtCore import QVariant
from qgis.core import (NULL, 
                       QgsWkbTypes, 
                       QgsFields, 
                       QgsField, 
                       #QgsPointXY,
                       QgsFeature,
                       QgsGeometry, 
                       QgsVectorLayer, 
                       QgsVectorFileWriter, 
                       QgsCoordinateReferenceSystem)


# 
#-----------------------------------------------------------
class QGISAgriFieldValueConverter(QgsVectorFileWriter.FieldValueConverter):
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, layer, cfg_fields):
        QgsVectorFileWriter.FieldValueConverter.__init__(self)
        self.__layer = layer
        self.__cfg_fields = cfg_fields
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def fieldDefinition(self, field):
        fldName = field.name()
        fldDef = self.__cfg_fields.get( field.name(), None )
        if fldDef is not None:
            fldType = str( fldDef.get( 'type', '' ) ).lower()
            if fldType == 'int':
                return QgsField( fldName, QVariant.Int )
        
        return field 
#         fields = self.__layer.fields()
#         idx = fields.indexFromName( fldName )
#         return fields[idx]
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def convert(self, idx, value):
        field = self.__layer.fields().at( idx )
        fldDef = self.__cfg_fields.get( field.name(), None )
        if fldDef is None:
            return value
        
        fldType = str( fldDef.get( 'type', '' ) ).lower()
        if fldType == 'int':
            return int(value)
        
        return value

# 
#-----------------------------------------------------------
class QGISAgriVectorFileWrite:
    """ Utiliy class for Agri layer exporting. """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self,
                 vectorFileName,
                 fileEncoding = "utf-8",
                 crs = None,
                 driverName = 'GeoJSON'):
        
        """Constructor"""
        self.__vectorFileName = vectorFileName
        self.__fileEncoding = fileEncoding
        self.__crs = crs
        self.__driverName = driverName
        self.__written = False
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def _createOutputLayerFields(self, layer, cfg_fields):
        """Private method to create output layer fields"""
        # define export fields
        layFields = layer.fields()
        outFields = QgsFields()
        suolo_key_field = None
        
        for fldName, fldDef in cfg_fields.items():
            index = layFields.indexFromName( fldName )
            if index != -1:
                field = layFields.field( index )
                
                # check if to rename
                rename = fldDef.get( 'rename', None )
                if rename:
                    field = QgsField( field )
                    field.setName( rename )
                    
                # add existing field
                outFields.append( field )
                
                # check if suolo key field
                is_suolo_key_field = fldDef.get( 'suolo_key_field', False ) or False
                if is_suolo_key_field:
                    suolo_key_field = fldName
            else:
                # create new missing field
                fldType = fldDef.get( 'type', 'String' )
                fldType = { 
                    
                  'int': QVariant.Int,
                  'integer': QVariant.Int,
                  'bool': QVariant.Int,
                  'boolean': QVariant.Int,
                  'double': QVariant.Double,
                  'str': QVariant.String,
                  'string': QVariant.String
                  
                }.get( fldType.lower(), QVariant.String )
                
                outFields.append( QgsField( fldName, fldType ) )
                
        return outFields, suolo_key_field
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _getFeatureValues(self, feature, cfg_fields):
        """Private method to get feature values"""
        fields = feature.fields()
        lstValues = []
        
        for fldName, fldDef in cfg_fields.items():
            # get value from feature
            index = fields.indexFromName( fldName )
            if index == -1:
                value = NULL
            else:
                value = feature.attribute( index )
            
            # correct value         
            if 'value' in fldDef:
                calcValue = fldDef.get( 'value' )
                if isinstance( calcValue, collections.Callable ):
                    try:
                        value = calcValue( feature, value )
                    except:
                        value = None
                else:
                    value = calcValue
            
            # append value to list        
            lstValues.append( value )
            
        return lstValues
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def writeLayer(self,
                   layer,
                   layerName,
                   cfg_fields,
                   featureSelExpr = None, 
                   layerOptions = None,
                   append = True,
                   skipEmptyGeom = False,
                   skipNullKeyField = False):
        """Method to append a vector layer to an exported file"""
        
        # init
        crs = self.__crs or QgsCoordinateReferenceSystem( 4326, QgsCoordinateReferenceSystem.EpsgCrsId )
        layerOptions = layerOptions or ["LAUNDER=NO","GEOMETRY_NAME=geometry"]
        layerName = layerName or layer.name()
        append = append if self.__written else False
        
        # define export fields
        outFields, suolo_key_field = self._createOutputLayerFields( layer, cfg_fields )
        
        # create memory vector layer
        outLayer = QgsVectorLayer( "{0}?crs={1}".format( QgsWkbTypes.displayString( layer.wkbType() ), crs.authid() ), 
                                   layerName, "memory" )
        provider = outLayer.dataProvider()
        provider.addAttributes( outFields )
        outLayer.updateFields()
        
        # Add a feature
        outFeatures = []
        featIter = layer.getFeatures( featureSelExpr ) if featureSelExpr else layer.getFeatures()
        for feature in featIter:
            # get source feature geometry
            geom = feature.geometry()
            
            # skip feature if empy or null 
            if skipEmptyGeom:
                if geom.isEmpty() or geom.isNull():
                    continue
            
            # skip if key field is null
            if skipNullKeyField:
                suolo_key_field_value = feature.attribute( suolo_key_field )
                if suolo_key_field_value == NULL:
                    continue
                                
            # create new feature to export
            outFeature = QgsFeature()
            outFeature.setGeometry( geom )
            outFeature.setAttributes( self._getFeatureValues( feature, cfg_fields ) )
            outFeatures.append( outFeature )#outLayer.addFeature( outFeature )
        
        # check if there are feature to write
        if not outFeatures:
            return
            
        # add new feature to temp layer to write out
        provider.addFeatures( outFeatures )
         
        #
        #converter = QGISAgriFieldValueConverter( outLayer, cfg_fields ) 
         
        # set layer options
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.layerName = layerName
        options.driverName = self.__driverName
        options.fileEncoding = self.__fileEncoding
        options.actionOnExistingFile = QgsVectorFileWriter.AppendToLayerAddFields if append else QgsVectorFileWriter.CreateOrOverwriteFile
        ###options.layerName = table
        ###options.forceMulti = True
        ###options.overrideGeometryType = QgsWkbTypes.Polygon
        options.layerOptions = layerOptions
        #options.fieldValueConverter = converter
         
        # export layer to existing file
        error, error_string = QgsVectorFileWriter.writeAsVectorFormat( outLayer, self.__vectorFileName, options )
        if error != QgsVectorFileWriter.NoError:
            raise Exception( error_string )
        
        self.__written = True
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def writeFictitiousFeature(self,
                               layer,
                               layerName,
                               cfg_fields,
                               extent = None,
                               layerOptions = None):
        """Method to append a fictitious feature for user settings or other layer
           where the geometry is fictitious: only attributes are needed.
        """
        
        # init
        extent = extent or layer.extent()
        value_lst = list( map( lambda e: e.get( 'value' ), cfg_fields.values() ) )
        crs = self.__crs or QgsCoordinateReferenceSystem( 4326, QgsCoordinateReferenceSystem.EpsgCrsId )
        layerOptions = layerOptions or ["LAUNDER=NO","GEOMETRY_NAME=geometry"]
        layerName = layerName or layer.name()
        append = True if self.__written else False
        
        # define export fields
        outFields, _ = self._createOutputLayerFields( layer, cfg_fields )
        
        # create memory vector layer
        outLayer = QgsVectorLayer( "{0}?crs={1}".format( QgsWkbTypes.displayString( layer.wkbType() ), crs.authid() ), 
                                   layerName+'_Header', "memory" )
        provider = outLayer.dataProvider()
        provider.addAttributes( outFields )
        outLayer.updateFields()
        
        # Add a feature point with settings
        outFeature = QgsFeature()
        #outFeature.setGeometry( QgsGeometry.fromPointXY( QgsPointXY(0,0) ) )
        outFeature.setGeometry( QgsGeometry.fromRect( extent ) )
        outFeature.setAttributes( value_lst )
   
        provider.addFeature( outFeature )
         
        #
        #converter = QGISAgriFieldValueConverter( outLayer, cfg_fields ) 
         
        # set layer options
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.layerName = layerName
        options.driverName = self.__driverName
        options.fileEncoding = self.__fileEncoding
        options.actionOnExistingFile = QgsVectorFileWriter.AppendToLayerAddFields if append else QgsVectorFileWriter.CreateOrOverwriteFile
        ###options.layerName = table
        ###options.forceMulti = True
        ###options.overrideGeometryType = QgsWkbTypes.Polygon
        options.layerOptions = layerOptions
        #options.fieldValueConverter = converter
         
        # export layer to existing file
        error, error_string = QgsVectorFileWriter.writeAsVectorFormat( outLayer, self.__vectorFileName, options )
        if error != QgsVectorFileWriter.NoError:
            raise Exception( error_string )
        
        self.__written = True
        
        