# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISAgri
                                 A QGIS plugin
 QGIS Agri Plugin
 Created by Sandro Moretti: sandro.moretti@ngi.it
                              -------------------
        begin                : 2022-03-08
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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

from qgis.core import QgsProject, QgsMapLayer
from qgis.utils import iface

from qgis_agri import agriConfig, tr
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.gui.layer_util import QGISAgriLayers

#
#-----------------------------------------------------------
class QGISAgriLayerImporter:
    """Class to import layes form external sources"""
    
    def selectQgisProjectFile(self, directory=''):
        # show file dialog
        res = QFileDialog.getOpenFileName(
            iface.mainWindow(),
            tr("Seleziona un file di progetto QGIS") ,
            str(directory),
            "File QGZ (*.qgz);;FILE QGIS (*.qgs *.QGS)")
        
        # get file name
        filePath = ''
        if res:
            filePath = res[0]
        return filePath
    
    def getLayerTreeNodes(self, project, layerTree):
        node_lst = []
        node = layerTree.parent()
        node_root = project.layerTreeRoot()
        while node and node != node_root:
            node_lst.append( node.name() )
            node = node.parent()
        node_lst.reverse()
        return '/'.join( node_lst )
    
    def getTocLayerByName(self, project, layerTreeName):
        """Serch a layer by name in TOC"""
        for l in project.layerTreeRoot().findLayers():
            if l.name() == layerTreeName:
                return l
        return None

    def importFromQgisProject(self, prj_filename, read_only_layer=True):
        try:
            # init
            tocgroup = agriConfig.get_value( 'commands/importProjectLayers/tocgroup', '' )
            tocgroup = str(tocgroup).strip()
            
            project = QgsProject.instance()
            project_ext = QgsProject()
            
            #
            logger.log(
                logger.Level.Info, 
                f"{tr('Avviata importazione dei livelli dal progetto')}: {prj_filename}" )
            
            # override cursor 
            logger.setOverrideCursor(Qt.WaitCursor)

            # Load another project
            project_ext.clear()
            _ = project_ext.read( prj_filename )

            # clone layers
            layerTreeLst = [l for l in project_ext.layerTreeRoot().findLayers()]
            layerTreeLst.reverse()
            for layerTree in layerTreeLst:
                layer = layerTree.layer()
                try:
                    # check if layer already in TOC
                    cloned_layer = self.getTocLayerByName( project, layer.name() )
                    if cloned_layer is not None:
                        logger.log(
                            logger.Level.Warning, 
                            f"{tr('Layer già presente')}: {layer.name()}" )
                        continue
                        
                    # clone external project layer in current map
                    cloned_layer = layer.clone()
                    if cloned_layer.type() == QgsMapLayer.VectorLayer:
                        cloned_layer.setReadOnly( read_only_layer )
                        
                    # add cloned layer to map
                    project.addMapLayer( cloned_layer, False )
                    
                    # add cloned layer to TOC
                    node_path = self.getLayerTreeNodes( project_ext, layerTree )
                    if tocgroup:
                        node_path = f"{tocgroup}/{node_path}".rstrip('/')
                    _, grp_node = QGISAgriLayers.create_toc_group_path( node_path, project.layerTreeRoot() )
                    _ = grp_node.insertLayer( 0, cloned_layer )
                    
                    logger.log(
                        logger.Level.Info, 
                        f"{tr('Importato il Layer')}: {layer.name()}" )
                    
                except Exception as e:
                    logger.log(
                        logger.Level.Warning, 
                        f"{tr('Impossibile importare il layer')} '{layer.name()}': {str(e)}" )
            
            # return successfully
            project_ext.deleteLater()
            project_ext = None
            return True
        
        finally:
            # restore cursor
            logger.restoreOverrideCursor()
            
        return False
    
