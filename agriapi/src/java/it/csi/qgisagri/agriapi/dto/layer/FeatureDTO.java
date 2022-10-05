package it.csi.qgisagri.agriapi.dto.layer;

import java.io.Serializable;

public class FeatureDTO implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = -3394720114502158948L;
  
  @SuppressWarnings("unused")
  private String            type;
  private String            geometry;

  public FeatureDTO(String geometry)
  {
    this.geometry=geometry;
  }

  public String getGeometry()
  {
    return geometry;
  }

  public void setGeometry(String geometry)
  {
    this.geometry = geometry;
  }

  public String getType()
  {
    return "Feature";
  }

}
