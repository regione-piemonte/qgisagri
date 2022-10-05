package it.csi.qgisagri.agriapi.util.rs.serialize;

import java.io.IOException;
import java.util.Iterator;

import org.codehaus.jackson.JsonNode;
import org.codehaus.jackson.JsonParser;
import org.codehaus.jackson.JsonProcessingException;
import org.codehaus.jackson.ObjectCodec;
import org.codehaus.jackson.map.DeserializationContext;
import org.codehaus.jackson.map.JsonDeserializer;
import org.codehaus.jackson.map.ObjectMapper;
import org.geotools.data.DataUtilities;
import org.geotools.feature.SchemaException;
import org.geotools.geojson.feature.FeatureJSON;
import org.opengis.feature.simple.SimpleFeature;
import org.opengis.feature.simple.SimpleFeatureType;
import org.opengis.referencing.crs.CoordinateReferenceSystem;

import it.csi.qgisagri.agriapi.dto.GeoJSONCRS;
import it.csi.qgisagri.agriapi.dto.GeoJSONFeatureCollection;
import it.csi.qgisagri.agriapi.util.conversion.CRSUtils;

/**
 * TODO
 * @author 1681
 *
 */
public class FeaturesDeserializer extends JsonDeserializer<GeoJSONFeatureCollection> {

	@Override
	public GeoJSONFeatureCollection deserialize(JsonParser jp, DeserializationContext ctxt)
			throws IOException, JsonProcessingException {
		ObjectMapper objectMapper = new ObjectMapper();
		ObjectCodec oc = jp.getCodec();
		JsonNode node = oc.readTree(jp);
		// The output object
		GeoJSONFeatureCollection featureCollection = new GeoJSONFeatureCollection();

		// The CRS (a standard GeoJSON would not have it)
		JsonNode crs = node.get("crs");
		GeoJSONCRS geoJSONCRS = null;
		if (crs != null) {
			geoJSONCRS = objectMapper.readValue(crs, GeoJSONCRS.class);
			//featureCollection.setCrs(geoJSONCRS);
		}

		// Elements for further computation
		CoordinateReferenceSystem coordinateReferenceSystem = null;
		try {
			coordinateReferenceSystem = CRSUtils.getCoordinateReferenceSystem(geoJSONCRS);
		} catch (Exception e) {
			throw new IOException("Unable to retrieve the 'CoordinateReferenceSystem' from the given geoJSONCRS: " + geoJSONCRS);
		}
		SimpleFeatureType crsAugmentedSimpleFeatureType = null;

		/* Getting the features */
		Iterator<JsonNode> features = node.get("features").getElements();
		while (features.hasNext()) {
			JsonNode jsonNode = (JsonNode) features.next();
			FeatureJSON fJ = new FeatureJSON();
			SimpleFeature sf = fJ.readFeature(jsonNode.toString());

			/* Define a type like the feature original one, but having the CRS */
			if (crsAugmentedSimpleFeatureType == null) {
				try {
					crsAugmentedSimpleFeatureType = DataUtilities.createSubType(sf.getFeatureType(), null, coordinateReferenceSystem);
				} catch (SchemaException e) {
					throw new IOException("Unable to derive a sub feature type with a specific coordinate reference system", e);
				}
			}

			// Generating the feature having the CRS in its type
			//sf = DataUtilities.reType(crsAugmentedSimpleFeatureType, sf);

			featureCollection.getFeatures().add(sf);
		}

		// Get the bounding box
		
		return featureCollection;
	}

}
