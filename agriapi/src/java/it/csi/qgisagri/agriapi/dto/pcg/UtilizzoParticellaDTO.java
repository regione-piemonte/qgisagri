package it.csi.qgisagri.agriapi.dto.pcg;

import java.io.Serializable;
import java.math.BigDecimal;

public class UtilizzoParticellaDTO implements Serializable
{
	/**
   * 
   */
  private static final long serialVersionUID = -8760574291404161953L;
  private BigDecimal superficie;
  private String utilizzo;
  private String destinazione;
  private String dettaglioUso;
  private String qualita;
  private String varieta;
  public BigDecimal getSuperficie()
  {
    return superficie;
  }
  public String getUtilizzo()
  {
    return utilizzo;
  }
  public String getDestinazione()
  {
    return destinazione;
  }
  public String getDettaglioUso()
  {
    return dettaglioUso;
  }
  public String getQualita()
  {
    return qualita;
  }
  public String getVarieta()
  {
    return varieta;
  }
  public void setSuperficie(BigDecimal superficie)
  {
    this.superficie = superficie;
  }
  public void setUtilizzo(String utilizzo)
  {
    this.utilizzo = utilizzo;
  }
  public void setDestinazione(String destinazione)
  {
    this.destinazione = destinazione;
  }
  public void setDettaglioUso(String dettaglioUso)
  {
    this.dettaglioUso = dettaglioUso;
  }
  public void setQualita(String qualita)
  {
    this.qualita = qualita;
  }
  public void setVarieta(String varieta)
  {
    this.varieta = varieta;
  }

}