package it.csi.qgisagri.agriapi.presentation.servlet;

import java.io.IOException;
import java.lang.management.ManagementFactory;

import javax.management.ObjectName;
import javax.servlet.ServletException;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;

import it.csi.qgisagri.agriapi.business.PianoColturaleBean;
import it.csi.qgisagri.agriapi.config.BeansConfig;
import it.csi.qgisagri.agriapi.dto.GestioneCookieDTO;
import it.csi.qgisagri.agriapi.util.AgriApiConstants;

public class RedirectServlet extends HttpServlet
{
  /** serialVersionUID */
  private static final long     serialVersionUID = 7743333684332642316L;
  public static final String    URL_REDIRECT     = "/redirect/";
  protected static final Logger logger           = Logger.getLogger(AgriApiConstants.LOGGING.LOGGER_NAME + ".business");

  public final PianoColturaleBean pianoColturaleBean = (PianoColturaleBean) BeansConfig.getBean("pianoColturaleBean");
  
  
  @Override
  public void service(HttpServletRequest request, HttpServletResponse response) throws IOException, ServletException
  {
    Object port = null;
    Object address = null;
    try
    {
      port = ManagementFactory.getPlatformMBeanServer()
          .getAttribute(new ObjectName("jboss.as:socket-binding-group=standard-sockets,socket-binding=http"), "port");
      address = ManagementFactory.getPlatformMBeanServer().getAttribute(new ObjectName("jboss.as:interface=public"),
          "inet-address");
      logger.info("[RedirectServlet:service] port = " + port);
      logger.info("[RedirectServlet:service] address = " + address);
    
      String queryStr = request.getQueryString();
      
      String[] query = queryStr.split("&");
      GestioneCookieDTO cookieDTO = null;
      if(query!=null)
      { 
        for(String item:query)
        {
          if(item.startsWith("token="))
          {
            cookieDTO = pianoColturaleBean.getCookiesFromToken(item.split("=")[1]);
            Cookie cookie = new Cookie(cookieDTO.getCookie1().split("##")[0], cookieDTO.getCookie1().split("##")[1]);
            cookie.setPath("/");
            //cookie.setMaxAge(3600);
            cookie.setHttpOnly(true);
            response.addCookie(cookie);
           
            Cookie cookie2 = new Cookie(cookieDTO.getCookie2().split("##")[0], cookieDTO.getCookie2().split("##")[1]);
            cookie2.setPath("/");
            //cookie2.setMaxAge(3600);
            cookie2.setHttpOnly(true);
            response.addCookie(cookie2);
            
            /*response.addCookie(new Cookie(cookieDTO.getCookie2().split("##")[0], cookieDTO.getCookie2().split("##")[1]));
            if(cookieDTO.getCookie3()!=null) response.addCookie(new Cookie(cookieDTO.getCookie3().split("##")[0], cookieDTO.getCookie3().split("##")[1]));
            if(cookieDTO.getCookie4()!=null) response.addCookie(new Cookie(cookieDTO.getCookie4().split("##")[0], cookieDTO.getCookie4().split("##")[1]));
            if(cookieDTO.getCookie5()!=null) response.addCookie(new Cookie(cookieDTO.getCookie5().split("##")[0], cookieDTO.getCookie5().split("##")[1]));*/
          }
        }
      }
      response.addCookie(new Cookie("PORTALE", "SISTEMAPIEMONTE"));
      response.sendRedirect(cookieDTO.getParametro());//E' la URL del documentale, messo nella colonna PARAMETRO della tabella
    }
    catch (Exception e)
    {
      logger.error("[RedirectServlet:service] ManagementFactory.getPlatformMBeanServer().getAttribute() error = ",
          e);
      throw new ServletException(e);
    }
  }
  
  
}