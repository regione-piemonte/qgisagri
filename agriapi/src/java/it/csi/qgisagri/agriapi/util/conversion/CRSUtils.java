package it.csi.qgisagri.agriapi.util.conversion;

import org.apache.commons.lang3.NotImplementedException;
import org.geotools.referencing.CRS;
import org.opengis.referencing.crs.CoordinateReferenceSystem;

import it.csi.qgisagri.agriapi.dto.GeoJSONCRS;

/**
 * Utilities for managing CRS on various aspects
 */
public class CRSUtils {

    /**
     * Compute the {@link CoordinateReferenceSystem} corresponding to the {@code geoJSONCRS}
     * @param geoJSONCRS The CRS of the GeoJSON format
     * @return The {@link CoordinateReferenceSystem} for the {@code geoJSONCRS}
     */
    public static CoordinateReferenceSystem getCoordinateReferenceSystem(GeoJSONCRS geoJSONCRS) throws Exception {
        if (geoJSONCRS == null) {
            return CRS.decode("EPSG:4326");
        }

        if (geoJSONCRS.getProperties() == null || geoJSONCRS.getProperties().size() == 0) {
            throw new Exception("The 'properties' field of the given object of type 'GeoJSONCRS' are null or the collection is empty");
        }

        // There are different approaches, but the addressed one in CSI is just 'name'
        if (!geoJSONCRS.getType().equals("name")) {
            throw new NotImplementedException("The CRS type '" + geoJSONCRS.getType() + "' is not yet supported.");
        }

        /* Getting the "EPSG:<code>" from the 'name' property */
        Object nameProperty = geoJSONCRS.getProperties().get("name");
        if (nameProperty == null || !(nameProperty instanceof String)) {
            throw new Exception("The CRS 'name' property is either null or not of type 'String'");
        }

        String epsg = (String) nameProperty;
        CoordinateReferenceSystem coordinateReferenceSystem = CRS.decode(epsg);
        return coordinateReferenceSystem;
    }
}
