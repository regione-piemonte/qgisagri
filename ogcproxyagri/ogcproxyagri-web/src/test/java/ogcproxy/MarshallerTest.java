package ogcproxy;

import java.util.List;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.Marshaller;
import javax.xml.bind.Unmarshaller;
import javax.xml.transform.stream.StreamSource;

import junit.framework.TestCase;
import net.opengis.wms.v_1_3_0.Layer;
import net.opengis.wms.v_1_3_0.WMSCapabilities;

public class MarshallerTest extends TestCase {

	public void testMarshalWMSCapabilities0() throws Exception {
//		http://<HOSTNAME>/ws/aera/rp-01/aerawms/wms_aera_m01?service=WMS&request=GetCapabilities
//		String url = "<HOSTNAME>/ws/taims/rp-01/taimsortoregp/wms_ortoregp2010?";
		String url = "<HOSTNAME>/ws/aera/rp-01/aerawms/wms_aera_m01?";
		StringBuilder sb = new StringBuilder();
		sb.append("http://");
		sb.append(url);
		sb.append("REQUEST=GetCapabilities&SERVICE=WMS");
		sb.append("&FORMAT=text/xml");
		// Create JAXB context for WMS 1.3.0
		JAXBContext context = JAXBContext.newInstance("net.opengis.wms.v_1_3_0");
		// Use the created JAXB context to construct an unmarshaller
		Unmarshaller unmarshaller = context.createUnmarshaller();
		// GetCapabilities URL of the Demis WorldMap WMS Server

		// Unmarshal the given URL, retrieve WMSCapabilities element
		JAXBElement<WMSCapabilities> wmsCapabilitiesElement = unmarshaller
				.unmarshal(new StreamSource(sb.toString()),
						WMSCapabilities.class);
		// Retrieve WMSCapabilities instance
		WMSCapabilities wmsCapabilities = wmsCapabilitiesElement.getValue();
		// Iterate over layers, print out layer names
		for (Layer layer : wmsCapabilities.getCapability().getLayer()
				.getLayer()) {
			System.out.println(layer.getName());
		}
		System.out.println("AFTER CLONING");
		WMSCapabilities clone = (WMSCapabilities) wmsCapabilities.clone();
		List<Layer> layerList = wmsCapabilities.getCapability().getLayer().getLayer();
		layerList.remove(0);
		clone.getCapability().getLayer().unsetLayer();
		clone.getCapability().getLayer().setLayer(layerList);
		for (Layer layer : clone.getCapability().getLayer().getLayer()) {
			System.out.println(layer.getName());
		}
		
		clone.getCapability().unsetExtendedCapabilities(); 

		
		Marshaller marshaller = context.createMarshaller();


		System.out.println("FINO A QUI TUTTO OK");
		marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
		marshaller.marshal(clone, System.out);

	}
	
}
