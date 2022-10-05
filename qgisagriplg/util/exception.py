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
# imports
from qgis_agri import __ERROR_TRACEBACK__

if __ERROR_TRACEBACK__:
    import traceback

# --------------------------------------
# noinspection PyPep8Naming
# -------------------------------------- 
def formatException(e):
    """Utility function to forma exception message.
    
    :param e: exception object.
    :type e: Exception
    """
    return traceback.format_exc() if __ERROR_TRACEBACK__ else str(e)

