package it.csi.qgisagri.agriapi.dto.layer;

public class FeaturePropertiesDTO implements IFeatureProperties
{
  /** serialVersionUID */
  private static final long serialVersionUID = -4756219882905485049L;
  private String            featureText;
  private String            featureDescription;

  public String getFeatureText()
  {
    return featureText;
  }

  public void setFeatureText(String featureText)
  {
    this.featureText = featureText;
  }

  public String getFeatureDescription()
  {
    return featureDescription;
  }

  public void setFeatureDescription(String featureDescription)
  {
    this.featureDescription = featureDescription;
  }
  
}
