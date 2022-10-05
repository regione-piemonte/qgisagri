package it.csi.qgisagri.agriapi.util.conversion;

import java.io.IOException;
import java.io.StringWriter;
import java.util.Map;

import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.node.ObjectNode;
import org.geotools.feature.simple.SimpleFeatureBuilder;
import org.geotools.feature.simple.SimpleFeatureTypeBuilder;
import org.geotools.geojson.feature.FeatureJSON;
import org.geotools.geojson.geom.GeometryJSON;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.io.ParseException;
import org.locationtech.jts.io.geojson.GeoJsonReader;
import org.locationtech.jts.io.geojson.GeoJsonWriter;
import org.opengis.feature.simple.SimpleFeature;
import org.springframework.util.StringUtils;

import it.csi.qgisagri.agriapi.util.AgriApiConstants;


public class GeoJSONGeometryConverter {
  
  /**
   * Combines a WKT string representation and a map containing all its attributes
   * to a String representing a GeoJSON object
   * 
   * @param wktStr        a wkt string representation of the geometry
   * @param attributesMap a map (Key/value) containing all the attributes of the
   *                      feature
   * @param crs           a string representation of the crs (can be EPSG:xxxx or
   *                      xxxx where xxxx is the corresponding EPSG id)
   * @param typeName      the name of the feature
   * @param featureId     the desired FeatureId, if null it will be automatically
   *                      generated
   * @return a String representing the desired GeoJSON object
   * @throws IOException
   * @throws ParseException
   */
  @SuppressWarnings("unchecked")
  public static String convertFeatureAndWktElementsToGeoJSON(final String wktStr, Map<String, Object> attributesMap,
      String crs, String typeName, String featureId) throws IOException, ParseException {
    FeatureTypeHandler fth = new FeatureTypeHandler(attributesMap);
    SimpleFeatureTypeBuilder builder = new SimpleFeatureTypeBuilder();
    builder.setName(typeName);
    if (crs.toUpperCase().startsWith(AgriApiConstants.EPSG_PREFIX)) {
      builder.setSRS(crs);
    } else {
      builder.setSRS("EPSG:" + crs);
    }
    Object[] values = new Object[fth.getOrderedAttributeList().length];
    for (int i = 0; i < fth.getOrderedAttributeList().length; i++) {
      
      if(((Map.Entry<String, Object>)fth.getOrderedAttributeList()[i]).getValue()==null){
        values[i] = new String("");
        builder.add(((Map.Entry<String, Object>)fth.getOrderedAttributeList()[i]).getKey(), String.class);
        continue;
      }
      
      builder.add(((Map.Entry<String, Object>)fth.getOrderedAttributeList()[i]).getKey(),
          ((Map.Entry<String, Object>)fth.getOrderedAttributeList()[i]).getValue().getClass());
      values[i] = ((Map.Entry<String, Object>)fth.getOrderedAttributeList()[i]).getValue();
    }
    SimpleFeatureBuilder featureBuilder = new SimpleFeatureBuilder(builder.buildFeatureType());
    SimpleFeature sf = featureBuilder.buildFeature(featureId, values);
    String tmpJson = GeoJSONGeometryConverter.simpleFeatureToGeoJSON(sf);
    ObjectMapper om = new ObjectMapper();
    ObjectNode node = (ObjectNode) new ObjectMapper().readTree(tmpJson);
    Geometry geometry = WKTGeometryConverter.getGeometryFromWKT(wktStr);
    ObjectNode geometryNode = (ObjectNode) om.readTree(GeoJSONGeometryConverter.convertJTSGeometryToGeoJSON(geometry));
    node.put("geometry", geometryNode);
    return node.toString().replace("EPSG:0","EPSG:3003").replace("\"[", "[").replace("]\"", "]").replace("\\\"", "\"").replace("&quada", "[").replace("&quadc", "]");
  }
  
  /**
   * Converts a JTSGeometry instance to a String representing a GeoJSON object
   * 
   * @param geometry a JTSGeometry instance
   * @return a String representing the desired GeoJSON object
   * @throws IOException
   */
  public static String convertJTSGeometryToGeoJSON(final Geometry geometry) throws IOException {
    
    GeoJsonWriter writer = new GeoJsonWriter();
    return writer.write(geometry);
  }

  /**
   * Converts a org.opengis.feature.simple.SimpleFeature instance to a String GeoJSON representation of the input feature
   * @param feature the feature to convert to GeoJSON String
   * @return a string representing the GeoJSON version of the feature
   * @throws IOException
   */
  public static String simpleFeatureToGeoJSON(final SimpleFeature feature) throws IOException {
    return new FeatureJSON().toString(feature);
  }

  /**
   * Converts a GeoJSON String representation of a feature to a SimpleFeature instance
   * @param geoJSON the GeoJSON String representation of a feature
   * @return a SimpleFeature instance instantiated from the GeoJSON representation
   * @throws IOException
   */
  public static SimpleFeature geoJSONToSimpleFeature(final String geoJSON) throws IOException {
    return new FeatureJSON().readFeature(geoJSON);
  }
  
  /**
     * Build the {@link Geometry} from the given GeoJSON {@code geoJSON}.
     * @param geoJSON The GeoJSON containing the geometry
     * @return The Geometry
     * @throws IOException The geoJSON cannot be correctly processed.
   * @throws ParseException 
     */
    public static Geometry getGeometryFromGeoJSON(String geoJSON) throws IOException, ParseException {
        if (StringUtils.isEmpty(geoJSON)) {
            return null;
        }

        
        GeoJsonReader writer = new GeoJsonReader();
        Geometry geometry = writer.read(geoJSON);
        return geometry;
    }

    
}

