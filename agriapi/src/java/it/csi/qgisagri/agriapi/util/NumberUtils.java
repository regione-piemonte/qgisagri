package it.csi.qgisagri.agriapi.util;

import java.math.BigDecimal;
import java.math.MathContext;

public abstract class NumberUtils
{

  /**
   * Somme e sottrazioni vengono arrotondate correttamente
   * 
   * @param numero
   * @param precisione
   * @return double
   */
  public double arrotonda(double numero, int precisione)
  {
    return new java.math.BigDecimal(numero).setScale(precisione, java.math.BigDecimal.ROUND_HALF_UP).doubleValue();
  }

  /**
   * Verifica se il valore è un numero
   * 
   * @param value
   * @return boolean
   */
  public boolean isNumericValue(String value)
  {
    boolean result = true;

    try
    {
      new Long(value);
    }
    catch (NumberFormatException ex)
    {
      result = false;
    }

    return result;
  }

  /**
   * Restituisce un numero oppure null se la stringa contiene caratteri alfanumerici
   * 
   * @param value
   * @return Long
   */
  public Long getNumericValue(String value)
  {
    Long result = null;

    try
    {
      result = new Long(value.trim());
    }
    catch (NumberFormatException ex)
    {
      // throw ex;
    }

    return result;
  }

  /**
   * Restituisce un numero oppure null se la stringa contiene caratteri alfanumerici
   * 
   * @param value
   * @return Long
   */
  public Integer getIntegerNull(String value)
  {
    Integer result = null;

    try
    {
      result = new Integer(value);
    }
    catch (NumberFormatException ex)
    {
      // throw ex;
    }

    return result;
  }

  public Double somma(Double totale, Double addendo, int precisione)
  {
    if (addendo == null)
      return totale;

    if (totale == null)
      totale = new Double(0);

    BigDecimal bdTotale = new BigDecimal(totale.doubleValue());
    BigDecimal bdAddendo = new BigDecimal(addendo.doubleValue());

    bdTotale = bdTotale.add(bdAddendo).setScale(precisione, BigDecimal.ROUND_HALF_UP);
    return new Double(bdTotale.doubleValue());
  }

  /**
   * Verifica che la stringa contenga un Long - Restituisce 0 non null
   * 
   * @param val
   * @return Long
   */
  public Long checkLong(String val)
  {
    try
    {
      return new Long(val.trim());
    }
    catch (Exception ex)
    {
      return new Long(0);
    }
  }

  /**
   * Verifica che la stringa contenga un Double
   * 
   * @param val
   * @return
   */
  public Double checkDouble(String val)
  {
    try
    {
      return new Double(val);
    }
    catch (Exception ex)
    {
      return new Double(0);
    }
  }

  public BigDecimal nvl(BigDecimal value)
  {
    return nvl(value, BigDecimal.ZERO);
  }
  
  public BigDecimal initNumberNvlZero(BigDecimal value, BigDecimal defVal)
  {
	if(value == null || value == BigDecimal.ZERO)
		return defVal;
	
    return nvl(value, BigDecimal.ZERO);
  }

  public BigDecimal nvl(BigDecimal value, BigDecimal defaultValue)
  {
    return value == null ? defaultValue : value;
  }
  
  public Double toDoubleAcceptNull(BigDecimal value)
  {
	  if(value != null)
	  {
		  return value.doubleValue();
	  }
	  else
	  {
		  return null;
	  }
  }
  
  public Double toDouble(BigDecimal value)
  {
	  return nvl(value).doubleValue();
  }

  public BigDecimal add(BigDecimal bd1, BigDecimal bd2)
  {
    return nvl(bd2).add(nvl(bd1), MathContext.DECIMAL128);
  }

  public BigDecimal subtract(BigDecimal bd1, BigDecimal bd2)
  {
    return nvl(bd1).subtract(nvl(bd2), MathContext.DECIMAL128);
  }

  public BigDecimal multiply(BigDecimal bd1, BigDecimal bd2)
  {
    return nvl(bd2).multiply(nvl(bd1), MathContext.DECIMAL128);
  }

  public long getValue(Long val)
  {
    return (val != null) ? val.longValue() : 0l;
  }
  
  public Long parseLongNull(String val)
  {
    try
    {
      return Long.parseLong(val.trim());
    }
    catch (Exception e)
    {
      return null;
    }
  }

  public BigDecimal getBigDecimal(String val)
  {
    try
    {
      return new BigDecimal(val.trim().replace(",", "."));
    }
    catch (Exception e)
    {
      return null;
    }
  }
  
  public BigDecimal getBigDecimal(long val)
  {
    try
    {
      return new BigDecimal(val);
    }
    catch (Exception e)
    {
      return null;
    }
  }
  
  public BigDecimal getBigDecimalNvl(String val)
  {
    try
    {
      return new BigDecimal(val.trim().replace(",", "."));
    }
    catch (Exception e)
    {
      return new BigDecimal(0);
    }
  }
  
  public BigDecimal getBigDecimalNvl(Long val)
  {
    try
    {
      return new BigDecimal(val);
    }
    catch (Exception e)
    {
    	return new BigDecimal(0);
    }
  }

  public int nvl(Integer value, int defaultValue)
  {
    return value == null ? defaultValue : value;
  }

  public Integer nvl(Integer value, Integer defaultValue)
  {
    return value == null ? defaultValue : value;
  }

  public long nvl(Long value, long defaultValue)
  {
    return value == null ? defaultValue : value;
  }

  public Long nvl(Long value, Long defaultValue)
  {
    return value == null ? defaultValue : value;
  }
  
  @SuppressWarnings({ "rawtypes", "unchecked" })
  public <T extends Comparable> T min(T v1, T v2)
  {
    if (v1==v2)
    {
      return v1;
    }
    return v1.compareTo(v2)<0?v1:v2;
  }
  
  @SuppressWarnings({ "rawtypes", "unchecked" })
  public <T extends Comparable> T max(T v1, T v2)
  {
    if (v1==v2)
    {
      return v1;
    }
    return v1.compareTo(v2)>0?v1:v2;
  }
  
}