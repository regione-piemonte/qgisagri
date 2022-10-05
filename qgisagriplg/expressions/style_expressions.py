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
from qgis.core import QgsProject, QgsDataSourceUri #, QgsExpressionContextScope, QgsExpressionContextUtils
from qgis.utils import qgsfunction, spatialite_connect

# --------------------------------------
# 
# -------------------------------------- 
@qgsfunction(args='auto', group='Custom') # do not use args='auto' | args=<num of params without last two ones(feature, parent)>
def getAgriDbEleggibilitaDescription(layer, code, feature, parent):
    """
    Expression function to obtain Eleggibilità description from DB table by its code
    """
    
    ret = ''
    conn = None
    curs = None
    layer_name = layer or ''
    
    try:
        # Get layer reference from layername
        layer = QgsProject.instance().mapLayersByName(layer)[0]
    
        # Raise if layer not found
        if layer is None:
            raise Exception( "Layer not found: " + layer_name )
            
        data_provider = layer.dataProvider()
        uri = QgsDataSourceUri( data_provider.dataSourceUri() )
    
        # execute query on Agri offline db
        conn = spatialite_connect( uri.database() )
        cur = conn.cursor()
        cur.execute( "SELECT descEleggibilitaRilevata FROM ClassiEleggibilita WHERE codiceEleggibilitaRilevata = '{0}'".format( code ) )
        result = cur.fetchone()
        ret = result[0] if result else ''
        
    except Exception as e:
        raise e
    
    finally:
        if curs is not None:
            curs.close()
        if conn is not None:
            conn.close()
        
    return ret


# --------------------------------------
# 
# -------------------------------------- 
@qgsfunction(args='auto', group='Custom') # do not use args='auto' | args=<num of params without last two ones(feature, parent)>
def isSuoloPropostoUsed(layer_name, suoloId, feature, parent):
    """
    Expression function to check if a 'Suolo proposto' is used
    """
    from qgis.core import QgsExpression, QgsFeatureRequest, QgsFeature
    
    it = None
    try:
        # init
        layer_name = layer_name or ''
    
        # get layer reference from layername
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    
        # raise if layer not found
        if layer is None:
            raise Exception( "Layer not found: " + layer_name )
            
        #  build the expression
        expr = QgsExpression( "_propostoRefId={}".format( suoloId ) )
        
        # get a featureIterator from an expression
        feat = QgsFeature()
        it = layer.getFeatures( QgsFeatureRequest( expr ) )
        if it.nextFeature( feat ):
            return True
        
        return False
        
    except Exception as e:
        raise e
    
    finally:
        if it is not None:
            it.close()



# --------------------------------------
# 
# -------------------------------------- 
@qgsfunction(args='auto', group='Custom')
def is_agri_valid_geom(geom, feature, parent):
    """
    Expression function to check if a valid feature geometry
    """
    try:
        return geom.isGeosValid()
    except Exception as e:
        return False
    
    
# --------------------------------------
# 
# -------------------------------------- 
@qgsfunction(args='auto', group='Custom')
def agri_format_numero_particella(mappale, num_zero, feature, parent):
    """
    Expression function to check if a valid feature geometry
    """
    try:
        return str(mappale).strip().lstrip('0').zfill(num_zero)
    except Exception as e:
        return mappale


# --------------------------------------
# 
# -------------------------------------- 
@qgsfunction(args='auto', group='Custom')
def isEditedFeature(layer_id, feature, parent):
    """
    Expression function to check if a feature is edited
    """
    try:
        # get layer reference from layer name
        layer = QgsProject.instance().mapLayer(layer_id)
        if not layer:
            return False
        # check if not editable layer
        if not layer.isEditable():
            return False
        # get feature id
        fid = feature.id()
        # get layer edit buffer
        edit_buffer = layer.editBuffer()
        # check if feature added
        if edit_buffer.isFeatureAdded(fid):
            return True
        # check if attribute changed
        if edit_buffer.isFeatureAttributesChanged(fid):
            return True
        # check if geometry changed
        if edit_buffer.isFeatureGeometryChanged(fid):
            return True
        return False
    
    except Exception:
        return False
    
"""
QgsExpressionContextUtils.setGlobalVariable('qgi_agri_curr_photo_fid', str(2))

# --------------------------------------
# 
# -------------------------------------- 
@qgsfunction(args='auto', group='Custom')
def getCurrAppezzPhotoId(feature, parent):
    #Returns the value of the variable 'var_name' 
    #Example usage: env('user_full_name')
    
    global_var_name = 'qgi_agri_curr_photo_fid'
    
    if not QgsExpressionContextScope.hasVariable(QgsExpressionContextUtils.globalScope(), global_var_name):
        return None
    
    return QgsExpressionContextScope.variable(QgsExpressionContextUtils.globalScope(), global_var_name)
"""
