package it.csi.proxy.ogcproxy.filter;

import java.io.IOException;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;

public class LoggingFilter extends AbstractFilter{
	

	public void doFilter(ServletRequest request, ServletResponse response,
			FilterChain chain) throws IOException, ServletException {
			long before = System.currentTimeMillis();
		    chain.doFilter(request, response);
		    long after = System.currentTimeMillis();
		    String name = "";
		    if (request instanceof HttpServletRequest) {
		      name = ((HttpServletRequest)request).getRequestURI();
		      doLog(name + ": " + (after - before) + "ms");
		    }
		    else {
		    	throw new UnsupportedOperationException("OGCPROXY ONLY SUPPORTS HTTP CALLS");
		    }
	}


}
