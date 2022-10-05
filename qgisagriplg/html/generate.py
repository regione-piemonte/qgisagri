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
from jinja2 import Environment, FileSystemLoader
import os
 
from PyQt5.QtCore import QByteArray, QBuffer 
from PyQt5.QtGui import QIcon, QPixmap, QImage 
 
# 
#-----------------------------------------------------------
class htmlUtil:

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def imgToBase64(img_path):
        pixmap = QPixmap(img_path)
        image = QImage( pixmap.toImage() )
        #icon = QIcon( img_path )
        #image = QImage( icon.pixmap(20,20).toImage() )
        data = QByteArray()
        buf = QBuffer( data )
        image.save( buf, 'png' )
        return "data:image/png;base64,{}".format( data.toBase64().data().decode('utf-8') )

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def generateTemplate(template_file): 
        def filter_supress_none(val):
            if not val is None:
                return val
            else:
                return ''
        
        root = os.path.dirname( os.path.abspath(__file__) )
        templates_dir = os.path.join(root, 'templates')
        env = Environment( loader = FileSystemLoader(templates_dir) )
        env.filters['sn'] = filter_supress_none
        template = env.get_template(template_file)
        return template
