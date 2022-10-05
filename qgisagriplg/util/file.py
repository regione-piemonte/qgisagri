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
import os
import errno
import shutil
import tempfile
import collections
import codecs
import glob

from PyQt5.QtCore import Qt, QObject, QTimer, pyqtSignal

# 
#-----------------------------------------------------------
class fileUtil(QObject):
    
    removeFileSchedule = pyqtSignal(str,object,int)
    
    __singleton = None
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self):
        QObject.__init__(self)
        self.removeFileSchedule.connect( fileUtil._removeScheduledFile, Qt.QueuedConnection )

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod   
    def _removeScheduledFile(filename, callback, delay=1000):
        """Remove file with delay"""
        QTimer.singleShot( delay, lambda : callback( filename ) )
     
    # --------------------------------------
    # 
    # --------------------------------------      
    def scheduleRemoveFile_impl(self, filename, callback, delay):
        """Schedule file to delete"""
        if isinstance( callback, collections.Callable ):
            self.removeFileSchedule.emit( filename, callback, delay )

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def instance():
        """Singleton"""
        if fileUtil.__singleton is None:
            fileUtil.__singleton = fileUtil()
        return fileUtil.__singleton
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @staticmethod
    def scheduleRemoveFile(filename, callback, delay=1000):
        fileUtil.instance().scheduleRemoveFile_impl( filename, callback, delay )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @staticmethod
    def removeFile(filename, noException=False):
        try:
            os.remove( filename )
        except OSError as e:
            if not noException:
                raise e
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @staticmethod        
    def removeFiles(path, extension=None, noException=False):
        try:
            files = os.listdir(path)
            for file in files:
                if not extension or file.endswith(extension):
                    os.remove(os.path.join(path, file))
        except FileNotFoundError as e:
            if not noException:
                raise e
        except OSError as e:
            if not noException:
                raise e
            
    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod       
    def removeFilesByFilter(path: str, namefilter: str, minfound: int, noException=False):
        """Try to remove files from a pathname"""
        pathname = os.path.join( str(path), str(namefilter) )
        lst_files = glob.glob( pathname )
        if len(lst_files) < minfound:
            return
        
        for filename in lst_files:
            fileUtil.removeFile( filename, noException )    

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def fileExists(filename):
        """Checks if file exist"""
        return os.path.exists( filename )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def createEmptyTemporaryFile(suffix=None):
        """
        Utility function to create an empty temporay file
        """
        tmpFile = tempfile.NamedTemporaryFile( mode='w', delete=False, suffix=suffix )
        tmpFilePath = tmpFile.name
        tmpFile.close()
        return tmpFilePath
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def createTemporaryCopy(filename, directory=None, delete=True, suffix='.tmp'):
        """
        Utility function to copy a file as temporay file
        
        :param src: file path
        :type src: string
        """
        # check if source file exists
        filename = str(filename)
        if not os.path.isfile( filename ):
            raise FileNotFoundError( errno.ENOENT, os.strerror(errno.ENOENT), filename ) 
        
        # create the temporary file in read/write mode (r+)
        tf = tempfile.NamedTemporaryFile( mode='r+b', dir=directory, delete=delete, suffix=suffix )
        
        # on windows, we can't open the the file again, either manually
        # or indirectly via shutil.copy2, but we *can* copy
        # the file directly using file-like objects, which is what
        # TemporaryFile returns to us.
        # Use `with open` here to automatically close the source file
        with open( filename,'r+b' ) as f:
            shutil.copyfileobj(f,tf)
        
        # rewind the temporary file, otherwise things will go
        # tragically wrong on Windows
        tf.seek(0) 
        return tf
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def makedirs(path: str) -> None:
        """
        Utility function to create target directory & 
        all intermediate directories if don't exists
        """
        try:
            os.makedirs(path)    
        except FileExistsError:
            pass
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def loadFileAsStr(file: str) -> str:
        """Load a file as string"""
        with codecs.open( file, 'r', encoding='utf-8', errors='ignore' ) as file:
            return file.read()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def basenameWithoutExt(file_path: str) -> str:
        file_name = os.path.basename( str(file_path) )
        tokens = file_name.split('.')[:-1]
        return ('.').join( tokens ) if tokens else file_name
    
    