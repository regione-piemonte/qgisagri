package it.csi.qgisagri.agriapi.dto.mygeojson;

import java.util.ArrayList;
import java.util.List;

public class MyGeoJsonFeatureCollection<T>
{
  private String                  type = "FeatureCollection";
  private List<MyGeoJsonFeature<T>> features = new ArrayList<MyGeoJsonFeature<T>>();
  public String getType()
  {
    return type;
  }

  public void setType(String type)
  {
    this.type = type;
  }

  public List<MyGeoJsonFeature<T>> getFeatures()
  {
    return features;
  }

  public void setFeatures(List<MyGeoJsonFeature<T>> features)
  {
    this.features = features;
  }

  public void addFeature(MyGeoJsonFeature<T> feature)
  {
    this.features.add(feature);
  }
}
