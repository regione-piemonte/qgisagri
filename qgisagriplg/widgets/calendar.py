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

# Import PyQt5 modules
##from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint, QSize, QRect
from PyQt5.QtWidgets import QCalendarWidget
from PyQt5.QtGui import QColor, QPen

# 
#-----------------------------------------------------------
class CalendarExt(QCalendarWidget):
    
    """
    A custom calendar to highlight a set of dates
    """
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self):
        super().__init__()
        self.selection_init = False
        self.dateList = []

        """
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setFontStrikeOut( True )
        self.highlight_format.setBackground(self.palette().brush(QPalette.Highlight))
        self.highlight_format.setForeground(self.palette().color(QPalette.HighlightedText))
        self.setDateTextFormat(QDate(-4713, -1, -1), self.highlight_format)
        """
        self.clicked.connect(self.date_is_clicked)
     
    # --------------------------------------
    # 
    # --------------------------------------
    def selectDates(self, qdatesList):
        self.dateList = qdatesList
        #this redraws the calendar with your updated date list
        self.updateCells() 
     
    # --------------------------------------
    # 
    # --------------------------------------   
    def setSelectedDate(self, date):  
        QCalendarWidget.setSelectedDate(self, date)
        self.selection_init = True
        
    # --------------------------------------
    # 
    # --------------------------------------
    def paintCell(self, painter, rect, adate):
        if adate in self.dateList:
            painter.save()
            painter.fillRect(rect, QColor("#ffffff"))
            painter.setPen(Qt.NoPen)
            if self.selection_init and adate == self.selectedDate():
                painter.setBrush(QColor("#0080ff"))
            else:
                painter.setBrush(QColor("#00ff00"))
            r = QRect(QPoint(), min(rect.width(), rect.height())*QSize(1, 1))
            r.moveCenter(rect.center())
            painter.drawEllipse(r)
            painter.setPen(QPen(QColor("black")))
            painter.drawText(rect, Qt.AlignCenter, str(adate.day()))
            painter.restore()
        else:
            QCalendarWidget.paintCell(self, painter, rect, adate)
            painter.save()
            col = QColor("#ffffff")
            col.setAlpha(200)
            painter.fillRect(rect, col)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#00ff00"))
            r = QRect(QPoint(), min(rect.width(), rect.height())*QSize(1, 1))
            painter.restore()
     
    # --------------------------------------
    # 
    # --------------------------------------
    def date_is_clicked(self, date):
        pass