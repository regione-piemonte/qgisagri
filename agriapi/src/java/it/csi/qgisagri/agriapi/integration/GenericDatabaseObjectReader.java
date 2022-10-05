package it.csi.qgisagri.agriapi.integration;

import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.sql.Blob;
import java.sql.Clob;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.dao.DataAccessException;
import org.springframework.dao.DataRetrievalFailureException;

class GenericDatabaseObjectReader<T>
{

  protected Class<T>                                      objClass;
  protected Map<String, Method>                           mapSetters;
  protected static final Map<String, Map<String, Method>> OBJECTS_CACHEMAP = new HashMap<String, Map<String, Method>>();

  public GenericDatabaseObjectReader(Class<T> objClass)
  {
    this.objClass = objClass;
    mapSetters = OBJECTS_CACHEMAP.get(objClass.getName());
    if (mapSetters == null)
    {
      loadSetters();
    }
  }

  protected synchronized void loadSetters()
  {
    Method methods[] = objClass.getMethods();
    mapSetters = new HashMap<String, Method>();
    for (Method method : methods)
    {
      String name = method.getName();
      if (name.startsWith("set") && method.getParameterTypes().length == 1)
      {
        mapSetters.put(name, method);
      }
    }
    OBJECTS_CACHEMAP.put(objClass.getName(), mapSetters);
  }

  public T extractObject(ResultSet rs) throws SQLException, DataAccessException
  {
    if (rs.next())
    {
      return readObject(rs);
    }
    else
    {
      return null;
    }
  }

  public List<T> extractList(ResultSet rs)
      throws SQLException, DataAccessException
  {
    List<T> list = new ArrayList<T>();
    while (rs.next())
    {
      list.add(readObject(rs));
    }
    return list.isEmpty() ? null : list;
  }

  protected T readObject(ResultSet rs)
  {
    T obj;
    try
    {
      obj = objClass.newInstance();
      ResultSetMetaData metaData = rs.getMetaData();
      int size = metaData.getColumnCount() + 1;
      for (int i = 1; i < size; ++i)
      {
        readField(obj, i, metaData, rs);
      }
    }
    catch (Exception e)
    {
      e.printStackTrace();
      throw new DataRetrievalFailureException("Reflection error", e);
    }
    return obj;
  }

  protected void readField(T obj, int idx, ResultSetMetaData metaData,
      ResultSet rs) throws SQLException
  {
    String setter = "set" + sql2Java(metaData.getColumnName(idx));
    try
    {
      Method m = mapSetters.get(setter);

      if (m != null)
      {
        Class<?> paramType = m.getParameterTypes()[0];
        Object paramValue = null;
        if (String.class == paramType)
        {
          paramValue = rs.getString(idx);
        }
        else
        {
          if (Long.class == paramType)
          {
            paramValue = readLong(rs, idx);
          }
          else
          {
            if (long.class == paramType)
            {
              paramValue = rs.getLong(idx);
            }
            else
            {
              if (BigDecimal.class == paramType)
              {
                paramValue = rs.getBigDecimal(idx);
              }
              else
              {
                if (Date.class == paramType || Timestamp.class == paramType)
                {
                  paramValue = rs.getTimestamp(idx);
                }
                else
                {
                  if (Integer.class == paramType)
                  {
                    paramValue = readInteger(rs, idx);
                  }
                  else
                  {
                    if (int.class == paramType)
                    {
                      paramValue = rs.getInt(idx);
                    }
                    else
                    {
                      if (Double.class == paramType)
                      {
                        paramValue = readDouble(rs, idx);
                      }
                      else
                      {
                        if (double.class == paramType)
                        {
                          paramValue = rs.getDouble(idx);
                        }
                        else
                        {
                          if (Float.class == paramType)
                          {
                            paramValue = readFloat(rs, idx);
                          }
                          else
                          {
                            if (float.class == paramType)
                            {
                              paramValue = rs.getFloat(idx);
                            }
                            else
                            {
                              if (Blob.class == paramType
                                  || byte.class == paramType
                                  || byte[].class == paramType)
                              {
                                paramValue = rs.getBytes(idx);
                              }
                              else
                              {
                                if (Clob.class == paramType)
                                {
                                  paramValue = rs.getClob(idx);
                                }
                                else
                                {
                                  if (Object.class == paramType)
                                  {
                                    paramValue = rs.getObject(idx);
                                  }
                                  else
                                  {
                                    if (boolean.class == paramType)
                                    {
                                      paramValue = rs.getBoolean(idx);
                                    }
                                    else
                                    {
                                      if (Boolean.class == paramType)
                                      {
                                        paramValue = readBoolean(rs, idx);
                                      }
                                      else
                                      {
                                        throw new DataRetrievalFailureException(
                                            "Invalid parameter type");
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        m.invoke(obj, paramValue);
      }
    }
    catch (Exception e)
    {
      e.printStackTrace();
    }
  }

  protected String sql2Java(String sqlIdentifier)
  {
    return sql2Java(sqlIdentifier, true);
  }

  protected String sql2Java(String sqlIdentifier, boolean isClass)
  {
    StringBuilder sb = new StringBuilder(sqlIdentifier.toLowerCase());
    int pos = sb.indexOf("_");
    while (pos >= 0)
    {
      sb.replace(pos, pos + 1, "");
      sb.replace(pos, pos + 1, String.valueOf(sb.charAt(pos)).toUpperCase());
      pos = sb.indexOf("_");
    }
    if (isClass && sb.length() > 0)
    {
      sb.replace(0, 1, String.valueOf(sb.charAt(0)).toUpperCase());
    }
    return sb.toString();
  }

  protected Long readLong(ResultSet rs, int idx) throws SQLException
  {
    String value = rs.getString(idx);
    if (value == null)
    {
      return null;
    }
    return new Long(value);
  }

  protected Integer readInteger(ResultSet rs, int idx) throws SQLException
  {
    String value = rs.getString(idx);
    if (value == null)
    {
      return null;
    }
    return new Integer(value);
  }

  protected Float readFloat(ResultSet rs, int idx) throws SQLException
  {
    String value = rs.getString(idx);
    if (value == null)
    {
      return null;
    }
    return new Float(value);
  }

  protected Boolean readBoolean(ResultSet rs, int idx) throws SQLException
  {
    String value = rs.getString(idx);
    if (value == null)
    {
      return null;
    }
    return rs.getBoolean(idx);
  }

  protected Double readDouble(ResultSet rs, int idx) throws SQLException
  {
    String value = rs.getString(idx);
    if (value == null)
    {
      return null;
    }
    return new Double(value);
  }

}