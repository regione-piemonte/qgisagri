# -*- coding: utf-8 -*-
"""Modulo per personalizzare lo stile di visualizzazione del pannello di controllo del plugin.

Descrizione
-----------

Implementazione della classe derivata da QProxyStyle per personalizzare lo stile 
di visualizzazione della toolbar del pannello di controllo del plugin. Permette di
cambiare le dimensioni dei bottoni della toolbar.

Librerie/Moduli
-----------------
    
Note
-----


TODO
----


Autore
-------

- Creato da Sandro Moretti il 23/09/2019.
- Modificato da Sandro Moretti il 28/10/2020.

Copyright (c) 2019 CSI Piemonte.

Membri
-------
"""
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QProxyStyle

# qgis modules import
from qgis.PyQt import QtWidgets

 
# Create a custom "QProxyStyle" to enlarge the QMenu icons
#-----------------------------------------------------------
class QGISAgriProxyStyle(QProxyStyle): 
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, parent, iconSize, *args):
        """Constructor""" 
        self.__iconSize = iconSize
        QProxyStyle.__init__(self, *args)
        self.setParent(parent)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):
        #if QStyle_PixelMetric == QStyle.PM_ToolBarIconSize:
        #    return 40
        #else:
        return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def drawControl(self, element, option, painter, widget=None):
        if element == QtWidgets.QStyle.CE_ToolButtonLabel:  
            icon = QIcon(option.icon)
            if icon.isNull():
                return
            
            if self.__iconSize:
                option.iconSize = self.__iconSize
                
            if widget:
                size = option.iconSize
                minSize = widget.property('iconMinSize')
                if minSize is None:
                    pass
                
                elif size.height() < minSize.height() or \
                     size.width() < minSize.width():
                    option.iconSize = minSize
                    widget.setFixedSize( minSize )
                    widget.setIconSize( minSize )     
            
        super(QGISAgriProxyStyle, self).drawControl(element, option, painter, widget)
       
