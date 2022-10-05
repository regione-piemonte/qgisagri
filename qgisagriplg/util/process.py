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
import sys

from PyQt5.QtCore import ( QObject,
                           QByteArray,
                           QSharedMemory,
                           QSystemSemaphore,
                           QCryptographicHash )


#
#-----------------------------------------------------------
class ProcessGuard(QObject):
    def __init__(self, key, parent=None):
        super().__init__( parent=parent )
        self._memLockKey = self._generateKeyHash( key, "_memLockKey" )
        self._sharedmemKey = self._generateKeyHash( key, "_sharedmemKey" )
        self._memLock = QSystemSemaphore( self._memLockKey, 1 )
        self._sharedMem = QSharedMemory( self._sharedmemKey )
        
        self._memLock.acquire()
        fix = QSharedMemory( self._sharedmemKey ) # Fix for *nix: http://habrahabr.ru/post/173281/
        fix.attach()
        self._memLock.release()
        
        self._is_running = False
    
    
    def __del__(self):
        self.release()
    
        
    def _generateKeyHash(self, key, salt) -> str:
        data = QByteArray()
        data.append( key )
        data.append( salt )
        data = QCryptographicHash.hash( data, QCryptographicHash.Sha1 ).toHex()
        return data.data().decode('utf8')
        
    def isAnotherRunning(self) -> bool:
        if self._sharedMem.isAttached():
            return False

        self._memLock.acquire()
        isRunning = self._sharedMem.attach()
        if isRunning:
            self._sharedMem.detach()
        self._memLock.release()

        return isRunning
    
    def isRunning(self):
        return self._is_running
    
    def tryToRun(self) -> bool:
        if self.isAnotherRunning():   # Extra check
            self._is_running = False
            return self._is_running

        self._memLock.acquire()
        result = self._sharedMem.create( sys.getsizeof(1) )
        self._memLock.release()
        if not result:
            self.release()
            self._is_running = False
            return self._is_running

        self._is_running = True
        return self._is_running

    def release(self):
        self._memLock.acquire()
        if self._sharedMem.isAttached():
            self._sharedMem.detach()
            self._is_running = False
        self._memLock.release()