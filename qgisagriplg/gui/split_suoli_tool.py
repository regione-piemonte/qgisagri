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

# imports

from qgis.core import ( QgsProject,
                        QgsGeometry,
                        QgsVectorLayerUtils, 
                        QgsVectorLayerEditUtils )

from qgis_agri import agriConfig
from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.gui.edit_suoli_tool import SuoliEditTool

# 
#-----------------------------------------------------------
class SplitSuoliTool(SuoliEditTool):
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, 
                 iface, 
                 layer,
                 suoliRefLayers=None,
                 copyAttribs=None,
                 suoliMinArea=agriConfig.TOLERANCES.AREA_MIN_VALID_SUOLO, 
                 snapTolerance=agriConfig.TOLERANCES.SNAP_TOLERANCE, 
                 suoliSnapLayers=None):
        
        """ Constructor """
        super().__init__( iface, layer, suoliRefLayers, copyAttribs, suoliMinArea, snapTolerance, suoliSnapLayers )
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def doOperation(self):
        # init
        layer = self.layer
        if not self.capturedPoints:
            return
        
        #
        suoliSnapLayers = None#QGISAgriLayers.get_vectorlayer( self.suoliSnapLayers )
        
        layer.beginEditCommand( 'SplitSuoliTool' )
        try:
            # start edit command
            layUtils = QgsVectorLayerEditUtils( layer )
            proj = QgsProject.instance()
            
            # loop all selected features
            for fid in self.selectedFeatures:
                # get selected features
                feature = layer.getFeature( fid )
                geometry = feature.geometry()
                if not geometry.isGeosValid():
                    continue
                
                # get geometry and try to repair
                ##geometry = self.snapFeature( feature, suoliSnapLayers )
                ##if not geometry.isGeosValid():
                ##    continue
                
                # split geometry on cutting points
                result, newGeometries, topoPoints = geometry.splitGeometry( self.capturedPoints, proj.topologicalEditing() )
                
                # check if there're splitting geoms
                if result == QgsGeometry.Success and newGeometries:
                    # create also feature for first splitted part!!
                    # All slitted parts must be a new feature
                    newGeometries.append( geometry )
                    
                    # define new features attributes
                    attribBaseMap = QGISAgriLayers.map_attribute_values( feature )
                    attribSetMap = QGISAgriLayers.map_attribute_values( feature, self.copyAttribs ) 
                    attribSetMap = { **attribBaseMap, **attribSetMap }
                    
                    # create remaining splitted features
                    for newGeom in newGeometries:
                        # check geometry area
                        if newGeom.area() < agriConfig.TOLERANCES.AREA_TOLERANCE:
                            continue
                        # add new feature
                        layer.addFeature( QgsVectorLayerUtils
                            .createFeature( layer, geometry=newGeom, attributes=attribSetMap ) )
                    
                    # remove original features
                    layer.deleteFeature( fid )
                        
                    # topological editing
                    for pt in topoPoints:
                        layUtils.addTopologicalPoints( pt )
                        
            # end edit command
            layer.endEditCommand()
            
        except Exception as e:
            layer.destroyEditCommand()
            raise e
