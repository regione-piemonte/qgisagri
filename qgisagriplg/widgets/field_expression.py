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
# PyQt5 modules
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QComboBox

# qgis modules
from qgis.PyQt.QtCore import pyqtSignal
from qgis.gui import QgsFieldExpressionWidget
from qgis.core import QgsExpression, QgsExpressionContext, QgsExpressionContextUtils

# 
#-----------------------------------------------------------
class QGISAgriFieldExpressionWidget(QgsFieldExpressionWidget):

    # --------------------------------------
    # signals 
    # --------------------------------------
    editingFinished = pyqtSignal()

    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, parent = None):
        # call parent constructor
        super().__init__( parent )
        # retrieve combo
        self._expr_combo = self.findChild( QComboBox )
        
    # --------------------------------------
    # 
    # --------------------------------------
    def clearButtonEnable(self, enable):
        if self._expr_combo:
            self._expr_combo.lineEdit().clearButtonEnabled( enable )
     
    # --------------------------------------
    # 
    # --------------------------------------   
    def eventFilter(self, watched, event):
        res = super().eventFilter( watched, event )
        
        #check if editing finished 
        if watched == self._expr_combo and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                # emit signal
                self.editingFinished.emit()

        return res
    
    # --------------------------------------
    # 
    # --------------------------------------
    def validate(self, validate: bool):
        # change combo edit text color
        if self._expr_combo is not None:
            self._expr_combo.lineEdit().setStyleSheet( 
                '' if validate else "QLineEdit {{ color: {}; }}".format( QColor( Qt.red ).name() ) ) 

    # --------------------------------------
    # 
    # --------------------------------------
    def isExpressionValid_ext(self, expressionStr):
        # check expression validitu
        context = QgsExpressionContext()
        context.appendScopes( QgsExpressionContextUtils.globalProjectLayerScopes(self.layer()) )
        expression = QgsExpression( expressionStr )
        expression.prepare( context )
        
        res = ( not expression.hasParserError() and 
                not expression.hasEvalError() )
        
        # change combo edit text color
        self.validate( res )
            
        return res
    