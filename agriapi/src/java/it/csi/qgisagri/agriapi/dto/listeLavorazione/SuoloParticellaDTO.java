package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

import org.locationtech.jts.geom.Geometry;

public class SuoloParticellaDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -9061749786913323750L;

  private Long              idEventoLavorazione;
  private Long              idFeature;
  private String            tipoSuolo;
  private String            layer;
  
  private String            codiceNazionale;
  private String            foglio;
  private String            codiceEleggibilitaRilevata;
  private String            numeroParticella;
  private String            subalterno;
  
  private Long              ogcLayerIDSuolo;
  private Long              ogcLayerIDParticella;
  
  private Long              ogcFidSuolo;
  private Long              ogcFidParticella;
  private Double            area;
  private Geometry          geometry;
  
  
  
  
  public Long getOgcLayerIDSuolo()
  {
    return ogcLayerIDSuolo;
  }
  public void setOgcLayerIDSuolo(Long ogcLayerIDSuolo)
  {
    this.ogcLayerIDSuolo = ogcLayerIDSuolo;
  }
  public Long getOgcLayerIDParticella()
  {
    return ogcLayerIDParticella;
  }
  public void setOgcLayerIDParticella(Long ogcLayerIDParticella)
  {
    this.ogcLayerIDParticella = ogcLayerIDParticella;
  }
  public Long getOgcFidParticella()
  {
    return ogcFidParticella;
  }
  public void setOgcFidParticella(Long ogcFidParticella)
  {
    this.ogcFidParticella = ogcFidParticella;
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
  public String getCodiceEleggibilitaRilevata()
  {
    return codiceEleggibilitaRilevata;
  }
  public void setCodiceEleggibilitaRilevata(String codiceEleggibilitaRilevata)
  {
    this.codiceEleggibilitaRilevata = codiceEleggibilitaRilevata;
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
  public String getTipoSuolo()
  {
    return tipoSuolo;
  }
  public void setTipoSuolo(String tipoSuolo)
  {
    this.tipoSuolo = tipoSuolo;
  }
  
  public Long getOgcFidSuolo()
  {
    return ogcFidSuolo;
  }
  public void setOgcFidSuolo(Long ogcFidSuolo)
  {
    this.ogcFidSuolo = ogcFidSuolo;
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
  public String getLayer()
  {
    return layer;
  }
  public void setLayer(String layer)
  {
    this.layer = layer;
  }

}
