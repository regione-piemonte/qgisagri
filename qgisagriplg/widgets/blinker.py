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
from threading import Timer
from PyQt5.QtCore import QObject
from qgis.PyQt.QtCore import pyqtSignal

# 
#-----------------------------------------------------------
class Blinker(QObject):
    
    blinking = pyqtSignal(bool)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, time=0.3):
        QObject.__init__(self)
        self.__time = time
        self.__statoAttuale = False
        self.__max_repeat = 15
        self.__num_repeat = 0
        self.__timer = self._createTimer()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _createTimer(self):
        return Timer(self.__time, self._onTimer)
     
    # --------------------------------------
    # 
    # -------------------------------------- 
    def start(self, max_repeat=5):
        self.__num_repeat = 0
        self.__max_repeat = max_repeat
        self.__timer.start()
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def cancel(self):
        self.__timer.cancel()
        self.setBoldStyle()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _onTimer(self):
        # check num of repeats
        self.__num_repeat = self.__num_repeat +1
        if (self.__num_repeat >= self.__max_repeat):
            self.blinking.emit( True )
            return
        
        self.__statoAttuale = not self.__statoAttuale
        self.blinking.emit( self.__statoAttuale )
            
        self.__timer = self._createTimer()
        self.__timer.start()
    