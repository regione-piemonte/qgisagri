package it.csi.qgisagri.agriapi.integration;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.ResultSetExtractor;

public class GenericListEstractor<T> implements ResultSetExtractor<List<T>>
{
  protected GenericDatabaseObjectReader<T> reader;
  public GenericListEstractor(Class<T> objClass)
  {
    reader=new GenericDatabaseObjectReader<T>(objClass);
  }

  @Override
  public List<T> extractData(ResultSet rs) throws SQLException, DataAccessException
  {
    return reader.extractList(rs);
  }
}
