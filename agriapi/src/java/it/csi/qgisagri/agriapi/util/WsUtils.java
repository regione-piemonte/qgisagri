package it.csi.qgisagri.agriapi.util;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;
import java.util.Random;
import java.util.ResourceBundle;

import javax.xml.ws.BindingProvider;

import org.apache.cxf.endpoint.Client;
import org.apache.cxf.frontend.ClientProxy;
import org.apache.cxf.message.Message;

import it.csi.qgisagri.agriapi.integration.ws.smrcomms.smrcommsrvservice.SmrcommSrvService;
import it.csi.smrcomms.siapcommws.interfacews.smrcomm.SmrcommSrv;


public class WsUtils
{
 
  public static  String        SIAPCOMM_WSDL                = null;

  public static final Random RANDOM                = new Random(System.currentTimeMillis());
  public static final int    SHORT_CONNECT_TIMEOUT = 1000;
  public static final int    SHORT_REQUEST_TIMEOUT = 5000;
  /* 10 secondi */
  public static final int    MAX_CONNECT_TIMEOUT   = 10 * 1000;
  /* 280 secondi */
  public static final int    MAX_REQUEST_TIMEOUT   = 280 * 1000;
  public static final int[]  SHORT_TIMEOUT         = new int[]
  { SHORT_CONNECT_TIMEOUT, SHORT_REQUEST_TIMEOUT };
  public static final int[]  MAX_TIMEOUT           = new int[]
  { MAX_CONNECT_TIMEOUT, MAX_REQUEST_TIMEOUT };
  static
  {
    ResourceBundle res = ResourceBundle.getBundle("config");
    SIAPCOMM_WSDL = res.getString("siapcomm.wsdl");
  }

  public void setTimeout(BindingProvider provider, int[] timeouts) throws MalformedURLException
  {
    Map<String, Object> requestContext = provider.getRequestContext();
    requestContext.put("javax.xml.ws.client.connectionTimeout", timeouts[0]);
    requestContext.put("javax.xml.ws.client.receiveTimeout", timeouts[1]);
  }

  
  public SmrcommSrv getSiapComm() throws MalformedURLException
  {
    final SmrcommSrv smrcomm = new SmrcommSrvService(new URL(SIAPCOMM_WSDL)).getSmrcommSrvPort();
    Client client = ClientProxy.getClient(smrcomm);
    client.getRequestContext().put(Message.ENDPOINT_ADDRESS, SIAPCOMM_WSDL);
    return smrcomm;
  }
}