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

from PyQt5.QtCore import Qt, QSortFilterProxyModel

# 
#-----------------------------------------------------------
class AgriSortFilterProxyModel(QSortFilterProxyModel):
    """
    Implements a QSortFilterProxyModel.
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, parent=None):
        super(AgriSortFilterProxyModel, self).__init__(parent)
        self.filterString = ''
        self.filterFunctions = {}
        
    # --------------------------------------
    # 
    # --------------------------------------     
    def indexColumn(self, colName):
        """
        """
        model = self.sourceModel()
        return model.indexColumn( colName )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setFilterString(self, text):
        """
        text : string
            The string to be used for pattern matching.
        """
        self.filterString = text.lower()
        self.invalidateFilter()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def addFilterFunction(self, name, new_func, invalidate=True):
        """
        """
        if new_func is None:
            return
        self.filterFunctions[name] = new_func
        if invalidate:
            self.invalidateFilter()
    # --------------------------------------
    # 
    # --------------------------------------
    def removeFilterFunctions(self):
        self.filterFunctions = {} 
        self.invalidateFilter()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def removeFilterFunction(self, name):
        """
        """
        if name in self.filterFunctions.keys():
            del self.filterFunctions[name]
            self.invalidateFilter()
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def filterAcceptsRow(self, row_num, parent):
        """
        """
        model = self.sourceModel()
        # The source model should have a method called row()
        # which returns the table row as a python list.
        tests = [func(model.row(row_num), self.filterString)
                 for func in self.filterFunctions.values()]
        return not False in tests
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getUniqueValues(self, idfldValue, idfldDesc, filterFn=None):
        # get unique values
        dictValues = {}
        
        for row_num in range( self.rowCount() ):
            value = self.data( self.index( row_num, idfldValue ) )
            if value is not None:
                value = str(value)
                descr = self.data( self.index( row_num, idfldDesc ) )
                descr = descr if descr is not None else value 
                dictValues[value] = descr
                
        return dictValues
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getSelectableRowIndeces(self):
        """ Returns a list of selectable row indeces """
        lst = []
        for i in range( self.rowCount() ):
            rowFlags = self.flags( self.index( i, 0 ) )
            if int(rowFlags & Qt.ItemIsSelectable):
                lst.append( i )                       
        return lst
        