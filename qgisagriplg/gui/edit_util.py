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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from qgis.gui import QgsMapTool

# pylint: disable=import-error
from qgis_agri.log.logger import QgisLogger as logger

# 
#-----------------------------------------------------------
class PointTool(QgsMapTool):

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def activate(self):
        self.canvas.setCursor(self.cursor)   

    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasPressEvent(self, event):
        pass

    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        logger.log_info(u"Inserito --- punto: {0},{1}".format(point.x(), point.y()))
        #deactivate the select tool
        self.canvas.unsetMapTool(self)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deactivate(self):
        QgsMapTool.deactivate(self)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isZoomTool(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isTransient(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isEditTool(self):
        return True