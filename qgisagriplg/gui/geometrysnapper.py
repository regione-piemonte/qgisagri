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
from qgis.core import (QgsWkbTypes,
                       qgsDoubleNear,
                       QgsSpatialIndex, 
                       QgsFeatureRequest, 
                       QgsRectangle, 
                       QgsGeometry,
                       QgsPoint,
                       QgsPointXY,
                       QgsPolygon,
                       QgsLineString,
                       QgsGeometryUtils)
# 
#-----------------------------------------------------------
class QGISAgriGeometrySnapper:
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self):
        self._layer = None
        self._index = None
        
    # --------------------------------------
    # 
    # --------------------------------------
    def buildSnapIndex(self):
        # init 
        pntId = 0
        anchor_points = []
        self._index = QgsSpatialIndex()
        
        # loop all layer features
        request = QgsFeatureRequest()
        request.setNoAttributes()
        for feat in self._layer.getFeatures( request ):
            geom = feat.geometry()
            for part in geom.parts():
                for pt in part.vertices():
                    rect = QgsRectangle( pt.x(), pt.y(), pt.x(), pt.y() )
                    fids = self._index.intersects( rect )
                    if not fids:
                        # add to tree and to structure
                        self._index.addFeature( pntId, pt.boundingBox() )
                        anchor_points.append( [ pt.x(), pt.y(), feat.id(), -1 ] )
                        pntId += 1
        
        # retun anchor points        
        return anchor_points
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def assignAnchors(self, anchor_points: list, thresh: float, excl_fid: int):
        # init
        thresh2 = thresh * thresh
        
        for i, pt in enumerate(anchor_points):
            if pt[-1] >= 0:
                continue
            
            if pt[-2] == excl_fid:
                continue
                
            pt[-1] = -2 # make it anchor
            
            # Find points in threshold
            x, y = pt[0], pt[1]
            rect = QgsRectangle( x - thresh, y - thresh, x + thresh, y + thresh )
            
            for pid in self._index.intersects( rect ):
                if pid == i:
                    continue
                
                x2 = anchor_points[pid][0]
                y2 = anchor_points[pid][1]
                anchor = anchor_points[pid][-1]
            
                dx = x2 - x
                dy = y2 - y
                dist2 = dx * dx + dy * dy
                if dist2 > thresh2:
                    continue # outside threshold
                    
                if anchor == -1:
                    # doesn't have an anchor yet
                    anchor_points[pid][-1] = i
                    
                elif anchor >= 0:
                    # check distance to previously assigned anchor
                    dx2 = anchor_points[anchor][0] - x2
                    dy2 = anchor_points[anchor][1] - y2
                    dist2_a = dx2 * dx2 + dy2 * dy2
                    if dist2 < dist2_a:
                        anchor_points[pid][-1] = i # replace old anchor
    
    # --------------------------------------
    # 
    # --------------------------------------
    def snapLineString(self, linestring: QgsLineString, anchor_points: list, thresh: float) -> bool:
        # init
        newPoints = []
        anchors = [] # indexes of anchors for vertices
        minDistX, minDistY = 0.0, 0.0 # coordinates of the closest point on the segment line
        thresh2 = thresh * thresh
        changed = False
        
        # snap vertices
        for v in range(linestring.numPoints()):
            x = linestring.xAt( v )
            y = linestring.yAt( v )
            rect = QgsRectangle( x, y, x, y )
            
            # Find point ( should always find one point )
            fids = self._index.intersects( rect )
            if not fids:
                continue
            
            spoint = fids[0]
            anchor = anchor_points[spoint][-1]
            if anchor >= 0:
                # to be snapped
                linestring.setXAt( v, anchor_points[anchor][0] )
                linestring.setYAt( v, anchor_points[anchor][1] )
                anchors.append( anchor ) # point on new location
                changed = True
                
            else:
                anchors.append( spoint ) # old point
               
        # Snap all segments to anchors in threshold
        for v in range(linestring.numPoints()-1):
            x1 = linestring.xAt( v )
            x2 = linestring.xAt( v + 1 )
            y1 = linestring.yAt( v )
            y2 = linestring.yAt( v + 1 )
  
            newPoints.append( linestring.pointN( v ) )
            
            # Box
            xmin, xmax, ymin, ymax = x1, x2, y1, y2
            if xmin > xmax:
                xmin, xmax = xmax, xmin # swap
            if ymin > ymax:
                ymin, ymax = ymax, ymin # swap
                
            rect = QgsRectangle( xmin - thresh, ymin - thresh, xmax + thresh, ymax + thresh )
            
            # Find points
            fids = self._index.intersects( rect )
            newVerticesAlongSegment = []
            
            # Snap to anchor in threshold different from end points
            for fid in fids:
                spoint = fid
  
                if spoint == anchors[v] or spoint == anchors[v + 1]:
                    continue # end point
                if anchor_points[spoint][-1] >= 0:
                    continue # point is not anchor
                    
                # Check the distance
                dist2, minDistX, minDistY = QgsGeometryUtils.sqrDistToLine( anchor_points[spoint][0], anchor_points[spoint][1], x1, y1, x2, y2, 0.0 )
               
                # skip points that are behind segment's endpoints or extremely close to them
                dx1, dx2 = minDistX - x1, minDistX - x2
                dy1, dy2 = minDistY - y1, minDistY - y2
                isOnSegment = not qgsDoubleNear( dx1 * dx1 + dy1 * dy1, 0.0 ) and\
                              not qgsDoubleNear( dx2 * dx2 + dy2 * dy2, 0.0 )
                              
                if isOnSegment and dist2 <= thresh2:
                    # an anchor is in the threshold
                    pt = QgsPointXY( x1, y1 ).distance( minDistX, minDistY )
                    newVerticesAlongSegment.append( (pt, spoint) )
                    
            if newVerticesAlongSegment:
                # sort by distance along the segment
                newVerticesAlongSegment.sort( key=lambda pt: pt[0] )
                # insert new vertices
                for vSeg in newVerticesAlongSegment:
                    anchor = vSeg[-1]
                    newPoints.append( QgsPoint( anchor_points[anchor][0], anchor_points[anchor][1], 0 ) )
                
                changed = True
  
        # append end point
        newPoints.append( linestring.pointN( linestring.numPoints() - 1 ) )
        
        # replace linestring's points
        if changed:
            linestring.setPoints( newPoints )
        
        return changed
    
    # --------------------------------------
    # 
    # --------------------------------------
    def snapPolygonGeometry(self, polygon: QgsPolygon, anchor_points: list, thresh: float) -> bool:
        exteriorRing = polygon.exteriorRing()
        changed = self.snapLineString( exteriorRing, anchor_points, thresh )
        
        for i in range( polygon.numInteriorRings() ):
            # init
            interiorRing = polygon.interiorRing( i )
            if self.snapLineString( interiorRing, anchor_points, thresh ):
                changed = changed or True
                
        return changed
            
    # --------------------------------------
    # 
    # --------------------------------------
    def snapGeometry(self, geom: QgsGeometry, anchor_points: list, thresh: float) -> bool:
        # init
        changed = False
        
        # check geometry type
        if geom.type() == QgsWkbTypes.PolygonGeometry:
            
            if geom.isMultipart():
                for part in geom.parts():
                    if self.snapPolygonGeometry( part, anchor_points, thresh ):
                        changed = changed or True
                    
            else:
                if self.snapPolygonGeometry( geom.get(), anchor_points, thresh ):
                    changed = changed or True
                
        return changed
    
    # --------------------------------------
    # 
    # --------------------------------------
    def rectifyGeomHoles(self, geom):
        # init
        geom = QgsGeometry( geom )
        if not geom.isGeosValid():
            return geom
        if geom.type() != QgsWkbTypes.PolygonGeometry:
            return geom
        
        # collect parts(polygons)
        lst_polyg = []
        multi_polyg = []
        if geom.isMultipart():
            multi_polyg = geom.asMultiPolygon()
        else:
            multi_polyg.append( geom.asPolygon() )
        
        # rectify holes    
        for polyg in multi_polyg:
            polig_geom = QgsGeometry.fromPolygonXY( [ polyg[0] ] )
            for ring in polyg[1:]:
                polig_geom = polig_geom.difference( QgsGeometry.fromPolygonXY( [ ring ] ) )
                if polig_geom.convertGeometryCollectionToSubclass( QgsWkbTypes.PolygonGeometry ):
                    polig_geom = polig_geom.asGeometryCollection()[0]
            lst_polyg.append( polig_geom.asPolygon() )
        
        # create new geometry    
        new_geom = QgsGeometry.fromMultiPolygonXY( lst_polyg )   
        if not new_geom.isGeosValid():
            return geom
        
        # return new geometry if valid
        return new_geom if qgsDoubleNear( new_geom.area(), geom.area(), 0.000001 ) else geom
    
    # --------------------------------------
    # 
    # --------------------------------------        
    def run(self, layer, feature, thresh: float):
        # init
        self._layer = layer    
        # step 1: record all point locations in a spatial index + extra data structure to keep
        anchor_points = self.buildSnapIndex()
        # step 2: go through all registered points and if not yet marked mark it as anchor and
        # assign this anchor to all not yet marked points in threshold
        self.assignAnchors( anchor_points, thresh, feature.id() )
        # step 3: alignment of vertices and segments to the anchors
        # Go through all lines and:
        #   1) for all vertices: if not anchor snap it to its anchor
        #   2) for all segments: snap it to all anchors in threshold (except anchors of vertices of course)
        geom = QgsGeometry( feature.geometry() )
        if self.snapGeometry( geom, anchor_points, thresh ):
            geom = self.rectifyGeomHoles( geom )
        geom.convertToMultiType()
        feature.setGeometry( geom )
        layer.changeGeometry( feature.id(), geom, True )

