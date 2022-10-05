# -*- coding: utf-8 -*-
"""QGISAgri plugin initialization

Description
-----------

This script initializes the plugin, making it known to QGIS.

Members
-------
"""

# Constants
__PLG_DB3__ = True
"""
Constant for DB3 plugin version 

.. note::
    FUTURE DEVELOP
"""

#: Constant to enable debug messages in plugin log.
__PLG_DEBUG__ = True

#: Constant to retrieve an exception stack traceback
__ERROR_TRACEBACK__ = False

#: Constant name of plugin
__QGIS_AGRI_NAME__ = "QGIS Agri"

#: Constant name of QGIS Agri authorization method by client certificate
__QGIS_AGRI_CERT_METHOD__ = "QGIS_AGRI_CERT"

#: Constant name to tag plugin layers
__QGIS_AGRI_LAYER_TAG__ = "QGIS_AGRI_LAYER"

#: Constant name to tag plugin layers
__QGIS_AGRI_VENV_NAME__ = 'venv'

#: Constant for domain cookies
__QGIS_AGRI_COOKIE_DOMAIN_FILTER__ = 'piemonte.it$'


#: Global instance of :class:`~qgis_agri.qgis_agri_config.QGISAgriConfig`
agriConfig = None

# --------------------------------------
# 
# -------------------------------------- 
def tr(message):
    """Get the translation for a string using Qt translation API.

    We implement this ourselves since we do not inherit QObject.

    :param message: String for translation.
    :type message: str, QString

    :returns: Translated version of message.
    :rtype: QString
    """
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    from PyQt5.QtCore import QCoreApplication
    return QCoreApplication.translate( __QGIS_AGRI_NAME__, message )


# --------------------------------------
# 
# --------------------------------------
class QGISAgriMessageLevel:
    Exception = 1
    Critical = 2
    Warning = 3
    Debug = 4
    
# --------------------------------------
# noinspection PyPep8Naming 
# --------------------------------------
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QGISAgri class from file QGISAgri; the starting point of the plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    # Instance global configuration class
    from qgis_agri.qgis_agri_config import QGISAgriConfig
    global agriConfig
    agriConfig = QGISAgriConfig()
    
    # Return an instance of main plugin class
    from qgis_agri.qgis_agri import QGISAgri
    return QGISAgri(iface)


