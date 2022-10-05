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

from qgis.core import QgsVectorLayer, QgsDataSourceUri

#-----------------------------------------------------------
class signalUtil:

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def formatSignalName(obj, signal):
        """
        Format signal name
        
        :param obj: object
        :type obj: QObject
        
        :param signalName: name of signal to connect.
        :type signalName: pyqtSignal
        """
        if isinstance( obj, QgsVectorLayer ):
            uri = QgsDataSourceUri( obj.dataProvider().dataSourceUri() )
            return '__sng_{0}__{1}'.format( str(signal.signal), uri.table() )
        
        return '__sng_{}'.format( str(signal.signal) )

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def connectUniqueSignal(obj, signal, slot):
        """
        Utility function to substitute dictionary values defined as variables 
        using the format: key: {var_name}
        
        :param obj: object
        :type obj: QObject
        
        :param signalName: name of signal to connect.
        :type signalName: pyqtSignal
        
        :param signal: signal to connect.
        :type signal: pyqtSignal
    
        :param slot: function slot.
        :type slot: function
        """
        try:
            attr = signalUtil.formatSignalName( obj, signal )
            if not hasattr( obj, attr ):
                setattr( obj, attr, slot )
                signal.connect( getattr( obj, attr ), Qt.UniqueConnection )
        except TypeError:
            pass
       
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def disconnectUniqueSignal(obj, signal):
        """
        Utility function to substitute dictionary values defined as variables 
        using the format: key: {var_name}
        
        :param obj: object
        :type obj: QObject
        
        :param signalName: name of signal to connect.
        :type signalName: pyqtSignal
        
        :param signal: signal to disconnect.
        :type signal: pyqtSignal
        """
        try:
            attr = signalUtil.formatSignalName( obj, signal )
            if hasattr( obj, attr ):
                signal.disconnect( getattr( obj, attr ) )
                delattr( obj, attr ) 
        except:
            pass

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def connectOnce(signal, slot):
        """Connect a signal to a slot only once"""
        def once_slot(*args, **kw):
            signal.disconnect( once_slot )
            slot(*args, **kw)
        signal.connect( once_slot )
    
    