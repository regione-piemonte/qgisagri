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
from qgis.core import QgsMapLayer

# 
#-----------------------------------------------------------
class LayerVirtualizer:
    def __init__(self, startId=0):
        """Constructor"""
        self.__currId = startId
        self.__lay_dict = {}
        
    def getVirtualId(self, layer: QgsMapLayer) -> int:
        """ Return an id per layer virtualized """
        if not layer:
            return -1
        layerId = layer.id()
        if layerId not in self.__lay_dict:
            self.__lay_dict[layerId] = self.__currId
            self.__currId += 1
        return self.__lay_dict[layerId]
    