package it.csi.qgisagri.agriapi.dto.mygeojson;

import java.io.IOException;

import org.codehaus.jackson.JsonProcessingException;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.node.ObjectNode;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.io.ParseException;

import it.csi.qgisagri.agriapi.util.AgriApiConstants;
import it.csi.qgisagri.agriapi.util.conversion.GeoJSONGeometryConverter;
import it.csi.qgisagri.agriapi.util.conversion.WKTGeometryConverter;

public class MyGeoJsonFeature<T>
{
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
  private String     type = "Feature";
  private ObjectNode geometry;
  private T          properties;

  public String getType()
  {
    return type;
  }

  public void setType(String type)
  {
    this.type = type;
  }

  public ObjectNode getGeometry()
  {
    return geometry;
  }

  public void setGeometry(ObjectNode geometry)
  {
    this.geometry = geometry;
  }
  
  public void setGeometry(String geometry, String srid) throws ParseException, JsonProcessingException, IOException
  {
    Geometry g = WKTGeometryConverter.getGeometryFromWKT(geometry);
    String epsg=srid==null?"EPSG:"+AgriApiConstants.DEFAULT_CRS_PIEMONTE:srid;
    ObjectNode geometryNode = (ObjectNode) OBJECT_MAPPER.readTree(GeoJSONGeometryConverter.convertJTSGeometryToGeoJSON(g).replace("EPSG:0", epsg));
    this.geometry = geometryNode;
  }

  public T getProperties()
  {
    return properties;
  }

  public void setProperties(T properties)
  {
    this.properties = properties;
  }
}
