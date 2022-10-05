'''
Created on 7 ago 2019

@author: 
'''
from qgis.core import QgsDataSourceUri
from .db_database import DbError

class DBConnector(object):

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __init__(self, uri):
        self.connection = None
        self._uri = uri

    # --------------------------------------
    # 
    # -------------------------------------- 
    def __del__(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = None

    # --------------------------------------
    # 
    # -------------------------------------- 
    def uri(self):
        return QgsDataSourceUri(self._uri.uri(False))

    # --------------------------------------
    # 
    # -------------------------------------- 
    def cancel(self):
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def close(self):
        pass
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def providerName(self):
        pass

    # --------------------------------------
    # 
    # -------------------------------------- 
    def publicUri(self):
        publicUri = QgsDataSourceUri.removePassword(self._uri.uri(False))
        return QgsDataSourceUri(publicUri)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasSpatialSupport(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def canAddGeometryColumn(self, table):
        return self.hasSpatialSupport()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def canAddSpatialIndex(self, table):
        return self.hasSpatialSupport()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasRasterSupport(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasCustomQuerySupport(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasTableColumnEditingSupport(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def hasCreateSpatialViewSupport(self):
        return False

    # --------------------------------------
    # 
    # -------------------------------------- 
    def execution_error_types(self):
        raise Exception("DBConnector.execution_error_types() is an abstract method")

    # --------------------------------------
    # 
    # -------------------------------------- 
    def connection_error_types(self):
        raise Exception("DBConnector.connection_error_types() is an abstract method")

    # --------------------------------------
    # 
    # -------------------------------------- 
    def error_types(self):
        return self.connection_error_types() + self.execution_error_types()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _execute(self, cursor, sql, *args):
        if cursor is None:
            cursor = self._get_cursor()
        try:
            cursor.execute(sql, *args)

        except self.connection_error_types() as e:
            raise ConnectionError(e)

        except self.execution_error_types() as e:
            # do the rollback to avoid a "current transaction aborted, commands ignored" errors
            self._rollback()
            raise DbError(e, sql)

        return cursor

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _execute_and_commit(self, sql):
        """ tries to execute and commit some action, on error it rolls back the change """
        self._execute(None, sql)
        self._commit()

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _get_cursor(self, name=None):
        try:
            if name is not None:
                name = str(name).encode('ascii', 'replace').replace('?', "_")
                self._last_cursor_named_id = 0 if not hasattr(self, '_last_cursor_named_id') else self._last_cursor_named_id + 1
                return self.connection.cursor("%s_%d" % (name, self._last_cursor_named_id))

            return self.connection.cursor()

        except self.connection_error_types() as e:
            raise ConnectionError(e)

        except self.execution_error_types() as e:
            # do the rollback to avoid a "current transaction aborted, commands ignored" errors
            self._rollback()
            raise DbError(e)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _close_cursor(self, c):
        try:
            if c and not c.closed:
                c.close()

        except self.error_types():
            pass

        return

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _fetchall(self, c):
        try:
            return c.fetchall()

        except self.connection_error_types() as e:
            raise ConnectionError(e)

        except self.execution_error_types() as e:
            # do the rollback to avoid a "current transaction aborted, commands ignored" errors
            self._rollback()
            raise DbError(e)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _fetchone(self, c):
        try:
            return c.fetchone()

        except self.connection_error_types() as e:
            raise ConnectionError(e)

        except self.execution_error_types() as e:
            # do the rollback to avoid a "current transaction aborted, commands ignored" errors
            self._rollback()
            raise DbError(e)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _commit(self):
        try:
            self.connection.commit()

        except self.connection_error_types() as e:
            raise ConnectionError(e)

        except self.execution_error_types() as e:
            # do the rollback to avoid a "current transaction aborted, commands ignored" errors
            self._rollback()
            raise DbError(e)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _rollback(self):
        try:
            self.connection.rollback()

        except self.connection_error_types() as e:
            raise ConnectionError(e)

        except self.execution_error_types() as e:
            raise DbError(e)

    # --------------------------------------
    # 
    # -------------------------------------- 
    def _get_cursor_columns(self, c):
        try:
            if c.description:
                return [x[0] for x in c.description]

        except (self.connection_error_types(), self.execution_error_types()):
            return []

    # --------------------------------------
    # 
    # -------------------------------------- 
    @classmethod
    def quoteId(self, identifier):
        if hasattr(identifier, '__iter__') and not isinstance(identifier, str):
            ids = list()
            for i in identifier:
                if i is None or i == "":
                    continue
                ids.append(self.quoteId(i))
            return u'.'.join(ids)

        identifier = str(
            identifier) if identifier is not None else str()  # make sure it's python unicode string
        return u'"%s"' % identifier.replace('"', '""')

    # --------------------------------------
    # 
    # -------------------------------------- 
    @classmethod
    def quoteString(self, txt):
        """ make the string safe - replace ' with '' """
        if hasattr(txt, '__iter__') and not isinstance(txt, str):
            txts = list()
            for i in txt:
                if i is None:
                    continue
                txts.append(self.quoteString(i))
            return u'.'.join(txts)

        txt = str(txt) if txt is not None else str()  # make sure it's python unicode string
        return u"'%s'" % txt.replace("'", "''")

    # --------------------------------------
    # 
    # -------------------------------------- 
    @classmethod
    def getSchemaTableName(self, table):
        if not hasattr(table, '__iter__') and not isinstance(table, str):
            return (None, table)
        if isinstance(table, str):
            table = table.split('.')
        if len(table) < 2:
            return (None, table[0])
        else:
            return (table[0], table[1])

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getComment(self, tablename, field):
        """Returns the comment for a field"""
        return ''

    # --------------------------------------
    # 
    # -------------------------------------- 
    def commentTable(self, schema, tablename, comment=None):
        """Comment the table"""
        pass

    # --------------------------------------
    # 
    # -------------------------------------- 
    def getQueryBuilderDictionary(self):

        return {}
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def executeSingle(self, sql, *args):
        """ tries to execute and commit some action, on error it rolls back the change """
        cur = None
        try:
            cur = self._get_cursor()
            self._execute( cur, sql, *args )
            return cur.fetchone()[0]
            
        finally:
            if cur is not None:
                cur.close()
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def executeAndCommit(self, sql):
        """ tries to execute and commit some action, on error it rolls back the change """
        self._execute_and_commit( sql )
    
    # --------------------------------------
    # 
    # -------------------------------------- 
    def executeScript(self, sql=None, sqlFile=None):
        """Execute a script file"""
        pass
    