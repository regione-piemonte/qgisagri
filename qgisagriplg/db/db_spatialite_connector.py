'''
Created on 8 ago 2019

@author: 
'''

import tempfile
from functools import cmp_to_key

from qgis.core import (Qgis, 
                       QgsDataSourceUri, 
                       QgsVectorFileWriter, 
                       QgsCoordinateReferenceSystem, 
                       QgsVectorLayer)

from qgis.PyQt.QtCore import QFile

from .db_database import DbError, Table
from .db_connector import DBConnector

from qgis.utils import spatialite_connect
import sqlite3 as sqlite

from qgis_agri import __PLG_DEBUG__, tr
from qgis_agri.log.logger import QgisLogger as logger
from qgis_agri.util.file import fileUtil
from qgis_agri.util.object import objUtil

#
#-----------------------------------------------------------
class SpatiaLiteDBConnector(DBConnector):

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, uri):
        DBConnector.__init__(self, uri)

        self.has_geometry_columns = False
        self.has_geometry_columns_access = False
        self.has_spatialite4 = False

        self.dbname = uri.database()
        if not QFile.exists(self.dbname):
            raise ConnectionError( tr( '"{0}" not found' ).format( self.dbname ) )

        try:
            self.connection = spatialite_connect(self._connectionInfo())

        except self.connection_error_types() as e:  # pylint: disable=catching-non-exception
            raise ConnectionError(e)

        self._checkSpatial()
        self._checkRaster()
        

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _connectionInfo(self):
        return str(self.dbname)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def cancel(self):
        if self.connection:
            self.connection.interrupt()
            
    # --------------------------------------
    # 
    # -------------------------------------- 
    def close(self):
        self.connection.close()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def providerName(self):
        return 'spatialite'
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def execution_error_types(self):
        return sqlite.Error, sqlite.ProgrammingError, sqlite.Warning # pylint: disable=no-member
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def connection_error_types(self):
        return sqlite.InterfaceError, sqlite.OperationalError # pylint: disable=no-member

    # --------------------------------------
    # 
    # -------------------------------------- 
    @classmethod
    def isValidDatabase(self, path):
        if not QFile.exists(path):
            return False
        try:
            conn = spatialite_connect(path)
        except sqlite.InterfaceError:# pylint: disable=no-member
            return False
        except sqlite.OperationalError:# pylint: disable=no-member
            return False

        isValid = False

        try:
            c = conn.cursor()
            c.execute("SELECT count(*) FROM sqlite_master")
            c.fetchone()
            isValid = True
        except sqlite.DatabaseError: # pylint: disable=no-member
            pass

        conn.close()
        return isValid

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _checkSpatial(self):
        """ check if it's a valid SpatiaLite db """
        self.has_spatial = self._checkGeometryColumnsTable()
        return self.has_spatial

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _checkRaster(self):
        """ check if it's a rasterite db """
        self.has_raster = self._checkRasterTables()
        return self.has_raster

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _checkGeometryColumnsTable(self):
        try:
            c = self._get_cursor()
            self._execute(c, u"SELECT CheckSpatialMetaData()")
            v = c.fetchone()[0]
            self.has_geometry_columns = v == 1 or v == 3
            self.has_spatialite4 = v == 3
        except Exception:
            self.has_geometry_columns = False
            self.has_spatialite4 = False

        self.has_geometry_columns_access = self.has_geometry_columns
        return self.has_geometry_columns

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _checkRasterTables(self):
        c = self._get_cursor()
        sql = u"SELECT count(*) = 3 FROM sqlite_master WHERE name IN ('layer_params', 'layer_statistics', 'raster_pyramids')"
        self._execute(c, sql)
        ret = c.fetchone()
        return ret and ret[0]
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def _checkLwgeomFeatures(self):
        try:
            c = self._get_cursor()
            self._execute(c, u"SELECT lwgeom_version();")
            return c.fetchone()[0]
        except Exception:
            return None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getInfo(self):
        c = self._get_cursor()
        self._execute(c, u"SELECT sqlite_version()")
        return c.fetchone()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getSpatialInfo(self):
        """ returns tuple about SpatiaLite support:
                - lib version
                - geos version
                - proj version
        """
        if not self.has_spatial:
            return

        c = self._get_cursor()
        try:
            self._execute(c, u"SELECT spatialite_version(), geos_version(), proj4_version()")
        except DbError:
            return

        return c.fetchone()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasSpatialSupport(self):
        return self.has_spatial

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasRasterSupport(self):
        return self.has_raster

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasCustomQuerySupport(self):
        return Qgis.QGIS_VERSION[0:3] >= "1.6"

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasTableColumnEditingSupport(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasCreateSpatialViewSupport(self):
        return True

    # --------------------------------------
    # 
    # -------------------------------------- 
    def fieldTypes(self):
        return [
            "integer", "bigint", "smallint",  # integers
            "real", "double", "float", "numeric",  # floats
            "varchar", "varchar(255)", "character(20)", "text",  # strings
            "date", "datetime"  # date/time
        ]

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getSchemas(self):
        return None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getTables(self, schema=None, add_sys_tables=False):
        """ get list of tables """
        tablenames = []
        items = []

        ####sys_tables = QgsSqliteUtils.systemTables()

        try:
            vectors = self.getVectorTables(schema)
            for tbl in vectors:
                ###if not add_sys_tables and tbl[1] in sys_tables:
                ###    continue
                tablenames.append(tbl[1])
                items.append(tbl)
        except DbError:
            pass

        try:
            rasters = self.getRasterTables(schema)
            for tbl in rasters:
                ##if not add_sys_tables and tbl[1] in sys_tables:
                ##    continue
                tablenames.append(tbl[1])
                items.append(tbl)
        except DbError:
            pass

        c = self._get_cursor()

        """
        if self.has_geometry_columns:
            # get the R*Tree tables
            sql = u"SELECT f_table_name, f_geometry_column FROM geometry_columns WHERE spatial_index_enabled = 1"
            self._execute(c, sql)
            for idx_item in c.fetchall():
                sys_tables.append('idx_%s_%s' % idx_item)
                sys_tables.append('idx_%s_%s_node' % idx_item)
                sys_tables.append('idx_%s_%s_parent' % idx_item)
                sys_tables.append('idx_%s_%s_rowid' % idx_item)
        """
        sql = u"SELECT name, type = 'view' FROM sqlite_master WHERE type IN ('table', 'view')"
        self._execute(c, sql)

        for tbl in c.fetchall():
            if tablenames.count(tbl[0]) <= 0 and not tbl[0].startswith('idx_'):
                ##if not add_sys_tables and tbl[0] in sys_tables:
                ##    continue
                item = list(tbl)
                item.insert(0, Table.TableType)
                items.append(item)

        for i, tbl in enumerate(items):
            #tbl.insert(3, tbl[1] in sys_tables)
            tbl.insert(3, False)

        return sorted(items, key=cmp_to_key(lambda x, y: (x[1] > y[1]) - (x[1] < y[1])))

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getVectorTables(self, schema=None): #pylint: disable=unused-argument
        """ get list of table with a geometry column
                it returns:
                        name (table name)
                        type = 'view' (is a view?)
                        geometry_column:
                                f_table_name (the table name in geometry_columns may be in a wrong case, use this to load the layer)
                                f_geometry_column
                                type
                                coord_dimension
                                srid
        """

        if self.has_geometry_columns:
            if self.has_spatialite4:
                cols = """CASE geometry_type % 10
                                  WHEN 1 THEN 'POINT'
                                  WHEN 2 THEN 'LINESTRING'
                                  WHEN 3 THEN 'POLYGON'
                                  WHEN 4 THEN 'MULTIPOINT'
                                  WHEN 5 THEN 'MULTILINESTRING'
                                  WHEN 6 THEN 'MULTIPOLYGON'
                                  WHEN 7 THEN 'GEOMETRYCOLLECTION'
                                  END AS gtype,
                                  CASE geometry_type / 1000
                                  WHEN 0 THEN 'XY'
                                  WHEN 1 THEN 'XYZ'
                                  WHEN 2 THEN 'XYM'
                                  WHEN 3 THEN 'XYZM'
                                  ELSE NULL
                                  END AS coord_dimension"""
            else:
                cols = "g.type,g.coord_dimension"

            # get geometry info from geometry_columns if exists
            sql = u"""SELECT m.name, m.type = 'view', g.f_table_name, g.f_geometry_column, %s, g.srid
                                                FROM sqlite_master AS m JOIN geometry_columns AS g ON upper(m.name) = upper(g.f_table_name)
                                                WHERE m.type in ('table', 'view')
                                                ORDER BY m.name, g.f_geometry_column""" % cols

        else:
            return []

        cur = None
        try:
            # execute query
            cur = self._get_cursor()
            self._execute(cur, sql)
            # collect layer data sources
            db_path = self.uri().database()
            items = []
            for tbl in cur.fetchall():
                item = list(tbl)
                uri = QgsDataSourceUri()
                uri.setDatabase(db_path)
                uri.setDataSource(' ', item[2], item[3], None)
                items.append(uri)
        except Exception as e:
            raise e        
        finally: 
            if cur is not None:
                cur.close()
            
        return items

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getRasterTables(self, schema=None): #pylint: disable=unused-argument
        """ get list of table with a geometry column
                it returns:
                        name (table name)
                        type = 'view' (is a view?)
                        geometry_column:
                                r.table_name (the prefix table name, use this to load the layer)
                                r.geometry_column
                                srid
        """

        if not self.has_geometry_columns:
            return []
        if not self.has_raster:
            return []

        c = self._get_cursor()

        # get geometry info from geometry_columns if exists
        sql = u"""SELECT r.table_name||'_rasters', m.type = 'view', r.table_name, r.geometry_column, g.srid
                                                FROM sqlite_master AS m JOIN geometry_columns AS g ON upper(m.name) = upper(g.f_table_name)
                                                JOIN layer_params AS r ON upper(REPLACE(m.name, '_metadata', '')) = upper(r.table_name)
                                                WHERE m.type in ('table', 'view') AND upper(m.name) = upper(r.table_name||'_metadata')
                                                ORDER BY r.table_name"""

        self._execute(c, sql)

        items = []
        for i, tbl in enumerate(c.fetchall()): # pylint: disable=unused-variable
            item = list(tbl)
            item.insert(0, Table.RasterType)
            items.append(item)

        return items

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getTableRowCount(self, table):
        c = self._get_cursor()
        self._execute(c, u"SELECT COUNT(*) FROM %s" % self.quoteId(table))
        ret = c.fetchone()
        return ret[0] if ret is not None else None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getTableFields(self, table):
        """ return list of columns in table """
        c = self._get_cursor()
        sql = u"PRAGMA table_info(%s)" % (self.quoteId(table))
        self._execute(c, sql)
        return c.fetchall()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasTableField(self, table, field):
        """ check if a field exists in table """
        field = str(field).lower()
        c = self._get_cursor()
        sql = u"PRAGMA table_info(%s)" % (self.quoteId(table))
        self._execute(c, sql)
        for rec in c.fetchall():
            if rec[1].lower() == field.lower():
                return True
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getTableIndexes(self, table):
        """ get info about table's indexes """
        c = self._get_cursor()
        sql = u"PRAGMA index_list(%s)" % (self.quoteId(table))
        self._execute(c, sql)
        indexes = c.fetchall()
        num, name, unique = None, None, None

        for i, idx in enumerate(indexes):
            # sqlite has changed the number of columns returned by index_list since 3.8.9
            # I am not using self.getInfo() here because this behavior
            # can be changed back without notice as done for index_info, see:
            # http://repo.or.cz/sqlite.git/commit/53555d6da78e52a430b1884b5971fef33e9ccca4
            if len(idx) == 3:
                num, name, unique = idx
            if len(idx) == 5:
                num, name, unique, _, _ = idx # num, name, unique, createdby, partial
            sql = u"PRAGMA index_info(%s)" % (self.quoteId(name))
            self._execute(c, sql)

            idx = [num, name, unique]
            cols = []
            for _, cid, _ in c.fetchall(): # seq, cid, cname
                cols.append(cid)
            idx.append(cols)
            indexes[i] = idx

        return indexes

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getTableConstraints(self, table): #pylint: disable=unused-argument
        return None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getTableTriggers(self, table):
        c = self._get_cursor()
        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        sql = u"SELECT name, sql FROM sqlite_master WHERE tbl_name = %s AND type = 'trigger'" % (
            self.quoteString(tablename))
        self._execute(c, sql)
        return c.fetchall()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteTableTrigger(self, trigger, table=None): #pylint: disable=unused-argument
        """ delete trigger """
        sql = u"DROP TRIGGER %s" % self.quoteId(trigger)
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getTableExtent(self, table, geom):
        """ find out table extent """
        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        c = self._get_cursor()

        if self.isRasterTable(table):
            tablename = tablename.replace('_rasters', '_metadata')
            geom = u'geometry'

        sql = u"""SELECT Min(MbrMinX(%(geom)s)), Min(MbrMinY(%(geom)s)), Max(MbrMaxX(%(geom)s)), Max(MbrMaxY(%(geom)s))
                                                FROM %(table)s """ % {'geom': self.quoteId(geom),
                                                                      'table': self.quoteId(tablename)}
        self._execute(c, sql)
        return c.fetchone()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getViewDefinition(self, view):
        """ returns definition of the view """
        schema, tablename = self.getSchemaTableName(view) # pylint: disable=unused-variable
        sql = u"SELECT sql FROM sqlite_master WHERE type = 'view' AND name = %s" % self.quoteString(tablename)
        c = self._execute(None, sql)
        ret = c.fetchone()
        return ret[0] if ret is not None else None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getSpatialRefInfo(self, srid):
        sql = u"SELECT ref_sys_name FROM spatial_ref_sys WHERE srid = %s" % self.quoteString(srid)
        c = self._execute(None, sql)
        ret = c.fetchone()
        return ret[0] if ret is not None else None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isVectorTable(self, table):
        if self.has_geometry_columns:
            schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
            sql = u"SELECT count(*) FROM geometry_columns WHERE upper(f_table_name) = upper(%s)" % self.quoteString(
                tablename)
            c = self._execute(None, sql)
            ret = c.fetchone()
            return ret is not None and ret[0] > 0
        return True

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isRasterTable(self, table):
        if self.has_geometry_columns and self.has_raster:
            schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
            if not tablename.endswith("_rasters"):
                return False

            sql = u"""SELECT count(*)
                                        FROM layer_params AS r JOIN geometry_columns AS g
                                                ON upper(r.table_name||'_metadata') = upper(g.f_table_name)
                                        WHERE upper(r.table_name) = upper(REPLACE(%s, '_rasters', ''))""" % self.quoteString(
                tablename)
            c = self._execute(None, sql)
            ret = c.fetchone()
            return ret is not None and ret[0] > 0

        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def createTable(self, table, field_defs, pkey):
        """ create ordinary table
                        'fields' is array containing field definitions
                        'pkey' is the primary key name
        """
        if len(field_defs) == 0:
            return False

        sql = "CREATE TABLE %s (" % self.quoteId(table)
        sql += u", ".join(field_defs)
        if pkey is not None and pkey != "":
            sql += u", PRIMARY KEY (%s)" % self.quoteId(pkey)
        sql += ")"

        self._execute_and_commit(sql)
        return True

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteTable(self, table):
        """ delete table from the database """
        if self.isRasterTable(table):
            return False

        c = self._get_cursor()
        sql = u"DROP TABLE %s" % self.quoteId(table)
        self._execute(c, sql)
        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        sql = u"DELETE FROM geometry_columns WHERE upper(f_table_name) = upper(%s)" % self.quoteString(tablename)
        self._execute(c, sql)
        self._commit()

        return True

    # --------------------------------------
    # 
    # -------------------------------------- 
    def emptyTable(self, table):
        """ delete all rows from table """
        if self.isRasterTable(table):
            return False

        sql = u"DELETE FROM %s" % self.quoteId(table)
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def renameTable(self, table, new_table):
        """ rename a table """
        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        if new_table == tablename:
            return False

        if self.isRasterTable(table):
            return False

        c = self._get_cursor()

        sql = u"ALTER TABLE %s RENAME TO %s" % (self.quoteId(table), self.quoteId(new_table))
        self._execute(c, sql)

        # update geometry_columns
        if self.has_geometry_columns:
            sql = u"UPDATE geometry_columns SET f_table_name = %s WHERE upper(f_table_name) = upper(%s)" % (
                self.quoteString(new_table), self.quoteString(tablename))
            self._execute(c, sql)

        self._commit()
        return True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def cloneTable(self, table, new_table, append=False):
        """ clone a table """
        curs = None
        try:
            schema, tablename = self.getSchemaTableName( table )
            if new_table == tablename:
                return False
    
            if self.isRasterTable( table ):
                return False
    
            sql = "SELECT CloneTable('main', '{0}', '{1}', 1 {2});".format( 
                table, 
                new_table,
                ", '::append::'" if append else ''
            )
            
            curs = self._get_cursor()
            self._execute( curs, sql )
            self.updateTableStatistics(table)
            self._commit()
            return True
        finally:
            if curs is not None:
                curs.close()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def moveTable(self, table, new_table, new_schema=None): #pylint: disable=unused-argument
        return self.renameTable(table, new_table)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def createView(self, view, query):
        sql = u"CREATE VIEW %s AS %s" % (self.quoteId(view), query)
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteView(self, view):
        c = self._get_cursor()

        sql = u"DROP VIEW %s" % self.quoteId(view)
        self._execute(c, sql)

        # update geometry_columns
        if self.has_geometry_columns:
            sql = u"DELETE FROM geometry_columns WHERE f_table_name = %s" % self.quoteString(view)
            self._execute(c, sql)

        self._commit()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def renameView(self, view, new_name):
        """ rename view """
        return self.renameTable(view, new_name)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def createSpatialView(self, view, query):

        self.createView(view, query)
        # get type info about the view
        sql = u"PRAGMA table_info(%s)" % self.quoteString(view)
        c = self._execute(None, sql)
        geom_col = None
        for r in c.fetchall():
            if r[2].upper() in ('POINT', 'LINESTRING', 'POLYGON',
                                'MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON'):
                geom_col = r[1]
                break
        if geom_col is None:
            return

        # get geometry type and srid
        sql = u"SELECT geometrytype(%s), srid(%s) FROM %s LIMIT 1" % (self.quoteId(geom_col), self.quoteId(geom_col), self.quoteId(view))
        c = self._execute(None, sql)
        r = c.fetchone()
        if r is None:
            return

        gtype, gsrid = r
        gdim = 'XY'
        if ' ' in gtype:
            zm = gtype.split(' ')[1]
            gtype = gtype.split(' ')[0]
            gdim += zm
        try:
            wkbType = ('POINT', 'LINESTRING', 'POLYGON', 'MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON').index(gtype) + 1
        except:  # pylint: disable=W0702
            wkbType = 0
        if 'Z' in gdim:
            wkbType += 1000
        if 'M' in gdim:
            wkbType += 2000

        sql = u"""INSERT INTO geometry_columns (f_table_name, f_geometry_column, geometry_type, coord_dimension, srid, spatial_index_enabled)
                                        VALUES (%s, %s, %s, %s, %s, 0)""" % (self.quoteId(view), self.quoteId(geom_col), wkbType, len(gdim), gsrid)
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def runVacuum(self):
        """ run vacuum on the db """
        # Workaround http://bugs.python.org/issue28518
        self.connection.isolation_level = None
        c = self._get_cursor()
        c.execute('VACUUM')
        self.connection.isolation_level = '' # reset to default isolation
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def duplicateTableColumn(self, table, field_name, field_def, field_upd_expr, update_statistics=True):
        """ add a column to table """
        sql = u"ALTER TABLE %s ADD %s" % (self.quoteId(table), field_def)
        self._execute(None, sql)
        
        sql = "UPDATE {0} SET {1}={2}".format( self.quoteId(table), field_name, field_upd_expr )
        self._execute(None, sql)   
        
        if update_statistics:
            sql = u"SELECT InvalidateLayerStatistics(%s)" % (self.quoteId(table))
            self._execute(None, sql)
    
            sql = u"SELECT UpdateLayerStatistics(%s)" % (self.quoteId(table))
            self._execute(None, sql)

        self._commit()
        return True

    # --------------------------------------
    # 
    # -------------------------------------- 
    def addTableColumn(self, table, field_def, update_statistics=True):
        """ add a column to table """
        sql = u"ALTER TABLE %s ADD %s" % (self.quoteId(table), field_def)
        self._execute(None, sql)
        
        if update_statistics:
            sql = u"SELECT InvalidateLayerStatistics(%s)" % (self.quoteId(table))
            self._execute(None, sql)
    
            sql = u"SELECT UpdateLayerStatistics(%s)" % (self.quoteId(table))
            self._execute(None, sql)

        self._commit()
        return True
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def updateTableStatistics(self, table):
        """ add a column to table """
        sql = "SELECT InvalidateLayerStatistics({0})".format( ( self.quoteId(table) ) )
        self._execute(None, sql)

        sql = "SELECT UpdateLayerStatistics({0})".format( ( self.quoteId(table) ) )
        self._execute(None, sql)
        return True

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteTableColumn(self, table, column):
        """ delete column from a table """
        if not self.isGeometryColumn(table, column):
            return False  # column editing not supported

        # delete geometry column correctly
        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        sql = u"SELECT DiscardGeometryColumn(%s, %s)" % (self.quoteString(tablename), self.quoteString(column))
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def updateTableColumn(self, table, column, new_name, new_data_type=None, new_not_null=None, new_default=None, comment=None):  #pylint: disable=unused-argument
        return False  # column editing not supported

    # --------------------------------------
    # 
    # -------------------------------------- 
    def renameTableColumn(self, table, column, new_name): #pylint: disable=unused-argument
        """ rename column in a table """
        return False  # column editing not supported

    # --------------------------------------
    # 
    # -------------------------------------- 
    def setColumnType(self, table, column, data_type): #pylint: disable=unused-argument
        """ change column type """
        return False  # column editing not supported

    # --------------------------------------
    # 
    # -------------------------------------- 
    def setColumnDefault(self, table, column, default): #pylint: disable=unused-argument
        """ change column's default value. If default=None drop default value """
        return False  # column editing not supported

    # --------------------------------------
    # 
    # -------------------------------------- 
    def setColumnNull(self, table, column, is_null): #pylint: disable=unused-argument
        """ change whether column can contain null values """
        return False  # column editing not supported

    # --------------------------------------
    # 
    # -------------------------------------- 
    def isGeometryColumn(self, table, column):

        c = self._get_cursor()
        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        sql = u"SELECT count(*) > 0 FROM geometry_columns WHERE upper(f_table_name) = upper(%s) AND upper(f_geometry_column) = upper(%s)" % (
            self.quoteString(tablename), self.quoteString(column))
        self._execute(c, sql)
        return c.fetchone()[0] == 't'

    # --------------------------------------
    # 
    # -------------------------------------- 
    def addGeometryColumn(self, table, geom_column='geometry', geom_type='POINT', srid=-1, dim=2):

        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        sql = u"SELECT AddGeometryColumn(%s, %s, %d, %s, %s)" % (
            self.quoteString(tablename), self.quoteString(geom_column), srid, self.quoteString(geom_type), dim)
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteGeometryColumn(self, table, geom_column):
        return self.deleteTableColumn(table, geom_column)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def addTableUniqueConstraint(self, table, column): #pylint: disable=unused-argument
        """ add a unique constraint to a table """
        return False  # constraints not supported

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteTableConstraint(self, table, constraint): #pylint: disable=unused-argument
        """ delete constraint in a table """
        return False  # constraints not supported

    # --------------------------------------
    # 
    # -------------------------------------- 
    def addTablePrimaryKey(self, table, column):
        """ add a primery key (with one column) to a table """
        sql = u"ALTER TABLE %s ADD PRIMARY KEY (%s)" % (self.quoteId(table), self.quoteId(column))
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def createTableIndex(self, table, name, column, unique=False):
        """ create index on one column using default options """
        unique_str = u"UNIQUE" if unique else ""
        sql = u"CREATE %s INDEX %s ON %s (%s)" % (
            unique_str, self.quoteId(name), self.quoteId(table), self.quoteId(column))
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteTableIndex(self, table, name):
        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        sql = u"DROP INDEX %s" % self.quoteId((schema, name))
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def createSpatialIndex(self, table, geom_column='geometry'):
        if self.isRasterTable(table):
            return False

        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        sql = u"SELECT CreateSpatialIndex(%s, %s)" % (self.quoteString(tablename), self.quoteString(geom_column))
        self._execute_and_commit(sql)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def deleteSpatialIndex(self, table, geom_column='geometry'):
        if self.isRasterTable(table):
            return False

        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        try:
            sql = u"SELECT DiscardSpatialIndex(%s, %s)" % (self.quoteString(tablename), self.quoteString(geom_column))
            self._execute_and_commit(sql)
        except DbError:
            sql = u"SELECT DeleteSpatialIndex(%s, %s)" % (self.quoteString(tablename), self.quoteString(geom_column))
            self._execute_and_commit(sql)
            # delete the index table
            idx_table_name = u"idx_%s_%s" % (tablename, geom_column)
            self.deleteTable(idx_table_name)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasSpatialIndex(self, table, geom_column='geometry'):
        if not self.has_geometry_columns or self.isRasterTable(table):
            return False
        c = self._get_cursor()
        schema, tablename = self.getSchemaTableName(table) # pylint: disable=unused-variable
        sql = u"SELECT spatial_index_enabled FROM geometry_columns WHERE upper(f_table_name) = upper(%s) AND upper(f_geometry_column) = upper(%s)" % (
            self.quoteString(tablename), self.quoteString(geom_column))
        self._execute(c, sql)
        row = c.fetchone()
        return row is not None and row[0] == 1
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def executeScript(self, sql=None, sqlFile=None):
        """Execute a file or string script"""
        curs = None
        try:
            # create missing Spatialite function
            if not self._checkLwgeomFeatures():
                # simulate ST_MakeValid function
                def makevalid(geom):
                    return geom
                self.connection.create_function("st_makevalid", 1, makevalid)
                logger.log( logger.Level.Warning, 
                            "Missing Spatialite LWGEOM features (ST_MakeValid, ...)" )

            # load script
            if sqlFile is not None:
                import codecs
                with codecs.open( sqlFile, 'r', encoding='utf-8', errors='ignore' ) as file:
                    sql = file.read()
            ##sqlite.complete_statement( sql )
            curs = self._get_cursor()
            curs.executescript( sql )
        finally:
            if curs is not None:
                curs.close()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def importTable(self, table, dictList, dropTable=True, conflictFields=None):
        """
        Load a list of dictionaries int a table: each item in list(each dictionary)
        represents a row of the table
        """
        
        # init
        if not dictList or not isinstance( dictList, list ):
            return
        
        curs = None
        try:
            # format table fields
            lstFields = []
            for name in dictList[0].keys():
                lstFields.append( "{0} TEXT".format( name ) )
            sqlFields = ','.join( lstFields )
            
            # format ON CONFLICT expression
            sqlOnConflict = ''
            if conflictFields:
                lstFields = []
                for name in dictList[0].keys():
                    lstFields.append( "{0} = :{0}".format( name ) )
                sqlOnConflict = "ON CONFLICT({0}) DO UPDATE SET {1}".format( conflictFields, ','.join( lstFields ) )
            
            
            curs = self._get_cursor()
            
            # drop table if exists
            if dropTable:
                query = "DROP TABLE IF EXISTS {0}".format( table )
                self._execute( curs, query )
            
            # create table schema
            query = "CREATE TABLE IF NOT EXISTS {0} ({1})".format( table, sqlFields )
            self._execute( curs, query )
            
            # insert to table
            for dictRow in dictList:
                columns = ', '.join( dictRow.keys() )
                placeholders = ':'+', :'.join( dictRow.keys() )
                query = "INSERT INTO {0} ({1}) VALUES ({2}) {3}".format( table, columns, placeholders, sqlOnConflict )
                curs.execute( query, dictRow )
            
            self._commit()
        except:
            raise
        finally:
            if curs is not None:
                curs.close()
        
        
    # --------------------------------------
    # 
    # -------------------------------------- 
    def dumpTable(self, table, fields=None, filterExpr=None):
        """
        Returns a list of dictionaries, each item in list(each dictionary)
        represents a row of the table
        """
        curs = None
        row_factory = None
        try:
            fields = '*' if fields is None else fields
            filterExpr = '' if not filterExpr else "WHERE {}".format( filterExpr )
            row_factory = self.connection.row_factory
            self.connection.row_factory = sqlite.Row # pylint: disable=maybe-no-member
            curs = self._get_cursor()
            curs.execute( "select {1} from {0} {2}".format( table, fields, filterExpr ) )
            return [dict(row) for row in curs.fetchall()]
        except Exception as e:
            raise e
        finally:
            self.connection.row_factory = row_factory
            if curs is not None:
                curs.close()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def forcePolygonCW(self, table):
        """
        Force (Multi)Polygons to use a clockwise orientation for their exterior ring, 
        and a counter-clockwise orientation for their interior rings.
        """
        # check if SpatiaLite db
        if not self.has_geometry_columns:
            return True
        
        # get geometry column name
        sql = "SELECT f_geometry_column FROM geometry_columns WHERE upper(f_table_name) = upper({0})".format( self.quoteString( table ) )
        curs = self._execute( None, sql )
        ret = curs.fetchone()
        if ret is None:
            return False
            
        geomField = ret[0]
        
        # force rings orientation
        sql = "UPDATE {0} SET {1} = ST_ForceLHR( {1} )".format( self.quoteString( table ), geomField )
        self._execute( None, sql )
        self._commit()
        return True
        
    # --------------------------------------
    # 
    # --------------------------------------             
    def importGeoJsonFromFile(self, table, geoJsonFile, layerOptions=None, layerSubsetString=None, createSchema=True):
        """
        Load a GeoJSON layer from file 
        """
        tmpLayer = None
        try:
            # init
            layerOptions = layerOptions or ["LAUNDER=NO","GEOMETRY_NAME=geometry"]
           
            # import temporary geojson layer    
            tmpLayer = QgsVectorLayer( geoJsonFile, table, "ogr" )
            
            # apply filter
            if layerSubsetString:
                tmpLayer.setSubsetString( layerSubsetString )
            
            # check crs
            crs = tmpLayer.crs()
            if not crs.isValid():
                crs = QgsCoordinateReferenceSystem.fromEpsgId( 4326 )
                
            # import layer
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = 'SpatiaLite'
            ####options.fileEncoding = 'utf-8'
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer if createSchema \
                                                else QgsVectorFileWriter.AppendToLayerNoNewFields 
            options.layerName = table
            options.forceMulti = True
            ###options.overrideGeometryType = QgsWkbTypes.Polygon
            options.layerOptions = layerOptions
             
            
            error, error_string = QgsVectorFileWriter.writeAsVectorFormat( tmpLayer, self.dbname, options )
            if error != QgsVectorFileWriter.NoError:
                raise Exception( error_string )
            
            # force rings orientation
            self.forcePolygonCW( table )
            
            # update table statistics
            if not createSchema:
                self.updateTableStatistics( table )
        
        except Exception as e:
            raise e
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def importGeoJsonFromData(self, table, data, layerOptions=None, layerSubsetString=None, createSchema=True):
        """
        Load a GeoJSON layer from data 
        """
        import json
        
        try:
            layerOptions = None ### FORCE NO LAYER OPTION (FOR NOW)
            
            # write json to temp file
            tmpFilePath = None
            with tempfile.NamedTemporaryFile( mode='w', delete=False ) as tmp:
                tmpFilePath = tmp.name
                # write json data to temp file 
                json.dump( data, tmp )
                
            self.importGeoJsonFromFile( table, tmpFilePath, layerOptions=layerOptions, layerSubsetString=layerSubsetString, createSchema=createSchema )
            
        finally:
            # remove temp file (without exception)
            if tmpFilePath is not None:
                fileUtil.scheduleRemoveFile( tmpFilePath, lambda f: fileUtil.removeFile( f, noException=True ), 1000 )
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def _filterSubData(self, table: str, dict_sub_data: dict, sub_fields: list) -> dict:
        # check if valid requested fields list
        if not sub_fields:
            return dict_sub_data
        
        # loop all filter fields
        res_dict = {}
        for fld_def in sub_fields:
            # get attribute name 
            fld_key = fld_def.get('name')
            if not fld_key:
                continue
            
            # get attribute value
            fld_value = dict_sub_data.get( fld_key, None )
            
            # get type of destination field
            fld_type = fld_def.get( 'type', None )
            
            # check if attribute value is valid for destination field
            if fld_type is None:
                # no field type defined
                pass
            elif fld_type == 'REAL' and objUtil.is_float(fld_value):
                # valid REAL\FLOAT value
                pass
            else:
                # not valid value: warns and skip
                if __PLG_DEBUG__:
                    logger.log( logger.Level.Warning, 
                                f"{table} - Attributo '{fld_key}' non valido: {fld_value}" )
                continue
            
            # store attribute value
            res_dict[fld_key] = fld_value
            
        # return filtered dictionary
        return res_dict if res_dict else dict_sub_data
        
    
    # --------------------------------------
    # 
    # --------------------------------------     
    def importGeoJsonSubData(self, 
                             table: str, 
                             sub_data_field: str, 
                             copy_layer_attribs: list,
                             sub_fields: dict, 
                             data: dict) -> bool:
        """
        Load a GeoJSON sub layer from data 
        """
        import json
        from qgis.core import QgsJsonUtils
        
        try:
            # init
            sub_data = []
            json_data = json.dumps(data)
            
            # prepare requested sub fields list
            sub_fields = sub_fields or []
            
            
            # parse GeoJSON for fields
            fields = QgsJsonUtils.stringToFields( json_data, None )
            if fields.count() == 0:
                return False 

            # parser GeoJSON as string
            feats = QgsJsonUtils.stringToFeatureList( str(json_data).replace("[]", "null"), fields, None )
            # if there are features in the list
            if len(feats) == 0:
                return False
            
            # read feature attributes
            for feat in feats:
                feat_data = {}
                
                # loop feature attributes
                fields = feat.fields()
                for attrib in copy_layer_attribs:
                    # check if attribute exists
                    attrib_name = attrib.get( 'name', '' )
                    attrib_rename = attrib.get( 'rename', attrib_name )
                    index = fields.indexFromName( attrib_name )
                    if index == -1:
                        continue
                    # store attibute value
                    feat_data[attrib_rename] = feat.attribute( index )
                    
                # extract sub data
                index = fields.indexFromName( sub_data_field )
                if index == -1:
                    continue
                
                # dump sub data
                val = feat.attribute( index )
                try:
                    lst_sub_data = json.loads( str(val) )
                except json.JSONDecodeError:
                    continue

                # check if dictionary
                if isinstance( lst_sub_data, dict ):
                    # assign as list of dictionary sum
                    lst_sub_data = [ lst_sub_data ]
                
                # check if list
                if not isinstance( lst_sub_data, list ):
                    continue
                        
                # store sub data
                for dict_sub_data in lst_sub_data:
                    # check if dictionary
                    if not isinstance( dict_sub_data, dict ):
                        continue
                    
                    # filter for requested attributes\fields
                    dict_sub_data = self._filterSubData( table, dict_sub_data, sub_fields )
                    
                    # sum feature data with sub data
                    dict_sub_data = {**feat_data, **dict_sub_data}
                    if dict_sub_data:
                        # collect sub data
                        sub_data.append( dict_sub_data )
               
            # check if read any data
            if not sub_data:
                return False
            
            # import normal table
            self.importTable( table, sub_data, dropTable=False )
            
            return True
            
        finally:
            pass
        