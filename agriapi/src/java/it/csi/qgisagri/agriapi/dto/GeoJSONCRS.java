package it.csi.qgisagri.agriapi.dto;

import java.util.HashMap;
import java.util.Map;

import org.codehaus.jackson.annotate.JsonProperty;

/**
 * Compliant with the obsolete GeoJSON 2008 format
 * https://geojson.org/geojson-spec#coordinate-reference-system-objects
 */
public class GeoJSONCRS {

    /**
     * The type
     */
    @JsonProperty("type")
    private String type;

    /**
     * The properties associated object
     */
    @JsonProperty("properties")
    private Map<String, Object> properties;

    public GeoJSONCRS() {
        this.properties = new HashMap<String, Object>();
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public Map<String, Object> getProperties() {
        return properties;
    }

    public void setProperties(Map<String, Object> properties) {
        this.properties = properties;
    }

    @Override
    public String toString() {
        return "GeoJSONCRS{" +
                "type='" + type + '\'' +
                ", properties=" + properties +
                '}';
    }
}
