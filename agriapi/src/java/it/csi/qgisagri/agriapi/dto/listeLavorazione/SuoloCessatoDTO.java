package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

import org.locationtech.jts.geom.Geometry;

public class SuoloCessatoDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -133917744481678108L;

  private Long              idEventoLavorazione;
  private Long              idFeature;
  private String            tipoSuolo;
  private String            layer;
  private Geometry          geometry;
  
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
