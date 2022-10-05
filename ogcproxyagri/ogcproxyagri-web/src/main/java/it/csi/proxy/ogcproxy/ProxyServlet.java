package it.csi.proxy.ogcproxy;

import it.csi.proxy.ogcproxy.util.Constants;
import it.csi.proxy.ogcproxy.util.JwtManager;
import it.csi.proxy.ogcproxy.util.Mocks;
import it.csi.proxy.ogcproxy.util.Utilities;
import it.csi.proxy.ogcproxy.vo.RequestVo;
import it.csi.proxy.ogcproxy.vo.ServiceVo;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;
import javax.xml.transform.stream.StreamSource;

import net.opengis.wms.v_1_3_0.Layer;
import net.opengis.wms.v_1_3_0.WMSCapabilities;

import org.apache.http.HttpHost;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;

import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.SignatureException;
import io.jsonwebtoken.UnsupportedJwtException;

/**
 * Servlet implementation class ProxyServlet
 */
public class ProxyServlet extends AbstractServlet {
	private static final long serialVersionUID = 1L;

	@Override
	protected HttpServletResponse doGetImpl(HttpServletRequest request,
			HttpServletResponse response) throws ServletException, IOException {
		CloseableHttpClient httpclient = HttpClients.createDefault();
		try {
			
			RequestVo r = Utilities.getRequestVo(request);
	        boolean enableJwt = this.getServletContext().getInitParameter("enable-jwt").equalsIgnoreCase("true");
	        String token = null;
	        
	        if (enableJwt) {
				
				String hostlessUrl = r.getHostlessUrl();
				int index1 = hostlessUrl.indexOf('/');
				int index2 = hostlessUrl.indexOf('/', index1+1);
				token = hostlessUrl.substring(index1+1, index2);
				
				r.setOriginalUrl(r.getOriginalUrl().replace("/"+token, ""));
	        }
	        
			String caller = r.getCaller();
			String reqService = r.getService();

			String sourceUrl = this.getServletContext().getInitParameter(Constants.SOURCE_URL);
			String destHost = this.getServletContext().getInitParameter(Constants.DEST_HOST);
			Integer destPort = Integer.parseInt(this.getServletContext().getInitParameter(Constants.DEST_PORT));
			boolean needsProxy = this.getServletContext().getInitParameter(Constants.NEEDS_PROXY).equalsIgnoreCase("true");
			String proxyHost = this.getServletContext().getInitParameter(Constants.PROXY_HOST);
			Integer proxyPort = Integer.parseInt(this.getServletContext().getInitParameter(Constants.PROXY_PORT));
			String proxyScheme = this.getServletContext().getInitParameter(Constants.PROXY_SCHEME);
			
			// db.getServiceForCaller(caller,reqService);
			HttpHost target = new HttpHost(destHost, destPort);
			HttpGet req = new HttpGet(r.getHostlessUrl());

			doLog("ProxyServlet: testing proxy");
			if (needsProxy) {
				HttpHost proxy = new HttpHost(proxyHost, proxyPort, proxyScheme);
				RequestConfig config = RequestConfig.custom().setProxy(proxy)
						.build();
				doLog(r.toString());
				req.setConfig(config);
				doLog("ProxyServlet: proxy set");
			}

			doLog("ProxyServlet: contacting " + target + " - " + req);
			CloseableHttpResponse resp = httpclient.execute(target, req);
			// modifies response
			response.setContentType(resp.getEntity().getContentType()
					.getValue());
			if (isTextResponse(resp.getEntity().getContentType()
					.getValue())) {
				doLog("ProxyServlet: Text response");
				// obtains response's output stream
				BufferedReader rd = new BufferedReader(new InputStreamReader(
						resp.getEntity().getContent()));
				StringBuilder content = new StringBuilder();
				String line;
				while (null != (line = rd.readLine())) {
					content.append(line);
				}
				doLog("ProxyServlet: " + sourceUrl);
//				TODO VERIFICARE ED EVENTUALMENTE MIGLIORARE LA LOGICA DI REPLACE
				String newS = null;				
				PrintWriter pw = response.getWriter();
				int newContentLength = 0;
				if (content.toString().contains(generateHostToCall(destHost, destPort))) {
					newS = content.toString().replace(
							generateHostToCall(destHost, destPort),
							generateHostToShowToCaller(r) + (enableJwt&&token!=null&&token.length()>0 ? "/"+token : ""));
					newContentLength = newS.length();
					doLog("Some contents to be replaced, moving response length from "+content.length()+" to "+newContentLength);
					//response.setContentLength(newContentLength);
					pw.append(newS);
				}		
				else {
					doLog("No contents to be replaced");
					pw.append(content.toString());
					newContentLength = content.length();
				}
				doLog("["+pw.toString()+"]");
				pw.flush();
				pw.close();
			} else {
				response.setContentLength(new Long(resp.getEntity()
						.getContentLength()).intValue());
				doLog("Binary response");
				resp.getEntity().writeTo(response.getOutputStream());
			}
			try {
				doLog("----------------------------------------");
				doLog(resp.getStatusLine().toString());
			} finally {
				resp.close();
			}
		} finally {
			httpclient.close();
		}
		
		return response;
	}

	private String generateHostToShowToCaller(RequestVo r) {
		StringBuilder sb = new StringBuilder();
		sb.append(r.getScheme());
		sb.append("://");
		sb.append(r.getServerName());
		if (r.getServerPort()!=443) {
			sb.append(":");
			sb.append(r.getServerPort());
		}
		sb.append("/ogcproxy");
		return sb.toString();
	}

	private String generateHostToCall(RequestVo r, ServiceVo requestedService) {
		StringBuilder sb = new StringBuilder();
		sb.append(requestedService.getPort()==443?"https":"http");
		sb.append("://");
		sb.append(requestedService.getHost());
		return sb.toString();
	}

	private String generateHostToCall(String host, int port) {
		StringBuilder sb = new StringBuilder();
		sb.append(port==443?"https":"http");
		sb.append("://");
		sb.append(host);
		sb.append(":"+port);
		return sb.toString();
	}

	private boolean isTextResponse(String contentType) {
		return (contentType.trim().toLowerCase().startsWith("text")
				|| contentType.trim().equalsIgnoreCase("application/vnd.ogc.wms_xml"));
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse
	 *      response)
	 */
	protected void doPost(HttpServletRequest request,
			HttpServletResponse response) throws ServletException, IOException {
		doLog("ProxyServlet.doPost - START");
		// TODO VERIFICARE SE SIA CORRETTO REDIRIGERE SU DOGET DATO CHE MAPSERVER NON SUPPORTA LA POST
		doGet(request, response);
	}

	@Override
	protected void responseProcessing(HttpServletResponse resp) {
		// TODO Auto-generated method stub
		
	}

}
