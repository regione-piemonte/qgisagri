package it.csi.qgisagri.agriapi.util;

import java.math.BigDecimal;
import java.text.DecimalFormat;

/**
 * Classe astratta per le funzioni di utilità sulle stringhe. La classe è abstract perchè non deve essere usata direttamente ma solo dalla sua implementazione
 * nella costante Utils.STRING
 * 
 * @author Stefano Einaudi (Matr. 70399)
 * 
 */
public abstract class FormatUtils
{
  public static final DecimalFormat FORMAT_4 = new DecimalFormat("###,##0.0000");
  public static final DecimalFormat FORMAT_2 = new DecimalFormat("###,##0.00");

  public String formatGenericNumber(BigDecimal number, int numDecimali, boolean decimaliObbligatori)
  {
    return formatGenericNumber(number, numDecimali, decimaliObbligatori, true);
  }
  
  public String formatGenericNumber(BigDecimal number, int numDecimali, boolean decimaliObbligatori, boolean separatoreMigliaia)
  {
    try
    {
      StringBuilder formatBuilder = new StringBuilder(separatoreMigliaia?"#,##0":"0");
      if (numDecimali > 0)
      {
        formatBuilder.append(".");
        char decimale = decimaliObbligatori ? '0' : '#';
        for (int i = 0; i < numDecimali; ++i)
        {
          formatBuilder.append(decimale);
        }
      }
      return new DecimalFormat(formatBuilder.toString()).format(number);
    }
    catch (Exception e)
    {
      return null;
    }
  }

  public String formatValue(DecimalFormat format, BigDecimal number)
  {
    try
    {
      if (number == null)
      {
        return "";
      }
      return format.format(number);
    }
    catch (Exception e)
    {
      return "";
    }
  }

  public String formatDecimal4(BigDecimal number)
  {
    return formatValue(FORMAT_4, number);
  }

  public String formatDecimal2(BigDecimal number)
  {
    return formatValue(FORMAT_2, number);
  }
  
  public String formatCurrency(BigDecimal number)
  {
    return formatValue(FORMAT_2, number);
  }
  
  public String preventNull(String str)
  {
    if (str == null || str.length() == 0)
    {
      return "";
    }

    return str.trim();
  }

  public String trim(String str)
  {
    if (str == null || str.length() == 0)
    {
      return str;
    }

    return str.trim();
  }

}