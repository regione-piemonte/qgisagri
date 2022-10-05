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
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from .style_expressions import (isEditedFeature,
                                    isSuoloPropostoUsed, 
                                    is_agri_valid_geom,
                                    agri_format_numero_particella
                                    ##, getAgriDbEleggibilitaDescription 
                                    )

# register custom expression functions
from qgis.core import QgsExpression
QgsExpression.registerFunction( isEditedFeature )
QgsExpression.registerFunction( isSuoloPropostoUsed )
QgsExpression.registerFunction( is_agri_valid_geom ) 
QgsExpression.registerFunction( agri_format_numero_particella )
#QgsExpression.registerFunction( getAgriDbEleggibilitaDescription ) 
