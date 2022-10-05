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

#from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QAbstractItemModel, QModelIndex
from PyQt5.QtCore import Qt as Qt5

# qgis modules import
from qgis.PyQt import QtGui

# 
#-----------------------------------------------------------
class TreeAgriItemNode:

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, in_data, icons=None, service=None): 
        self._data = in_data  
        if type(in_data) == tuple:  
            self._data = list(in_data)  
        if type(in_data) == str or not hasattr(in_data, '__getitem__'):  
            self._data = [in_data]  
  
        self._columncount = len(self._data)
        self._children = []  
        self._parent = None  
        self._row = 0
        self._icons = icons or []
        self._service = service
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def service(self):
        """ Returns service name linked to item """
        return self._service
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def data(self, in_column):  
        if in_column >= 0 and in_column < len(self._data):  
            return self._data[in_column]  
  
    # --------------------------------------
    # 
    # -------------------------------------- 
    def columnCount(self):  
        return self._columncount  
  
    # --------------------------------------
    # 
    # -------------------------------------- 
    def childCount(self):  
        return len(self._children)  
  
    # --------------------------------------
    # 
    # -------------------------------------- 
    def child(self, in_row):  
        if in_row >= 0 and in_row < self.childCount():  
            return self._children[in_row]  
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def parent(self):  
        return self._parent  
  
    # --------------------------------------
    # 
    # -------------------------------------- 
    def row(self):  
        return self._row  
  
  
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setParent(self, in_parent, row):  
        self._parent = in_parent  
        self._row = row
        in_parent.addChild( self )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def addChild(self, in_child):
        if in_child in self._children:
            return
        self._children.append(in_child)
        in_child.setParent( self, len(self._children) )
        self._columncount = max(in_child.columnCount(), self._columncount)
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def addChilds(self, in_childs):
        for in_child in in_childs:
            self.addChild(in_child)
        
    # --------------------------------------
    # 
    # --------------------------------------         
    def removeChilds(self):
        self._children = []
        self._columncount = 0
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def getIcon(self, in_column):
        if in_column >= 0 and in_column < len(self._icons):
            icon_path = self._icons[in_column]
            if isinstance(icon_path, str):
                return QtGui.QIcon(icon_path)
        return None
  
# 
#-----------------------------------------------------------  
class TreeAgriModel(QAbstractItemModel):

    # --------------------------------------
    # 
    # --------------------------------------  
    def __init__(self, in_nodes, header=None):  
        QAbstractItemModel.__init__(self) 
        self._header = header or []
        self._root = TreeAgriItemNode(None)
        for node in in_nodes:  
            self._root.addChild(node)
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def headerData(self, col, orientation, role):
        if col < len(self._header):
            if orientation == Qt5.Horizontal and role == Qt5.DisplayRole:
                return self._header[col]
        return None
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def rowCount(self, in_index):  
        if in_index.isValid():  
            return in_index.internalPointer().childCount()  
        return self._root.childCount()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def addChild(self, in_node, in_parent):  
        if not in_parent or not in_parent.isValid():  
            parent = self._root  
        else:  
            parent = in_parent.internalPointer()  
        parent.addChild(in_node)
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def index(self, in_row, in_column, in_parent=None):  
        if not in_parent or not in_parent.isValid():  
            parent = self._root  
        else:  
            parent = in_parent.internalPointer()  
      
        if not QAbstractItemModel.hasIndex(self, in_row, in_column, in_parent):  
            return QModelIndex()  
      
        child = parent.child(in_row)  
        if child:  
            return QAbstractItemModel.createIndex(self, in_row, in_column, child)  
        else:  
            return QModelIndex()
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def parent(self, in_index):  
        if in_index.isValid():  
            p = in_index.internalPointer().parent()  
            if p:  
                return QAbstractItemModel.createIndex(self, p.row(),0,p)  
        return QModelIndex() 
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def columnCount(self, in_index):  
        if in_index.isValid():  
            return in_index.internalPointer().columnCount()  
        return self._root.columnCount()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def data(self, in_index, role):  
        if not in_index.isValid():  
            return None  
        node = in_index.internalPointer()  
        if role == Qt5.DisplayRole:  
            return node.data(in_index.column())
        if role == Qt5.DecorationRole:
            return node.getIcon(in_index.column())
     
        return None
