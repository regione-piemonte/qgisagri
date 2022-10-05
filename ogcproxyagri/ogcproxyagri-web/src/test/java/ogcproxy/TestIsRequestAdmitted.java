package ogcproxy;

import static org.junit.Assert.assertTrue;
import it.csi.proxy.ogcproxy.util.Utilities;

import org.junit.Test;

public class TestIsRequestAdmitted {
	
	@Test
	public void testIsRequestAdmitted() {
		assertTrue(Utilities.isRequestAdmitted("http://localhost:8080/ogcproxy/ws/taims/rp-01/taimsortoregp/wms_ortoregp2010?service=WMS&request=getCapabilities"));
	}
	
	@Test
	public void testIsRequestAdmittedF() {
		assertTrue(!Utilities.isRequestAdmitted("http://localhost:8080/ogcproxy/ws/taims/rp-01/taimsortoregp/wms_ortoregp2010?service=WMS&request="));
	}
	
	@Test
	public void testIsRequestAdmittedFF() {
		assertTrue(!Utilities.isRequestAdmitted("http://www.google.it"));
	}
	
	@Test
	public void testIsRequestAdmittedGF() {
		assertTrue(Utilities.isRequestAdmitted("http://localhost:8080/ogcproxy/ws/taims/rp-01/taimslimammwms/wms_limitiAmm?STYLES=%2C&TRANSPARENT=true&LAYERS=LimitiComunali&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A32632&BBOX=-144176.93556729425,4611641.381907559,974488.9355672942,5414076.618092441&WIDTH=1698&HEIGHT=1218"));
	}
	
	@Test
	public void testIsRequestAdmittedGg() {
		assertTrue(!Utilities.isRequestAdmitted("http://localhost:8080/ogcproxy/ws/taims/rp-01/taimslimammwms/wms_limitiAmm?STYLES=%2C&TRANSPARENT=true&LAYERS=LimitiComunali&SERVICE=WMS&VERSION=1.1.1&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A32632&BBOX=-144176.93556729425,4611641.381907559,974488.9355672942,5414076.618092441&WIDTH=1698&HEIGHT=1218"));
	}

}
