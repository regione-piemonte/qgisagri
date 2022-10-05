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

from PyQt5.QtCore import Qt, QCoreApplication, QPoint
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QLabel, QDialog
# 
#-----------------------------------------------------------
class Spinner(QDialog):
    """ 
    A Spinner Dialog
    """
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, parent=None):
        super(Spinner, self).__init__(parent)
        self.__parent = parent
        self.__closed = True
        #self.setModal(True)
        
        # set windows flags
        self.installEventFilter(self)
        self.setWindowFlags( Qt.X11BypassWindowManagerHint | 
                             Qt.FramelessWindowHint |
                             Qt.WindowStaysOnTopHint | 
                             Qt.Tool )
        #self.setWindowFlags(Qt.FramelessWindowHint )
        self.setAttribute( Qt.WA_TranslucentBackground )
        
        # add movie
        self._movie = QMovie(":/plugins/qgis_agri/images/spinner.gif", parent=self)
        processLabel = QLabel( parent=self )
        processLabel.setSizePolicy( QSizePolicy.Ignored, QSizePolicy.Ignored )
        processLabel.setScaledContents( True )
        processLabel.setMovie( self._movie )
        
        # add layout
        layout = QHBoxLayout( self )
        layout.setMargin( 0 )
        layout.setSpacing( 0 )
        layout.addWidget( processLabel )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onApplicationStateChanged(self, state):
        """Slot to main application state changed"""
        if state == Qt.ApplicationActive:
            self.setWindowFlag( Qt.WindowStaysOnTopHint )
            self.setVisible( True )
        else:
            self.setWindowFlag( Qt.WindowStaysOnTopHint, False )
            ##self.hide()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def closeEvent(self, evnt):
        # disconnect signal
        try:
            QCoreApplication.instance().applicationStateChanged.disconnect( self.onApplicationStateChanged )
        except TypeError as e:
            pass
        super().closeEvent(evnt)
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def show(self):
        """Show and run spinner"""
        
        # center in parent
        if self.__parent is not None:
            hostRect = self.__parent.geometry()
            x = (hostRect.width() - self.rect().width()) // 2
            y = (hostRect.height() - self.rect().height()) // 2
            self.move( self.__parent.mapToGlobal( QPoint( x, y ) ) )
        
        # call base class method
        super(Spinner, self).show()
        
        # connect signal
        QCoreApplication.instance().applicationStateChanged.connect( self.onApplicationStateChanged )
        
        
        # start movie
        self._movie.start()
