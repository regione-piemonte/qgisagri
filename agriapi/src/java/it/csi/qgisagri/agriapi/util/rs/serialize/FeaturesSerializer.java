package it.csi.qgisagri.agriapi.util.rs.serialize;

import java.io.IOException;
import java.util.Iterator;

import org.codehaus.jackson.JsonGenerator;
import org.codehaus.jackson.JsonProcessingException;
import org.codehaus.jackson.map.JsonSerializer;
import org.codehaus.jackson.map.SerializerProvider;
import org.geotools.geojson.feature.FeatureJSON;
import org.opengis.feature.simple.SimpleFeature;

import it.csi.qgisagri.agriapi.dto.GeoJSONFeatureCollection;

public class FeaturesSerializer extends JsonSerializer<GeoJSONFeatureCollection> {

	@Override
	public void serialize(GeoJSONFeatureCollection value, JsonGenerator jgen, SerializerProvider provider)
			throws IOException, JsonProcessingException {
		jgen.writeStartObject();
		// The "type" as GeoJSON requires
		jgen.writeStringField("type", value.getType());

		/* features array */
		jgen.writeArrayFieldStart("features");
		/*Iterator<SimpleFeature> fjList =  value.getFeatures().iterator();
		while (fjList.hasNext()) {
			SimpleFeature featureJSON = (SimpleFeature) fjList.next();
			jgen.writeRaw(new FeatureJSON().toString(featureJSON));
			// In case there is another value, need to write the separator
			if (fjList.hasNext()) {
				jgen.writeRaw(",");
			}
		}
		*/
		if(value.getFeaturesString()!=null)
		{
  		Iterator<String> fjList =  value.getFeaturesString().iterator();
      while (fjList.hasNext()) {
        String featureJSON = (String) fjList.next();
        jgen.writeRaw(featureJSON);
        // In case there is another value, need to write the separator
        if (fjList.hasNext()) {
          jgen.writeRaw(",");
        }
      }
		}
		else if(value.getFeatures()!=null)
		{
		  Iterator<SimpleFeature> fjList =  value.getFeatures().iterator();
	    while (fjList.hasNext()) {
	      SimpleFeature featureJSON = (SimpleFeature) fjList.next();
	      jgen.writeRaw(new FeatureJSON().toString(featureJSON));
	      // In case there is another value, need to write the separator
	      if (fjList.hasNext()) {
	        jgen.writeRaw(",");
	      }
	    }
		}
		
		
		jgen.writeEndArray();


		jgen.writeEndObject();
		
	}

}
