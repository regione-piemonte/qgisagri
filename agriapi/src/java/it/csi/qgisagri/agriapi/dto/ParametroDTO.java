package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

import org.codehaus.jackson.annotate.JsonIgnore;

import it.csi.qgisagri.agriapi.util.GraficoUtils;

public class ParametroDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -3853973259900506764L;
  private long idParametroPlugin;
  private String codice;
  private String descrizione;
  private String tipo;
  private String valoreStringa;
  private BigDecimal valoreNumerico;
  private Date valoreData;
  
  @JsonIgnore
  public long getIdParametroPlugin()
  {
    return idParametroPlugin;
  }
  public String getCodice()
  {
    return codice;
  }
  public String getDescrizione()
  {
    return descrizione;
  }
  public String getTipo()
  {
    return tipo;
  }
  public String getValoreStringa()
  {
    return valoreStringa;
  }
  public BigDecimal getValoreNumerico()
  {
    return valoreNumerico;
  }
  public String getValoreData()
  {
    return GraficoUtils.DATE.formatDate(valoreData);
  }
  public void setIdParametroPlugin(long idParametroPlugin)
  {
    this.idParametroPlugin = idParametroPlugin;
  }
  public void setCodice(String codice)
  {
    this.codice = codice;
  }
  public void setDescrizione(String descrizione)
  {
    this.descrizione = descrizione;
  }
  public void setTipo(String tipo)
  {
    this.tipo = tipo;
  }
  public void setValoreStringa(String valoreStringa)
  {
    this.valoreStringa = valoreStringa;
  }
  public void setValoreNumerico(BigDecimal valoreNumerico)
  {
    this.valoreNumerico = valoreNumerico;
  }
  public void setValoreData(Date valoreData)
  {
    this.valoreData = valoreData;
  }
  
}
