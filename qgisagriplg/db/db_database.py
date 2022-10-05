'''
Created on 8 ago 2019

@author: Sandro
'''
from qgis.core import QgsMapLayer
from qgis_agri import tr


class BaseError(Exception):

    """Base class for exceptions in the plugin."""

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, e):
        if isinstance(e, Exception):
            msg = e.args[0] if len(e.args) > 0 else ''
        else:
            msg = e

        if not isinstance(msg, str):
            msg = str(msg, 'utf-8', 'replace')  # convert from utf8 and replace errors (if any)

        self.msg = msg
        Exception.__init__(self, msg)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __unicode__(self):
        return self.msg


class InvalidDataException(BaseError):
    pass

class DbError(BaseError):

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, e, query=None):
        BaseError.__init__(self, e)
        self.query = str(query) if query is not None else None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __unicode__(self):
        if self.query is None:
            return BaseError.__unicode__(self)

        msg = tr( "Error:\n{0}" ).format( BaseError.__unicode__(self) )
        if self.query:
            msg += tr( "\n\nQuery:\n{0}" ).format( self.query )
        return msg


class Table:
    TableType, VectorType, RasterType = list(range(3))



class Database:
    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, uri):
        self.connector = None #SpatiaLiteDBConnector(uri)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __del__(self):
        self.close()
        self.connector = None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def uri(self):
        return self.connector.uri()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def providerName(self):
        return self.connector.providerName()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def close(self):
        if self.connector is not None:
            self.connector.close()
        #ret = self.connection().close()
        #return ret
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getConnector(self):
        return self.connector

    """
    def columnUniqueValuesModel(self, col, table, limit=10):
        l = ""
        if limit is not None:
            l = "LIMIT %d" % limit
        return self.sqlResultModel("SELECT DISTINCT %s FROM %s %s" % (col, table, l), self)
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def uniqueIdFunction(self):
        """Return a SQL function used to generate a unique id for rows of a query"""
        # may be overloaded by derived classes
        return "row_number() over ()"

    # --------------------------------------
    # 
    # -------------------------------------- 
    def toSqlLayer(self, sql, geomCol, uniqueCol, layerName="QueryLayer", layerType=None, avoidSelectById=False, _filter=""):
        from qgis.core import QgsVectorLayer, QgsRasterLayer

        if uniqueCol is None:
            if hasattr(self, 'uniqueIdFunction'):
                uniqueFct = self.uniqueIdFunction()
                if uniqueFct is not None:
                    q = 1
                    while "_subq_%d_" % q in sql:
                        q += 1
                    sql = u"SELECT %s AS _uid_,* FROM (%s\n) AS _subq_%d_" % (uniqueFct, sql, q)
                    uniqueCol = "_uid_"

        uri = self.uri()
        uri.setDataSource("", u"(%s\n)" % sql, geomCol, _filter, uniqueCol)
        if avoidSelectById:
            uri.disableSelectAtId(True)
        provider = self.connector.providerName()
        if layerType == QgsMapLayer.RasterLayer:
            return QgsRasterLayer(uri.uri(False), layerName, provider)
        return QgsVectorLayer(uri.uri(False), layerName, provider)

    """
    def tablesFactory(self, row, db, schema=None):
        typ, row = row[0], row[1:]
        if typ == Table.VectorType:
            return self.vectorTablesFactory(row, db, schema)
        elif typ == Table.RasterType:
            return self.rasterTablesFactory(row, db, schema)
        return self.dataTablesFactory(row, db, schema)


    
    def tables(self, schema=None, sys_tables=False):
        tables = self.connector.getTables(schema.name if schema else None, sys_tables)
        if tables is not None:
            ret = []
            for t in tables:
                table = self.tablesFactory(t, self, schema)
                ret.append(table)

                # Similarly to what to browser does, if the geom type is generic geometry,
                # we additionnly add three copies of the layer to allow importing
                if isinstance(table, VectorTable):
                    if table.geomType == 'GEOMETRY':
                        point_table = self.tablesFactory(t, self, schema)
                        point_table.geomType = 'POINT'
                        ret.append(point_table)

                        line_table = self.tablesFactory(t, self, schema)
                        line_table.geomType = 'LINESTRING'
                        ret.append(line_table)

                        poly_table = self.tablesFactory(t, self, schema)
                        poly_table.geomType = 'POLYGON'
                        ret.append(poly_table)

        return ret
    """
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def getVectorTables(self, schema=None):
        return self.connector.getVectorTables(schema)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def createTable(self, table, fields, schema=None):
        field_defs = [x.definition() for x in fields]
        pkeys = [x for x in fields if x.primaryKey]
        pk_name = pkeys[0].name if len(pkeys) > 0 else None

        ret = self.connector.createTable((schema, table), field_defs, pk_name)
        return ret

    # --------------------------------------
    # 
    # -------------------------------------- 
    def createVectorTable(self, table, fields, geom, schema=None):
        ret = self.createTable(table, fields, schema)
        if not ret:
            return False

        createGeomCol = geom is not None
        if createGeomCol:
            geomCol, geomType, geomSrid, geomDim = geom[:4]
            createSpatialIndex = geom[4] if len(geom) > 4 else False

            self.connector.addGeometryColumn((schema, table), geomCol, geomType, geomSrid, geomDim)

            if createSpatialIndex:
                # commit data definition changes, otherwise index can't be built
                self.connector._commit()
                self.connector.createSpatialIndex((schema, table), geomCol)

        return True