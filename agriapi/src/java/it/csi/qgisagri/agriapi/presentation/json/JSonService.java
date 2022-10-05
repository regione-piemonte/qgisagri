package it.csi.qgisagri.agriapi.presentation.json;

import java.io.File;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import javax.naming.NamingException;
import javax.servlet.ServletException;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.ResponseBuilder;

import org.apache.commons.io.FileUtils;
import org.apache.log4j.Logger;
import org.locationtech.jts.io.ParseException;
import org.opengis.feature.simple.SimpleFeature;

import it.csi.iride2.policy.entity.Identita;
import it.csi.papua.papuaserv.dto.gestioneutenti.Ruolo;
import it.csi.papua.papuaserv.dto.gestioneutenti.ws.UtenteAbilitazioni;
import it.csi.papua.papuaserv.exception.InternalException;
import it.csi.papua.papuaserv.presentation.rest.profilazione.client.PapuaservProfilazioneServiceFactory;
import it.csi.qgisagri.agriapi.business.PianoColturaleBean;
import it.csi.qgisagri.agriapi.config.BeansConfig;
import it.csi.qgisagri.agriapi.dto.AgriAPIResult;
import it.csi.qgisagri.agriapi.dto.DatiSuoloDTO;
import it.csi.qgisagri.agriapi.dto.EsitoDTO;
import it.csi.qgisagri.agriapi.dto.GeoJSONFeatureCollection;
import it.csi.qgisagri.agriapi.dto.GestioneCookieDTO;
import it.csi.qgisagri.agriapi.dto.ImmagineAppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.ParametroDTO;
import it.csi.qgisagri.agriapi.dto.RuoloDTO;
import it.csi.qgisagri.agriapi.dto.SuoloRilevatoDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.AllegatoParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.AziendaListeLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ClasseEleggibilitaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.DichiarazioneConsistenzaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.FoglioAziendaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ListaLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.MotivoSospensioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ParticellaLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.mygeojson.MyGeoJsonFeature;
import it.csi.qgisagri.agriapi.dto.mygeojson.MyGeoJsonFeatureCollection;
import it.csi.qgisagri.agriapi.dto.pcg.AppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.UnarAppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.UtilizzoParticellaDTO;
import it.csi.qgisagri.agriapi.util.AgriApiConstants;

@Consumes(
{ "application/json" })
@Produces(
{ "application/json" })
@Path("/")
public class JSonService
{
  public final PianoColturaleBean pianoColturaleBean = (PianoColturaleBean) BeansConfig.getBean("pianoColturaleBean");
  public static final String      AUTH_ID_MARKER     = "Shib-Iride-IdentitaDigitale";
  protected static final Logger   logger             = Logger
      .getLogger(AgriApiConstants.LOGGING.LOGGER_NAME + ".presentation");
  private static final String     THIS_CLASS         = JSonService.class.getSimpleName();

  /******************************************************************************
   * API IN LETTURA
   ******************************************************************************/

  
  
  
  @GET
  @Path("/layer/2.0/getLista")
  public AgriAPIResult<List<ListaLavorazioneDTO>> getLista(@Context HttpServletRequest request,
      @QueryParam("codiceRuolo") String codiceRuolo) throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getLista";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN. INI TST");
    }

    if (codiceRuolo != null)
      selezionaRuolo(request, codiceRuolo);
    UtenteAbilitazioni utenteAbilitazioni = getUtenteAbilitazioni(request.getSession());
    List<ListaLavorazioneDTO> elenco = null;
    AgriAPIResult<List<ListaLavorazioneDTO>> result = new AgriAPIResult<List<ListaLavorazioneDTO>>();
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      elenco = pianoColturaleBean.getElencoListeLavorazione(utenteAbilitazioni);

      if (elenco != null && elenco.size() > 0)
      {
        result.setDati(elenco);
      }
      else
      {
        esitoDTO.setEmptyMessage("Non sono state trovate liste di lavorazione disponibili.");
      }
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }

    return result;
  }

  @GET
  @Path("/layer/2.0/getRuoli")
  public AgriAPIResult<List<RuoloDTO>> getRuoli(@Context HttpServletRequest request,@QueryParam("versionePlugin") String versionePlugin)
      throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getRuoli";
    logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    
    AgriAPIResult<List<RuoloDTO>> result = new AgriAPIResult<List<RuoloDTO>>();
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      
      Map<String, String> mapParametri = pianoColturaleBean.getParametri(new String[]
          { AgriApiConstants.PARAMETRI.VERSIONE_PLUGIN});

      String versioneMinimaPlugin = mapParametri.get(AgriApiConstants.PARAMETRI.VERSIONE_PLUGIN);
      
      if(versioneMinimaPlugin!=null && versionePlugin!=null && versionePlugin.trim().length()>0)
      {
        //verifico che versionePlugin sia >= a versioneMinimaPlugin
        String[] versioneMinimaPluginVct = versioneMinimaPlugin.split("\\."); //verrà diviso in 3 parti
        String[] versionePluginVct = versionePlugin.split("\\."); //verrà diviso in 3 parti 
        
        if( (Long.parseLong(versionePluginVct[0]) < Long.parseLong(versioneMinimaPluginVct[0]))
            || (Long.parseLong(versionePluginVct[1]) < Long.parseLong(versioneMinimaPluginVct[1]) ) 
            || (  (Long.parseLong(versionePluginVct[1]) == Long.parseLong(versioneMinimaPluginVct[1])) && (Long.parseLong(versionePluginVct[2]) < Long.parseLong(versioneMinimaPluginVct[2]))  )
            )
        {
          esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
          esitoDTO.setEmptyMessage("E' necessario aggiornare la versione del plugin qgisagri: versione minima "+versioneMinimaPlugin);
          return result;
        }
      }
      
      Identita identita = (Identita) request.getSession().getAttribute("identita");
      if (identita == null)
      {
        throw new ServletException(AgriApiConstants.ESITO.MESSAGGIO.SESSION_EXPIRED);
      }
      else
      {

        UtenteAbilitazioni utenteAbilitazioni = (UtenteAbilitazioni) request.getSession().getAttribute("utenteAbilitazioni");

        Ruolo[] ruoli;
        try
        {
          ruoli = PapuaservProfilazioneServiceFactory.getRestServiceClient().findRuoliForPersonaInApplicazione(
              identita.getCodFiscale(), identita.getLivelloAutenticazione(), AgriApiConstants.ID_PROCEDIMENTO);

          if (ruoli != null && ruoli.length > 0)
          {
            List<RuoloDTO> elencoRuoli = new ArrayList<RuoloDTO>();
            for (Ruolo ruolo : ruoli)
              {
                UtenteAbilitazioni u = PapuaservProfilazioneServiceFactory.getRestServiceClient().login(
                  identita.getCodFiscale(), identita.getCognome(), identita.getNome(),
                  identita.getLivelloAutenticazione(),
                  AgriApiConstants.ID_PROCEDIMENTO, ruolo.getCodice());
                elencoRuoli.add(new RuoloDTO(u.getIdUtenteLogin(), ruolo.getCodice(), ruolo.getDescrizione(),identita.getCodFiscale()));
              }

            // TODO remove -> ruolo temporaneo
           // elencoRuoli.add(new RuoloDTO(-2l, "TEMP_ADMIN", "Amministratore - ruolo creato per i test",identita.getCodFiscale()));

            result.setDati(elencoRuoli);
          }
          else
          {
            esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
            esitoDTO.setEmptyMessage("Non esistono ruoli disponibili per l'utente connesso.");
          }
          
        }
        catch (InternalException e)
        {
          throw new ServletException(AgriApiConstants.ESITO.MESSAGGIO.ACCESS_ERROR);
        }

        if (utenteAbilitazioni!=null && !identita.getCodFiscale().equals(utenteAbilitazioni.getCodiceFiscale()))
        {
          throw new ServletException(AgriApiConstants.ESITO.MESSAGGIO.ACCESS_FORBIDDEN);
        }
      }
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }

    return result;
  }

  /*
   * 
   * NON LO USIAMO PERCHé IL CODICe RUOLO VIENE PASSATO NELLA GET LISTA
   */
  @GET
  @Path("/layer/2.0/selezionaRuolo")
  public AgriAPIResult<List<Ruolo>> selezionaRuolo(
      @Context HttpServletRequest request,
      @QueryParam("codiceRuolo") String codiceRuolo)
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<List<Ruolo>> result = new AgriAPIResult<List<Ruolo>>();
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);
    try
    {
      Identita identita = (Identita) request.getSession().getAttribute("identita");
      if (identita == null)
      {
        throw new ServletException(AgriApiConstants.ESITO.MESSAGGIO.SESSION_EXPIRED);
      }
      else
      {
        try
        {

          UtenteAbilitazioni utenteAbilitazioni = (UtenteAbilitazioni) request.getSession()
              .getAttribute("utenteAbilitazioni");
          utenteAbilitazioni = PapuaservProfilazioneServiceFactory.getRestServiceClient().login(
              identita.getCodFiscale(), identita.getCognome(), identita.getNome(),
              identita.getLivelloAutenticazione(),
              AgriApiConstants.ID_PROCEDIMENTO, codiceRuolo);
          request.getSession().setAttribute("utenteAbilitazioni", utenteAbilitazioni);
        }
        catch (InternalException e)
        {
          throw new ServletException(AgriApiConstants.ESITO.MESSAGGIO.ACCESS_ERROR);
        }

      }

    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }

    return result;
  }

  @GET
  @Path("/layer/2.0/getElencoAziende")
  public AgriAPIResult<List<AziendaListeLavorazioneDTO>> getElencoAziende(@Context HttpServletRequest request,
      @QueryParam("idListaLavorazione") int idListaLavorazione,
      @QueryParam("cuaa") String cuaa,
      @QueryParam("escludiLavorate") String escludiLavorate,
      @QueryParam("escludiBloccate") String escludiBloccate,
      @QueryParam("escludiSospese") String escludiSospese)
      throws ClassNotFoundException, SQLException, NamingException
  {

    final String THIS_METHOD = "getElencoAziende";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }

    List<AziendaListeLavorazioneDTO> elenco = null;
    AgriAPIResult<List<AziendaListeLavorazioneDTO>> result = new AgriAPIResult<List<AziendaListeLavorazioneDTO>>();

    EsitoDTO esitoAbilitazioni = verificaAbilitazioniListaLavorazione(getUtenteAbilitazioni(request.getSession()), idListaLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn("[" + THIS_CLASS + "." + THIS_METHOD + "] Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      elenco = pianoColturaleBean.getElencoAziende(idListaLavorazione, cuaa, escludiLavorate, escludiBloccate, escludiSospese);
      if (elenco != null && elenco.size() > 0)
      {
        result.setDati(elenco);
        
        if(cuaa!=null && cuaa.trim().length()>0)
        {
          if(elenco.get(0).getDataLavorazione()!=null && !"N".equals(escludiLavorate))
          {
            esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FILTRI_ERRATI);
            esitoDTO.setMessaggio("L'azienda risulta lavorata: impostare il filtro di ricerca");
          }else if("S".equals(elenco.get(0).getIsSospesa()) && !"N".equals(escludiSospese))
          {
            esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FILTRI_ERRATI);
            esitoDTO.setMessaggio("L'azienda risulta sospesa: impostare il filtro di ricerca");
          }else if(elenco.get(0).getIsAziendaBloccata() && !"N".equals(escludiBloccate))
          {
            esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FILTRI_ERRATI);
            esitoDTO.setMessaggio("L'azienda risulta in carico: impostare il filtro di ricerca");
          }else {
            esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FILTRI_ERRATI);
            esitoDTO.setMessaggio("L'azienda ancora da lavorare: deselezionare i filtri di ricerca");
          }
        }
        
      }
      else
      {
        esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_NO_RECORD);
        esitoDTO.setEmptyMessage("Non sono state trovate aziende disponibili.");
      }
      
      
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }

    return result;
  }

  @GET
  @Path("/layer/2.0/getElencoFogliAzienda")
  public AgriAPIResult<List<FoglioAziendaDTO>> getElencoFogliAzienda(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione )
      throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getElencoFogliAzienda";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    List<FoglioAziendaDTO> elenco = null;
    AgriAPIResult<List<FoglioAziendaDTO>> result = new AgriAPIResult<List<FoglioAziendaDTO>>();
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      elenco = pianoColturaleBean.getElencoFogliAzienda(idEventoLavorazione);

      if (elenco != null && elenco.size() > 0)
      {
        result.setDati(elenco);
      }
      else
      {
        esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
        esitoDTO.setEmptyMessage("Non sono stati trovati fogli disponibili.");
      }
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
    return result;

  }

  @GET
  @Path("/layer/2.0/getSuoliFoglio")
  public AgriAPIResult<GeoJSONFeatureCollection> getSuoliFoglio(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("codiceNazionale") String codiceNazionale, // obbligatorio
      @QueryParam("foglio") long foglio // obbligatorio
  )
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<GeoJSONFeatureCollection> result = new AgriAPIResult<GeoJSONFeatureCollection>();

    final String THIS_METHOD = "getSuoliFoglio";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    UtenteAbilitazioni utenteAbilitazioni = getUtenteAbilitazioni(request.getSession());
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(utenteAbilitazioni, idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    
    try
    {

      if (pianoColturaleBean.isEventoBloccato(idEventoLavorazione, utenteAbilitazioni.getIdUtenteLogin()))
      {
        EsitoDTO esitoDTO = new EsitoDTO();
        esitoDTO.setError();
        esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.EVENTO_BLOCCATO);
        result.setEsitoDTO(esitoDTO);
        return result;
      }
      if (pianoColturaleBean.isFoglioBloccato(foglio, codiceNazionale, utenteAbilitazioni.getIdUtenteLogin()))
      {
        EsitoDTO esitoDTO = new EsitoDTO();
        esitoDTO.setError();
        esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.FOGLIO_BLOCCATO);
        result.setEsitoDTO(esitoDTO);
        return result;      
        }

      GeoJSONFeatureCollection suoli =  pianoColturaleBean.getSuoliFoglio(idEventoLavorazione, codiceNazionale, foglio,
          getUtenteAbilitazioni(request.getSession()).getIdUtenteLogin());
      result.setDati(suoli);
      EsitoDTO esitoDTO = new EsitoDTO();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      EsitoDTO esitoDTO = new EsitoDTO();
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }

  @GET
  @Path("/layer/2.0/getSuoliProposti")
  public AgriAPIResult<GeoJSONFeatureCollection> getSuoliProposti(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("codiceNazionale") String codiceNazionale,
      @QueryParam("foglio") Long foglio)
      throws ClassNotFoundException, SQLException, NamingException
  {

    final String THIS_METHOD = "getSuoliProposti";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }

    AgriAPIResult<GeoJSONFeatureCollection> result = new AgriAPIResult<GeoJSONFeatureCollection>();
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      GeoJSONFeatureCollection suoli =  pianoColturaleBean.getSuoliProposti(idEventoLavorazione, codiceNazionale, foglio);
      result.setDati(suoli);
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
    }
    return result;
  }

  @GET
  @Path("/layer/2.0/getParticelleFoglio")
  public AgriAPIResult<GeoJSONFeatureCollection> getParticelleFoglio(
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("cuaa") String cuaa,
      @QueryParam("codiceNazionale") String codiceNazionale,
      @QueryParam("foglio") long foglio,
      @QueryParam("annoCampagna") long annoCampagna)
      throws ClassNotFoundException, SQLException, NamingException
  {

    final String THIS_METHOD = "getParticelleFoglio";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }

    AgriAPIResult<GeoJSONFeatureCollection> result = new AgriAPIResult<GeoJSONFeatureCollection>();
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
      GeoJSONFeatureCollection dati = pianoColturaleBean.getParticelleFoglio(idEventoLavorazione, cuaa, codiceNazionale, foglio, annoCampagna);
      result.setDati(dati);
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] FINE.");
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
    }

    return result;
  }

  @GET
  @Path("/layer/2.0/getClassiEleggibilita")
  public AgriAPIResult<List<ClasseEleggibilitaDTO>> getClassiEleggibilita()
      throws ClassNotFoundException, SQLException, NamingException
  {

    List<ClasseEleggibilitaDTO> elenco = null;
    AgriAPIResult<List<ClasseEleggibilitaDTO>> result = new AgriAPIResult<List<ClasseEleggibilitaDTO>>();
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      elenco = pianoColturaleBean.getClassiEleggibilita();

      if (elenco != null && elenco.size() > 0)
      {
        result.setDati(elenco);
      }
      else
      {
        esitoDTO.setEmptyMessage("Non sono state trovate classi di eleggibilità disponibili.");
      }
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }

    return result;
  }

  @GET
  @Path("/layer/2.0/getMotivoSospensione")
  public AgriAPIResult<List<MotivoSospensioneDTO>> getMotiviSospensione()
      throws ClassNotFoundException, SQLException, NamingException
  {

    List<MotivoSospensioneDTO> elenco = null;
    AgriAPIResult<List<MotivoSospensioneDTO>> result = new AgriAPIResult<List<MotivoSospensioneDTO>>();
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      elenco = pianoColturaleBean.getMotiviSospensione();

      if (elenco != null && elenco.size() > 0)
      {
        result.setDati(elenco);
      }
      else
      {
        esitoDTO.setEmptyMessage("Non sono stati trovati motivi di esclusione disponibili.");
      }
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }

    return result;
  }

  @GET
  @Path("/layer/2.0/isFoglioBloccato")
  public AgriAPIResult<List<MotivoSospensioneDTO>> isFoglioBloccato(@Context HttpServletRequest request,
      @QueryParam("foglio") long foglio,
      @QueryParam("codiceNazionale") String codiceNazionale)
      throws ClassNotFoundException, SQLException, NamingException
  {

    AgriAPIResult<List<MotivoSospensioneDTO>> result = new AgriAPIResult<List<MotivoSospensioneDTO>>();
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      boolean isFoglioBloccato = pianoColturaleBean.isFoglioBloccato(foglio, codiceNazionale,
          getUtenteAbilitazioni(request.getSession()).getIdUtenteLogin());

      if (isFoglioBloccato)
      {
        esitoDTO.setEsito(0);
        esitoDTO.setMessaggio("Il foglio è attualmente bloccato da altri utenti.");
      }
      else
      {
        esitoDTO.setEsito(1);
        esitoDTO.setMessaggio("Il foglio NON è attualmente bloccato da altri utenti.");
      }
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }

    return result;
  }
  
  
  @GET
  @Path("/layer/2.0/getFoglioRiferimento")
  public AgriAPIResult<GeoJSONFeatureCollection> getFoglioRiferimento(@Context HttpServletRequest request,
      @QueryParam("annoCampagna") long annoCampagna,// obbligatorio
      @QueryParam("codiceNazionale") String codiceNazionale, // obbligatorio
      @QueryParam("foglio") long foglio // obbligatorio
  )
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<GeoJSONFeatureCollection> result = new AgriAPIResult<GeoJSONFeatureCollection>();

    final String THIS_METHOD = "getFoglioRiferimento";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }

    try
    {
      GeoJSONFeatureCollection suoli =  pianoColturaleBean.getFoglioRiferimento(annoCampagna, codiceNazionale, foglio);

      EsitoDTO esitoDTO = new EsitoDTO();
      result.setEsitoDTO(esitoDTO);
      result.setDati(suoli);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      EsitoDTO esitoDTO = new EsitoDTO();
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }
  
  @GET
  @Path("/layer/2.0/getSessionToken")
  public String getSessionToken(@Context HttpServletRequest request,
      @QueryParam("codiceFunzione") String codiceFunzione,  // D: documentale C: contradditorio
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("idAzienda") long idAzienda,
      @QueryParam("codiceRuolo") String codiceRuolo,
      @QueryParam("idIstanzaRiesame") String idIstaRies)
      throws ClassNotFoundException, SQLException, NamingException, UnsupportedEncodingException
  
  {
    final String THIS_METHOD = "getSessionToken";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    GestioneCookieDTO cookieDTO = new GestioneCookieDTO();
    Cookie[] cookie =  request.getCookies();
    for(Cookie item : cookie)
    {
      if(item.getName().startsWith("_shibsession") && cookieDTO.getCookie1()==null) {
        cookieDTO.setCookie1(item.getName()+"##"+item.getValue());
      }
      else if(item.getName().startsWith("_shibsession") && cookieDTO.getCookie1()!=null && cookieDTO.getCookie2()==null) {
        cookieDTO.setCookie2(item.getName()+"##"+item.getValue());
      }
      
      if(cookieDTO.getCookie2()==null)
        cookieDTO.setCookie2("PORTALE##SISTEMAPIEMONTE");
      
    }
   
    UtenteAbilitazioni utenteAbilitazioni = (UtenteAbilitazioni) request.getSession().getAttribute("utenteAbilitazioni");
    
    if(codiceFunzione==null || codiceFunzione.trim().length()<=0)
      codiceFunzione = AgriApiConstants.SESSION_TOKEN.DOCUMENTALE; // defalut per garantire funzionamento con vecchi plugin qgis non aggiornati
    
    if(codiceFunzione.equals(AgriApiConstants.SESSION_TOKEN.DOCUMENTALE))
      cookieDTO.setParametro(getAgriwellWebUrl(utenteAbilitazioni,codiceRuolo,idAzienda,idIstaRies,idEventoLavorazione));
    else if(codiceFunzione.equals(AgriApiConstants.SESSION_TOKEN.CONTRADDITORIO))
      cookieDTO.setParametro(getContradditorioUrl(utenteAbilitazioni,codiceRuolo,idEventoLavorazione));

    
    String token= pianoColturaleBean.getToken(cookieDTO);
    return token;
  }
  
  protected String getContradditorioUrl(UtenteAbilitazioni utenteAbilitazioni,String codiceRuolo, long idEventoLavorazione) throws UnsupportedEncodingException
  {
    String baseUrl = AgriApiConstants.URL.CONTRADDITORIO.BASE_URL_CONTROCAMPO;
    
    StringBuilder sb = new StringBuilder(baseUrl)
        .append("?CF=").append(utenteAbilitazioni.getCodiceFiscale())
        .append("&ruolo=").append(urlEncode(codiceRuolo));
         sb.append("&idProcedimento=").append(AgriApiConstants.ID_PROCEDIMENTO)
        .append("&liv=").append(utenteAbilitazioni.getLivelloAutenticazione())
        .append("&idEventoLavorazione=").append(idEventoLavorazione); 
         

    return sb.toString();
  }
  
  protected String getAgriwellWebUrl(UtenteAbilitazioni utenteAbilitazioni,String codiceRuolo, long idAzienda, String idIstaRies, long idEventoLavorazione) throws UnsupportedEncodingException
  {
    String baseUrl = AgriApiConstants.URL.AGRIWELLWEB.BASE_URL_QGIS;
    
    StringBuilder sb = new StringBuilder(baseUrl)
        .append("?CF=").append(utenteAbilitazioni.getCodiceFiscale())
        .append("&ruolo=").append(urlEncode(codiceRuolo));
         sb.append("&idpr_a=").append(AgriApiConstants.ID_PROCEDIMENTO)
        .append("&liv=").append(utenteAbilitazioni.getLivelloAutenticazione())
        .append("&extId=").append(idAzienda)
        .append("&idpr_u=").append("7")
        .append("&key=").append(pianoColturaleBean.getIdentificativoPraticaOrigine(idAzienda,idEventoLavorazione)); 
         
         if(idIstaRies!=null && idIstaRies.trim().length()>0)
         {
           sb.append("&id_dett=").append(idIstaRies);
         }
         
         logger.debug("[" + THIS_CLASS + ".getAgriwellWebUrl] BASE_URL_QGIS: "+sb.toString());

    return sb.toString();
  }
  
  public String urlEncode(String text) throws UnsupportedEncodingException
  {
    if(text==null) return "";
    return urlEncode(text, StandardCharsets.ISO_8859_1.toString());
  }
  public String urlEncode(String text, String encoding) throws UnsupportedEncodingException
  {
    return URLEncoder.encode(text, encoding);
  }
  
  
  @GET
  @Path("/layer/2.0/getParametri")
  public AgriAPIResult<List<ParametroDTO>> getParametri(@Context HttpServletRequest request  )
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<List<ParametroDTO>> result = new AgriAPIResult<List<ParametroDTO>>();

    final String THIS_METHOD = "getParametri";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    EsitoDTO esitoDTO = new EsitoDTO();

    try
    {
      List<ParametroDTO> elenco = pianoColturaleBean.getElencoParametri();
      
      if (elenco != null && elenco.size() > 0)
      {
        result.setDati(elenco);
      }
      else
      {
        esitoDTO.setEmptyMessage("Non sono stati trovati parametri.");
      }
      
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }
  
  @GET
  @Path("/layer/2.0/leggiDatiSuolo")
  public AgriAPIResult<DatiSuoloDTO> leggiDatiSuolo(
		  @Context HttpServletRequest request,
		  @QueryParam("idSuoloRilevato") long idSuoloRilevato)
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<DatiSuoloDTO> result = new AgriAPIResult<DatiSuoloDTO>();

    final String THIS_METHOD = "leggiDatiSuolo";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    EsitoDTO esitoDTO = new EsitoDTO();

    try
    {
      DatiSuoloDTO datiSuolo = pianoColturaleBean.leggiDatiSuolo(idSuoloRilevato);
      if (datiSuolo != null)
      {
        result.setDati(datiSuolo);
      }
      else
      {
        esitoDTO.setEmptyMessage("Non sono stati trovati i dati suolo.");
      }
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }
  
  
  @GET
  @Path("/layer/2.0/leggiDatiUnarPoligono")
  public AgriAPIResult<List<UnarAppezzamentoDTO>> leggiDatiUnarPoligono(
		  @Context HttpServletRequest request,
		  @QueryParam("idSuoloRilevato") long idSuoloRilevato)
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<List<UnarAppezzamentoDTO>> result = new AgriAPIResult<List<UnarAppezzamentoDTO>>();

    final String THIS_METHOD = "leggiDatiUnar";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    EsitoDTO esitoDTO = new EsitoDTO();

    try
    {
      SuoloRilevatoDTO suoloRilevato = pianoColturaleBean.getSuoloRilevato(idSuoloRilevato);
      if(suoloRilevato == null)
      {
    	  esitoDTO.setError();
    	  esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.ID_SUOLO_RILEVATO_NON_TROVATO);
    	  result.setEsitoDTO(esitoDTO);
      }
      else
      {
    	  List<UnarAppezzamentoDTO> unarAppezzamento = pianoColturaleBean.leggiDatiUnarPoligono(idSuoloRilevato, suoloRilevato.getDataFineValidita());
    	  
    	  if (unarAppezzamento != null)
    	  {
    		  result.setDati(unarAppezzamento);
    	  }
    	  else
    	  {
    		  esitoDTO.setEmptyMessage("Non sono state trovate UNAR.");
    	  }
      }
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }
  
  @GET
  @Path("/layer/2.0/leggiDatiUnarParticella")
  public AgriAPIResult<List<UnarAppezzamentoDTO>> leggiDatiUnarParticella(
		  @Context HttpServletRequest request,
		  @QueryParam("idSuoloRilevato") long idSuoloRilevato)
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<List<UnarAppezzamentoDTO>> result = new AgriAPIResult<List<UnarAppezzamentoDTO>>();

    final String THIS_METHOD = "leggiDatiUnarParticella";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    EsitoDTO esitoDTO = new EsitoDTO();

    try
    {
      SuoloRilevatoDTO suoloRilevato = pianoColturaleBean.getSuoloRilevato(idSuoloRilevato);
      if(suoloRilevato == null)
      {
    	  esitoDTO.setError();
    	  esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.ID_SUOLO_RILEVATO_NON_TROVATO);
    	  result.setEsitoDTO(esitoDTO);
      }
      else
      {
    	  List<Long> particelle = pianoColturaleBean.getListIdParticellaAssociataASuolo(idSuoloRilevato);
    	  List<UnarAppezzamentoDTO> unarAppezzamento = pianoColturaleBean.leggiDatiUnarParticella(idSuoloRilevato, suoloRilevato.getDataFineValidita(), particelle);
    	  
    	  if (unarAppezzamento != null)
    	  {
    		  result.setDati(unarAppezzamento);
    	  }
    	  else
    	  {
    		  esitoDTO.setEmptyMessage("Non sono state trovate UNAR.");
    	  }
      }
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }
  
  @GET
  @Path("/layer/2.0/leggiDatiUnarCatasto")
  public AgriAPIResult<List<UnarAppezzamentoDTO>> leggiDatiUnarCatasto(
      @Context HttpServletRequest request,
      @QueryParam("foglio") long foglio,
      @QueryParam("codiceNazionale") String codiceNazionale,
      @QueryParam("subalterno") String subalterno,
      @QueryParam("numeroParticella") String numeroParticella,
      @QueryParam("sezione") String sezione
      )
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<List<UnarAppezzamentoDTO>> result = new AgriAPIResult<List<UnarAppezzamentoDTO>>();

    final String THIS_METHOD = "leggiDatiUnarCatasto";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    EsitoDTO esitoDTO = new EsitoDTO();

    try
    {
      List<Long> particelle = pianoColturaleBean.getListIdParticellaCatasto(foglio, codiceNazionale, subalterno, numeroParticella, sezione);
      List<UnarAppezzamentoDTO> unarAppezzamento = pianoColturaleBean.leggiDatiUnarParticella(null, null, particelle);
        
        if (unarAppezzamento != null)
        {
          result.setDati(unarAppezzamento);
        }
        else
        {
          esitoDTO.setEmptyMessage("Non sono state trovate UNAR.");
        }
      
      result.setEsitoDTO(esitoDTO);
      return result;
    }catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }
  
  @GET
  @Path("/layer/2.0/leggiDatiUtilizzoCatasto")
  public AgriAPIResult<List<UtilizzoParticellaDTO>> leggiDatiUtilizzoCatasto(
      @Context HttpServletRequest request,
      @QueryParam("foglio") long foglio,
      @QueryParam("codiceNazionale") String codiceNazionale,
      @QueryParam("subalterno") String subalterno,
      @QueryParam("numeroParticella") String numeroParticella,
      @QueryParam("sezione") String sezione,
      @QueryParam("annoCampagna") int campagna)
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<List<UtilizzoParticellaDTO>> result = new AgriAPIResult<List<UtilizzoParticellaDTO>>();

    final String THIS_METHOD = "leggiDatiUtilizzoCatasto";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    EsitoDTO esitoDTO = new EsitoDTO();

    try
    {
        List<Long> particelle = pianoColturaleBean.getListIdParticellaCatasto(foglio, codiceNazionale, subalterno, numeroParticella, sezione);
        List<UtilizzoParticellaDTO> unarParticella = pianoColturaleBean.leggiDatiUtilizzoParticella(campagna, null, particelle);
        
        if (unarParticella != null)
        {
          result.setDati(unarParticella);
        }
        else
        {
          esitoDTO.setEmptyMessage("Non sono stati trovati dati utilizzo particella per il suolo selezionato.");
        }
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }
  
  @GET
  @Path("/layer/2.0/leggiDatiUtilizzoParticella")
  public AgriAPIResult<List<UtilizzoParticellaDTO>> leggiDatiUtilizzoParticella(
      @Context HttpServletRequest request,
      @QueryParam("idSuoloRilevato") long idSuoloRilevato,
      @QueryParam("annoCampagna") int campagna)
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<List<UtilizzoParticellaDTO>> result = new AgriAPIResult<List<UtilizzoParticellaDTO>>();

    final String THIS_METHOD = "leggiDatiUtilizzoParticella";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    EsitoDTO esitoDTO = new EsitoDTO();

    try
    {
      SuoloRilevatoDTO suoloRilevato = pianoColturaleBean.getSuoloRilevato(idSuoloRilevato);
      if(suoloRilevato == null)
      {
        esitoDTO.setError();
        esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.ID_SUOLO_RILEVATO_NON_TROVATO);
        result.setEsitoDTO(esitoDTO);
      }
      else
      {
        List<Long> particelle = pianoColturaleBean.getListIdParticellaAssociataASuolo(idSuoloRilevato);
        List<UtilizzoParticellaDTO> unarParticella = pianoColturaleBean.leggiDatiUtilizzoParticella(campagna, suoloRilevato.getDataFineValidita(), particelle);
        
        if (unarParticella != null)
        {
          result.setDati(unarParticella);
        }
        else
        {
          esitoDTO.setEmptyMessage("Non sono stati trovati dati utilizzo particella per il suolo selezionato.");
        }
      }
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }

  /******************************************************************************
   * API IN SCRITTURA *
   ******************************************************************************/

  @POST
  @Path("/layer/2.0/salvaSuoli")
  public AgriAPIResult<Void> salvaSuoli(GeoJSONFeatureCollection geoJson,
      @Context HttpServletRequest request)
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<Void> result = new AgriAPIResult<Void>();
    EsitoDTO esitoDTO = new EsitoDTO();
    long idEventoLavorazione = 0;
    
    try
    {
      esitoDTO = pianoColturaleBean.salvaSuoli(geoJson, getUtenteAbilitazioni(request.getSession()).getIdUtenteLogin());
      //Chiamo in asincrono il batch di salvataggio istanza di anagrafe
      for(SimpleFeature feature : geoJson.getFeatures())
      {
        if(feature.getProperty("idEventoLavorazione")!=null)
        {
          idEventoLavorazione = (Long) feature.getProperty("idEventoLavorazione").getValue();
          break;
        }
      }
      pianoColturaleBean.callMainSalvaIstanzaAnagrafe(idEventoLavorazione);
      result.setEsitoDTO(esitoDTO);
    }
    catch (Exception e)
    {
      pianoColturaleBean.aggiornaStatoSalvataggioEventoLavorazione(idEventoLavorazione, AgriApiConstants.ESITO.STATO_SALVATAGGIO.SALVATAGGIO_ISTANZA_TERMINATO_CON_ERRORE);
      esitoDTO.setError();
      esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.SALVA_SUOLI_GENERICO);
    }
    
    result.setEsitoDTO(esitoDTO);
    return result;
  }

  @GET
  @Path("/layer/2.0/sbloccoForzato")
  public AgriAPIResult<Void> sbloccoForzato(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione)
      throws ClassNotFoundException, SQLException, NamingException
  {

    AgriAPIResult<Void> result = new AgriAPIResult<Void>();
    final String THIS_METHOD = "[" + THIS_CLASS + ".leggiDatiUtilizzoParticella] BEGIN.";
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);
    UtenteAbilitazioni utenteAbilitazioni = getUtenteAbilitazioni(request.getSession());

    int rowsSbloccate = pianoColturaleBean.sbloccoForzato(idEventoLavorazione, utenteAbilitazioni.getIdUtenteLogin());
    
    if(rowsSbloccate>0) 
      esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO);
    else
    {
      esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
      esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.EVENTO_BLOCCATO_DA_ALTRI);
    }
    return result;
  }

  @GET
  @Path("/layer/2.0/sbloccoForzatoFoglio")
  public AgriAPIResult<Void> sbloccoForzatoFoglio(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("foglio") int foglio,
      @QueryParam("codiceNazionale") String codiceNazionale)
      throws ClassNotFoundException, SQLException, NamingException
  {

    AgriAPIResult<Void> result = new AgriAPIResult<Void>();
    final String THIS_METHOD = "[" + THIS_CLASS + ".leggiDatiUtilizzoParticella] BEGIN.";
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    try
    {
        EsitoDTO esitoDTO = pianoColturaleBean.sbloccoForzatoFoglio(idEventoLavorazione, foglio, codiceNazionale, getUtenteAbilitazioni(request.getSession()).getIdUtenteLogin());
        result.setEsitoDTO(esitoDTO);
    }
    catch (Exception e)
    {
      EsitoDTO esitoDTO = new EsitoDTO();
      esitoDTO.setError();
    }

    return result;
  }

  /******************************************************************************
   * UTILS *
   ******************************************************************************/
  protected UtenteAbilitazioni getUtenteAbilitazioni(HttpSession session)
  {
    return (UtenteAbilitazioni) session.getAttribute("utenteAbilitazioni");
  }
  
  
  @GET
  @Path("/layer/2.0/getStoricoFoglioGeoPCK")
  @Produces(MediaType.TEXT_PLAIN)
  public Response getGeoPCK(@Context HttpServletRequest request,
      @QueryParam("foglio") int foglio,
      @QueryParam("codiceNazionale") String codiceNazionale,
      @QueryParam("annoCampagna") Integer annoCampagna /* OPZIONALE */)
      throws ClassNotFoundException, SQLException, NamingException
  {
    try
    {
      /*
      foglio = 58;
      codiceNazionale = "D205";
      annoCampagna=2019;
      */
      File geopck = pianoColturaleBean.getGeoPCK(foglio, codiceNazionale, annoCampagna, getUtenteAbilitazioni(request.getSession()).getIdUtenteLogin());
      byte[] filesBytes = FileUtils.readFileToByteArray(geopck);
      
      ResponseBuilder response = Response.ok((Object) filesBytes);
      return response.build();
    }
    catch (Exception e)
    {
      EsitoDTO esitoDTO = new EsitoDTO();
      esitoDTO.setError();
      return null;
    }
  }
  
  @GET
  @Path("/layer/2.0/getImmagineFromIdAppezzamento")
  @Produces(MediaType.TEXT_PLAIN)
  public Response getImmagineFromIdAppezzamento(@Context HttpServletRequest request,
      @QueryParam("id") int idFotoAppezzamentoCons )
      throws ClassNotFoundException, SQLException, NamingException
  {
    try
    {
       
      ImmagineAppezzamentoDTO imgDTO = pianoColturaleBean.getImmagineAppezzamentoFromId(idFotoAppezzamentoCons);
      
      ResponseBuilder response = Response.ok((Object) imgDTO.getContent());
      response.header("Content-Disposition",
          "attachment; filename="+imgDTO.getfileNameDownload());
      return response.build();
    }
    catch (Exception e)
    {
      EsitoDTO esitoDTO = new EsitoDTO();
      esitoDTO.setError();
      return null;
    }

  }
  @GET
  @Path("/layer/2.0/leggiValidazioniAzienda")
  public AgriAPIResult<List<DichiarazioneConsistenzaDTO>> leggiValidazioniAzienda(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione )
  {
    final String THIS_METHOD = "[" + THIS_CLASS + ".leggiValidazioniAzienda]";
    AgriAPIResult<List<DichiarazioneConsistenzaDTO>> result = new AgriAPIResult<List<DichiarazioneConsistenzaDTO>>();
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    try
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + "] BEGIN.");
      }

      List<DichiarazioneConsistenzaDTO> validazioni = pianoColturaleBean.leggiValidazioniAzienda(idEventoLavorazione);
      result.setDati(validazioni);
      result.setEsitoDTO(new EsitoDTO());
      
      return result;
    }
    catch (Exception e)
    {
      logger.debug(THIS_METHOD + "] Eccezione non prevista: ", e);
      EsitoDTO esitoDTO = new EsitoDTO();
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      result.setDati(null);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + "] END.");
      }
    }
  }

  @GET
  @Path("/layer/2.0/leggiAppezzamentiScheda")
  public AgriAPIResult<MyGeoJsonFeatureCollection<AppezzamentoDTO>> leggiAppezzamentiScheda(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("idDichiarazioneConsistenza") long idDichiarazioneConsistenza,
      @QueryParam("codNazionale") String codNazionale,
      @QueryParam("foglio") int foglio) throws IllegalArgumentException, IllegalAccessException, IOException, ParseException
  {
    final String THIS_METHOD = "[" + THIS_CLASS + ".leggiAppezzamentiScheda]";
    AgriAPIResult<MyGeoJsonFeatureCollection<AppezzamentoDTO>> result = new AgriAPIResult<MyGeoJsonFeatureCollection<AppezzamentoDTO>>();
    if (codNazionale == null)
    {
      EsitoDTO esito = new EsitoDTO();
      esito.setEsito(AgriApiConstants.ESITO.ERRORE);
      esito.setMessaggio("Parametro OBBLIGATORIO \"codNazionale\" non valorizzato");
      result.setEsitoDTO(esito);
      logger.warn(THIS_METHOD + " Errore nella verifica dell'obbligatorietà dei parametri: " + esito.getMessaggio());
      return result;
    }
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
    if (esitoAbilitazioni != null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD + " Errore nella verifica delle abilitazioni: " + esitoAbilitazioni.getMessaggio());
      return result;
    }
    List<AppezzamentoDTO> appezzamenti = pianoColturaleBean.leggiAppezzamentiScheda(idEventoLavorazione, idDichiarazioneConsistenza, codNazionale, foglio);
    MyGeoJsonFeatureCollection<AppezzamentoDTO> geojsonFeatures = new MyGeoJsonFeatureCollection<AppezzamentoDTO>();
    if (appezzamenti!=null)
    {
      for(AppezzamentoDTO appezzamento:appezzamenti)
      {
        MyGeoJsonFeature<AppezzamentoDTO> feature = new MyGeoJsonFeature<AppezzamentoDTO>();
        feature.setGeometry(appezzamento.getGeometry(), appezzamento.getSrid());
        feature.setProperties(appezzamento);
        geojsonFeatures.addFeature(feature);
      }
    }
    result.setDati(geojsonFeatures);
    result.setEsitoDTO(new EsitoDTO());
    return result;
  }

  @GET
  @Path("/layer/2.0/getParticelleLavorazioni")
  public AgriAPIResult<List<ParticellaLavorazioneDTO>> getParticelleLavorazioni(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("codiceNazionale") String codiceNazionale, // obbligatorio
      @QueryParam("foglio") long foglio // obbligatorio
  )
      throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getParticelleLavorazioni";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    List<ParticellaLavorazioneDTO> elenco = null;
    AgriAPIResult<List<ParticellaLavorazioneDTO>> result = new AgriAPIResult<List<ParticellaLavorazioneDTO>>();
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      elenco = pianoColturaleBean.getParticelleLavorazioni(idEventoLavorazione, codiceNazionale, foglio);

      if (elenco != null && elenco.size() > 0)
      {
        result.setDati(elenco);
      }
      else
      {
        esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
        esitoDTO.setEmptyMessage("Non sono state trovate particelle disponibili.");
      }
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
    return result;

  }
  
  @GET
  @Path("/layer/2.0/getCxfParticella")
  public AgriAPIResult<GeoJSONFeatureCollection> getCxfParticella(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione, // obbligatorio
      @QueryParam("codiceNazionale") String codiceNazionale, // obbligatorio
      @QueryParam("foglio") long foglio // obbligatorio
  )
      throws ClassNotFoundException, SQLException, NamingException
  {
    AgriAPIResult<GeoJSONFeatureCollection> result = new AgriAPIResult<GeoJSONFeatureCollection>();

    final String THIS_METHOD = "getCxfParticella";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    UtenteAbilitazioni utenteAbilitazioni = getUtenteAbilitazioni(request.getSession());
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(utenteAbilitazioni, idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    
    try
    {
      GeoJSONFeatureCollection suoli =  pianoColturaleBean.getCxfParticella(codiceNazionale, foglio,
          getUtenteAbilitazioni(request.getSession()).getIdUtenteLogin(),idEventoLavorazione);
      result.setDati(suoli);
      EsitoDTO esitoDTO = new EsitoDTO();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    catch (Exception e)
    {
      logger.error(THIS_METHOD, e);
      EsitoDTO esitoDTO = new EsitoDTO();
      esitoDTO.setError();
      result.setEsitoDTO(esitoDTO);
      return result;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
  }
  
  
  @GET
  @Path("/layer/2.0/getElencoAllegatiParticella")
  public AgriAPIResult<List<AllegatoParticellaDTO>> getElencoAllegatiParticella(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("codiceNazionale") String codiceNazionale, // obbligatorio
      @QueryParam("foglio") long foglio // obbligatorio
  )
      throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getElencoFogliAzienda";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    List<AllegatoParticellaDTO> elenco = null;
    AgriAPIResult<List<AllegatoParticellaDTO>> result = new AgriAPIResult<List<AllegatoParticellaDTO>>();
    EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
    if (esitoAbilitazioni!=null)
    {
      result.setEsitoDTO(esitoAbilitazioni);
      logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
      return result;
    }
    
    EsitoDTO esitoDTO = new EsitoDTO();
    result.setEsitoDTO(esitoDTO);

    try
    {
      elenco = pianoColturaleBean.getElencoAllegatiParticella(codiceNazionale, foglio, idEventoLavorazione);

      if (elenco != null && elenco.size() > 0)
      {
        result.setDati(elenco);
      }
      else
      {
        esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
        esitoDTO.setEmptyMessage("Non sono state trovate particelle disponibili.");
      }
    }
    catch (Exception e)
    {
      esitoDTO.setError();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + " END.");
      }
    }
    return result;
  }
  
  @GET
  @Path("/layer/2.0/getAllegatoParticella")
  @Produces(MediaType.TEXT_PLAIN)
  public Response getAllegatoParticella(@Context HttpServletRequest request,
      @QueryParam("idEventoLavorazione") long idEventoLavorazione,
      @QueryParam("idAllegato") long idAllegato
      )
      throws ClassNotFoundException, SQLException, NamingException
  {
    try
    {
      final String THIS_METHOD = "getAllegatoParticella";
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
      }
      
      EsitoDTO esitoAbilitazioni = verificaAbilitazioniEventoLavorazione(getUtenteAbilitazioni(request.getSession()), idEventoLavorazione);
      if (esitoAbilitazioni!=null)
      {
        logger.warn(THIS_METHOD+" Errore nella verifica delle abilitazioni: "+esitoAbilitazioni.getMessaggio());
        return Response.ok((Object) esitoAbilitazioni).build();
      }
      
      byte[] filesBytes = pianoColturaleBean.geAllegatoFromDoqui(idEventoLavorazione, idAllegato);
      
      ResponseBuilder response = Response.ok((Object) filesBytes);
      return response.build();
    }
    catch (Exception e)
    {
      EsitoDTO esitoDTO = new EsitoDTO();
      esitoDTO.setError();
      return null;
    }
  }
  
  
  protected EsitoDTO verificaAbilitazioniListaLavorazione(UtenteAbilitazioni utenteAbilitazioni, long idListaLavorazione)
  {
    if (!pianoColturaleBean.verificaAbilitazioneListaLavorazione(utenteAbilitazioni, idListaLavorazione))
    {
      EsitoDTO esito = new EsitoDTO();
      esito.setError();
      esito.setMessaggio("Utente non abilitato alla lista di lavorazione #" + idListaLavorazione);

    }
    return null;
  }

  protected EsitoDTO verificaAbilitazioniEventoLavorazione(UtenteAbilitazioni utenteAbilitazioni, long idEventoLavorazione)
  {
    if (!pianoColturaleBean.verificaAbilitazioneEventoLavorazione(utenteAbilitazioni, idEventoLavorazione))
    {
      EsitoDTO esito = new EsitoDTO();
      esito.setError();
      esito.setMessaggio("Utente non abilitato all'evento di lavorazione #" + idEventoLavorazione);

    }
    return null;
  }
}
