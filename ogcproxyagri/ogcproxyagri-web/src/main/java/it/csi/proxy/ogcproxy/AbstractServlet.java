package it.csi.proxy.ogcproxy;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public abstract class AbstractServlet extends HttpServlet {

	/**
	 * 
	 */
	private static final long serialVersionUID = 7868221424239602797L;

	protected void doLog(String message) {
		this.getServletContext().log(message);
	}
	
	@Override
	public void init() throws ServletException {
		super.init();
	}
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		HttpServletResponse response = doGetImpl(req, resp);
		responseProcessing(response);
	}
	
	protected abstract HttpServletResponse doGetImpl(HttpServletRequest req, HttpServletResponse resp)  throws ServletException, IOException;
	protected abstract void responseProcessing(HttpServletResponse resp);
	
}
