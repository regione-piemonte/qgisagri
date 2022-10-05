package it.csi.proxy.ogcproxy.filter;

import java.io.IOException;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;

public abstract class AbstractFilter implements Filter {
	
	protected FilterConfig config = null;

	@Override
	public void destroy() {
		this.config = null;
	}

	@Override
	public void doFilter(ServletRequest arg0, ServletResponse arg1,
			FilterChain arg2) throws IOException, ServletException {
		// TODO Auto-generated method stub

	}

	@Override
	public void init(FilterConfig config) throws ServletException {
		this.config = config;
	}
	
	protected void doLog(String message) {
		this.config.getServletContext().log(message);
	}

}
