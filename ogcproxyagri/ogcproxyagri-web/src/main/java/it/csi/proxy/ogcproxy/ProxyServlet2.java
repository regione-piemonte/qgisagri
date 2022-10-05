package it.csi.proxy.ogcproxy;

import it.csi.proxy.ogcproxy.util.Constants;
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

/**
 * Servlet implementation class ProxyServlet
 */
public class ProxyServlet2 extends AbstractServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse
	 *      response)
	 */
	protected void doGet(HttpServletRequest request,
			HttpServletResponse response) throws ServletException, IOException {
		doLog("ProxyServlet.doGet - START");
		RequestVo r = Utilities.getRequestVo(request);
		if (!r.getRequestType().equals(Constants.GETCAPABILITIES))
			doGetOldImpl(r, response);
		else {
			try {
				handleGetCapabilities(r, response);
			} catch (JAXBException e) {
				// TODO Gestire l'eccezione
				e.printStackTrace();
			}
		}
	}

	/**
	 * Metodo che prende in ingresso la request parsificata e la response
	 * Gestisce la sola getCapabilities in modo da poter esporre al fruitore i soli layers scelti dall'erogatore del servizio
	 * @param r
	 * @param response
	 * @throws JAXBException
	 */
	private void handleGetCapabilities(RequestVo r,
			HttpServletResponse response) throws JAXBException {
		// Create JAXB context for WMS 1.3.0
		JAXBContext context = JAXBContext.newInstance("net.opengis.wms.v_1_3_0");
		// Use the created JAXB context to construct an unmarshaller
		Unmarshaller unmarshaller = context.createUnmarshaller();
		// Unmarshal the given URL, retrieve WMSCapabilities element
		//JAXBElement<WMSCapabilities> wmsCapabilitiesElement = unmarshaller
		//		.unmarshal(new StreamSource(r.getOriginalUrl()), WMSCapabilities.class);
		ServiceVo requestedService = Mocks.getMockServiceVo();// TODO
		JAXBElement<WMSCapabilities> wmsCapabilitiesElement = unmarshaller
				.unmarshal(new StreamSource(
						"http://"+requestedService.getHost()+":"+requestedService.getPort()
						+r.getHostlessUrl()), WMSCapabilities.class);
		// Retrieve WMSCapabilities instance
		WMSCapabilities clone = null;
		WMSCapabilities wmsCapabilities = wmsCapabilitiesElement.getValue();
		wmsCapabilities.copyTo(clone);
		// Iterate over layers, print out layer names
		for (Layer layer : wmsCapabilities.getCapability().getLayer().getLayer()) {
			System.out.println(layer.getName());
		}
		
//		WMSCapabilities outputCap =  wmsCapabilities;
//		outputCap.getCapability().set
	}

	private void doGetOldImpl(RequestVo r,
			HttpServletResponse response) throws IOException,
			ClientProtocolException {
		CloseableHttpClient httpclient = HttpClients.createDefault();
		try {
			
			String caller = r.getCaller();
			String reqService = r.getService();

			ServiceVo requestedService = Mocks.getMockServiceVo();// TODO
			// db.getServiceForCaller(caller,reqService);
//			request.setAttribute(Constants.SERVICE_REQ_PARAM, requestedService);
			HttpHost target = new HttpHost(requestedService.getHost(),
					requestedService.getPort());
			HttpGet req = new HttpGet(r.getHostlessUrl());

			boolean needsProxy = this.getServletContext().getInitParameter(Constants.NEEDS_PROXY).equalsIgnoreCase("true");
			if (needsProxy 
					&& !requestedService.getHost().contains("csi.it")
					&& !requestedService.getHost().contains("nivolapiemonte.it") ) {
				HttpHost proxy = new HttpHost("<HOSTNAME>", <PORT>, "<PROTOCOL>");
				RequestConfig config = RequestConfig.custom().setProxy(proxy)
						.build();
				doLog(r.toString());
				req.setConfig(config);
			}

			CloseableHttpResponse resp = httpclient.execute(target, req);
			// modifies response
			response.setContentType(resp.getEntity().getContentType()
					.getValue());
			response.setContentLength(new Long(resp.getEntity()
					.getContentLength()).intValue());
			if (isTextResponse(resp.getEntity().getContentType()
					.getValue())) {
				doLog("Text response");
				// obtains response's output stream
				BufferedReader rd = new BufferedReader(new InputStreamReader(
						resp.getEntity().getContent()));
				StringBuilder content = new StringBuilder();
				String line;
				while (null != (line = rd.readLine())) {
					content.append(line);
				}
				doLog(requestedService.getHost());
//				TODO VERIFICARE ED EVENTUALMENTE MIGLIORARE LA LOGICA DI REPLACE
				String newS = null;				
				PrintWriter pw = response.getWriter();
				if (content.toString().contains(generateHostToCall(r, requestedService))) {
					doLog("Some contents to be replaced");
					newS = content.toString().replace(
							generateHostToCall(r, requestedService),
							generateHostToShowToCaller(r));
					pw.append(newS);
				}		
				else {
					doLog("No contents to be replaced");
					pw.append(content.toString());
				}
				doLog("["+pw.toString()+"]");
				pw.flush();
				pw.close();
			} else {
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
	}

	private String generateHostToShowToCaller(RequestVo r) {
		StringBuilder sb = new StringBuilder();
		sb.append(r.getScheme());
		sb.append("://");
		sb.append(r.getServerName());
		sb.append(":");
		sb.append(r.getServerPort());
		sb.append("/ogcproxy");
		return sb.toString();
	}

	private String generateHostToCall(RequestVo r, ServiceVo requestedService) {
		StringBuilder sb = new StringBuilder();
		sb.append(r.getScheme());
		sb.append("://");
		sb.append(requestedService.getHost());
		return sb.toString();
	}

	private boolean isTextResponse(String contentType) {
		return contentType.trim().toLowerCase().startsWith("text");
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
	protected HttpServletResponse doGetImpl(HttpServletRequest req, HttpServletResponse resp) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	protected void responseProcessing(HttpServletResponse resp) {
		// TODO Auto-generated method stub
		
	}

}
