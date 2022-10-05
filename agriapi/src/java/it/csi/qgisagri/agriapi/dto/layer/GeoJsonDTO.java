package it.csi.qgisagri.agriapi.dto.layer;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class GeoJsonDTO implements Serializable
{
  /** serialVersionUID */
  private static final long   serialVersionUID = 1560174980009515076L;

  @SuppressWarnings("unused")
  private String            type;
  private List<FeatureDTO> features;
  
  public GeoJsonDTO()
  {
    features = new ArrayList<FeatureDTO>();
  }
  public String getType()
  {
    return "FeatureCollection";
  }
  public List<FeatureDTO> getFeatures()
  {
    return features;
  }
  public void setFeatures(List<FeatureDTO> features)
  {
    this.features = features;
  }
 
}
