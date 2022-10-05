package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

import org.codehaus.jackson.annotate.JsonIgnore;

import it.csi.qgisagri.agriapi.dto.Geometry;

public class ParticellaDTO implements Serializable
{

  private static final long serialVersionUID = -5161229193264642420L;
  private Long idFeature;
  private String geometriaWkt;
  private String numeroParticella;
  private String subalterno;
  private String flagConduzione;
  private String flagSospensione;
  private String descrizioneSospensione;
  private String flagPartLav;
  private String errore;
  private Geometry geometry;
  private String srid;
  
  
  public String getFlagSospensione()
  {
    return flagSospensione;
  }
  public void setFlagSospensione(String flagSospensione)
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
  public String getSrid()
  {
    return srid;
  }
  public void setSrid(String srid)
  {
    this.srid = srid;
  }
  public Long getIdFeature()
  {
    return idFeature;
  }
  public void setIdFeature(Long idFeature)
  {
    this.idFeature = idFeature;
  }
  @JsonIgnore
  public String getGeometriaWkt()
  {
    return geometriaWkt;
  }
  public void setGeometriaWkt(String geometriaWkt)
  {
    this.geometriaWkt = geometriaWkt;
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
  public String getFlagConduzione()
  {
    return flagConduzione;
  }
  public void setFlagConduzione(String flagConduzione)
  {
    this.flagConduzione = flagConduzione;
  }
  
  
 
  
  public Geometry getGeometry()
  {
    return geometry;
  }
  public void setGeometry(Geometry geometry)
  {
    this.geometry = geometry;
  }
  public String getFlagPartLav()
  {
    return flagPartLav;
  }
  public void setFlagPartLav(String flagPartLav)
  {
    this.flagPartLav = flagPartLav;
  }
  public String getErrore()
  {
    return errore;
  }
  public void setErrore(String errore)
  {
    this.errore = errore;
  }

}
