package it.csi.qgisagri.agriapi.integration;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import javax.sql.DataSource;

import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.ResultSetExtractor;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.core.namedparam.SqlParameterSource;

import it.csi.qgisagri.agriapi.util.AgriApiConstants;

public class BaseDAO
{
  NamedParameterJdbcTemplate namedParameterJdbcTemplate;
  protected static final Logger logger     = Logger.getLogger(AgriApiConstants.LOGGING.LOGGER_NAME + ".integration");
  protected final int                  PASSO      = 900;
  private static final String THIS_CLASS = BaseDAO.class.getSimpleName();
  
  
  @Autowired
  protected ApplicationContext         appContext;
  
  @Autowired
  public void setDataSource(DataSource dataSource)
  {
    this.namedParameterJdbcTemplate = new NamedParameterJdbcTemplate(dataSource);
    ((JdbcTemplate) this.namedParameterJdbcTemplate.getJdbcOperations()).setQueryTimeout(120); //120 secondi query timeout
  }

  protected <T> T queryForNullableObject(String query, MapSqlParameterSource mapSqlParameterSource, Class<T> clazz)
  {
    try
    {
      return namedParameterJdbcTemplate.queryForObject(query, mapSqlParameterSource, clazz);
    }
    catch (Exception e)
    {
      return null;
    }
  }

  public <T> T queryForObject(String query, SqlParameterSource parameters, Class<T> objClass, ResultSetExtractor<T> re)
  {
    return namedParameterJdbcTemplate.query(query, parameters, re);
  }

  public <T> T queryForObject(String query, SqlParameterSource parameters, Class<T> objClass)
  {
    ResultSetExtractor<T> re = new GenericObjectExtractor<T>(objClass);
    return namedParameterJdbcTemplate.query(query, parameters, re);
  }

  public String queryForString(String query, SqlParameterSource parameters, final String field)
  {
    return namedParameterJdbcTemplate.query(query, parameters, new ResultSetExtractor<String>()
    {
      @Override
      public String extractData(ResultSet rs) throws SQLException, DataAccessException
      {
        String sql = "";
        while (rs.next())
        {
          sql = rs.getString(field);
        }
        return sql;
      }
    });
  }
  
  public String queryForNullableString(String query, SqlParameterSource parameters)
  {
    return namedParameterJdbcTemplate.query(query, parameters, new ResultSetExtractor<String>()
    {
      @Override
      public String extractData(ResultSet rs) throws SQLException, DataAccessException
      {
        if (rs.next())
        {
          return rs.getString(1);
        }
        return null;
      }
    });
  }

  /**
   * Assicurarsi che i nomi dei campi del DTO siano UGUALI ai campi (o alias)
   * richiesti nella query ma in camel case senza spazi e punteggiatura,
   * <b>rispettando anche i tipi.</b> (es: "TIPO_RICHIESTA" sul db =>
   * "tipoRichiesta" sul dto)
   */
  public <T> List<T> queryForList(String query, SqlParameterSource parameters, Class<T> objClass)
  {
    ResultSetExtractor<List<T>> re = new GenericListEstractor<T>(objClass);
    return namedParameterJdbcTemplate.query(query, parameters, re);
  }
  
  
  public String getInCondition(String campo, List<?> vId, boolean andClause)
  {
    int cicli = vId.size() / PASSO;
    if (vId.size() % PASSO != 0)
      cicli++;

    StringBuffer condition = new StringBuffer(" ");
    
    if (andClause)
      condition.append(" AND ( ");
    
    for (int j = 0; j < cicli; j++)
    {
      if (j != 0)
      {
        condition.append(" OR ");
      }
      boolean primo = true;
      for (int i = j * PASSO; i < ((j + 1) * PASSO) && i < vId.size(); i++)
      {
        if (primo)
        {
          condition.append(" " + campo + " IN (" + getIdFromvId(vId, i));
          primo = false;
        }
        else
        {
          condition.append("," + getIdFromvId(vId, i));
        }
      }
      condition.append(")");
    }
    if (andClause)
      condition.append(")");
    
    return condition.toString();

  } 

  public String getInCondition(String campo, Vector<?> vId, boolean andClause)
  {
    int cicli = vId.size() / PASSO;
    if (vId.size() % PASSO != 0)
      cicli++;
    StringBuffer condition = new StringBuffer("  ");

    if (andClause)
      condition.append(" AND ( ");

    for (int j = 0; j < cicli; j++)
    {
      if (j != 0)
      {
        condition.append(" OR ");
      }
      boolean primo = true;
      for (int i = j * PASSO; i < ((j + 1) * PASSO) && i < vId.size(); i++)
      {
        if (primo)
        {
          condition.append(" " + campo + " IN (" + getIdFromvId(vId, i));
          primo = false;
        }
        else
        {
          condition.append("," + getIdFromvId(vId, i));
        }
      }
      condition.append(")");
    }

    if (andClause)
      condition.append(")");

    return condition.toString();

  }

  public String getNotInCondition(String campo, List<?> vId)
  {
    int cicli = vId.size() / PASSO;
    if (vId.size() % PASSO != 0)
      cicli++;

    StringBuffer condition = new StringBuffer(" AND ( ");
    for (int j = 0; j < cicli; j++)
    {
      if (j != 0)
      {
        condition.append(" OR ");
      }
      boolean primo = true;
      for (int i = j * PASSO; i < ((j + 1) * PASSO) && i < vId.size(); i++)
      {
        if (primo)
        {
          condition.append(" " + campo + " NOT IN (" + getIdFromvId(vId, i));
          primo = false;
        }
        else
        {
          condition.append("," + getIdFromvId(vId, i));
        }
      }
      condition.append(")");
    }
    condition.append(")");
    return condition.toString();
  }

  protected String getIdFromvId(List<?> vId, int idx)
  {

    Object o = vId.get(idx);

    if (o instanceof String)
    {
      return "'" + (String) o + "'";
    }
    else
      return o.toString();
  }

  @SuppressWarnings("deprecation")
  public long getNextSequenceValue(String sequenceName)
  {
    String query = " SELECT " + sequenceName + ".NEXTVAL FROM DUAL";
    return namedParameterJdbcTemplate.queryForLong(query, (SqlParameterSource) null);
  }
  
  
  public Map<String, String> getParametri(String[] paramNames) 
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getParametri]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }
    StringBuilder query = new StringBuilder();
    query.append(" SELECT CODICE, VALORE FROM QGIS_D_PARAMETRO P WHERE P.CODICE IN (");
    boolean needComma = false;
    try
    {
      int len = paramNames.length;
      MapSqlParameterSource params = new MapSqlParameterSource();
      for (int i = 0; i < len; ++i)
      {
        if (needComma)
        {
          query.append(",");
        }
        else
        {
          needComma = true;
        }
        String name = "PARAM_" + i;
        query.append(':').append(name);
        params.addValue(name, paramNames[i], Types.VARCHAR);
      }
      query.append(")");
      return namedParameterJdbcTemplate.query(query.toString(), params, new ResultSetExtractor<Map<String, String>>()
      {

        @Override
        public Map<String, String> extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          Map<String, String> map = new HashMap<String, String>();
          while (rs.next())
          {
            map.put(rs.getString("CODICE"), rs.getString("VALORE"));
          }
          return map;
        }
      });
    }
    catch (Throwable t)
    {
      throw t;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  protected String safeMessaggioPLSQL(String msg)
  {
    if (msg != null && msg.indexOf("ORA-") >= 0)
    {
      msg = "Si è verificato un errore di sistema";
    }
    return msg;
  }
}