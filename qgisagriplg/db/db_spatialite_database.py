'''
Created on 8 ago 2019

@author: Sandro
'''
from .db_database import Database
from .db_spatialite_connector import SpatiaLiteDBConnector

class SpatialiteDatabase(Database):
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, uri):
        Database.__init__(self, uri)
        self.connector = SpatiaLiteDBConnector(uri)
