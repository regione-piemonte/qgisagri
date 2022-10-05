package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

import it.csi.qgisagri.agriapi.dto.Geometry;

public class CxfParticellaDTO implements Serializable
{

  private static final long serialVersionUID = 109524330298406944L;

  private long idCxfParticella;
  private String extCodNazionale;
  private String foglio;
  private String particella;
  private String subalterno;
  private String srid;
  private String allegato;
  private String sviluppo;
  private Geometry  geometry;
  private String geometriaWkt;
  private String errore;
  
  
  
  public String getSrid()
  {
    return srid;
  }
  public void setSrid(String srid)
  {
    this.srid = srid;
  }
  public String getErrore()
  {
    return errore;
  }
  public void setErrore(String errore)
  {
    this.errore = errore;
  }
  public long getIdCxfParticella()
  {
    return idCxfParticella;
  }
  public void setIdCxfParticella(long idCxfParticella)
  {
    this.idCxfParticella = idCxfParticella;
  }
  public String getExtCodNazionale()
  {
    return extCodNazionale;
  }
  public void setExtCodNazionale(String extCodNazionale)
  {
    this.extCodNazionale = extCodNazionale;
  }
  public String getFoglio()
  {
    return foglio;
  }
  public void setFoglio(String foglio)
  {
    this.foglio = foglio;
  }
  public String getParticella()
  {
    return particella;
  }
  public void setParticella(String particella)
  {
    this.particella = particella;
  }
  public String getSubalterno()
  {
    return subalterno;
  }
  public void setSubalterno(String subalterno)
  {
    this.subalterno = subalterno;
  }
  public String getAllegato()
  {
    return allegato;
  }
  public void setAllegato(String allegato)
  {
    this.allegato = allegato;
  }
  public String getSviluppo()
  {
    return sviluppo;
  }
  public void setSviluppo(String sviluppo)
  {
    this.sviluppo = sviluppo;
  }
  public Geometry getGeometry()
  {
    return geometry;
  }
  public void setGeometry(Geometry geometry)
  {
    this.geometry = geometry;
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
