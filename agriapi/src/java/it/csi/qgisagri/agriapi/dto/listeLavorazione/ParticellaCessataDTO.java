package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

import org.locationtech.jts.geom.Geometry;

public class ParticellaCessataDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -133917744481678108L;

  private Long              idEventoLavorazione;
  private Long              idFeature;
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
