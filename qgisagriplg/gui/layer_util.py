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
from os import path
from urllib import parse
#from distutils.util import strtobool

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMessageBox

from qgis.core import (NULL,
                       Qgis,
                       #QgsSettings,
                       #QgsMapSettings,
                       #QgsSnappingUtils, 
                       QgsCoordinateTransform,
                       QgsDataSourceUri,
                       QgsProject,
                       QgsGeometry,
                       QgsFeature,
                       QgsVectorLayerUtils,
                       QgsMapLayer,
                       QgsPoint,
                       QgsFeatureSource,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsVectorLayerEditUtils,
                       QgsCoordinateReferenceSystem,
                       QgsSpatialIndex,
                       QgsFieldConstraints,
                       QgsWkbTypes,
                       QgsProviderRegistry)


from qgis.utils import iface
from qgis.analysis import QgsGeometrySnapper

from qgis_agri import __QGIS_AGRI_LAYER_TAG__, agriConfig, tr
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.gui.geometry_util import QGISAgriGeometry
from qgis_agri.gui.geometrysnapper import QGISAgriGeometrySnapper
from qgis_agri.qgis_agri_exceptions import QGISAgriException



# 
#-----------------------------------------------------------
class QGISAgriLayers:
    """ Utiliy class for Agri layer manipulation. """
    
    __isLayerStyleUpdating = False
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def removeAllMapLayers():
        """Remove all map layers in project"""
        project = QgsProject.instance()
        project.removeAllMapLayers()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def clear_toc(skipRasterLayer=False):
        """Remove layers in TOC"""
        # Get the project instance
        project = QgsProject.instance()
        # loop layers in TOC
        root_node = project.layerTreeRoot()
        for layer in project.mapLayers().values():
            # check if raster layer
            if skipRasterLayer and layer.type() == QgsMapLayer.RasterLayer:
                continue
            
            # find layer node in TOC
            node = root_node.findLayer( layer )
            if node is None:
                continue
                
            # remove layer\node in TOC
            grp_node = node.parent()
            grp_node.removeLayer( layer )
        
        # remove empty group nodes
        root_node.removeChildrenGroupWithoutLayers()
         
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def extract_geometry_vertices(geom):
        n = 0
        ver = geom.vertexAt(0)
        points = []
         
        # extract nodes
        while(ver != QgsPoint(0,0)):
            n +=1
            points.append(ver)
            ver=geom.vertexAt(n)

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def set_current_layer(layer):
        curlayer = iface.activeLayer()
        if curlayer == layer:
            return
        view = iface.layerTreeView()
        view.setCurrentLayer( None ) 
        view.setCurrentLayer( layer )
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def read_only_layers(vlay_list, read_only=True):
        # loop layers
        for vlayer in vlay_list:
            vlayer.setReadOnly(read_only)
    
    """
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def update_layer_snap_locator(layer, enableSnappingForInvisibleFeature=False):
        #init
        #value = QgsSettings().value( "/qgis/digitizing/snap_invisible_feature", False )
        #enableSnappingForInvisibleFeature = bool( strtobool(value) )
        # get map canvas
        canvas = iface.mapCanvas()
        # update  map canvas util
        snapUtils = canvas.snappingUtils()
        map_settings = snapUtils.mapSettings()
        #
        snapUtils.setEnableSnappingForInvisibleFeature( enableSnappingForInvisibleFeature )
        snapUtils.setMapSettings( QgsMapSettings() )
        snapUtils.setMapSettings( map_settings )
        # 
        canvas.setSnappingUtils( QgsSnappingUtils( snapUtils.parent() ) )
        canvas.setSnappingUtils( snapUtils )
    """    
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def start_editing(vlay_list, force_edit=False):
        # loop layers
        for vlayer in vlay_list:
            if not vlayer.isEditable():
                if force_edit:
                    vlayer.setReadOnly( False )
                    #QGISAgriLayers.update_layer_snap_locator( vlayer, enableSnappingForInvisibleFeature=True )
                vlayer.startEditing()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def end_editing(vlay_list, allowCancel=False):
        # loop layers
        res = True
        for vlayer in vlay_list:
            if vlayer.isEditable():
                res = res and iface.vectorLayerTools().stopEditing( vlayer, allowCancel )
        return res
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def end_editing_ext(vlay_list, 
                        buttons=QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel, 
                        noMessage=False, 
                        callback=None,
                        headerMessage=None,
                        msgLevel=Qgis.Info):
        # loop layers
        buttons = QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel if buttons is None else buttons
        headerMessage = headerMessage or ''
        oper = QMessageBox.Save if noMessage else None
        
        # compose message
        lays = [l.name() for l in vlay_list if l.isEditable()]
        if len(lays) == 1:
            msg = tr( 'Voi salvare le modifiche apportate al vettore?' )
        else:
            msg = tr( 'Voi salvare le modifiche apportate ai vettori?' )
            
        msg_lays = ''.join( map(lambda x: f'<li>{x}</li>', lays) )
        msg = f"{msg}<ul>{msg_lays}</ul>"
        
        if headerMessage:
            msg = f"{headerMessage}{msg}" 
        
        # close editing for each layer
        for vlayer in vlay_list:
            if not vlayer.isEditable():
                continue
            
            if not vlayer.isModified():
                if not vlayer.commitChanges():
                    raise Exception( vlayer.commitErrors() )
                continue
            
            if oper is None:
                oper = logger.htmlMsgbox( 
                    msgLevel, 
                    msg, 
                    title= tr( 'Interrompi modifica' ),
                    standardButtons= buttons )
                """
                oper = QMessageBox.information( 
                    iface.mainWindow(), 
                    tr( 'Interrompi modifica' ), 
                    msg, 
                    btns_ext if allowCancel else btns_def )
                """
                if oper == QMessageBox.Cancel:
                    return False
            
                if callback:
                    callback( vlayer, oper, True )    
                
            if oper == QMessageBox.Save:
                if not vlayer.commitChanges():
                    raise Exception( vlayer.commitErrors() )
                
            elif oper == QMessageBox.Discard:
                if not vlayer.rollBack():
                    raise Exception( vlayer.commitErrors() )
                
            if callback:
                callback( vlayer, oper, False )
   
        return True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def end_all_editing(allowCancel=False):
        # loop layers in editing mode
        res = True
        vlay_list = iface.editableLayers()
        for vlayer in vlay_list:
            res = res and iface.vectorLayerTools().stopEditing( vlayer, allowCancel )
        return res
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def is_requested_vectorlayer(layer, data_source_uri_lst):
        # check if vector layer
        if layer is None:
            return False
        if layer.type() != QgsMapLayer.VectorLayer:
            return False
        # check data source uri
        lay_source = QGISAgriLayers.get_data_source_file_path( layer )
        data_provider = layer.dataProvider()
        ds_uri = data_provider.dataSourceUri()
        uri = QgsDataSourceUri( ds_uri )
        ds_lst = [ path.normpath( uri.database() ), uri.table() ]
        
        for data_source_uri in data_source_uri_lst:
            if isinstance( data_source_uri, QgsDataSourceUri ):
                params = [path.normpath(data_source_uri.database()), data_source_uri.table()] 
                if all((a.lower() == b.lower()) for a, b in zip(params, ds_lst)):
                    return True
            else:
                data_source_uri = path.normpath( str( data_source_uri ) )
                if data_source_uri == lay_source:
                    return True
                
        return False
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_data_source_uri(layer_lst):
        res = []
        for layer in layer_lst:
            provider = layer.dataProvider()
            res.append( QgsDataSourceUri( provider.dataSourceUri() ) )
        return res
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_data_source_file_path(layer):
        # get source path
        provider = layer.dataProvider().name()
        source_parts = QgsProviderRegistry.instance().decodeUri( provider, layer.source() )
        source_path = source_parts.get( 'path', '' )
        if 'ogr' == provider.lower():
            source_path = source_path.split('|')[0]
        return path.normpath( source_path )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_vectorlayer(data_source_uri_lst, source_other_than_rdbms=False):
        data_source_uri_lst = data_source_uri_lst or []
        layer_lst = []
        layers = QgsProject.instance().layerTreeRoot().findLayers()
        for data_source_uri in data_source_uri_lst:
            if not data_source_uri:
                continue
            
            elif source_other_than_rdbms and isinstance( data_source_uri, str ):
                data_source_uri = path.normpath( data_source_uri )
                for node_layer in layers:
                    layer = node_layer.layer()
                    layer_type = layer.type()
                    if layer_type != QgsMapLayer.VectorLayer:
                        continue
                    
                    ds_uri = QGISAgriLayers.get_data_source_file_path( layer )
                    if data_source_uri == ds_uri:
                        layer_lst.append( layer )
            
            else:
                params = [path.normpath(data_source_uri.database()), data_source_uri.table()]
                for node_layer in layers:
                    layer = node_layer.layer()
                    layer_type = layer.type()
                    if layer_type != QgsMapLayer.VectorLayer:
                        continue
                
                    data_provider = layer.dataProvider()
                    uri = QgsDataSourceUri(data_provider.dataSourceUri())
                    ds_lst = [path.normpath(uri.database()), uri.table()]
                    if all((a.lower() == b.lower()) for a, b in zip(params, ds_lst)):
                        layer_lst.append(layer)
        return layer_lst
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_toc_vectorlayer(data_source_uri,
                           provider=None,
                           toc_grp_name=None):
        
        """Get Ari layer from Toc."""
        
        # check dat source uri
        if data_source_uri is None:
            return None
        
        
        # get group node from toc
        # pylint: disable=E1101
        root_node = grp_node = QgsProject.instance().layerTreeRoot()
        if toc_grp_name is not None:
            grp_node = root_node.findGroup(toc_grp_name)
        if grp_node is None:
            return None
        
        #
        params = [path.normpath(data_source_uri.database()), data_source_uri.table()]
        
        # get layer in group node
        layers = grp_node.findLayers()
        for node in layers:
            layer = node.layer()
            layer_type = layer.type()
            # pylint: disable=E1101
            if layer_type != QgsMapLayer.VectorLayer:
                continue
            
            # get layer provider data
            data_provider = layer.dataProvider()
            if (provider is not None and 
                data_provider.name().lower() != provider.lower()):
                continue
            
            # pylint: disable=E1101
            uri = QgsDataSourceUri( data_provider.dataSourceUri() )
            ds_lst = [path.normpath(uri.database()), uri.table()]
            if all((a.lower() == b.lower()) for a, b in zip(params, ds_lst)):
                return layer
          
        return None
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_toc_vectorlayer_by_uri(uriDict: dict, 
                                   provider: str, 
                                   toc_grp_name: str =None) -> QgsVectorLayer:
        # get formatted uri
        uriDict = uriDict or {}
        
        # get group node from toc
        root_node = grp_node = QgsProject.instance().layerTreeRoot()
        if toc_grp_name is not None:
            grp_node = root_node.findGroup(toc_grp_name)
        if grp_node is None:
            return None
        
        # get layer in group node
        layers = grp_node.findLayers()
        for node in layers:
            layer = node.layer()
            layer_type = layer.type()
            if layer_type != QgsMapLayer.VectorLayer:
                continue
            
            # get layer provider data
            lay_provider = layer.dataProvider()
            if lay_provider.name().lower() != provider.lower():
                continue
            
            # get source path
            source_parts = QgsProviderRegistry.instance().decodeUri( 
                layer.dataProvider().name(), layer.source() )
            source_path = source_parts.get( 'path', '' )
            if 'ogr' == provider.lower():
                source_path = source_path.split('|')[0]
            source_path = path.normpath( source_path )
            
            # get source layer name
            layer_name = source_parts.get( 'layerName', '' )
            if not layer_name or layer_name == NULL:
                layer_name = layer.name()
            
            # check if equal source
            if source_path == path.normpath( uriDict.get( 'path', '' ) ) and\
               layer_name == uriDict.get( 'layerName', '' ):
                return layer
          
        return None
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_layers_id_by_filesource(fileSource: str) -> QgsMapLayer:
        # init
        fileSource = path.normpath( fileSource )
        lstLayers = []
        
        # loop all layer in group node
        for k, layer in QgsProject.instance().mapLayers().items():
            laySource = QGISAgriLayers.get_data_source_file_path( layer ) 
            if laySource == fileSource:
                lstLayers.append( k )
          
        return lstLayers
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod    
    def create_toc_group_path(grp_path, parent_node, start=0):
        node = parent_node
        new_lst = []
        grp_lst = str(grp_path).split('/')
        grp_len = len( grp_lst )
        for grp_name in grp_lst:
            create_node = True
            if grp_len == 1 and grp_name.startswith( '*' ):
                create_node = False
                grp_name = grp_name[1:]
            node = parent_node.findGroup( grp_name )
            if node is None:
                if not create_node:
                    return '/'.join( new_lst ), node
                node = parent_node.insertGroup( start, grp_name )
            new_lst.append( grp_name )
            parent_node = node
            start = -1
        return '/'.join( new_lst ), node   
     
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod    
    def create_toc_groups(lst_grp_name, start=0):
        index = start
        root_node = QgsProject.instance().layerTreeRoot()
        for toc_grp_name in lst_grp_name:
            # create group node
            new_path, _ = QGISAgriLayers.create_toc_group_path( 
                toc_grp_name, root_node, index )
            if toc_grp_name.startswith( '*' ):
                toc_grp_name = toc_grp_name[1:]
            if new_path == toc_grp_name:
                index += 1
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod    
    def add_toc_vectorlayer(data_source_uri,
                             provider,
                             crs=None,
                             toc_lay_name=None,
                             toc_grp_name=None,
                             toc_grp_index=-1,
                             toc_lay_order=-1,
                             exclude_empty=False,
                             style_file=None,
                             show_total=True,
                             node_expanded=True,
                             toc_grp_sort_fn=None):
        """Add Agri vector layer to Toc."""
      
        # check dat source uri & provider
        if data_source_uri is None:
            return None
        
        uri = ''
        vlayer = None
        if isinstance( data_source_uri, dict ):
            uri = data_source_uri.get( 'uri', '' )
            vlayer = QGISAgriLayers.get_toc_vectorlayer_by_uri( 
                data_source_uri, provider, toc_grp_name=toc_grp_name )
        else:
            # format params
            uri = data_source_uri.uri()
            toc_lay_name = toc_lay_name or data_source_uri.table()
            vlayer = QGISAgriLayers.get_toc_vectorlayer( data_source_uri )
            
            
        # check if layer already exists
        root_node = grp_node = QgsProject.instance().layerTreeRoot()
        if vlayer is not None:
            # show layer
            lay_node = root_node.findLayer( vlayer.id() )
            lay_node.setItemVisibilityCheckedRecursive( True ) 
            return vlayer
        
        # create vector layer
        opts = QgsVectorLayer.LayerOptions()
        opts.loadDefaultStyle = False
        vlayer = QgsVectorLayer( uri, toc_lay_name, provider, options=opts )
        if not vlayer.isValid():
            raise Exception( vlayer.error().message() )
        
        # mark as plugin layer
        vlayer.setProperty( __QGIS_AGRI_LAYER_TAG__, True )
        
        # set crs
        if crs is not None:
            vlayer.setCrs( QgsCoordinateReferenceSystem( crs ), False )
        
        # load layer style
        if style_file is not None:
            vlayer.loadNamedStyle( style_file, True )
        
        
        # load layer in TOC
        if exclude_empty and vlayer.hasFeatures() == QgsFeatureSource.NoFeaturesAvailable:
            return vlayer
        
        # add layer to QGIS layers registry
        QgsProject.instance().addMapLayer( vlayer, False )
        
        # create toc group node if not exists
        if toc_grp_name is not None:
            _, grp_node = QGISAgriLayers.create_toc_group_path( toc_grp_name, root_node, toc_grp_index )
            
        # add layer in TOC
        layNode = grp_node.insertLayer( toc_lay_order, vlayer )
        layNode.setExpanded(node_expanded)
        
        # sort layer group
        if toc_grp_sort_fn is not None:
            lyrList = [c.layer() for c in grp_node.children()]
            lyrSortList = sorted(lyrList, key=toc_grp_sort_fn)
    
            for idx, lyr in enumerate(lyrSortList):
                _ = grp_node.insertLayer(idx, lyr)
    
            grp_node.removeChildren(len(lyrList),len(lyrList))
                    
        
        ## set custom property to show total features per layer
        if show_total:
            layNode.setCustomProperty( "showFeatureCount", True )
            # patch to update feature counts
            filterExpr = vlayer.subsetString()
            if not filterExpr:
                vlayer.setSubsetString( 'FALSE' )
                vlayer.setSubsetString( filterExpr )
                renderer = vlayer.renderer().clone()
                vlayer.setRenderer( renderer )
        
        return vlayer
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def reorder_layer(layer, index):
        root = QgsProject.instance().layerTreeRoot()
        nodeLayer = root.findLayer(layer.id())
        nodeClone = nodeLayer.clone()
        nodeParent = nodeLayer.parent()
        nodeParent.insertChildNode(index, nodeClone)
        nodeParent.removeChildNode(nodeLayer)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod    
    def add_toc_owslayer(ows_url_params,
                          toc_lay_name=None,
                          toc_grp_name=None,
                          toc_grp_index=-1, 
                          style_file=None,
                          allowInvalidSource=False,
                          recreateLayer=False):
        """Add Agri raster layer to Toc."""
        
        # check params
        if not isinstance( ows_url_params, dict ):
            return None
        
        lay_name = ows_url_params.get( 'layers', None )
        if lay_name is None:
            return None
        
        url = ows_url_params.get( 'url', None )
        if url is None:
            return None
        
        # correct url
        qUrl = QUrl( url )
        qUrl.setQuery( QUrl.toPercentEncoding( qUrl.query() ).data().decode() )
        ows_url_params[ 'url' ] = qUrl.toString()
        
#        # extract info from ows layer
#         try:
#             # get ows Capabilities
#             from owslib.wmts import WebMapTileService
#             wmts = WebMapTileService( ows_url_params.get('url') )
#             ows_layer = wmts.contents.get(lay_name)
#             if ows_layer is not None:
#                 if toc_lay_name is None: 
#                     toc_lay_name = ows_layer.title
#         except Exception as e:
#             print( str(e) )
        
        # format parameter
        toc_lay_name = toc_lay_name or lay_name
        
        # check if group node exists
        grp_lay_index = 0
        root_node = grp_node = QgsProject.instance().layerTreeRoot()
        if toc_grp_name is not None:         
            grp_node = root_node.findGroup( toc_grp_name )
            if grp_node is None:
                grp_node = root_node.insertGroup( toc_grp_index, toc_grp_name )
                
        
        # URL construction
        wms_url_final = parse.unquote( parse.urlencode( ows_url_params ) )
        uri = QgsDataSourceUri( wms_url_final )
        uri_match = re.sub( r"\/ogcproxy\/[^\/]*\/", "/ogcproxy/", uri.encodedUri().data().decode() )
        
        # get layer in group node
        recreateNodeVisible = None
        layers = grp_node.findLayers()
        for node in layers:
            layer = node.layer()
            layer_type = layer.type()
            if layer_type != QgsMapLayer.RasterLayer:
                continue
            
            # get layer provider data
            data_provider = layer.dataProvider()
            umatch = re.sub( r"\/ogcproxy\/[^\/]*\/", "/ogcproxy/", data_provider.uri().encodedUri().data().decode() )
            if umatch != uri_match:
                pass
            
            elif recreateLayer or not layer.isValid():
                try:
                    grp_lay_index = grp_node.children().index( layer )
                except:
                    grp_lay_index = 0
                    
                recreateNodeVisible = node.isVisible()
                
                grp_node.removeChildNode( node )
                QgsProject.instance().removeMapLayer( layer.id() )
                break
            
            else:
                return layer
                
        # let's try to add it to the map canvas
        rlayer = QgsRasterLayer( wms_url_final, toc_lay_name, 'wms' )
        if not rlayer.isValid():
            if not allowInvalidSource:
                raise Exception( rlayer.error().message() )
            
        # mark as plugin layer
        rlayer.setProperty( __QGIS_AGRI_LAYER_TAG__, True )

        # add layer to QGIS layers registry
        QgsProject.instance().addMapLayer( rlayer, False )
        
        # load layer in toc
        node = grp_node.insertLayer( grp_lay_index, rlayer )
        
        if recreateNodeVisible is not None:
            node.setItemVisibilityChecked( recreateNodeVisible )
        
        return rlayer
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def layer_editFormFields_setReadOnly(vlayer, str_fld_list, read_only=True):
        # format list of fields to set read only in edit form
        if not isinstance( str_fld_list, str ):
            return
        
        fld_list = [ k.strip() for k in str_fld_list.split( ',' ) ]
        if not fld_list:
            return
        
        filter_fields = '*' not in fld_list
        
        # get layer edit form instance
        layEditFormCfg = vlayer.editFormConfig()
        # loop all field widgets in field form
        layFields = vlayer.fields()
        for idx in range( layFields.count() ):
            # filter field widget 
            field = layFields.at( idx )
            if ( filter_fields and 
                 field is not None and 
                 field.name() not in fld_list ):
                continue
            # set field widget as read only
            layEditFormCfg.setReadOnly( idx, readOnly=read_only )
        # re apply edit format 
        vlayer.setEditFormConfig( layEditFormCfg )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def update_layers(lay_list):
        if type(lay_list) is not list:
            return
        for layer in lay_list:
            # pylint: disable=E1101
            if isinstance(layer, QgsMapLayer):
                layer.triggerRepaint()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def update_layers_renderer(lay_list):
        try:
            if QGISAgriLayers.__isLayerStyleUpdating:
                return
            QGISAgriLayers.__isLayerStyleUpdating = True
            
            if type(lay_list) is not list:
                return
            
            for layer in lay_list:
                # pylint: disable=E1101
                if isinstance(layer, QgsMapLayer):
                    renderer = layer.renderer().clone()
                    layer.setRenderer( renderer )     
        finally:
            QGISAgriLayers.__isLayerStyleUpdating = False
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def hide_layers(lay_list, hide=True):
        if type(lay_list) is not list:
            return
        # pylint: disable=E1101
        root_node = QgsProject.instance().layerTreeRoot()
        for layer in lay_list:
            # pylint: disable=E1101
            if isinstance(layer, QgsMapLayer):
                lay_node = root_node.findLayer( layer.id() )
                lay_node.setItemVisibilityCheckedRecursive( not hide )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod           
    def show_layer_labels(lay_list):      
        for layer in lay_list:
            layer.setLabelsEnabled( not layer.labelsEnabled() )
        QGISAgriLayers.update_layers( lay_list )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod           
    def activate_layer_Labeling(lay_list, label_name, active=True, activeSwitch=False):
        from qgis.core import QgsRuleBasedLabeling
        
        # prepare label rule name
        hide_min_scale = False
        label_negate = False
        label_name = str(label_name).strip()  
        if label_name.startswith('!'):
            label_name = label_name[1:]
            label_negate = True
         
        for layer in lay_list:
            # get type of labelling
            layer_settings = layer.labeling()
            if not isinstance( layer_settings, QgsRuleBasedLabeling ):
                # if not rule base
                if activeSwitch:
                    active = not layer.labelsEnabled()
                layer.setLabelsEnabled( active )
                continue
            
            # activate\deactivate rule
            for rule in layer_settings.rootRule().descendants():
                labe_eq = rule.description() == label_name
                if label_negate ^ labe_eq:
                    # activate\deactivate rule
                    if activeSwitch:
                        active = not rule.active()
                    rule.setActive( active )
                    # if activated rule, check scale visibility
                    if active and\
                       rule.dependsOnScale() and\
                       rule.minimumScale() < iface.mapCanvas().scale():
                        hide_min_scale = True
                        
         
        # update layers   
        QGISAgriLayers.update_layers( lay_list )
        
        # return 
        return { 'hide_min_scale': hide_min_scale }
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def zoom_layers_ext(lay_list): 
        ##xform = QgsCoordinateTransform(layer.crs(), canvas.mapSettings().destinationCrs()) for CRS
        ###canvas.setExtent(xform.transform(layer.extent()))
        
        p = QgsProject.instance()
        
        extent = None
        for layer in lay_list:
            if ( layer.type() == QgsMapLayer.VectorLayer and
                 layer.hasFeatures() == QgsFeatureSource.NoFeaturesAvailable ):
                continue
            
            xform = QgsCoordinateTransform( layer.crs(), p.crs(), p )
            lay_extent = xform.transform( layer.extent() )
            if extent is None:
                extent = lay_extent
            else:
                extent.combineExtentWith( lay_extent )
                
        if extent is None:
            return
        
        canvas = iface.mapCanvas()
        canvas.setExtent( extent )
        canvas.refresh()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def zoom_full_extent():
        # pylint: disable=E1101    
        canvas = iface.mapCanvas()
        canvas.zoomToFullExtent()
        canvas.refresh()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def remove_layers(layers: list, noException: bool =True) -> None:
        try:
            lstIdLays = [l.id() for l in layers]
            QgsProject.instance().removeMapLayers( lstIdLays )
        except Exception as ex:
            if not noException:
                raise ex
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def change_map_crs(crs):
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(crs))
    
     
    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod        
    def repair_feature_single(layer, 
                       feature, 
                       attr_dict=None, 
                       splitMultiParts=False,
                       autoSnap=False,
                       suoliMinArea=agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO,
                       suoliSnapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE,
                       suoliSnapLayerUris=None,
                       addTopologicalPoints=False):
        
        """ Method to auto repair a feature geometry """
        
        # init
        res = True
        errMsg = ''
        geom = None
        
        # get auto repai attribute
        if not attr_dict:
            attr_dict = {}
            fld_lst = agriConfig.get_value( 'commands/repairsuolo/wrkFields', [] )
            for fld_def in fld_lst:
                if 'setValue' not in fld_def:
                    continue
                fld_name = fld_def.get( 'name', '' )
                fld_value = fld_def.get( 'setValue', None )
                attr_dict[fld_name] = fld_value
        
        # snap geometry (make valid)
        if autoSnap and suoliSnapLayerUris is not None and suoliSnapLayerUris:
            suoliSnapLayers = QGISAgriLayers.get_vectorlayer( suoliSnapLayerUris )
            geom = QGISAgriLayers.snapFeature( suoliSnapLayers, feature, snapTolerance=suoliSnapTolerance ) 
            
        else:
            geom = QgsGeometry( feature.geometry() )   
            
        # repair geometry
        if geom.isGeosValid():
            newGeom = geom
        else:
            newGeom = geom.makeValid()
            if not newGeom.isGeosValid():
                res = False
                errMsg += newGeom.lastError()
                newGeom = QgsGeometry( feature.geometry() )
                
        # bufferize
        """
        newGeom = newGeom.buffer( -(agriConfig.TOLERANCES.CLEAN_VERTEX_TOLERANCE), 0 )\
                         .buffer( agriConfig.TOLERANCES.CLEAN_VERTEX_TOLERANCE*1.3, 0 )\
                         .intersection( newGeom )\
                         .simplify( agriConfig.TOLERANCES.CLEAN_VERTEX_TOLERANCE )
        """
            
        # split parts
        newFeatureLst = []
        if splitMultiParts and \
           newGeom.isMultipart() and \
           len( newGeom.asGeometryCollection() ) > 1:
            # get mapped attributes
            attribBaseMap = QGISAgriLayers.map_attribute_values( feature )
        
            # split feature for each geometry part 
            for part in QGISAgriGeometry.get_geometry_single_parts( newGeom ):
                # skip small parts
                if part.area() < suoliMinArea:
                    continue
                
                #
                part.convertToMultiType()
                 
                # add new feature
                attribMap = QGISAgriLayers.map_attribute_values( feature, attr_dict )  
                attribMap = { **attribBaseMap, **attribMap }
                newFeature = QgsVectorLayerUtils.createFeature( 
                    layer, 
                    geometry= QgsGeometry( part ),
                    attributes= attribMap )
                layer.addFeature( newFeature )
                newFeatureLst.append( newFeature )
                
            # remove original feature
            layer.deleteFeature( feature.id() )
            
        else:
            # apply new feature geometry
            newGeom.convertToMultiType()
            feature.setGeometry( newGeom )
            layer.changeGeometry( feature.id(), newGeom )
            newFeatureLst.append( feature )
            
        try:
            snapper = QGISAgriGeometrySnapper()
            for feature in newFeatureLst:
                snapper.run( layer, feature, 0.005 )
            
        except Exception as e:
            res = False
            errMsg += str(e)
            
        # add topological points
        if addTopologicalPoints:
            layUtils = QgsVectorLayerEditUtils( layer )
            for feature in newFeatureLst:
                layUtils.addTopologicalPoints( feature.geometry() )
            
        return res, errMsg, newFeatureLst
    
    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod        
    def repair_feature(layer, 
                       feature, 
                       attr_dict=None, 
                       splitMultiParts=False,
                       autoSnap=False,
                       suoliMinArea=agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO,
                       suoliSnapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE,
                       suoliSnapLayerUris=None,
                       addTopologicalPoints=False):
        
        res, errMsg, newFeatureLst = QGISAgriLayers.repair_feature_single(
                layer, 
                feature, 
                attr_dict=attr_dict, 
                splitMultiParts=splitMultiParts,
                autoSnap=autoSnap,
                suoliMinArea=suoliMinArea,
                suoliSnapTolerance=suoliSnapTolerance,
                suoliSnapLayerUris=suoliSnapLayerUris,
                addTopologicalPoints=addTopologicalPoints
        )
        for feat in newFeatureLst:
            res, errMsg, _ = QGISAgriLayers.repair_feature_single(
                layer, 
                feat, 
                attr_dict=attr_dict, 
                splitMultiParts=splitMultiParts,
                autoSnap=autoSnap,
                suoliMinArea=suoliMinArea,
                suoliSnapTolerance=suoliSnapTolerance,
                suoliSnapLayerUris=suoliSnapLayerUris,
                addTopologicalPoints=addTopologicalPoints
            )
            
        return True, ''
    
    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod
    def repair_feature_by_geom(layer, 
                               feature, 
                               attr_dict=None, 
                               splitMultiParts=False,
                               autoSnap=False,
                               suoliMinArea=agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO,
                               suoliSnapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE,
                               suoliSnapLayerUris=None,
                               addTopologicalPoints=False):
        # init
        attr_dict = attr_dict or {}
        inGeometry = QgsGeometry( feature.geometry() )
        delta = 10.0 / 100.0
        repaired = 0
        
        # get features that insersect the input feature
        fids = QGISAgriLayers.getFeaturesIdByGeom( layer, inGeometry )
    
        # loop features for intersection\difference
        for fid in fids:
            # get feature geometry
            feat = layer.getFeature( fid )
            featGeom = QgsGeometry( feat.geometry() )
            # check if there are intersections
            if not inGeometry.intersects( featGeom ):
                continue
            # get difference geometries
            intersGeom = featGeom.intersection( inGeometry )
            # check if valid
            if intersGeom.isEmpty():
                continue
            if intersGeom.isNull():
                continue
                
            # check area
            min_area = featGeom.area() * delta
            if intersGeom.area() < min_area:
                continue
                
            # repair feature
            QGISAgriLayers.repair_feature( 
                layer, 
                feat, 
                attr_dict=attr_dict, 
                splitMultiParts=splitMultiParts,
                autoSnap=autoSnap,
                suoliMinArea=suoliMinArea,
                suoliSnapTolerance=suoliSnapTolerance,
                suoliSnapLayerUris=suoliSnapLayerUris,
                addTopologicalPoints=addTopologicalPoints )
                    
            # incr
            repaired += 1
                    
        return repaired > 0
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def clone_features(layer, features, copyAttributesList, defaultAttributes=None):
        # init
        defaultAttributes = defaultAttributes or {}
        copyAttributesDict = {}
        defaultValues = {}
        lstFilterSrcAttribs = []
        newFeatures = []
        
        # prepare attributes
        for fld_def in copyAttributesList:
            field_name = fld_def.get( 'name', None )
            if not field_name:
                continue
            # popolate attribute dictionary
            copyAttributesDict[field_name] = fld_def
            # populate list of source attribute to copy
            lstFilterSrcAttribs.append( field_name )
            # get default values
            if 'default' in fld_def:
                destAttName = fld_def.get( 'destname', field_name )
                val = fld_def.get( 'default', '' )
                defaultValues[destAttName] = val
                
        defaultAttributes = {**defaultValues, **defaultAttributes}
        
        #create features to layer
        for srcFeat in features:
            # clone geometry
            geom = srcFeat.geometry()
            newFeat = QgsFeature( layer.fields() )
            newFeat.setGeometry( geom )
            
            # clone attributes
            srcAttribs = QGISAgriLayers.get_attribute_values( srcFeat, lstFilterSrcAttribs )
            attribs = {}
            for srcAttName,val in srcAttribs.items():
                attDef = copyAttributesDict.get( srcAttName, {} )
                destAttName = attDef.get( 'destname', srcAttName )
                if destAttName:
                    attribs[destAttName] = val 
                
            attribs = {**defaultAttributes, **attribs}
            for k,v in attribs.items(): 
                newFeat.setAttribute( k, v )
             
            # add new feature to layer  
            layer.addFeature( newFeat )
            newFeatures.append( newFeat )
            
        # return new features
        return newFeatures
                
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def change_attribute_values(layer, 
                                feat_lst, 
                                attr_dic, 
                                add_fields_dic=None, 
                                unvalorized_attr_dic=None):
        # init 
        res = False
        
        # add new fields
        fields = layer.fields()
        if isinstance(add_fields_dic, dict):
            nadd = 0
            provider = layer.dataProvider()
            for fld_name, field in add_fields_dic.items():
                idx = provider.fieldNameIndex(fld_name)
                if (idx is None or idx == -1):
                    nadd += 0
                    provider.addAttributes( field )
            if nadd > 0:
                res = True
                layer.updateFields()
    
        # loop all feature
        for feat in feat_lst:
            fields = feat.fields()
            # loop dictionaty of attributes
            for attr_name, attr_val in attr_dic.items():
                # format attribute value setting
                if not isinstance( attr_val, dict ):
                    attr_val = { 'value': attr_val, 'skipValorized': False }
                
                # get attribute index
                idx = fields.indexFromName( attr_name )
                if idx == -1:
                    continue
                
                # check if attribute valorized 
                curVal = feat.attribute( idx )
                if curVal != NULL and attr_val.get( 'skipValorized', False ):
                    continue
                
                # assign attribute to feature if changed
                newVal = attr_val.get( 'value' )
                if curVal != newVal:
                    #newVal = NULL if newVal is None else newVal
                    res = True
                    feat.setAttribute( idx, newVal )
                    layer.changeAttributeValue( feat.id(), idx, newVal, oldValue=curVal )
                        
        # return if were changes
        return res
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def map_attribute_values(feature, attr_dict=None):
        res = {}
        # loop feature fields  
        for k, field in enumerate( feature.fields() ):
            if field.constraints().constraints() & QgsFieldConstraints.ConstraintUnique:
                continue
            
            elif not attr_dict:
                res[k] = feature.attribute( k )
                
            elif field.name() in attr_dict:
                res[k] = attr_dict.get( field.name() )
     
        return res    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_attribute_values(feature, attr_list=None):
        attr_dic = {}
        fields = feature.fields()
        
        if attr_list is None:
            for fld in fields:
                attr = fld.name()
                attr_dic[attr] = feature[attr]
        else:
            for attr in attr_list:
                attr = str(attr)
                index = fields.indexFromName( attr )
                if index != -1: 
                    attr_dic[attr] = feature.attribute( index )
                
        return attr_dic
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_attribute_values_ext(feature, attr_list=None):
        attr_dic = {}
        fields = feature.fields()
        
        if attr_list is None:
            for fld in fields:
                attr = fld.name()
                attr_dic[attr] = feature[attr]
        else:
            for attr in attr_list:
                if not isinstance( attr, dict ):
                    attr = { 'name': str(attr), 'from': str(attr) }
                    
                attr_name = attr.get( 'name', '' )
                fld_name = attr.get( 'from', attr_name )
                index = fields.indexFromName( fld_name )
                if index != -1: 
                    attr_dic[attr_name] = feature.attribute( index )
                
        return attr_dic
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def snapGeometry(geom, 
                     otherGeoms, 
                     snapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE, 
                     mode=QgsGeometrySnapper.PreferClosest):
        
        # init
        inGeom = QgsGeometry( geom )
        
        # get snapped geometry
        inGeom = QgsGeometrySnapper.snapGeometry( inGeom, 
                                                  snapTolerance, 
                                                  otherGeoms, 
                                                  mode )
            
        # get snapped geometry
        return inGeom.makeValid()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def snapFeature(vlay_list, 
                    inFeature, 
                    snapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE, 
                    mode=QgsGeometrySnapper.PreferClosest):
        
        # init
        vlay_list = vlay_list or []
        inGeom = QgsGeometry( inFeature.geometry() )
        
        
        # make valid geometry
        validGeom = inGeom
        if not validGeom.isGeosValid():
            validGeom = validGeom.makeValid()
            
        return validGeom
    
#         # get list of geometries
#         for layer in vlay_list:
#     
#             # get features that insersect the input feature
#             refGeometries = []
#             for fid in QGISAgriLayers.getFeaturesIdByGeom( layer, validGeom, searchTolerance=snapTolerance ):
#                 feat = layer.getFeature( fid )
#                 if feat == inFeature:
#                     continue
#                 
#                 # collect valid geometry
#                 geom = QgsGeometry( feat.geometry() )
#                 geom = geom.makeValid()
#                 refGeometries.append( geom )
#                 
#             # get snapped geometry
#             for g in refGeometries:
#                 snapGeom = QgsGeometrySnapper.snapGeometry( validGeom, 
#                                                             snapTolerance, 
#                                                             [g], 
#                                                             mode )
#                 if snapGeom.length() > snapTolerance:
#                     validGeom = snapGeom
#                 
#             """
#             validGeom = QgsGeometrySnapper.snapGeometry( validGeom, 
#                                                          snapTolerance, 
#                                                          refGeometries, 
#                                                          mode )
#             """
#         # get snapped geometry
#         return validGeom.makeValid()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def getFeaturesIdByGeom(vlayer, 
                            geomSelector, 
                            expression=None, 
                            areaTolerance=agriConfig.TOLERANCES.AREA_TOLERANCE, 
                            searchTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE, 
                            skipInvaliGeom=False,
                            raiseExceptInvaliGeom=False,
                            tryMakeValid=False):
        """
        Function get layer features by a geometry.
        Do not evaluate if layer is hidden.
        """
        
        # init
        areaTolerance = areaTolerance or agriConfig.TOLERANCES.AREA_TOLERANCE
        searchTolerance = searchTolerance or agriConfig.TOLERANCES.SNAP_TOLERANCE
        if not geomSelector:
            return []
        
        if vlayer is None or not vlayer.isValid() or vlayer.type() != QgsMapLayer.VectorLayer:
            return []
        
        if not geomSelector.isGeosValid():
            # repair invalid geometry
            geomSelector = geomSelector.makeValid()
        
        # create spatial index
        index = QgsSpatialIndex( vlayer.getFeatures( expression ) ) \
                    if expression else QgsSpatialIndex( vlayer.getFeatures() )
        
        # Find all features that intersect the bounding box of the geometry selector
        bbox = geomSelector.boundingBox()
        bbox.grow( 2*searchTolerance )
        intersecting_ids = index.intersects( bbox )
        
        # loop all selected features
        res = []
        for fid in intersecting_ids:
            # check if feature with valid geometry
            feat = vlayer.getFeature( fid )
            geom = feat.geometry()
            if not geom:
                continue
            
            # check if valid geom
            if not geom.isGeosValid():
                if raiseExceptInvaliGeom:
                    # raise exceprion
                    raise QGISAgriException( 
                        tr( "Presente feature non valida.\n\n"
                            "Correggere le geometrie errate nell'area di applicazione.\n" 
                            "Utilizzare il comando 'Ripara suolo'." ) )
                
                elif tryMakeValid:
                    geom = geom.makeValid()
                
            # check if feature geometry intersects the selection rectangle
            if not geomSelector.intersects( geom ) and \
               not geomSelector.contains( geom ):
                continue
            
            # check tollerance and validity
            geomInt = geomSelector.intersection( geom )
            if (skipInvaliGeom and not geomInt.isGeosValid()) or \
                geomInt.isNull() or \
                geomInt.isEmpty() or \
                geom.area() < areaTolerance: # VERIFY CONDITION
                continue
            
            # collect feature
            res.append( fid )
                
        return res
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def cut_not_overlapping_feature(inFeature, 
                                   overlapLayers, 
                                   expression=None, 
                                   areaTolerance=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO):
        # init
        cuttedGeom = QgsGeometry( inFeature.geometry() )
      
        # loop overlap layers
        for overLayer in overlapLayers:
            # get features that overlap the input feature
            outFeats_ids = QGISAgriLayers.getFeaturesIdByGeom( 
                overLayer, cuttedGeom, expression=expression, tryMakeValid=True )
            # loop features for intersection\difference
            for fid in outFeats_ids:
                # get feature geometry
                feat = overLayer.getFeature( fid )
                featGeom = QgsGeometry( feat.geometry() )
                
                if not featGeom.intersects( cuttedGeom ):
                    continue
                
                # create difference feature
                cuttedGeom = QgsGeometry( cuttedGeom.difference( featGeom ) )
                #if not diffGeom.isEmpty():
                #    cuttedGeom = diffGeom
        
        # check if valid cutted geometry
        if cuttedGeom.isNull() or \
           cuttedGeom.isEmpty() or \
           cuttedGeom.area() < agriConfig.TOLERANCES.AREA_TOLERANCE:
            return True
                    
        # cut not overlap geometry
        inGeom = QgsGeometry( inFeature.geometry() )
        overGeom = inGeom.difference( cuttedGeom )
      
        # check if valid result geometry
        if overGeom.isNull() or \
           overGeom.isEmpty() or \
           overGeom.area() < areaTolerance:
            return False
               
        # re assign new cutted geometry
        inFeature.setGeometry( overGeom )
        
        return True
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def cut_interserct_feature(inFeature, cutLayerLst):
        # init
        inGeometry = QgsGeometry( inFeature.geometry() )
        
        # loop cutting layers
        for layer in cutLayerLst:
            # get features that insersect the input feature
            outFeats_ids = QGISAgriLayers.getFeaturesIdByGeom( layer, inGeometry )
            # loop features for intersection\difference
            for fid in outFeats_ids:
                # get feature geometry
                feat = layer.getFeature( fid )
                featGeom = QgsGeometry( feat.geometry() )
                
                if not featGeom.intersects( inGeometry ):
                    continue
                
                # create difference feature
                diffGeom = QgsGeometry( inGeometry.difference( featGeom ) )
                if not diffGeom.isEmpty():
                    inGeometry = diffGeom
                    
        # re assign new cutted geometry
        inFeature.setGeometry( inGeometry )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_interserct_feature(inFeature, 
                               layer, 
                               getDiffGeom=True, 
                               getIntersGeom=True, 
                               getMaxIntersGeom=False, 
                               layerFilterExpr=None,
                               areaTolerance=agriConfig.TOLERANCES.AREA_TOLERANCE,
                               suoliSnapLayers=None,
                               snapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE):
        """
        Find difference geometries of a layer 
        """
        
        # init
        interMaxArea = -1.0
        featMaxArea = None
        overlapFeatIdList = []
        delFeatIdList = []
        diffFeatList = []
        intersFeatList = []
        ##inGeometry = QgsGeometry( inFeature.geometry() )
        
        # get output fields
        ndx = 0
        outAttrIdLst = []
        outFields = layer.fields()
        for field in outFields:
            if field.constraints().constraints() & QgsFieldConstraints.ConstraintUnique:
                pass
            else:
                outAttrIdLst.append(ndx)
            ndx += 1
        

        inGeometry =  QGISAgriLayers.snapFeature( suoliSnapLayers, 
                                                  inFeature, 
                                                  snapTolerance=snapTolerance )
        
        # get features that insersect the input feature
        outFeats_ids = QGISAgriLayers.getFeaturesIdByGeom( layer, 
                                                           inGeometry, 
                                                           expression=layerFilterExpr,
                                                           raiseExceptInvaliGeom=True )
        
        
        
        # loop features for intersection\difference
        for fid in outFeats_ids:
            # get feature geometry
            feat = layer.getFeature( fid )
            featGeom = QgsGeometry( feat.geometry() )
            
            featGeom = QGISAgriLayers.snapFeature( suoliSnapLayers, 
                                                   feat, 
                                                   snapTolerance=snapTolerance )
        
            
            # check if vadil geometry
            #if not featGeom.isGeosValid():
            #    outLayer.selectByIds( [fid], QgsVectorLayer.SetSelection )
            #    msg = msgTag + self.tr( "Geometria invalida" )
            #    raise QGISAgriException( msg )
            
            # check if there are intersections
            if not featGeom.intersects( inGeometry ):
                continue
        
            
            # get difference geometries
            if getDiffGeom:
                # create difference feature
                diffGeom = QgsGeometry( featGeom.difference( inGeometry ) )
                if not diffGeom.isEmpty():
                    #if False and not diffGeom.isGeosValid():
                    #    msg = msgTag + self.tr( "Create delle geometrie invalide" )
                    #    raise QGISAgriException( msg )
                    if not(diffGeom.area() < agriConfig.TOLERANCES.AREA_TOLERANCE_SUOLO):
                        outFeat = QgsFeature()
                        outFeat.setGeometry( diffGeom )
                        outFeat.setFields( outFields )
                        for ndx in outAttrIdLst: 
                            outFeat.setAttribute( ndx, feat.attribute(ndx) ) 
                        diffFeatList.append( outFeat )
                    else:
                        overlapFeatIdList.append( feat.id() )
                        
                    delFeatIdList.append( feat.id() )
                    
            # get difference geometries
            if getIntersGeom or getMaxIntersGeom:
                # create intersection feature
                interGeom = QgsGeometry( featGeom.intersection( inGeometry ) )
                
                # correct intersection
                if interGeom.wkbType() == QgsWkbTypes.Unknown or \
                   QgsWkbTypes.flatType( interGeom.wkbType() ) == QgsWkbTypes.GeometryCollection:
                    interGeom = QgsGeometry()
                    comGeom = featGeom.combine( inGeometry )
                    if comGeom is not None:
                        symGeom = featGeom.symDifference( inGeometry )
                        interGeom = QgsGeometry( comGeom.difference( symGeom ) )
                 
                # check if valid intersection geometry        
                if not interGeom.isEmpty():
                    interGeomArea = 0.0
                    
                    if getMaxIntersGeom:
                        # get feature with max intersecting surface
                        interGeomArea = interGeom.area()
                        if interGeomArea > interMaxArea:
                            interMaxArea = interGeomArea
                            featMaxArea = feat
                    
                     
                    if interGeom.area() < areaTolerance:
                        continue
                    
                    deltaArea = featGeom.area() - interGeomArea
                    if deltaArea < agriConfig.TOLERANCES.AREA_TOLERANCE:
                        delFeatIdList.append( feat.id() )
                    
                    overlapFeatIdList.append( feat.id() )    
                    """
                    if not getMaxIntersGeom or deltaArea < 0.000001:
                        # create new intersecting feature
                        outFeat = QgsFeature()
                        outFeat.setGeometry( interGeom )
                        outFeat.setFields( outFields )
                        for ndx in outAttrIdLst: 
                            outFeat.setAttribute( ndx, feat.attribute(ndx) ) 
                        intersFeatList.append( outFeat )
                        delFeatIdList.append( feat.id() )
                    """
                    
        # create new max intersecting surface feature
        if getMaxIntersGeom and featMaxArea is not None:
            outFeat = QgsFeature()
            outFeat.setGeometry( QgsGeometry( inGeometry ) )
            outFeat.setFields( outFields )
            for ndx in outAttrIdLst: 
                outFeat.setAttribute( ndx, featMaxArea.attribute(ndx) ) 
            intersFeatList.append( outFeat )
            delFeatIdList.append( featMaxArea.id() )
            
        
        # return
        return (
            intersFeatList,
            diffFeatList,
            delFeatIdList,
            overlapFeatIdList,
            featMaxArea
        )
        