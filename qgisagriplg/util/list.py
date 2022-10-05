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

from operator import itemgetter as i
from functools import cmp_to_key


def cmp(x, y):
    """
    Replacement for built-in function cmp that was removed in Python 3

    Compare the two objects x and y and return an integer according to
    the outcome. The return value is negative if x < y, zero if x == y
    and strictly positive if x > y.

    https://portingguide.readthedocs.io/en/latest/comparisons.html#the-cmp-function
    """

    return (x > y) - (x < y)

# 
#-----------------------------------------------------------
class listUtil:

    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def index(l, value):
        """
        Utility function to get a list element index; if not found returns -1
        
        :param l: A list
        :type l: list
    
        :param variables: value to find in list
        :type variables: 
        """
        try:
            return l.index( value )
        except:
            return -1
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def concatNoDuplicate(l1, l2):
        """
        Utility function to concatenate two list withot duplicate
        
        :param l1: A list
        :type l1: list
    
        :param l2: A list
        :type l2: list
        """
        res = list(l1)
        res.extend(x for x in list(l2) if x not in res)
        return res
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def multikeysort(l, columns):
        """
        Utility function to sort a list of dictionaries by multiple dict attributes
        
        :param l: A list of dictionaries
        :type l: list
    
        :param columns: A list of dict attributesused to sort (prefix with char '-' to desc sort)
        :type columns: list
        """
        if not columns:
            return l
        
        comparers = [
            ((i(col[1:].strip()), -1) if col.startswith('-') else (i(col.strip()), 1))
            for col in columns
        ]
        def comparer(left, right):
            comparer_iter = (
                cmp(fn(left), fn(right)) * mult
                for fn, mult in comparers
            )
            return next((result for result in comparer_iter if result), 0)
        return sorted(l, key=cmp_to_key(comparer))