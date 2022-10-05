package it.csi.proxy.ogcproxy.vo;

import java.io.Serializable;

public class ServiceVo implements Serializable {

	/**
	 * 
	 */
	private static final long serialVersionUID = 4619824103080859744L;
	private String host;
	private int port;
	private String serviceName;
	private String serviceType;
	
	public String getHost() {
		return host;
	}
	public void setHost(String host) {
		this.host = host;
	}
	public int getPort() {
		return port;
	}
	public void setPort(int port) {
		this.port = port;
	}
	public String getServiceName() {
		return serviceName;
	}
	public void setServiceName(String serviceName) {
		this.serviceName = serviceName;
	}
	public String getServiceType() {
		return serviceType;
	}
	public void setServiceType(String serviceType) {
		this.serviceType = serviceType;
	}
	
	
	
}
