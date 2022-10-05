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
import string
from datetime import datetime

from PyQt5.QtGui import QFontMetrics, QIcon, QColor, QBrush, QPalette, QFont
from PyQt5.QtCore import Qt, QSize, QRect, QAbstractTableModel
from PyQt5.QtWidgets import QApplication, QHeaderView, QStyledItemDelegate, QLineEdit, QComboBox

from qgis.PyQt.QtCore import pyqtSignal
from qgis_agri import tr


# Constants
DISPLAY_MAP_VALUES = Qt.UserRole+1
FORMAT_DISPLAY_VALUE = Qt.UserRole+2

# 
#-----------------------------------------------------------
class StringFormatter(string.Formatter):
    # --------------------------------------
    # 
    # --------------------------------------
    def format_field(self, value, format_spec):
        if format_spec.startswith('s'):
            if value is None:
                value = ''
        return super().format( str(value), format_spec)  

# 
#-----------------------------------------------------------
class AgriSelectionModel():
    """
    Table view model
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self):
        self._rows = []
        self._rowFilter = {}
        self._refData = {}
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def rows(self):
        """ Returns data rows """
        return self._rows
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def rowFilter(self):
        """ Returns selection filter """
        return self._rowFilter
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def refData(self):
        """ Returns reference data """
        return self._refData
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setRows(self, rows, rowfilter=None):
        """Set model rows and selected row"""
        self._rows = list(rows or [])
        rowfilter = rowfilter or {}
        self._rowFilter = rowfilter if isinstance( rowfilter, dict ) else {}
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setRefData(self, refData):
        """Set data row"""
        refData = refData or {}
        self._refData = refData if isinstance( refData, dict ) else {}
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getRow(self, index, default=None):
        """ Return row at index """
        try:
            return self._rows[index]
        except IndexError:
            return default
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getRowsWithSelectedField(self, selectedfieldName='_selected'):
        for row in self._rows:
            row[selectedfieldName] = 1 if row == self._rowFilter else 0
        return self._rows
    
# 
#-----------------------------------------------------------
class AgriElencoItemModel(dict):
    """
    Table view model item
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, *args):
        """ Constructor """
        super().__init__( *args )
        self.__itemData = None
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getItemData(self, key, defValue=None):
        """ Return item data """
        itemData = self.__itemData
        if itemData is None:
            return defValue
        return itemData.get( str(key), defValue )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setItemData(self, key, value):
        """ Return item data """
        self.__itemData = self.__itemData or {}
        self.__itemData[ str(key) ] = value
# 
#-----------------------------------------------------------
class AgriElencoModel(QAbstractTableModel):
    """
    Table view model
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, serviceList, *args):
        # init
        QAbstractTableModel.__init__(self, *args)
        self.serviceList = []
        self.header = []
        self.header_info = {}
        self.row_info = {}
        
        # populate list
        serviceList = serviceList or []
        for row in serviceList:
            self.serviceList.append( AgriElencoItemModel(row) )
        
        # auto compose header data
        if self.serviceList:
            self.header = list(self.serviceList[0].keys())
            self.header_info = { k : { 
                "align": Qt.AlignLeft, 
                "text": k,
                "format": None,
                "mapValues": {
                    #'value': { 'text': "", 'icon': "", 'tooltip': "", 'rowBackgroundColor': "", 'selectable': false }
                },
            } for k in self.serviceList[0].keys() }
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _formatVariables(self, index, value):
        """Format a string value substituting field values for a defined row"""
        try:
            if isinstance( value, str ) and str:
                row = self.serviceList[index.row()]
                #return value.format( **row )
                return StringFormatter().format( value, **row )
        except:
            pass   
        return value
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _getHeaderMapValue(self, index, infoType, defValue):
        # init
        value = defValue
        
        # get mapped values for column
        colName = self.header[index.column()]
        colInfo = self.header_info.get( colName, {} )
        colMapVal = colInfo.get( 'mapValues', {} )
        if colMapVal:
            # get cell value 
            value = self.serviceList[index.row()].get( colName, None )
            # get mapped type values (tooltip, text, icon, ...)
            for mapValue, cfg in colMapVal.items():
                if self._checkMapValue( mapValue, str(value) ):
                    value = cfg.get( infoType, defValue )
            """
            # get mapped type values (tooltip, text, icon, ...)
            colInfo = colMapVal.get( str(value), {} )
            # return mapped value of request type (tooltip or text or icon, ...)
            value = colInfo.get( infoType, defValue )
            """
            
        return self._formatVariables( index, value )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _formatDisplayValue(self, index, colValue):
        """ Format display value """
        try:
            colName = self.header[index.column()]
            colInfo = self.header_info.get( colName, {} )
            colFormat = colInfo.get( 'format', {} )
            if not colFormat:
                return colValue
                    
            
            
            func_params = colFormat.get( 'params', "" )
            func_str = str( colFormat.get( 'function', "" ) ).strip().lower()
            if not func_str:
                return colValue
            
            func_tokens = func_str.split(' ')
            func = func_tokens[0]
            
            if func == 'datetime':
                return colValue.strftime( func_params )
                
            elif func == 'utcfromtimestamp':
                ts = int( colValue )
                if 'milliseconds' in func_tokens:
                    ts /= 1000
                return datetime.utcfromtimestamp(ts).strftime( func_params )
            
            return colValue
            
        except:
            return colValue 
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _checkMapValue(self, mapValue, colValue):
        """ Check if column value is equal to mapped value """
        # check if mapped value is an expression
        exprValue = str( mapValue ).strip()  
        if not exprValue.startswith('{') or\
           not exprValue.endswith('}'):
            # check if equal values
            return mapValue == colValue
        
        # extract expression tokens
        exprTokens = exprValue.strip('{}').strip().split('|')
        if len( exprTokens ) < 2:  
            # check if equal values
            return mapValue == colValue
        
        # evaluate expression for unary value
        exprName = exprTokens[0].strip().upper()
        exprValue = exprTokens[1].strip()
        try:  
            if exprName == 'ISEQUALTO':
                return float(colValue) == float(exprValue)
            elif exprName == 'ISNOTEQUALTO':
                return float(colValue) != float(exprValue)
            elif exprName == 'ISGREATERTHAN':
                return float(colValue) > float(exprValue)     
            elif exprName == 'ISGREATERTHANOREQUALTO':
                return float(colValue) >= float(exprValue)     
            elif exprName == 'ISLESSTHAN':
                return float(colValue) < float(exprValue)
            elif exprName == 'ISLESSTHANOREQUALTO':
                return float(colValue) <= float(exprValue)
        except ValueError:
            pass
        
        # check if equal values
        return mapValue == colValue
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _updateRow(self, rowItem):
        """ Update row item data """
        
        # get item data
        rowSelectable = True
        backgroundColors = []
        
        # loop column config
        for col, info in self.header_info.items():
            # loop column mapped values
            colMapVal = info.get( 'mapValues', {} )
            for mapValue, cfg in colMapVal.items():
                # selectable flag 
                if rowSelectable and 'rowSelectable' in cfg:
                    colValue = str( rowItem.get( col ) )
                    if self._checkMapValue( mapValue, colValue ):
                        rowSelectable = cfg.get( 'rowSelectable', True )
                # background color        
                if 'rowForegroundColor' in cfg or\
                   'rowBackgroundColor' in cfg:
                    colValue = str( rowItem.get( col ) )
                    if self._checkMapValue( mapValue, colValue ):
                        fkColor = cfg.get( 'rowForegroundColor', None )
                        bkColor = cfg.get( 'rowBackgroundColor', None )
                        priority = cfg.get( 'priority', -1 )
                        backgroundColors.append( (priority, fkColor, bkColor ) )
                    
        # set row item data
        rowItem.setItemData( 'selectable', rowSelectable )
        
        if backgroundColors:
            backgroundColors.sort( key= lambda x: x[0], reverse= True )
            rowItem.setItemData( 'foregroundColor', backgroundColors[0][1] )
            rowItem.setItemData( 'backgroundColor', backgroundColors[0][2] )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _updateRows(self):
        for rowItem in self.serviceList:
            self._updateRow( rowItem )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getMapValues(self, index):
        # get mapped values for column
        colName = self.header[index.column()]
        colInfo = self.header_info.get( colName, {} )
        return colInfo.get( 'mapValues', {} )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def resetRowInfo(self):
        self.row_info = {} 
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def indexColumn(self, colName):
        # return column index by name
        try:
            return self.header.index( colName )
        except:
            return -1
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getUniqueValues(self, fldValue, fldDesc, filterFn=None):
        # get unique values
        dictValues = {}
        for data in self.serviceList:
            value = data.get(fldValue, None)
            if value is not None:
                value = str(value)
                descr = data.get(fldDesc, None)
                descr = descr if descr is not None else value 
                dictValues[value] = descr
                
        return dictValues
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def rowCount(self, parent):
        return len(self.serviceList) if self.serviceList else 0

    # --------------------------------------
    # 
    # -------------------------------------- 
    def columnCount(self, parent):
        return len(self.serviceList[0]) if self.serviceList else 0
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def data(self, index, role):
        # init
        if not index.isValid():
            return None
        
        colName = self.header[index.column()]    
        
        # cell value
        if role == Qt.DisplayRole:
            colTxt = self._getHeaderMapValue( index, 'text', None )
            if colTxt is not None:
                return colTxt
            value = self.serviceList[index.row()][colName]
            value = self._formatDisplayValue( index, value )
            return value
        
        # font
        elif role == Qt.FontRole:
            colBold = self._getHeaderMapValue( index, 'boldFont', False )
            if colBold == True:
                font = QFont()
                font.setBold( True )
                return font
        
        # column alignement
        elif role == Qt.TextAlignmentRole:
            colInfo = self.header_info.get( colName, {} )
            return ( colInfo.get( 'align', Qt.AlignLeft ) | Qt.AlignVCenter )
        
        # column decoration
        elif role == Qt.DecorationRole:
            colIcon = self._getHeaderMapValue( index, 'icon', None )
            if colIcon:
                return QIcon( str(colIcon) )
            
        # tooltip
        elif role == Qt.ToolTipRole:
            colTooltip = self._getHeaderMapValue( index, 'tooltip', None )
            if colTooltip is not None:
                return colTooltip
         
        # foreground row color
        elif role == Qt.TextColorRole:
            row = self.serviceList[ index.row() ]
            selectable = row.getItemData( 'selectable', True )
            if not selectable:
                color = row.getItemData( 'foregroundColor', None )
                if color:
                    return QColor( color )
                
                
        # background row color
        elif role == Qt.BackgroundRole:
            # get row color
            row = self.serviceList[ index.row() ]
            color = row.getItemData( 'backgroundColor', None )
            if color:
                return QColor( color )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def dataRow(self, index):
        if not index.isValid():
            return None
        return self.serviceList[index.row()]
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def row(self, row_num):
        return self.serviceList[row_num]
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def rows(self):
        return self.serviceList
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setHeaderData(self, col, orientation, value, role):
        if orientation == Qt.Horizontal:
            # column header text
            if role == Qt.DisplayRole:
                colName = self.header[col]
                colInfo = self.header_info.get( colName, {} )
                colInfo['text'] = value
                self.headerDataChanged.emit( Qt.Horizontal, col, col )
                return True
                
            # column alignement
            elif role == Qt.TextAlignmentRole:
                colName = self.header[col]
                colInfo = self.header_info.get( colName, {} )
                colInfo['align'] = value
                self.headerDataChanged.emit( Qt.Horizontal, col, col )
                return True
            
            # column map values
            elif role == DISPLAY_MAP_VALUES:
                colName = self.header[col]
                colInfo = self.header_info.get( colName, {} )
                colInfo['mapValues'] = value
                self._updateRows()
                self.headerDataChanged.emit( Qt.Horizontal, col, col )
                return True
            
            # format dispay text values
            elif role == FORMAT_DISPLAY_VALUE:
                colName = self.header[col]
                colInfo = self.header_info.get( colName, {} )
                colInfo['format'] = value
                #self._updateRows()
                self.headerDataChanged.emit( Qt.Horizontal, col, col )
                return True
                  
        return False
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setData(self, index, value, role):
        #if role == Qt.BackgroundRole:
        #    return True
        return False
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal:
            # column header text
            if role == Qt.DisplayRole:
                colName = self.header[col]
                colInfo = self.header_info.get( colName, {} )
                return colInfo.get( 'text', colName )
                
    # --------------------------------------
    # 
    # -------------------------------------- 
    def headerField(self, col_num):
        return self.header[col_num]
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def sort(self, col, order):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.serviceList = sorted(self.serviceList, 
                                  key=lambda x: x[self.header[col]], 
                                  reverse=True if order == Qt.DescendingOrder else False)
        self.layoutChanged.emit()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def flags(self, index):
        if index.isValid():
            row = index.row()
            selectable = self.serviceList[row].getItemData( 'selectable', True )
            if not selectable:
                return Qt.NoItemFlags
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def clear(self):
        # reset to ensure any views know that everything has changed.
        self.beginResetModel()
        # remove data
        self.serviceList = []
        # end reset
        self.endResetModel()
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def findIndexByFunction(self, fn):
        i = 0
        for row in self.serviceList:
            if fn( row ):
                return self.index( i, 0 )
            i += 1
        return self.index( -1, 0 )
# 
#-----------------------------------------------------------
class AgriIconValuesDelegate(QStyledItemDelegate):    
    """
    Custom Styled Item Delegate
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, parent=None, alignment=Qt.AlignHCenter, invalidIconAsText=False):
        super().__init__(parent)
        self._alignment = alignment
        self._invalidIconAsText = invalidIconAsText
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def paint(self, painter, option, index):
        # check if valid icon
        icon = index.data( Qt.DecorationRole )
        if icon is not None:
            # deafult paint   
            rect = option.rect
            option.icon = QIcon()
            option.text = ""
            option.decorationSize = QSize(-1, -1)
            #QStyledItemDelegate.paint( self, painter, option, index )
            
            if not option.showDecorationSelected or \
               not bool( option.state & QApplication.style().State_Selected ):
                bkColor = index.data( Qt.BackgroundRole )
                if bkColor is not None:
                    painter.fillRect( rect, QBrush( bkColor ) )
            
            # draw icon
            style = QApplication.style()
            style.drawItemPixmap( painter, rect, Qt.AlignHCenter|Qt.AlignVCenter, icon.pixmap( rect.size() ) )
        
        #elif self._invalidIconAsText:
        else:
            QStyledItemDelegate.paint(self, painter, option, index)

# 
#-----------------------------------------------------------
class AgriHeaderView(QHeaderView):    
    """
    Custom header for Table view with column settings
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def sectionSizeFromContents(self, logicalIndex):
        """
        """
        size = super().sectionSizeFromContents( logicalIndex )
        if self.model():
            headerText = self.model().headerData( logicalIndex,
                                                  self.orientation(),
                                                  Qt.DisplayRole )
            options = self.viewOptions()
            metrics = QFontMetrics( options.font )
            maxWidth = self.sectionSize( logicalIndex )
            rect = metrics.boundingRect( QRect( 0, 0, maxWidth, 5000 ),
                                         self.defaultAlignment() |
                                         Qt.TextWordWrap | Qt.TextExpandTabs,
                                         headerText, 4 )
            size = size.expandedTo( rect.size() )
        return size
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def configureColumns(self, columnConfig):
        """
        Columm configuration Method
        
        :param columnConfig: a dictionary containing columns configuration:
                {
                    "field_name": {"align":"AlignHCenter",  "position":1, "text":"name", "visible":True, "width": 50}
                }
        :type columnConfig: dictionary
        """
        
        # check if valid configuration
        if not columnConfig:
            return
        
        
        # init
        parent = self.parent()
        tableModel = self.model()
        
        # initial config
        self.setStretchLastSection( True )
        
        # loop column config
        for fldName, cfg in columnConfig.items():
            
            # get column logical index
            logicalIndex = tableModel.indexColumn( fldName )
            if logicalIndex == -1:
                continue
            
            # set column header text   
            colText = cfg.get( 'text', '' )
            if colText:
                tableModel.setHeaderData( logicalIndex, Qt.Horizontal, colText, Qt.DisplayRole )
                
            # set column map values 
            colIconVal = cfg.get( 'mapValues', {} )
            if colIconVal:
                if parent is not None:
                    parent.setItemDelegateForColumn( logicalIndex, AgriIconValuesDelegate( parent, Qt.AlignHCenter ) )
                tableModel.setHeaderData( logicalIndex, Qt.Horizontal, colIconVal, DISPLAY_MAP_VALUES )
                
            # set format display values 
            colFormatVal = cfg.get( 'format', {} )
            if colFormatVal:
                tableModel.setHeaderData( logicalIndex, Qt.Horizontal, colFormatVal, FORMAT_DISPLAY_VALUE )
                
            # hide column
            if not cfg.get( 'visible', True ):
                self.hideSection( logicalIndex )
                continue
                
            # set column width
            colWidth = cfg.get( 'width', 0 )
            if colWidth > 0:
                self.resizeSection( logicalIndex, colWidth )
            
            # set column resize mode
            colResizable = cfg.get( 'resizable', True )
            if not colResizable:
                self.setSectionResizeMode( logicalIndex, QHeaderView.ResizeToContents )
    
            elif cfg.get( 'autoWidth', False ):
                self.setSectionResizeMode( logicalIndex, QHeaderView.Stretch )
                self.setStretchLastSection( False )
                
            # set column alignement
            colAlign = cfg.get( 'align', 'AlignLeft' )
            if isinstance( colAlign, str ):
                colAlign = { 
                    
                  'alignleft': Qt.AlignLeft,
                  'alignright': Qt.AlignRight,
                  'alignhcenter': Qt.AlignHCenter,
                  'alignjustify': Qt.AlignJustify
                  
                }.get( colAlign.lower(), Qt.AlignLeft )
                
                tableModel.setHeaderData( logicalIndex, Qt.Horizontal, colAlign, Qt.TextAlignmentRole )
            
        # reorder columns    
        for fldName, cfg in columnConfig.items():
            # get column logical index
            logicalIndex = tableModel.indexColumn( fldName )
            if logicalIndex == -1:
                continue
            
            # get column visual index
            visualIndex = self.visualIndex( logicalIndex )
            if visualIndex == -1:
                continue
                 
            # set column position
            colPos = cfg.get( 'position', -1 )
            if colPos > -1:
                self.moveSection( visualIndex, colPos )

# 
#-----------------------------------------------------------
class AgriFilterHeader(AgriHeaderView):
    """
    Custom filter header for Table view
    """
    filterActivated = pyqtSignal(str)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, parent):
        super().__init__(Qt.Horizontal, parent)
        self._headerHt = 24
        self._editors = []
        self._padding = 4
        self._placeholderText = tr( 'Filtra' )
        
        self.setStretchLastSection(True)
        self.setSectionResizeMode( QHeaderView.Stretch )
        self.setDefaultAlignment( Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap )
        self.setSortIndicatorShown(False)
        self.sectionResized.connect( self.adjustPositions ) #SMXX
        self.sectionMoved.connect( self.adjustPositions )
        parent.horizontalScrollBar().valueChanged.connect( self.adjustPositions )
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _removeFilterBoxes(self):
        # remove old filter widgets
        while self._editors:
            editor = self._editors.pop()
            editor.deleteLater()
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setBaseFilterBoxes(self):
        # remove old filter widgets
        self._removeFilterBoxes()
        
        # create all new filter widgets as line edit 
        model = self.parent().model() 
        for index in range( model.columnCount() ):
            editor = QLineEdit( self )
            editor.setPlaceholderText( self._placeholderText )
            editor.textChanged.connect( self.filterActivated.emit )
            editor.setVisible( True )
            self._editors.append( editor )
            
        # adjust widgets position
        self.adjustPositions()
        
    # --------------------------------------
    # 
    # --------------------------------------
    def setFilterBoxes(self):
        try: 
            # remove old filter widgets
            self._removeFilterBoxes()
            
            # prepare comco style sheet
            colBkEdt = QLineEdit().palette().color( QPalette.Base )
            colTxtEdt = QLineEdit().palette().color( QPalette.WindowText )
#             colPlaceHold = QColor( "#80{0:02x}{1:02x}{2:02x}".format( colTxtEdt.red(), colTxtEdt.green(), colTxtEdt.blue() ) )
#             cmbColor = "QComboBox {{ background-color: {0}; color: {1}; }} QComboBox:on {{ color: {1}; }}".format( 
#                 colBkEdt.name(), 
#                 "#80{0:02x}{1:02x}{2:02x}".format( colTxtEdt.red(), colTxtEdt.green(), colTxtEdt.blue() ),
#                 colTxtEdt.name() )
            cmbColor = "QComboBox {{ background-color: {0}; color: {1}; }}".format( 
                colBkEdt.name(), 
                colTxtEdt.name() )
            
            # create new filter widgets   
            filterModel = self.parent().model()
            model = filterModel.sourceModel()
            for col in range( filterModel.columnCount() ):
                # get map values sor current column
                index = filterModel.mapToSource( filterModel.index( 0, col ) )
                mapValues = model.getMapValues( index )
                if mapValues:
                    # create filter combo
                    combo = QComboBox( self )
                    combo.setStyleSheet( cmbColor )
#                     palette = combo.palette()
#                     palette.setColor( QPalette.Text, colPlaceHold )
#                     combo.setPalette( palette )
                    
                    # populate filter combo with mapped values
                    for k,v in mapValues.items():
                        # get combo text
                        text = v.get( 'tag', None )
                        if not text:
                            text = v.get( 'text', None )
                        if not text:
                            text = k 
                        # add new item to combo
                        combo.addItem( text, k )
                        
                    # sort combo items
                    cmbModel = combo.model()
                    cmbModel.sort( 0 )
                    # insert an select first neutral combo item
                    combo.insertItem( 0, self._placeholderText, '' )
                    #combo.setItemData( 0, QBrush( QColor( colTxtEdt ) ), Qt.ForegroundRole )
                    combo.setCurrentIndex( 0 )
                    # add combo to filter widget collection
                    combo.currentTextChanged.connect( self.filterActivated.emit )
                    combo.setVisible( True )
                    self._editors.append( combo )
                    
                else:
                    # create filter edit
                    editor = QLineEdit( self )
                    editor.setPlaceholderText( self._placeholderText )
                    editor.textChanged.connect( self.filterActivated.emit )
                    editor.setVisible( True )
                    self._editors.append( editor )
            
            # adjust widgets position
            self.adjustPositions()
            
        except:
            self.setBaseFilterBoxes()
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def sizeHint(self):
        size = super().sizeHint()
        self._headerHt = size.height() 
        if self._editors:
            height = self._editors[0].sizeHint().height()
            size.setHeight(size.height() + height + self._padding)
        return size

    # --------------------------------------
    # 
    # -------------------------------------- 
    def updateGeometries(self):
        if self._editors:
            height = self._editors[0].sizeHint().height()
            self.setViewportMargins(0, 0, 0, height + self._padding)
        else:
            self.setViewportMargins(0, 0, 0, 0)
        super().updateGeometries()
        self.adjustPositions()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def adjustPositions(self):
        for index, editor in enumerate(self._editors):
            height = editor.sizeHint().height()
            editor.move(
                self.sectionPosition(index) - self.offset(),
                self._headerHt + (self._padding // 2))
            editor.resize(self.sectionSize(index), height)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def filterText(self, index):
        if index < 0 or index >= len(self._editors):
            return ''
        
        filterWidget = self._editors[index]
        if isinstance( filterWidget, QLineEdit ):
            return filterWidget.text()
        
        elif isinstance( filterWidget, QComboBox ):
            return str( filterWidget.currentData() )
        
        else:
            return ''
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def setFilterText(self, index, text):
        if 0 <= index < len(self._editors):
            self._editors[index].setText(text)
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def clearFilters(self):
        for editor in self._editors:
            if isinstance( editor, QLineEdit ):
                editor.clear()
            elif isinstance( editor, QComboBox ):
                editor.setCurrentIndex( 0 )
            
    