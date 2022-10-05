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

from qgis.core import QgsProcessingProvider

from .force_right_handle_rule import ForceRHR
from .sliver_polygons import SliverPolygons

# 
#-----------------------------------------------------------
class Provider(QgsProcessingProvider):
    # --------------------------------------
    # 
    # -------------------------------------- 
    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(ForceRHR())
        self.addAlgorithm(SliverPolygons())
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def id(self, *args, **kwargs):
        """The ID of your plugin, used for identifying the provider.

        This string should be a unique, short, character only string,
        eg "qgis" or "gdal". This string should not be localised.
        """
        return 'qgis_agri'
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def name(self, *args, **kwargs):
        """The human friendly name of your plugin in Processing.

        This string should be as short as possible (e.g. "Lastools", not
        "Lastools version 1.0.1 64-bit") and localised.
        """
        return 'QGisAgri'
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def icon(self):
        """Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)