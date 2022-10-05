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
from PyQt5.QtGui import QCursor

from qgis.core import ( QgsApplication,
                        QgsGeometry,
                        QgsVectorLayerUtils )

from qgis_agri import agriConfig
from qgis_agri.gui.layer_util import QGISAgriLayers
from qgis_agri.gui.edit_suoli_tool import SuoliEditTool

# 
#-----------------------------------------------------------
class FillSuoliTool(SuoliEditTool):

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
                 suoliSnapLayers=None,
                 attribCallbackFn=None):
        
        """ Constructor """
        super().__init__( iface, layer, suoliRefLayers, copyAttribs, suoliMinArea, snapTolerance, suoliSnapLayers )
        self.autoClosure = True
        self.canAutoSelect = False
        self.canRedrawAreas = False
        self.attribCallbackFn = attribCallbackFn
        self.customCursor = QCursor( QgsApplication.getThemeCursor( QgsApplication.CapturePoint ) )

    # --------------------------------------
    # 
    # --------------------------------------
    def doOperation(self):
        """ Create a filling Suolo feature """
        
        # check number of captured points
        numPoints = len(self.capturedPoints)
        if numPoints < 4:
            return
        
        # create geometry from captured points
        inGeometry = QgsGeometry.fromPolygonXY( [self.capturedPoints] ) 
        
        # list all cutting layers
        cutLayers = [ self.layer ]
        cutLayers.extend(x for x in self.suoliRefLayers if x not in cutLayers)
        
        # loop over all cutting layers
        nFeatFound = 0
        selFeats_ids = []
        for layer in cutLayers: 
            # get features that insersect the input feature
            outFeats_ids = QGISAgriLayers.getFeaturesIdByGeom( layer, 
                                                               inGeometry, 
                                                               expression=None )
            
            # loop features for intersection\difference
            for fid in outFeats_ids:
                # get feature geometry
                feat = layer.getFeature( fid )
                featGeom = QgsGeometry( feat.geometry() )
                
                # check if there are intersections
                if not inGeometry.intersects( featGeom ):
                    continue
                
                # create difference feature
                inGeometry = inGeometry.difference( featGeom )
                if inGeometry.isEmpty():
                    return 
                
                # check area
                if inGeometry.area() < self.suoliMinArea:
                    return 
                
                # collect used feature
                nFeatFound += 1
                if layer == self.layer:
                    selFeats_ids.append( fid )
            
        # check if feature found
        ###if not selFeats_ids:
        ###    pass
        
        # start edit command   
        self.layer.beginEditCommand( 'FillSuoliTool' )
        try:
            # add new feature
            newFeat = QgsVectorLayerUtils.createFeature( self.layer, geometry=inGeometry )
            self.layer.addFeature( newFeat )
            
            if self.copyAttribs:
                QGISAgriLayers.change_attribute_values( self.layer, [newFeat], self.copyAttribs )
                
            
            while True:
                # show attribute form
                res = self.iface.openFeatureForm( self.layer, newFeat, showModal=True )
                if not res:
                    # rollback for user cancel
                    self.layer.destroyEditCommand()
                    return
                elif self.attribCallbackFn is None:
                    # break loop if no attribute check callback
                    break
                elif self.attribCallbackFn( self.layer, newFeat ):
                    # break loop if successful attribute check callback
                    break
            
            # repair geometry
            QGISAgriLayers.repair_feature(self.layer, 
                                           newFeat, 
                                           attr_dict=None, 
                                           splitMultiParts=True,
                                           autoSnap=False,
                                           suoliMinArea=self.suoliMinArea,
                                           suoliSnapTolerance=self.snapTolerance,
                                           suoliSnapLayerUris=None,
                                           addTopologicalPoints=True)
            
            
            # end edit command
            self.layer.endEditCommand()
            
        except Exception as e:
            self.layer.destroyEditCommand()
            raise e
        