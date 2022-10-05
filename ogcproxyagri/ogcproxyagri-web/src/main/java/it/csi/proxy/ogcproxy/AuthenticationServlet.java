package it.csi.proxy.ogcproxy;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.concurrent.ThreadLocalRandom;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import it.csi.proxy.ogcproxy.pojo.Authorization;
import it.csi.proxy.ogcproxy.pojo.AuthorizationManager;

/**
 * Servlet implementation class AuthenticationServlet
 */
public class AuthenticationServlet extends AbstractServlet {
	private static final long serialVersionUID = 1L;
	public static final String AUTH_ID_MARKER = "Shib-Iride-IdentitaDigitale";

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse
	 *      response)
	 */
	protected void doGet(HttpServletRequest request,
			HttpServletResponse response) throws ServletException, IOException {
		doLog("AuthenticationServlet.doGet - START");
		
		try {
	        String result = "";
	        
			if (request.getHeader(AUTH_ID_MARKER)==null) {
				doLog("AuthenticationServlet.doGet - no auth header found, redirecting 401 error");
				response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid Auth Id Marker.");
			}
			
			String id = request.getHeader(AUTH_ID_MARKER);
			doLog("AuthenticationServlet.doGet - header found: " + id);
			
			// nextInt is normally exclusive of the top value,
			// so add 1 to make it inclusive
			int min = 10000000;
			int max = 90000000;
			int randomNum = ThreadLocalRandom.current().nextInt(min, max + 1);
			result = "<token>" + randomNum + "</token>";
	        
			if (AuthorizationManager.theInstance.getMap().containsKey(id)) {
				Authorization authorization = AuthorizationManager.theInstance.getMap().get(id);
				doLog("AuthenticationServlet.doGet - cache found: " + id + " - " + authorization.getOneShotToken() + " - " + authorization.getStart());
				AuthorizationManager.theInstance.getMap().put(authorization.getOneShotToken(), null);
				authorization.setOneShotToken(Integer.toString(randomNum));
				authorization.setStart(System.currentTimeMillis());
				AuthorizationManager.theInstance.getMap().put(id, authorization);
				AuthorizationManager.theInstance.getMap().put(Integer.toString(randomNum), authorization);
				doLog("AuthenticationServlet.doGet - cache updated: " + id + " - " + authorization.getOneShotToken() + " - " + authorization.getStart());
			} else {
				Authorization authorization = new Authorization();
				authorization.setToken(id);
				authorization.setOneShotToken(Integer.toString(randomNum));
				authorization.setStart(System.currentTimeMillis());
				AuthorizationManager.theInstance.getMap().put("token", authorization);
				doLog("AuthenticationServlet.doGet - cache created: " + id + " - " + authorization.getOneShotToken() + " - " + authorization.getStart());
			}
			
			PrintWriter out = response.getWriter();
	        response.setContentType("application/json");
	        response.setCharacterEncoding("UTF-8");
	        out.print(result);
	        out.flush();   
		} catch (Exception e) {
		
		} finally {
			doLog("AuthenticationServlet.doGet - START");
		}
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse
	 *      response)
	 */
	protected void doPost(HttpServletRequest request,
			HttpServletResponse response) throws ServletException, IOException {
		doLog("AuthenticationServlet.doPost - START");
		// TODO VERIFICARE SE SIA CORRETTO REDIRIGERE SU DOGET DATO CHE MAPSERVER NON SUPPORTA LA POST
		doGet(request, response);
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
