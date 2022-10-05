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
from qgis.core import (QgsGeometry, QgsPoint, QgsPointXY)
from qgis.analysis import QgsGeometrySnapper

# 
#-----------------------------------------------------------
class QGISAgriGeometry:
    """ Utiliy class for Agri layer manipulation. """
    
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
            points.append(QgsPointXY(ver))
            ver=geom.vertexAt(n)
            
        return points
            
    # --------------------------------------
    # 
    # --------------------------------------         
    @staticmethod
    def dissolve_points(geom):
        """
        Dissolves a generic geometry as multipoint geometry
        """
        return QgsGeometry.fromMultiPointXY(QGISAgriGeometry.extract_geometry_vertices(geom))
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_geometry_single_parts(geom):
        res = []
        # split feature for each geometry part 
        for part in geom.asGeometryCollection():
            # check in single part geometry
            if len(part.asGeometryCollection()) > 1:
                res = res + QGISAgriGeometry.get_geometry_single_parts( part )
            else:
                res.append(part)
        return res
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_geometries_from_rings(geom):
        res = []
        multi = []
        if not geom.isMultipart():
            multi.append( geom.asPolygon() )
        else:
            multi = geom.asMultiPolygon()
            
        for polyg in multi:
            part = []
            for ring in polyg:
                part.append( QgsGeometry.fromPolygonXY([ ring ]) )
            res.append( part )            
        return res
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def snapGeometry(geom, snapTolerance, refGeometries, mode = QgsGeometrySnapper.PreferNodes):
        # snap input geometry to references geometries
        snappedGeom = QgsGeometrySnapper.snapGeometry( geom, 
                                                       snapTolerance, 
                                                       refGeometries, 
                                                       mode )
        return snappedGeom    
            
            
            
            
