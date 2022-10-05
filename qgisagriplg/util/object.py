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
import types
import functools
from datetime import datetime

#-----------------------------------------------------------
class invalid_datetime(datetime):
    def __new__(cls, *args, **kwargs):
        cls.__import_value = None
        return datetime.__new__(cls, 1, 1, 1)
        
    def __str__(self):
        return str(self.__import_value)
        
    def __repr__(self):
        return str(self.__import_value)
        
    def strftime(self, format):
        return str(self.__import_value)
    
    def set_import_value(self, value):
        self.__import_value = value
        return self

#-----------------------------------------------------------
class objUtil:

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def wrapFunction(func, postFunc=None):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            """ Wrapper Function """
            res = func(*args, **kwargs)
            if postFunc is not None:
                postFunc(*args, **kwargs)
            return res
        return wrap

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def bindFunction(obj, func):
        """Bind function to instance, unbind if needed"""
        return types.MethodType(func.__func__ if hasattr(func, "__self__") else func, obj)


    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def is_float(v):
        try:
            x = float(str(v))
        except ValueError:
            return False
        return True
    
    # --------------------------------------
    # 
    # --------------------------------------
    @staticmethod 
    def datetime_from_str(date_str, datetime_format, no_excption=False):
        # init
        date_str = str( date_str )
        if not isinstance( datetime_format, list ):
            datetime_format = [ datetime_format ]
        
        # loop formats
        for fmt in datetime_format:
            try:
                return datetime.strptime( date_str, fmt )
            except (TypeError, ValueError):
                pass
            
        # return bogus datetime
        if no_excption:
            return invalid_datetime().set_import_value( date_str ) #datetime.min
        
        #  raise exception
        raise ValueError( 'Invalid date or no valid date format found' )
    
    

    