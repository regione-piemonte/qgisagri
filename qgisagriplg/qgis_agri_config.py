# -*- coding: utf-8 -*-
"""Plugin configuration.

Description
-----------

Defines the plugin configuration class

Libraries/Modules
-----------------

- None.
    
Notes
-----

- None.

TODO
----

- None.

Author(s)
---------

- Created by Sandro Moretti on 23/09/2019.
- Modified by Sandro Moretti on 28/10/2020.

Copyright (c) 2019 CSI Piemonte.

Members
-------
"""
import os.path

from qgis_agri.util.dictionary import AttributeDict
from qgis_agri.settings.config import ConfigBase



# Create class for plugin configuration
#-----------------------------------------------------------
class QGISAgriConfig(ConfigBase):  
    
    # deafult tolerances
    __DEFAULT_TOLERANCES = AttributeDict({
        'AREA_MIN_VALID_SUOLO': 2.0,
        'AUTO_SNAP_TOLERANCE': 0.1,
        'THICKNESS_TOLERANCE': 20.0,
        'THICKNESS_MAXAREA': 0.0,
        'TOLL_COMP_SUOLO': 10.0,
        'TOLL_COMP_CESSATI': 5.0,
        'CLEAN_VERTEX_TOLERANCE': 0.00001,
        'SNAP_TOLERANCE': 0.001,
        'AREA_TOLERANCE': 0.001,
        'VERTEX_TOLERANCE': 0.01,
        'AREA_TOLERANCE_SUOLO': 0.1
    })
    
    # config service member
    __DEFAULT_SERVICES = AttributeDict({
        "listaLavorazione": {
          "name": "ListaLavorazione",
          "annoField": "campagna",
          "idTipoLista": "idTipoLista",
          "idTipoListaParticella": 1
        },
        "Aziende": {
          "name": "ElencoAziende",
        }, 
        "fogliAzienda": {
          "name": "ElencoFogliAzienda",
          "selectedField": "_selected",
          "statoField": "_statoLavorazione",
          "docFlagField": "isDocumentoPresente",
          "statoFieldDone": 100,
          "statoFieldReject": 999
        }, 
        "fogliAziendaOffline": {
          "name": "ElencoFogliAziendaOffline",
          "codNazionaleField": "codiceNazionale",
          "sezioneField": "sezione",
          "foglioField": "foglio",
          "statoFieldEdit": "_statoLavorazioneEdit",
          "statoPartFieldEdit": "_statoLavorazionePartEdit",
          "comuneField": "descrizioneComune",
          "statoFieldEditDone": 100
        },
        "suoliLavorazioneOffline": {
            "name": "SuoliLavorazioneOffline",
            "featureIdField": "idFeature",
            "featureIdFieldPadre": "idFeaturePadre",
            "suoliInLavorazioneFilter": "tipoSuolo in ('LAV','LAV_KO','COND_KO')"
        },
        "ParticelleLavorazioni": {
            "name": "ParticelleLavorazioni",
            "view": "ParticelleLavorazioni_v",
            "id": "idParticellaLavorazione",
            "idEventoLavField": "idEventoLavorazione",
            "idParticellaLavorazione": "idParticellaLavorazione",
            "codNazionaleField": "codiceNazionale",
            "foglioField": "foglio",
            "numParticellaField": "numeroParticella",
            "subalternoField": "subalterno",
            "descSospensioneField": "descrizioneSospensione",
            "numParticellaCxfField": "particella",
            "hasGeometryField": "_has_geometry",
            "flagCxfField": "flagPresenzaCxf",
            "flagAllegatiField": "flagPresenzaAllegati",
            "flagSospensioneField": "flagSospensione",
            "statoLavPartField": "_statoLavorazionePart",
            
            "flagFieldTrueValue": "S",
            "flagFieldFalseValue": "N",
            "statoLavPartSuspendItemValue": 33
        }
    })
    
    SERVICES = AttributeDict( __DEFAULT_SERVICES )
    
    TOLERANCES = AttributeDict( __DEFAULT_TOLERANCES )
    
    # config functionalities 
    FUNCTIONALITIES = AttributeDict({
        'rejectListaLav': 1011
    })
    
    # number of decimals to display
    DISPLAY_DECIMALS = 3
    
    # config files
    CFG_PLUGIN_FILE_NAME = 'config.yaml'
    CFG_PROFILE_FILE_NAME = 'profiles.yaml'
    CFG_PROCESSING_FILE_NAME = 'processing.yaml'
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, cfg_file=None):
        """ Constructor """
        super().__init__( self.get_config_file_fullame( cfg_file or self.CFG_PLUGIN_FILE_NAME ) )
        
        # read services config
        services_cfg = self.get_value( 'context/controlbox/services', {} ) or {}
        self.SERVICES = AttributeDict( {**self.__DEFAULT_SERVICES, **services_cfg} )
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def reloadConfig(self, conf_file):
        """ """
        self.__init__ (conf_file)
    
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def get_config_file_fullame(cfg_file: str=None):
        cfg_file = cfg_file or ''
        return os.path.join( os.path.dirname(__file__), 'conf', str(cfg_file) ) 
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    @staticmethod
    def loadOtherConfig(cfg_file: str) -> ConfigBase:
        return ConfigBase( QGISAgriConfig.get_config_file_fullame( cfg_file ) )
     
        
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def services(self):
        """ Returns services configuration """
        return self.SERVICES
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def default_tolerances(self):
        """ Returns default plugin tolerances """
        return AttributeDict( self.__DEFAULT_TOLERANCES )
        
    
    # --------------------------------------
    # 
    # --------------------------------------     
    @property
    def display_decimals(self):
        """ Returns the number of decimal to display """
        try:
            return int( self.get_value( 'context/display/numOfDigits', self.DISPLAY_DECIMALS ) )
            
        except ValueError:
            return self.DISPLAY_DECIMALS
    
        