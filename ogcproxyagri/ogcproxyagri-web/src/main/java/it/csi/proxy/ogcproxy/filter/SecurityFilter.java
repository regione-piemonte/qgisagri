package it.csi.proxy.ogcproxy.filter;

import it.csi.proxy.ogcproxy.util.JwtManager;
import it.csi.proxy.ogcproxy.util.Utilities;
import it.csi.proxy.ogcproxy.vo.RequestVo;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Enumeration;

import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.SignatureException;
import io.jsonwebtoken.UnsupportedJwtException;

public class SecurityFilter extends AbstractFilter {
	
	public static final String AUTH_ID_MARKER = "Shib-Iride-IdentitaDigitale";
    protected FilterConfig config;
    
	@Override
	public void init(FilterConfig config) throws ServletException {
		super.init(config);
		this.config = config;
	}

	public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    	doLog("SecurityFilter.doFilter - START");
    	String requestStr = Utilities.getFullURL(request);
    	doLog("SecurityFilter.doFilter - Requested URI [" + requestStr + "]");   
    	
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        ServletContext context = config.getServletContext();

		String userid = httpRequest.getHeader(AUTH_ID_MARKER);
        boolean enableJwt = context.getInitParameter("enable-jwt").equalsIgnoreCase("true");
        
        if (enableJwt) {
            HttpServletResponse httpResponse = (HttpServletResponse) response;

            String tokenContext = context.getInitParameter("token-context");
            String userKey = context.getInitParameter("user-key");
            String featureKey = context.getInitParameter("feature-key");
            
    		if (httpRequest.getPathInfo().contains(tokenContext)) {
    			String user = userid;
    			if (user==null) {
    				user = httpRequest.getParameter(userKey);
    			}
    			String feature = httpRequest.getParameter(featureKey);
    			doLog("SecurityFilter.doFilter - creating token with user: "+user+", subject: " + feature);
    			String token = JwtManager.createToken(user, feature);
    			response.getWriter().write(token);
    			doLog("SecurityFilter.doFilter - returned token ["+token+"]");
    			return;
    		}
    		
    		RequestVo r = Utilities.getRequestVo(request);
    		
    		String hostlessUrl = r.getHostlessUrl();
    		int index1 = hostlessUrl.indexOf('/');
    		int index2 = hostlessUrl.indexOf('/', index1+1);
    		String token = hostlessUrl.substring(index1+1, index2);
    		try {
    			Jws<Claims> claims = JwtManager.parseToken(token);
    			doLog("SecurityFilter.doFilter - parsed claims ["+claims+"]");
    		} catch (ExpiredJwtException e) {
    			doLog("SecurityFilter.doFilter - ExpiredJwtException - sending 401 / UNAUTHORIZED:  ["+e.getMessage()+"]");
    			//httpResponse.sendError(HttpServletResponse.SC_UNAUTHORIZED, e.getMessage());
    			//e.printStackTrace();
    			sendXRed(httpRequest, httpResponse);
    		} catch (UnsupportedJwtException e) {
    			doLog("SecurityFilter.doFilter - UnsupportedJwtException - sending 401 / UNAUTHORIZED:  ["+e.getMessage()+"]");
    			//httpResponse.sendError(HttpServletResponse.SC_UNAUTHORIZED, e.getMessage());
    			//e.printStackTrace();
    			sendXRed(httpRequest, httpResponse);
    		} catch (MalformedJwtException e) {
    			doLog("SecurityFilter.doFilter - MalformedJwtException - sending 401 / UNAUTHORIZED:  ["+e.getMessage()+"]");
    			//httpResponse.sendError(HttpServletResponse.SC_UNAUTHORIZED, e.getMessage());
    			//e.printStackTrace();
    			sendXRed(httpRequest, httpResponse);
    		} catch (SignatureException e) {
    			doLog("SecurityFilter.doFilter - SignatureException - sending 401 / UNAUTHORIZED:  ["+e.getMessage()+"]");
    			//httpResponse.sendError(HttpServletResponse.SC_UNAUTHORIZED, e.getMessage());
    			//e.printStackTrace();
    			sendXRed(httpRequest, httpResponse);
    		} catch (IllegalArgumentException e) {
    			doLog("SecurityFilter.doFilter - IllegalArgumentException - sending 401 / UNAUTHORIZED:  ["+e.getMessage()+"]");
    			//httpResponse.sendError(HttpServletResponse.SC_UNAUTHORIZED, e.getMessage());
    			//e.printStackTrace();
    			sendXRed(httpRequest, httpResponse);
    		}
        	
        }
		chain.doFilter(request, response);

    }    
	
	 public void sendXRed(HttpServletRequest request, HttpServletResponse resp) throws IOException {

	      ServletContext context = config.getServletContext();
	      // Get the absolute path of the image
	      String filename = context.getRealPath("WEB-INF/classes/img/X-RED-1.png");
	      // retrieve mimeType dynamically
	      String mime = context.getMimeType(filename);
	      if (mime == null) {
	        resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
	        return;
	      }

	      resp.setContentType(mime);
	      File file = new File(filename);
	      resp.setContentLength((int)file.length());

	      FileInputStream in = new FileInputStream(file);
	      OutputStream out = resp.getOutputStream();

	      // Copy the contents of the file to the output stream
	       byte[] buf = new byte[1024];
	       int count = 0;
	       while ((count = in.read(buf)) >= 0) {
	         out.write(buf, 0, count);
	      }
	    out.close();
	    in.close();

	}
}
