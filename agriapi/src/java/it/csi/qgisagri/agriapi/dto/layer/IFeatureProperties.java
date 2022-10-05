package it.csi.qgisagri.agriapi.dto.layer;

import java.io.Serializable;

public interface IFeatureProperties extends Serializable
{
  public String getFeatureText();

  public String getFeatureDescription();
}
