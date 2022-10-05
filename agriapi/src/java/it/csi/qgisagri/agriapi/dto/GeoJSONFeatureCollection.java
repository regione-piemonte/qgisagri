package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import org.codehaus.jackson.annotate.JsonProperty;
import org.codehaus.jackson.map.annotate.JsonDeserialize;
import org.codehaus.jackson.map.annotate.JsonSerialize;
import org.codehaus.jackson.map.annotate.JsonSerialize.Inclusion;
import org.opengis.feature.simple.SimpleFeature;

import it.csi.qgisagri.agriapi.util.rs.serialize.FeaturesDeserializer;
import it.csi.qgisagri.agriapi.util.rs.serialize.FeaturesSerializer;

/**
 * The GeoJSON representation of type 'FeatureCollection'
 */
@JsonDeserialize(using = FeaturesDeserializer.class)
@JsonSerialize(using = FeaturesSerializer.class)
public class GeoJSONFeatureCollection implements Serializable {

  private static final long serialVersionUID = 1L;

  @JsonProperty("type")
  private String type;

  private List<SimpleFeature> features;
  private List<String> featuresString;


  public GeoJSONFeatureCollection() {
    this.type = "FeatureCollection";
    this.features = new ArrayList<>();
  }

  public String getType() {
    return type;
  }

  @JsonProperty("features")
  @JsonSerialize(include = Inclusion.NON_EMPTY)
  public List<SimpleFeature> getFeatures() {
    return features;
  }
  public void setFeatures(List<SimpleFeature> features) {
    this.features = features;
  }

  public List<String> getFeaturesString()
  {
    return featuresString;
  }

  public void setFeaturesString(List<String> featuresString)
  {
    this.featuresString = featuresString;
  }
  
}
