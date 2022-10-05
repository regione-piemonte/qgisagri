package it.csi.proxy.ogcproxy.util;

import it.csi.proxy.ogcproxy.vo.RequestVo;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;

import javax.servlet.ServletRequest;
import javax.servlet.http.HttpServletRequest;

public class Utilities {

	private static final int BUFFER_SIZE = 4 * 1024;
	 
	public static String inputStreamToString(InputStream inputStream)
	        throws IOException {
	    StringBuilder builder = new StringBuilder();
	    InputStreamReader reader = new InputStreamReader(inputStream);
	    char[] buffer = new char[BUFFER_SIZE];
	    int length;
	    while ((length = reader.read(buffer)) != -1) {
	        builder.append(buffer, 0, length);
	    } 
	    return builder.toString();
	} 
	
	public static String getFullURL(ServletRequest request) {
		HttpServletRequest request2 = null;
		if (request instanceof HttpServletRequest) {
			request2 = (HttpServletRequest)request;
			StringBuffer requestURL = request2.getRequestURL();
			String queryString = request2.getQueryString();
			
			if (queryString == null) {
				return requestURL.toString();
			} else { 
				return requestURL.append('?').append(queryString).toString();
			} 
		}
		else {
			return null;
		}
	} 
	
	public static RequestVo getRequestVo(ServletRequest request) {
		RequestVo req = new RequestVo();
		HttpServletRequest http_request = null;
		if (request instanceof HttpServletRequest) {
			http_request = (HttpServletRequest)request;
			//TODO gestire anche il parametro normale in request 
			req.setCaller(http_request.getHeader(Constants.CALLER_REQ_PARAM));
			req.setSupposedApacheUrl(http_request.getHeader("x-forwarded-proto"));
			req.setScheme(http_request.getScheme());
			req.setServerName(http_request.getServerName());
			req.setServerPort(http_request.getServerPort());
			req.setServletPath(http_request.getServletPath());
			
			StringBuffer requestURL = http_request.getRequestURL();
			String queryString = http_request.getQueryString();
			if (queryString == null) {
				req.setOriginalUrl(requestURL.toString());
			} else { 
				req.setOriginalUrl(requestURL.append('?').append(queryString).toString());
			} 
			req.setRequestType(detectRequestType(req.getOriginalUrl()));
		}
		return req;
	}
	
	private static String detectRequestType(String originalUrl) {
		if (originalUrl.toUpperCase().contains("REQUEST=GETCAPABILITIES")) {
			return Constants.GETCAPABILITIES;
		}
		else {
			return Constants.UNHANDLEDREQUEST;
		}
	}

	private static ArrayList<String[]> _admittedPatterns = new ArrayList<String[]>();
	static {
		String[] getCapabilities =new String[]{"GetCapabilities","service","request"};
		String[] getResourceByIds =new String[]{"service","request","version"};
		String[] otherCalls =new String[]{"GetResourceByID","service","request","version","resourceID","token"};
		String[] tms =new String[]{"tms"};
		String[] wmts =new String[]{"wmts"};
		_admittedPatterns.add(getCapabilities);
		_admittedPatterns.add(getResourceByIds);
		_admittedPatterns.add(otherCalls);
		_admittedPatterns.add(tms);
		_admittedPatterns.add(wmts);
	}

	public static boolean isRequestAdmitted(final String requestStr) {
		boolean admitted = false;
    	for (String[] patterns : _admittedPatterns) {
    		//System.out.println("patterns: " + patterns.toString());
    		if (admitted) {
    			break;
    		}
			for (int j = 0; j < patterns.length; j++) {
				//System.out.println("isRequestAdmitted - testing " + requestStr.toLowerCase() + " vs " + patterns[j].toLowerCase());
				if (!requestStr.toLowerCase().contains(patterns[j].toLowerCase())) {		
					admitted = false;
					//break;
				}
				else {
					admitted = true;
					break;
				}
				//System.out.println("admitted: " + admitted);
			}			
		}
		return admitted;
	} 
}
