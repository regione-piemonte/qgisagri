package it.csi.proxy.ogcproxy;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class StartupServlet extends AbstractServlet {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1865097878458285721L;

	@Override
	public void init() throws ServletException {
		super.init();
		doLog("StartupServlet.init - START - DB PARAMETERS TO BE LOADED HERE ONCE");
	}

	@Override
	protected HttpServletResponse doGetImpl(HttpServletRequest req, HttpServletResponse resp) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	protected void responseProcessing(HttpServletResponse resp) {
		// TODO Auto-generated method stub
		
	}
}
