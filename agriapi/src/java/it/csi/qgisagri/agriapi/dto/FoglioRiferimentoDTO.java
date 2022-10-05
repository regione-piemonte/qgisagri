package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;
import java.util.Date;

import it.csi.qgisagri.agriapi.util.GraficoUtils;

public class FoglioRiferimentoDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -2959924007522361802L;

  private Long idFoglioRiferimento;
  private Long idGeoFoglio;
  private String codComBelfiore;
  private String codComIstat;
  private String comune;
  private String sezione;
  private String allegato;
  private String sviluppo;
  private Date aggiornatoAl;
  private String stato;
  private String codComIstatBdtre;
  private String geometriaWkt;
  private String srid;
  
  
  public String getSrid()
  {
    return srid;
  }
  public void setSrid(String srid)
  {
    this.srid = srid;
  }
  public Long getIdFoglioRiferimento()
  {
    return idFoglioRiferimento;
  }
  public Long getIdGeoFoglio()
  {
    return idGeoFoglio;
  }
  public String getCodComBelfiore()
  {
    return codComBelfiore;
  }
  public String getCodComIstat()
  {
    return codComIstat;
  }
  public String getComune()
  {
    return comune;
  }
  public String getSezione()
  {
    return sezione;
  }
  public String getAllegato()
  {
    return allegato;
  }
  public String getSviluppo()
  {
    return sviluppo;
  }
  public String getAggiornatoAl()
  {
    return GraficoUtils.DATE.formatDate(aggiornatoAl);
  }
  public String getStato()
  {
    return stato;
  }
  public String getCodComIstatBdtre()
  {
    return codComIstatBdtre;
  }
  public void setIdFoglioRiferimento(Long idFoglioRiferimento)
  {
    this.idFoglioRiferimento = idFoglioRiferimento;
  }
  public void setIdGeoFoglio(Long idGeoFoglio)
  {
    this.idGeoFoglio = idGeoFoglio;
  }
  public void setCodComBelfiore(String codComBelfiore)
  {
    this.codComBelfiore = codComBelfiore;
  }
  public void setCodComIstat(String codComIstat)
  {
    this.codComIstat = codComIstat;
  }
  public void setComune(String comune)
  {
    this.comune = comune;
  }
  public void setSezione(String sezione)
  {
    this.sezione = sezione;
  }
  public void setAllegato(String allegato)
  {
    this.allegato = allegato;
  }
  public void setSviluppo(String sviluppo)
  {
    this.sviluppo = sviluppo;
  }
  public void setAggiornatoAl(Date aggiornatoAl)
  {
    this.aggiornatoAl = aggiornatoAl;
  }
  public void setStato(String stato)
  {
    this.stato = stato;
  }
  public void setCodComIstatBdtre(String codComIstatBdtre)
  {
    this.codComIstatBdtre = codComIstatBdtre;
  }
  public String getGeometriaWkt()
  {
    return geometriaWkt;
  }
  public void setGeometriaWkt(String geometriaWkt)
  {
    this.geometriaWkt = geometriaWkt;
  }

}
