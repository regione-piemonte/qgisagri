package it.csi.proxy.ogcproxy.vo;

import java.io.Serializable;

public class RequestVo implements Serializable {

	/**
	 * 
	 */
	private static final long serialVersionUID = -9192127027711022715L;
	private String supposedApacheUrl;
	private String scheme;
	private String service;
	private String serverName;
	private int serverPort = 80;
	private String servletPath;
	private String originalUrl;
	private String caller;
	private String requestType;
	
	public String getRequestType() {
		return requestType;
	}

	public void setRequestType(String requestType) {
		this.requestType = requestType;
	}

	public String getService() {
		return service;
	}
	
	public void setService(String service) {
		this.service = service;
	}

	public String getCaller() {
		return caller;
	}

	public void setCaller(String caller) {
		this.caller = caller;
	}

	public String getOriginalUrl() {
		return originalUrl;
	}

	public void setOriginalUrl(String originalUrl) {
		this.originalUrl = originalUrl;
	}

	public String getSupposedApacheUrl() {
		return supposedApacheUrl;
	}

	public void setSupposedApacheUrl(String supposedApacheUrl) {
		this.supposedApacheUrl = supposedApacheUrl;
	}

	public String getScheme() {
		return scheme;
	}

	public void setScheme(String scheme) {
		this.scheme = scheme;
	}

	public String getServerName() {
		return serverName;
	}

	public void setServerName(String serverName) {
		this.serverName = serverName;
	}

	public int getServerPort() {
		return serverPort;
	}

	public void setServerPort(int serverPort) {
		this.serverPort = serverPort;
	}

	public String getServletPath() {
		return servletPath;
	}

	public void setServletPath(String servletPath) {
		this.servletPath = servletPath;
	}
	
	public String getHostlessUrl(){
		return getOriginalUrl().substring(getOriginalUrl().indexOf("/ogcproxy")+("/ogcproxy".length()));
	}
	
	@Override
	public String toString() {
		StringBuilder sb = new StringBuilder();
		sb.append("*************************************");
		sb.append("RequestVo:");
		sb.append("\n\toriginalUrl " + getOriginalUrl());
		sb.append("\n\tsupposedApacheUrl " + getSupposedApacheUrl());
		sb.append("\n\tscheme " + getScheme());
		sb.append("\n\tserverName " + getServerName());
		sb.append("\n\tserverPort " + getServerPort());
		sb.append("\n\tservletPath " + getServletPath());
		sb.append("\n\thostlessUrl " + getHostlessUrl());
		sb.append("\n*************************************");
		return sb.toString();
	}
}
