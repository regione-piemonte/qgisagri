# -*- coding: utf-8 -*-
"""Modulo per la gestione dei ruoli di autenticazione del plugin

Descrizione
-----------

Implementazione delle classi per la gestione dei ruoli di autenticazione del plugin.
Gestite le funzionalità associate al ruolo.

Librerie/Moduli
-----------------
    
Note
-----


TODO
----

Attualmente le funzionalità di un ruolo sono definite nel file di configurazione del
plugin; un domani potranno essere passate dalle API del server Agri.

Autore
-------

- Creato da Sandro Moretti il 23/09/2019.
- Modificato da Sandro Moretti il 28/10/2020.

Copyright (c) 2019 CSI Piemonte.

Membri
-------
"""
# system modules import
import copy

# qt modules import
from PyQt5.QtCore import QObject

# qgis modules import
from qgis.PyQt.QtCore import pyqtSignal, pyqtSlot

# plugin modules import
from qgis_agri import agriConfig

# QGISAgriFunctionality
#-----------------------------------------------------------
class QGISAgriFunctionality():
    """Class for Agri functionality"""
    
    def __init__(self, code, defaultEnabled=True):
        """Constructor"""
        self.__code = code
        self.__defaultEnabled = defaultEnabled
        
    @property
    def code(self):
        """Returns functionality code"""
        return self.__code
    
    @property
    def isDefaultEnabled(self):
        """Returns true if functionality is enabled by default"""
        return self.__defaultEnabled
    
    
# QGISAgriRole
#-----------------------------------------------------------
class QGISAgriRole():
    """Class for Agri role"""
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, idRole, code, description, cf):
        """Constructor"""
        self.__id = idRole
        self.__code = code
        self.__description = description
        self.__cf = cf
        self.__funcs = {}
        # assign role functionalities
        self._assignFuncionalities()
        
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def id(self):
        """Returns role id"""
        return self.__id
        
    # --------------------------------------
    # 
    # --------------------------------------    
    @property
    def codice(self):
        """Returns role code"""
        return self.__code
        
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def descrizione(self):
        """Returns role code"""
        return self.__description
    
    # --------------------------------------
    # 
    # --------------------------------------
    @property
    def cod_fiscale(self):
        """Returns cod fiscale"""
        return self.__cf
        
    # --------------------------------------
    # 
    # --------------------------------------
    def _assignFuncionalities(self):
        """Assign functionalities to a new role"""
        
        try:
            # get role functionalities from config
            roles_cfg = agriConfig.get_value( 'roles', {} )
            role_cfg = roles_cfg.get( self.__code, None )
            if not role_cfg:
                return
            
            funcs_cfg = role_cfg.get( 'functionalities', None )
            if not funcs_cfg:
                return
            
            if not isinstance( funcs_cfg, dict ):
                return
            
            # save functionalities to role object
            self.__funcs = copy.deepcopy( funcs_cfg )
        except Exception as e:
            pass
    
    # --------------------------------------
    # 
    # --------------------------------------    
    def isfunctionalityEnabled(self, functionality, defaultEnabled=True):
        """Returns if a functionality is disabled"""
        functCode = None
        if not functionality:
            return defaultEnabled
        
        elif isinstance( functionality, QGISAgriFunctionality ):
            functCode = functionality.code
            defaultEnabled = functionality.isDefaultEnabled
            
        else:
            functCode = functionality
        
        func_cfg = self.__funcs.get( functCode, None )
        if func_cfg is not None:
            enabled = func_cfg.get( 'enabled', True )
            return enabled
            
        return defaultEnabled

# QGISAgriRoleManager
#-----------------------------------------------------------
class QGISAgriRoleManager(QObject):
    """Class for Agri role management"""
    
    # constants
    ID_ATTRIBUTE = 'idRuolo'
    CODE_ATTRIBUTE = 'codice'
    DESC_ATTRIBUTE = 'descrizione'
    CF_ATTRIBUTE = 'codiceFiscale'
    
    ID_ATTRIBUTE_DEF_VALUE = None
    CODE_ATTRIBUTE_DEF_VALUE = '-- ruolo non definito --'
    DESC_ATTRIBUTE_DEF_VALUE = '-- descrizione ruolo non definita --'
    CF_ATTRIBUTE_DEF_VALUE = '-- cod. fiscale non definito --'
    
    
    # signals
    selectedRole = pyqtSignal(object)
    
    # --------------------------------------
    # 
    # --------------------------------------
    def __init__(self, parent=None):
        """Constructor"""
        super().__init__( parent=parent )
        self._roles = {}
        self._selRole = None
        
    # --------------------------------------
    # 
    # --------------------------------------    
    @property
    def currentRole(self):
        """Returns the current Role"""
        return self._selRole
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def count(self):
        """Returns number of loaded roles"""
        return len( self._roles )
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def getRole(self, role_code):
        """Method to get role data from its code"""
        if role_code:
            # return requested role
            return self._roles.get( role_code, None )
        
        elif len(self._roles) == 1:
            # if there is only one role, return that
            return list( self._roles.values() )[0]
     
        return None
        
    # --------------------------------------
    # 
    # --------------------------------------    
    def setRoles(self, roles):
        """Set roles list for user selection"""
        self._roles = {}
        self._selRole = None
        try:
            # collect roles
            for role in roles:
                # get role code
                codice = role.get( self.CODE_ATTRIBUTE, self.CODE_ATTRIBUTE_DEF_VALUE )
                if not codice:
                    continue
                
                codice = str( codice ).strip()
                if not codice:
                    continue
                
                # role id
                idRole = role.get( self.ID_ATTRIBUTE, self.ID_ATTRIBUTE_DEF_VALUE )
                
                # role description
                desc = role.get( self.DESC_ATTRIBUTE, self.DESC_ATTRIBUTE_DEF_VALUE )
                
                # codice fiscale
                cf = role.get( self.CF_ATTRIBUTE, self.CF_ATTRIBUTE_DEF_VALUE )
                
                # add new role
                self._roles[codice] = QGISAgriRole( idRole, codice, desc, cf )
                
        except Exception as e:
            self._roles = {}
            self._selRole = None
            
    # --------------------------------------
    # 
    # --------------------------------------    
    def getDefaultRole(self):
        """Return default role"""
        return QGISAgriRole( idRole = self.ID_ATTRIBUTE_DEF_VALUE,
                             code = self.CODE_ATTRIBUTE_DEF_VALUE, 
                             description = self.DESC_ATTRIBUTE_DEF_VALUE,
                             cf = self.CF_ATTRIBUTE_DEF_VALUE )
                             
    # --------------------------------------
    # 
    # --------------------------------------    
    def getSelectedRole(self):
        """Returns selected role"""
        return self._selRole if self._selRole else self.getDefaultRole()
        
    # --------------------------------------
    # 
    # --------------------------------------
    @pyqtSlot('QString', result=bool)
    def set_selected_role(self, role_code):
        """Selected role slot"""
        # set selected role
        self._selRole = self.getRole( role_code ) or self.getDefaultRole()
        # emit signal for service load
        self.selectedRole.emit( self._selRole )
        return True
