package it.csi.qgisagri.agriapi.util.conversion;

import org.geotools.geometry.jts.JTSFactoryFinder;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.io.ParseException;
import org.locationtech.jts.io.WKTReader;

public class WKTGeometryConverter {

  /**
     * Build the {@link Geometry} from the given WKT {@code wkt}.
     * @param wkt The WKT describing the geometry
     * @return The Geometry
     * @throws ParseException The WKT cannot be correctly processed.
     */
    public static Geometry getGeometryFromWKT(String wkt) throws ParseException {
        if (org.springframework.util.StringUtils.isEmpty(wkt)) {
            return null;
        }

        //GeometryFactory geometryFactory = JTSFactoryFinder.getGeometryFactory();
        WKTReader reader = new WKTReader();
        Geometry geometry = reader.read(wkt);

        return geometry;
    }
}
