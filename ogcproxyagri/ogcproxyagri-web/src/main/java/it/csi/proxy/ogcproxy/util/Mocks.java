package it.csi.proxy.ogcproxy.util;

import it.csi.proxy.ogcproxy.vo.ServiceVo;

public class Mocks {

	public static final ServiceVo getNigerMockServiceVo() {
		ServiceVo requestedService = new ServiceVo();
		requestedService.setHost("<HOSTNAME>");
		requestedService.setPort(<PORT>);
		requestedService.setServiceName("mp");
		requestedService.setServiceType("WMS");
		return requestedService;
	}
	
	public static final ServiceVo getMockServiceVo() {
		ServiceVo requestedService = new ServiceVo();
		requestedService.setHost("<HOSTNAME>");
		requestedService.setPort(<PORT>);
		requestedService.setServiceName("wmspiemonteagri");
		requestedService.setServiceType("WMS");
		return requestedService;
	}
}
