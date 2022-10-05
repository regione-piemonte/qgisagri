package it.csi.proxy.ogcproxy.filter;

import it.csi.proxy.ogcproxy.util.Utilities;

import java.io.IOException;
import java.util.Enumeration;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class ProxyFilter extends AbstractFilter {

    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    	doLog("ProxyFilter.doFilter - START");
    	String requestStr = Utilities.getFullURL(request);
    	doLog("Requested URI [" + requestStr + "]");   
    	
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        Enumeration<String> headerNames = httpRequest.getHeaderNames();

        if (headerNames != null) {
                while (headerNames.hasMoreElements()) {
                	String headerName = headerNames.nextElement();
                    doLog("Header: " + headerName + " - " + httpRequest.getHeader(headerName));
                }
        }    	
    	
    	if (Utilities.isRequestAdmitted(requestStr)) {
    		doLog("Request admitted");    		
    		chain.doFilter(request, response);
    	}
    	else {
    		doLog("Request not admitted");
    		if (response instanceof HttpServletResponse) {
    			((HttpServletResponse)response).setStatus(HttpServletResponse.SC_METHOD_NOT_ALLOWED);
    			response.flushBuffer();
    		}
    		else {
    			throw new UnsupportedOperationException("OGCPROXY SUPPORTS ONLY HTTP CALLS");
    		}
    	}
    }    
	

}
