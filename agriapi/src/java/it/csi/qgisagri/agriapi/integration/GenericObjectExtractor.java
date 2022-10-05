package it.csi.qgisagri.agriapi.integration;

import java.sql.ResultSet;
import java.sql.SQLException;

import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.ResultSetExtractor;

public class GenericObjectExtractor<T> implements ResultSetExtractor<T>
{

  protected GenericDatabaseObjectReader<T> reader;

  public GenericObjectExtractor(Class<T> objClass)
  {
    reader = new GenericDatabaseObjectReader<T>(objClass);
  }

  @Override
  public T extractData(ResultSet rs) throws SQLException, DataAccessException
  {
    return reader.extractObject(rs);
  }
}
