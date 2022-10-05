package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

import org.locationtech.jts.geom.Geometry;

public class ParticellaLavorataDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -133917744481678108L;

  private Long              idEventoLavorazione;
  private Long              idParticellaLavorazione;
  private Long              idFeature;
  private Long              ogcFid;
  private Long              ogcLayerID;
  private String codiceNazionale;
  private String foglio;
  private String numeroParticella;
  private String subalterno;
  private Long flagSospensione;
  private String descrizioneSospensione;
  private String flagConduzione;
  private String noteLavorazione;
  private Geometry          geometry;
  private Double  area;
  
  
  
  
  public Long getOgcLayerID()
  {
    return ogcLayerID;
  }
  public void setOgcLayerID(Long ogcLayerID)
  {
    this.ogcLayerID = ogcLayerID;
  }
  public Long getOgcFid()
  {
    return ogcFid;
  }
  public void setOgcFid(Long ogcFid)
  {
    this.ogcFid = ogcFid;
  }
  public Long getIdParticellaLavorazione()
  {
    return idParticellaLavorazione;
  }
  public void setIdParticellaLavorazione(Long idParticellaLavorazione)
  {
    this.idParticellaLavorazione = idParticellaLavorazione;
  }
  public String getFlagConduzione()
  {
    return flagConduzione;
  }
  public void setFlagConduzione(String flagConduzione)
  {
    this.flagConduzione = flagConduzione;
  }
  public Double getArea()
  {
    return area;
  }
  public void setArea(Double area)
  {
    this.area = area;
  }
  public Geometry getGeometry()
  {
    return geometry;
  }
  public void setGeometry(Geometry geometry)
  {
    this.geometry = geometry;
  }
  public String getCodiceNazionale()
  {
    return codiceNazionale;
  }
  public void setCodiceNazionale(String codiceNazionale)
  {
    this.codiceNazionale = codiceNazionale;
  }
  public String getFoglio()
  {
    return foglio;
  }
  public void setFoglio(String foglio)
  {
    this.foglio = foglio;
  }
  public String getNumeroParticella()
  {
    return numeroParticella;
  }
  public void setNumeroParticella(String numeroParticella)
  {
    this.numeroParticella = numeroParticella;
  }
  public String getSubalterno()
  {
    return subalterno;
  }
  public void setSubalterno(String subalterno)
  {
    this.subalterno = subalterno;
  }
  public Long getFlagSospensione()
  {
    return flagSospensione;
  }
  public void setFlagSospensione(Long flagSospensione)
  {
    this.flagSospensione = flagSospensione;
  }
  public String getDescrizioneSospensione()
  {
    return descrizioneSospensione;
  }
  public void setDescrizioneSospensione(String descrizioneSospensione)
  {
    this.descrizioneSospensione = descrizioneSospensione;
  }
  public String getNoteLavorazione()
  {
    return noteLavorazione;
  }
  public void setNoteLavorazione(String noteLavorazione)
  {
    this.noteLavorazione = noteLavorazione;
  }
  public Long getIdEventoLavorazione()
  {
    return idEventoLavorazione;
  }
  public void setIdEventoLavorazione(Long idEventoLavorazione)
  {
    this.idEventoLavorazione = idEventoLavorazione;
  }
  public Long getIdFeature()
  {
    return idFeature;
  }
  public void setIdFeature(Long idFeature)
  {
    this.idFeature = idFeature;
  }
  
  

}
