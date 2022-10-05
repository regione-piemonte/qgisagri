# -*- coding: utf-8 -*-
"""Modulo per la visualizzazione delle foto appezzamenti dei suoli proposti.

Descrizione
-----------

Implementazione della classe che gestisce la visualizzazione delle foto degli appezzamenti 
dei suoli proposti tramite una finestra di dialogo specializzata; utilizzata dal codice che
 gestisce lo scarico delle immagini tramite le API del server Agri. E' prevista la possibilità
 di visualizzare le immagini con l'applicativo di defaul del sistema operativo.

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
import os
import sys
import tempfile

from PyQt5.QtCore import Qt, QUrl
from PyQt5 import QtWidgets 
from PyQt5.QtGui import QIcon, QPixmap, QImage, QImageWriter, QDesktopServices, QTransform

from qgis.PyQt.QtCore import pyqtSignal

from qgis_agri import tr
from qgis_agri.widgets.photo_viewer import PhotoViewer
#from qgis_agri.qgis_agri_proxystyle import QGISAgriProxyStyle
from qgis_agri.log.logger import QgisLogger as logger

# try to import module for image exif metadata
try:
    import exifread
except ModuleNotFoundError as e:
    logger.log( logger.Level.Warning, "Modulo non reperito: 'ExifRead'" )
    logger.log( logger.Level.Warning, "Usa: python3 -m pip install ExifRead" )
    
    
# QGISAgri error dialog
#-----------------------------------------------------------
class QGISAgriImageViewer(QtWidgets.QDialog):
    
    # QT signals
    zoomToPhoto = pyqtSignal(str)
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, parent=None, flags=Qt.WindowFlags(), enable_zoom_to_feature=False):
        super(QGISAgriImageViewer, self).__init__(parent, flags)
        # 
        self.orig_img_file = ''
        self.enable_zoom_to_feature = enable_zoom_to_feature
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(Qt.AlignLeft)
        VBlayout.addLayout(HBlayout)
        # Create menu
        self.createActions()
        self.createMenus()
        # Add tab widget
        self.tabwidget = QtWidgets.QTabWidget()
        self.tabwidget.currentChanged.connect( self.onTabChanged )
        VBlayout.addWidget(self.tabwidget)
        # Show sizer grip 
        self.setSizeGripEnabled(True)
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def currentPhotoViewer(self):
        """ Returns image viewer """
        return self.tabwidget.currentWidget()
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def onTabChanged(self, index):
        viewer = self.tabwidget.widget( index )
        if viewer and not viewer.shown:
            viewer.fitInView()
            viewer.shown = True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def zoomIn(self):
        viewer = self.currentPhotoViewer
        if viewer:
            viewer.zoom(1)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def zoomOut(self):
        viewer = self.currentPhotoViewer
        if viewer:
            viewer.zoom(-1)
     
    # --------------------------------------
    # 
    # --------------------------------------    
    def normalSize(self):
        viewer = self.currentPhotoViewer
        if viewer:
            viewer.fitInView()
            
    # --------------------------------------
    # 
    # --------------------------------------    
    def rotate(self):
        viewer = self.currentPhotoViewer
        if viewer:
            viewer.rotate(90)
            
    # --------------------------------------
    # 
    # --------------------------------------    
    def getTabIndexByTitle(self, title):
        index = 0
        title = str(title).lower()
        tw = self.tabwidget
        for i in range(tw.count()):
            if tw.tabText( i ).lower() > title:
                break
            index += 1 
        return index


    # --------------------------------------
    # 
    # -------------------------------------- 
    def _get_rotation_transform(self, image, angle):
        center = image.rect().center()
        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.rotate(angle)
        return transform
    

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _get_image_correct_exif_orientation(self, imgFile):
        im = QImage(imgFile)
        if 'exifread' not in sys.modules:
            # return image if module 'exifread' not loaded
            return im
        
        tags = {}
        try:
            # read image exif metadata
            with open(imgFile, 'rb') as f:
                tags = exifread.process_file(f, details=False)         
        except Exception as e:
            logger.log( logger.Level.Critical, "Exifread image tags: {}".format( str(e) ) )
            return im     
                
        # correct image rotation from exif metadata
        if "Image Orientation" in tags.keys():
            orientation = tags["Image Orientation"]
            val = orientation.values
            if 5 in val:
                val += [4,8]
            if 7 in val:
                val += [4, 6]
            if 3 in val:
                # Rotating by 180 degrees clockwise
                im = im.transformed( self._get_rotation_transform(im, -180.0) )
            if 4 in val:
                # Mirroring horizontally.
                im = im.mirrored(horizontal=True, vertical=False)
            if 6 in val:
                # Rotating by 270 degrees clockwise
                im = im.transformed( self._get_rotation_transform(im, -270.0) )
            if 8 in val:
                # Rotating by 90 degrees clockwise
                im = im.transformed( self._get_rotation_transform(im, -90.0) )
        
        
        # return image        
        return im

    # --------------------------------------
    # 
    # -------------------------------------- 
    def loadImage(self, 
                  imgFile, 
                  imgTitle,
                  sorted_tab=False, 
                  orig_img_file=False, 
                  photoId=None):
        
        # check if valid image file name
        imgTitle = str(imgTitle)
        if not imgFile:
            return False
        
        # load image
        image = self._get_image_correct_exif_orientation(imgFile)#QImage(imgFile)
        if image.isNull():
            QtWidgets.QMessageBox.information(self, "Image Viewer", "Cannot load %s." % imgFile)
            return False
        
        self.orig_img_file = imgFile if orig_img_file else ''

        viewer = PhotoViewer(self)
        ###viewer.setStyleSheet("border: 1px solid rgb(185,185,185)")
        viewer.setPhoto( pixmap=QPixmap.fromImage(image), filename=imgFile, photoId=photoId )
        if sorted_tab:
            self.tabwidget.insertTab( self.getTabIndexByTitle( imgTitle ), viewer, imgTitle )
        else:
            self.tabwidget.addTab( viewer, imgTitle )
        viewer.fitInView()
        
        #self.saveAct.setEnabled(True)
        #self.printAct.setEnabled(True)
        self.zoomInAct.setEnabled(True)
        self.zoomOutAct.setEnabled(True)
        self.zoomExtAct.setEnabled(True)
        self.rotateAct.setEnabled(True)
        return True
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def showImage(self, clear_tabs=False):
        # remove all tabs
        if clear_tabs:
            self.tabwidget.clear()
        # show dialog
        self.show()
        

    # --------------------------------------
    # 
    # -------------------------------------- 
    def open(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'QFileDialog.getOpenFileName()', '',
            'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        imgTitle = os.path.basename( fileName )
        self.loadImage( fileName, imgTitle )
       
    # --------------------------------------
    # 
    # --------------------------------------      
    def save(self):
        # init
        viewer = self.currentPhotoViewer
        if viewer is None:
            return
        
        pxImage = viewer.getPhoto()
        if pxImage is None:
            return
        if pxImage.isNull():
            return
                
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'QFileDialog.getSaveFileName()', 
            '', 'Images (*.png *.jpeg *.jpg *.bmp *.gif)', options=options)
        if fileName:
            writer = QImageWriter(fileName)
            if not writer.write(pxImage.toImage()):
                QtWidgets.QMessageBox.information( self, 'QGIS Agri', writer.errorString() )
       
    # --------------------------------------
    # 
    # --------------------------------------         
    def print_(self):
        pass
        """
        viewer = self.currentPhotoViewer
        if viewer is None:
            return
        
        pxImage = viewer.getPhoto()
        if pxImage is None:
            return
            
        self.printer = QPrinter()
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = pxImage.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pxImage.rect())
            painter.drawPixmap(0, 0, pxImage)
        """
    
    # --------------------------------------
    # 
    # --------------------------------------      
    def showExternalViewer(self):
        # init
        viewer = self.currentPhotoViewer
        if viewer is None:
            return
        pxImage = viewer.getPhoto()
        if pxImage is None:
            return
        if pxImage.isNull():
            return
        
        tmpFilePath = self.orig_img_file
        if not self.orig_img_file:
            # write image as temp file
            fileBase = os.path.basename( str(viewer.getPhotoFile()) )
            fileName, fileExt = os.path.splitext( fileBase )
            tmp = tempfile.NamedTemporaryFile( mode='w', prefix=fileName+'_', suffix=fileExt, delete=False )
            tmpFilePath = tmp.name
            
            writer = QImageWriter(tmpFilePath)
            if not writer.write( pxImage.toImage() ):
                QtWidgets.QMessageBox.information( self, 'QGIS Agri', writer.errorString() )
        
        # open image with default OS viewer
        QDesktopServices.openUrl( QUrl.fromLocalFile(tmpFilePath) )
        
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def zoomToFeature(self):
        # get current image viewer
        viewer = self.currentPhotoViewer
        if not viewer:
            return 
        
        # get photo id
        photoId = viewer.photoId
        if not photoId:
            return
        
        # emit signal
        self.zoomToPhoto.emit( str(photoId) )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def createActions(self):
        self.openAct = QtWidgets.QAction("&Apri...", self, shortcut="Ctrl+O", enabled=False, triggered=self.open)
        self.saveAct = QtWidgets.QAction("&Salva...", self, shortcut="Ctrl+S", enabled=False, triggered=self.save)
        self.printAct = QtWidgets.QAction("Stampa...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
        self.exitAct = QtWidgets.QAction("&Esci", self, shortcut="Ctrl+Q", triggered=self.close)
        
        if self.enable_zoom_to_feature:
            self.zoomToAct = QtWidgets.QAction(
                QIcon( ':/plugins/qgis_agri/images/action-zoom-icon.png' ), 
                "Zoom su &Mappa", self, shortcut="Ctrl+Z", triggered=self.zoomToFeature)
        
        self.externViewerAct = QtWidgets.QAction(
            QIcon( ':/plugins/qgis_agri/images/action-external-icon.png' ), 
            "Visualizzatore di sistema", self, shortcut="Ctrl+V", triggered=self.showExternalViewer)
        
        self.zoomInAct = QtWidgets.QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QtWidgets.QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.zoomExtAct = QtWidgets.QAction("Zoom &Ext", self, shortcut="Ctrl+E", enabled=False, triggered=self.normalSize)
        self.rotateAct = QtWidgets.QAction("&Rotate", self, shortcut="Ctrl+R", enabled=False, triggered=self.rotate)
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def createMenus(self):
        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.fileMenu.addAction( self.openAct )
        self.fileMenu.addAction( self.saveAct )
        self.fileMenu.addAction( self.printAct )
        self.fileMenu.addSeparator()
        self.fileMenu.addAction( self.externViewerAct )
        self.fileMenu.addSeparator()
        self.fileMenu.addAction( self.exitAct )
        
        self.viewMenu = QtWidgets.QMenu("&Visualizza", self)
        if self.enable_zoom_to_feature:
            self.viewMenu.addAction( self.zoomToAct )
            self.viewMenu.addSeparator()
        self.viewMenu.addAction( self.zoomInAct )
        self.viewMenu.addAction( self.zoomOutAct )
        self.viewMenu.addAction( self.zoomExtAct )
        self.viewMenu.addSeparator()
        self.viewMenu.addAction( self.rotateAct )
        
        
        mbar = QtWidgets.QMenuBar()
        self.layout().setMenuBar( mbar )
        self.layout().menuBar().addMenu( self.fileMenu )
        self.layout().menuBar().addMenu( self.viewMenu )
        
        # Add toolbar
        toolBar = QtWidgets.QToolBar()
        ##toolBar.setMinimumHeight( 36 )
        ##toolBar.setIconSize( QSize( 32, 32 ) )
        ##toolBar.setStyle( QGISAgriProxyStyle( self, toolBar.iconSize() ) )
        #self.layout().addWidget(toolBar)
        
        if self.enable_zoom_to_feature:
            action = toolBar.addAction( self.zoomToAct )
        
        action = toolBar.addAction( self.externViewerAct )
        #widget = toolBar.widgetForAction( action )
        #widget.setFixedSize( toolBar.iconSize() )
        #widget.setIconSize( toolBar.iconSize() )
        
        self.layout().menuBar().setCornerWidget( toolBar )
        