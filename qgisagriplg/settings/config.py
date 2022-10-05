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
# import itertools
# import warnings
import os
import copy
import yaml

from qgis_agri import tr
from qgis_agri.util.dictionary import dictUtil


# # 
# #-----------------------------------------------------------
# def iter_split(string, sep=None):
#     """Generatore per splittamento stringa."""
#     sep = sep or ' '
#     groups = itertools.groupby(string, lambda s: s != sep)
#     return (''.join(g) for k, g in groups if k)

# 
#-----------------------------------------------------------
class ConfigBase:
    """ Plugin configuration class. """

    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, cfg_file=None):
        """Constructor"""
        self.__config = {}
        self.__config_file = cfg_file
        self.__initialized = False
        if self.__config_file is not None:
            self.initialize( self.__config_file )
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    @property
    def initialized(self) -> bool:
        """Returns true if inizialized """
        return self.__initialized
            
    # --------------------------------------
    # 
    # --------------------------------------
    def initialize(self, cfg_file=None):
        """Inizializza classe importando il file .yaml"""
        
        # init
        #if self.__initialized:
        #    return
        if cfg_file is None:
            return
        
        cfg = {}
        cfg_main = {}
        cfg_file = cfg_file or self.__config_file
        cfg_path = os.path.dirname( cfg_file )
        
        # load yaml file
        with open(cfg_file, 'r') as stream:
            # load config main file
            cfg_main = yaml.load( stream, Loader=yaml.loader.Loader )
            
        # load possible includes files
        for cfg_inc_file in cfg_main.get("includes", []):
            cfg_inc_file = os.path.join( cfg_path, cfg_inc_file )
            with open(cfg_inc_file, 'r') as stream:
                cfg = dictUtil.dict_merge(cfg, yaml.load( stream, Loader=yaml.loader.Loader ))
                
        # add main config
        cfg = dictUtil.dict_merge(cfg, cfg_main)
        
        # set internal members
        self.__config = cfg
        self.__config_file = cfg_file
        self.__initialized = True

    # --------------------------------------
    # 
    # --------------------------------------
    def get_value(self, cfgPath, default=None, clone=True):
        """Returns a config value by a key path, with slash as separator"""
        
        # init
        self.initialize()
        
        # ricerca valore scorrendo il percorso dato
        cfgPath = cfgPath or ''
        value = None
        dt = self.__config
        for key in cfgPath.split( '/' ): #iter_split(cfgPath, '/'):
            if dt is None:
                break
            value = dt = dt.get(key)
       
        # verifica se reperito un valore     
        if value is not None:
            # restituisci il valore reperito
            return ( copy.deepcopy(value) if clone else value )
        
        elif default is not None:
            #restituisci il valore di default
            return default
        
        # solleva eccezione se valore non reperito
        raise Exception( "{0}: '{1}'".format(
             tr( "Percorso non trovato nel file di configurazione" ),
             cfgPath ) )
                         
    # --------------------------------------
    # 
    # --------------------------------------
    def get_asFloat(self, cfgPath, default=None, clone=True):
        """
        Returns a config value as float number by a key path, 
        with slash as character separator
        """
        value = self.get_value( cfgPath, default, clone )
        try:
            return float( value )
        except ValueError:
            raise ValueError( "{0} '{1}'\n{2}: {3}".format(
                tr( "Impossibile la conversione in numero decimale per il valore" ),
                value,
                tr( "Percorso nel file di configurazione" ),
                cfgPath ) )
