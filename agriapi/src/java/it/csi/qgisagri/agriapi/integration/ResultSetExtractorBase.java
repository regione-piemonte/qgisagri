package it.csi.qgisagri.agriapi.integration;

import java.math.BigDecimal;
import java.sql.SQLException;
import java.util.Date;

import it.csi.qgisagri.agriapi.util.GraficoUtils;
import oracle.sql.Datum;

public abstract class ResultSetExtractorBase
{
  public static String gestisciCampo(Object valore) throws SQLException
  {

    String ret = null;

    try
    {
      if (valore != null)
        ret = ((Datum) valore).stringValue();

    }
    catch (SQLException e)
    {
      throw e;
    }

    return ret;
  }
  
  public static Integer gestisciCampoInteger(Object valore)
      throws SQLException
  {

    BigDecimal ret = null;

    try
    {
      if (valore != null)
        ret = ((Datum) valore).bigDecimalValue();
      if (ret != null)
      {
        return ret.intValueExact();
      }

    }
    catch (SQLException e)
    {
      throw e;
    }
    return null;
  }
  
  public static Long gestisciCampoLong(Object valore) throws SQLException
  {

    BigDecimal ret = null;

    try
    {
      if (valore != null)
        ret = ((Datum) valore).bigDecimalValue();
      if (ret != null)
      {
        return ret.longValueExact();
      }

    }
    catch (SQLException e)
    {
      throw e;
    }
    return null;
  }
  
  public static Date gestisciCampoData(Object valore) throws SQLException
  {

    Date ret = null;

    try
    {
      if (valore != null)
        ret = ((Datum) valore).timestampValue();
      return ret;
    }
    catch (SQLException e)
    {
      throw e;
    }
  }
  
  public static String gestisciCampoDataAsString(Object valore) throws SQLException
  {

    String ret = null;

    try
    {
      if (valore != null)
        ret = GraficoUtils.DATE.formatDate(((Datum) valore).dateValue());
      return ret;
    }
    catch (SQLException e)
    {
      throw e;
    }
  }
  
  public static String gestisciCampoTimestampAsString(Object valore) throws SQLException
  {
    
    String ret = null;
    
    try
    {
      if (valore != null)
        ret = GraficoUtils.DATE.formatDateTime(((Datum) valore).dateValue());
      return ret;
    }
    catch (SQLException e)
    {
      throw e;
    }
  }
  
  
  public static Date gestisciCampoTimestamp(Object valore) throws SQLException
  {
    
    Date ret = null;
    
    try
    {
      if (valore != null)
        ret = ((Datum) valore).dateValue();
      return ret;
    }
    catch (SQLException e)
    {
      throw e;
    }
  }
  
  public static BigDecimal gestisciCampoBigDecimal(Object valore)
      throws SQLException
  {

    BigDecimal ret = null;

    try
    {
      if (valore != null)
        ret = ((Datum) valore).bigDecimalValue();
      if (ret != null)
      {
        return ret;
      }

    }
    catch (SQLException e)
    {
      throw e;
    }
    return null;
  }
  
  
  public static Long getLong(String valore)
  {
    Long l=null;
    if(valore != null && !valore.trim().equals(""))
    {
      l = Long.valueOf(valore);
    }
    return l;
  }
  
  public static Integer getInteger(String valore)
  {
    Integer l=null;
    if(valore != null && !valore.trim().equals(""))
    {
      l = Integer.valueOf(valore);
    }
    return l;
  }
  
  public static String getDateAsString(Date valore) throws SQLException
  {
    if(valore != null)
    {
      return GraficoUtils.DATE.formatDate(valore);
    }
    else
    {
      return null;
    }
  }
  
  public static String getDateToString(Date valore) throws SQLException
  {
    if(valore != null)
    {
      return valore.toString();
    }
    else
    {
      return null;
    }
  }
}


