package it.csi.qgisagri.agriapi.config;

import java.io.IOException;

import javax.servlet.DispatcherType;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.log4j.Logger;

import it.csi.iride2.policy.entity.Identita;
import it.csi.papua.papuaserv.dto.gestioneutenti.Ruolo;
import it.csi.papua.papuaserv.dto.gestioneutenti.ws.UtenteAbilitazioni;
import it.csi.papua.papuaserv.exception.InternalException;
import it.csi.papua.papuaserv.presentation.rest.profilazione.client.PapuaservProfilazioneServiceFactory;
import it.csi.qgisagri.agriapi.util.AgriApiConstants;


@WebFilter(dispatcherTypes = {DispatcherType.REQUEST }, urlPatterns = { "/json/layer/*" })
public class AuthenticationFilter implements Filter {
  
  protected static final Logger logger     = Logger.getLogger(AgriApiConstants.LOGGING.LOGGER_NAME + ".config");

  
	public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain) throws IOException, ServletException {

    HttpServletRequest request = (HttpServletRequest) req;
    HttpServletResponse response = (HttpServletResponse) resp;
	  
	  logger.debug("--- AuthenticationInterceptor.preHandle ---");
    logger.debug("Request URL: " + request.getRequestURL());
    logger.debug("Controllo autenticazione.");

    //controllo che ci sia un'identita in sessione
    Identita identita = (Identita) request.getSession().getAttribute("identita");
    if(identita==null)
    {
      throw new ServletException(AgriApiConstants.ERRORS.SESSION_EXPIRED);
    }
    else
    {
      UtenteAbilitazioni utenteAbilitazioni = (UtenteAbilitazioni) request.getSession().getAttribute("utenteAbilitazioni");
      if(utenteAbilitazioni==null)
      {
        //se utenteabilitazioni non è in sessione lo carico
        Ruolo[] ruoli;
        try
        {
          
          logger.debug("IDENTITA");
          logger.debug("codice fiscale:  " + identita.getCodFiscale());
          logger.debug("nome:  " + identita.getNome() + " " + identita.getCognome());
          logger.debug("livello:  " + identita.getLivelloAutenticazione());

          ruoli = PapuaservProfilazioneServiceFactory.getRestServiceClient().findRuoliForPersonaInApplicazione(
              identita.getCodFiscale(), identita.getLivelloAutenticazione(), AgriApiConstants.ID_PROCEDIMENTO);
          logger.debug("chiamata a findRuoliForPersonaInApplicazione terminata ");
          if(ruoli!=null && ruoli.length>0) {
            
            logger.debug("Ruoli trovati");
            logger.debug("Ruolo: " + ruoli[0].getCodice());

            utenteAbilitazioni = PapuaservProfilazioneServiceFactory.getRestServiceClient().login(
              identita.getCodFiscale(), identita.getCognome(), identita.getNome(),
              identita.getLivelloAutenticazione(),
             AgriApiConstants.ID_PROCEDIMENTO, ruoli[0].getCodice());
            request.getSession().setAttribute("utenteAbilitazioni", utenteAbilitazioni);
            logger.debug("TUTTO OK");

          }
          else {
            logger.debug("Nessun ruolo trovato");
            //throw new ServletException(AgriApiConstants.ERRORS.ACCESS_FORBIDDEN);
            // Volutamente connesso, questa situazione viene intercettata dalle API e viene restituito un messaggio parlante all'utente
          }
        }
        catch (InternalException e)
        {
          throw new ServletException(AgriApiConstants.ERRORS.ACCESS_ERROR);
        }

      }
      
      if(utenteAbilitazioni!=null && !identita.getCodFiscale().equals(utenteAbilitazioni.getCodiceFiscale()))
      {
        throw new ServletException(AgriApiConstants.ERRORS.ACCESS_FORBIDDEN);
      }
    }
		// pass the request along the filter chain
		chain.doFilter(request, response);
	}

	
	public void init(FilterConfig fConfig) throws ServletException {
		// TODO Auto-generated method stub
	}

  public void destroy() {
    // TODO Auto-generated method stub
  }

}
