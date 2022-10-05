package it.csi.qgisagri.agriapi.business;

import java.io.File;
import java.io.IOException;
import java.math.BigDecimal;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.activation.DataHandler;
import javax.naming.NamingException;

import org.apache.log4j.Logger;
import org.codehaus.jackson.map.ObjectMapper;
import org.geotools.data.DataUtilities;
import org.geotools.data.simple.SimpleFeatureCollection;
import org.geotools.feature.simple.SimpleFeatureBuilder;
import org.geotools.geometry.jts.Geometries;
import org.geotools.geometry.jts.ReferencedEnvelope;
import org.geotools.geopkg.FeatureEntry;
import org.geotools.geopkg.GeoPackage;
import org.geotools.referencing.ReferencingFactoryFinder;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.io.ParseException;
import org.opengis.feature.Property;
import org.opengis.feature.simple.SimpleFeature;
import org.opengis.feature.simple.SimpleFeatureType;
import org.opengis.referencing.crs.CRSAuthorityFactory;
import org.opengis.referencing.crs.CoordinateReferenceSystem;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.interceptor.TransactionAspectSupport;

import it.csi.papua.papuaserv.dto.gestioneutenti.ws.UtenteAbilitazioni;
import it.csi.qgisagri.agriapi.dto.DatiSuoloDTO;
import it.csi.qgisagri.agriapi.dto.EsitoDTO;
import it.csi.qgisagri.agriapi.dto.FoglioRiferimentoDTO;
import it.csi.qgisagri.agriapi.dto.GeoJSONFeatureCollection;
import it.csi.qgisagri.agriapi.dto.GestioneCookieDTO;
import it.csi.qgisagri.agriapi.dto.ImmagineAppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.MainControlloDTO;
import it.csi.qgisagri.agriapi.dto.ParametroDTO;
import it.csi.qgisagri.agriapi.dto.SuoloRilevatoDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.AllegatoParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.AziendaListeLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ClasseEleggibilitaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.CxfParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.DichiarazioneConsistenzaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.FoglioAziendaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ListaLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.MotivoSospensioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ParticellaCessataDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ParticellaLavorataDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ParticellaLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloCessatoDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloConfigurazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloLavoratoDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloPropostoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.AppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.UnarAppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.UtilizzoParticellaDTO;
import it.csi.qgisagri.agriapi.integration.PianoColturaleDAO;
import it.csi.qgisagri.agriapi.util.AgriApiConstants;
import it.csi.qgisagri.agriapi.util.AgriApiUtils;
import it.csi.qgisagri.agriapi.util.GraficoUtils;
import it.csi.qgisagri.agriapi.util.conversion.GeoJSONGeometryConverter;
import it.csi.qgisagri.agriapi.util.conversion.WKTGeometryConverter;

@Component("pianoColturaleBean")
@Transactional(timeout = 300)
public class PianoColturaleBean
{
  protected static final Logger logger = Logger.getLogger(AgriApiConstants.LOGGING.LOGGER_NAME + ".business");
  protected static final Logger logger_geojson = Logger.getLogger(AgriApiConstants.LOGGING.LOGGER_GEOJSON_NAME + ".business");
  protected static final String THIS_CLASS = PianoColturaleBean.class.getSimpleName();
  
  @Autowired
  private PianoColturaleDAO pianoColturaleDAO;

  public List<ListaLavorazioneDTO> getElencoListeLavorazione(UtenteAbilitazioni utenteAbilitazioni)
      throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getElencoListeLavorazione";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getElencoListeLavorazione(utenteAbilitazioni);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  public List<AllegatoParticellaDTO> getElencoAllegatiParticella(
      String codiceNazionale, long foglio, long idEventoLavorazione) throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getElencoAllegatiParticella";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getElencoAllegatiParticella(codiceNazionale, foglio, idEventoLavorazione);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  public List<AziendaListeLavorazioneDTO> getElencoAziende(int idListaLavorazione, String cuaa, String escludiLavorate, String escludiBloccate, String escludiSospese)
      throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getElencoAziende";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getElencoAziende(idListaLavorazione, cuaa, escludiLavorate, escludiBloccate, escludiSospese);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  public List<FoglioAziendaDTO> getElencoFogliAzienda(long idEventoLavorazione)
      throws ClassNotFoundException, SQLException, NamingException
  {
    final String THIS_METHOD = "getElencoFogliAzienda";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      List<FoglioAziendaDTO> fogli = pianoColturaleDAO.getElencoFogliAzienda(idEventoLavorazione);
      
      if(fogli!=null)
      {
       for(FoglioAziendaDTO item : fogli)
       {
         if(item.getNumeroSuoliSospesi()>0)
           item.setStatoLavorazioneOrig(AgriApiConstants.STATO_FOGLIO.SOSPESO);
         else
           item.setStatoLavorazioneOrig(pianoColturaleDAO.isFoglioLavorato(idEventoLavorazione,item.getFoglio()) ? AgriApiConstants.STATO_FOGLIO.LAVORATO : AgriApiConstants.STATO_FOGLIO.NON_LAVORATO );
       }
      }
      
      return fogli;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public GeoJSONFeatureCollection getSuoliFoglio(long idEventoLavorazione,
      String codiceNazionale, Long foglio, Long idUtenteLogin) throws Exception
  { 
    final String THIS_METHOD = "getSuoliFoglio";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      List<SuoloLavorazioneDTO> suoli = pianoColturaleDAO.getSuoliFoglio(idEventoLavorazione, codiceNazionale, foglio, idUtenteLogin);
      GeoJSONFeatureCollection featureCollection = new GeoJSONFeatureCollection();
      ArrayList<String> listFeaturesString = new ArrayList<String>();

      if(suoli!=null)
      {
        for(SuoloLavorazioneDTO suolo : suoli)
        {
          try {
            listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON(suolo.getGeometriaWkt(),setAttributeSuolo(suolo),setNvlSRID(suolo.getSrid()),"Feature",null));
          }
          catch (IllegalArgumentException e)
          {
            //La funzionalità di conversione fallisce se la geometria è "sporca"
            try {
              //FIXSHAPE - funzione che pulisce la geometria
              String wktCorretto = pianoColturaleDAO.fixShape(suolo.getGeometriaWkt());
              //Riporvo a convertire la geometria pulita
              listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON(wktCorretto,setAttributeSuolo(suolo),setNvlSRID(suolo.getSrid()),"Feature",null));
            }
            catch(IllegalArgumentException e2)
            {
              //Se fallisce di nuovo allora segnalo l'errore.
              logger.debug("La geometria presenta degli errori.");
              e2.printStackTrace();
              suolo.setErrore("La geometria presenta degli errori.");
              //e aggiungo l'attributo "errore" al geoJson, mentre la geometria passata sarà vuota
              listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON("POLYGON EMPTY",setAttributeSuolo(suolo),setNvlSRID(suolo.getSrid()),"Feature",null));
            }
         }
        }

        //BLOCCO L'EVENTO IN QUESTIONE SE NON è BLOCCATO, e blocco il foglio
        if(pianoColturaleDAO.isEventoBloccato(idEventoLavorazione, null))
        {
          Long idEventoBloccato = pianoColturaleDAO.getIdBloccoEvento(idEventoLavorazione, idUtenteLogin);
          pianoColturaleDAO.sbloccaFoglio(foglio.intValue(), codiceNazionale, idUtenteLogin);
          pianoColturaleDAO.insertBloccoFoglio(idEventoBloccato, foglio, codiceNazionale, idUtenteLogin);
        }
        else
        {
          Long idEventoBloccato = pianoColturaleDAO.insertBloccoEvento(idEventoLavorazione, idUtenteLogin);
          pianoColturaleDAO.insertBloccoFoglio(idEventoBloccato, foglio, codiceNazionale, idUtenteLogin);
        }
       
        pianoColturaleDAO.assegnaEventoAllUtente(idEventoLavorazione, idUtenteLogin);
      }
      featureCollection.setFeaturesString(listFeaturesString);
      return featureCollection ;
    }
    catch (Exception e)
    {
      e.printStackTrace();
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }


  public GeoJSONFeatureCollection getSuoliProposti(long idEventoLavorazione,
      String codiceNazionale, Long foglio) throws ParseException, IOException
  {
    final String THIS_METHOD = "getSuoliProposti";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      GeoJSONFeatureCollection featureCollection = new GeoJSONFeatureCollection();
      ArrayList<String> listFeaturesString = new ArrayList<String>();

      List<SuoloPropostoDTO> suoli = pianoColturaleDAO.getSuoliProposti(idEventoLavorazione, codiceNazionale, foglio);
      if(suoli!=null)
      for(SuoloPropostoDTO suolo : suoli)
      {
        listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON(suolo.getGeometriaWkt(),setAttributeSuoloProposto(suolo),setNvlSRID(suolo.getSrid()),"Feature",null));
      }
      featureCollection.setFeaturesString(listFeaturesString);
      return featureCollection;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  
  private Map<String, Object> setAttributeCxf(CxfParticellaDTO particella)
  {
    HashMap<String, Object> attributesMap = new HashMap<String, Object>();
    attributesMap.put("idCxfParticella", particella.getIdCxfParticella());
    attributesMap.put("codiceNazionale", particella.getExtCodNazionale());
    attributesMap.put("foglio", particella.getFoglio());
    attributesMap.put("particella", particella.getParticella());
    attributesMap.put("subalterno", particella.getSubalterno());
    attributesMap.put("allegato", particella.getAllegato());
    attributesMap.put("sviluppo", particella.getSviluppo());
    attributesMap.put("srid", setNvlSRID(null));
    return attributesMap;
  }
  
  private HashMap<String, Object> setAttributeSuolo(SuoloLavorazioneDTO suolo)
  {
    HashMap<String, Object> attributesMap = new HashMap<String, Object>();
    attributesMap.put("idFeature", suolo.getIdFeature());
    attributesMap.put("codiceNazionale", suolo.getCodiceNazionale());
    attributesMap.put("flagPresenzaUnar", (suolo.getFlagPresenzaUnar()!=null ? suolo.getFlagPresenzaUnar() : "N" ));
    attributesMap.put("foglio", suolo.getFoglio());
    attributesMap.put("idEleggibilitaRilevata", suolo.getIdEleggibilitaRilevata());
    attributesMap.put("codiceEleggibilitaRilevata", suolo.getCodiceEleggibilitaRilevata());
    
    attributesMap.put("idTipoMotivoSospensione", suolo.getIdTipoMotivoSospensione());
    attributesMap.put("flagControlloCampo",  ( (suolo.getIdTipoSorgenteSuolo() == null || suolo.getIdTipoSorgenteSuolo().trim().length()<=0 ) ? "N" : pianoColturaleDAO.getDecodificaTipoSorgenteSuolo(suolo.getIdTipoSorgenteSuolo())  )  );
    attributesMap.put("flagSospensioneOrig", suolo.getFlagSospensione());
    attributesMap.put("descrizioneSospensione", suolo.getDescrizioneSospensione());
    
    if(suolo.getNote()!=null) {
      //replace fatta per problemi nel parsing json del converter
      attributesMap.put("note", suolo.getNote().replace('"', '\'').replace("\n", "").replace("[", "&quada").replace("]", "&quadc"));
    }
    else
      attributesMap.put("note", suolo.getNote());
    attributesMap.put("noteLavorazione", suolo.getNoteLavorazione());
    attributesMap.put("tipoSuolo", suolo.getTipoSuolo());
    attributesMap.put("srid", setNvlSRID(suolo.getSrid()));
    return attributesMap;
  }
  
  private String setNvlSRID(String srid) {
    return srid!=null ? srid : AgriApiConstants.DEFAULT_CRS_PIEMONTE;
  }
  
  private Map<String, Object> setAttributeSuoloProposto(SuoloPropostoDTO suolo)
  {
    HashMap<String, Object> attributesMap = new HashMap<String, Object>();
    attributesMap.put("idFeature", suolo.getIdFeature());
    attributesMap.put("codiceNazionale", suolo.getCodiceNazionale());
    attributesMap.put("foglio", suolo.getFoglio());
    attributesMap.put("idEleggibilitaRilevata", suolo.getIdEleggibilitaRilevata());
    attributesMap.put("codiceEleggibilitaRilevata", suolo.getCodiceEleggibilitaRilevata());
    attributesMap.put("descEleggibilitaRilevata", suolo.getDescEleggibilitaRilevata());
    attributesMap.put("idIstanzaRiesame", suolo.getIdIstanzaRiesame());
    attributesMap.put("coordinateFotoAppezzamento", suolo.getCoordinateFotoAppezzamentoStrJson());
    attributesMap.put("srid", setNvlSRID(suolo.getSrid()));
    
    return attributesMap;
  }

  private Map<String, Object> setAttributeFoglioRiferimento(FoglioRiferimentoDTO suolo)
  {
    HashMap<String, Object> attributesMap = new HashMap<String, Object>();
    //attributesMap.put("idFoglioRiferimento", suolo.getIdFoglioRiferimento());
    attributesMap.put("idGeoFoglio", suolo.getIdGeoFoglio());
    attributesMap.put("codComBelfiore", suolo.getCodComBelfiore());
    attributesMap.put("codComIstat", suolo.getCodComIstat());
    attributesMap.put("comune", suolo.getComune());
    attributesMap.put("sezione", suolo.getSezione());
    attributesMap.put("allegato", suolo.getAllegato());
    attributesMap.put("sviluppo", suolo.getSviluppo());
    attributesMap.put("aggiornatoAl", suolo.getAggiornatoAl());
    attributesMap.put("stato", suolo.getStato());
    attributesMap.put("srid", setNvlSRID(suolo.getSrid()));
    attributesMap.put("codComIstatBdtre", suolo.getCodComIstatBdtre());
    return attributesMap;
  }

  private Map<String, Object> setAttributeParticella(ParticellaDTO particella)
  {
    HashMap<String, Object> attributesMap = new HashMap<String, Object>();
    attributesMap.put("idFeature", particella.getIdFeature());
    attributesMap.put("numeroParticella", particella.getNumeroParticella());
    attributesMap.put("subalterno", particella.getSubalterno());
    attributesMap.put("srid", setNvlSRID(particella.getSrid()));
    attributesMap.put("flagConduzione", particella.getFlagConduzione());
    attributesMap.put("flagSospensioneOrig", particella.getFlagSospensione());
    attributesMap.put("descrizioneSospensione", particella.getDescrizioneSospensione());
    if(particella.getErrore()!=null)
      attributesMap.put("errore", particella.getErrore());

    return attributesMap;
  }
  public GeoJSONFeatureCollection getParticelleFoglio(long idEventoLavorazione, String cuaa,
      String codiceNazionale, long foglio, long annoCampagna) throws ParseException, IOException
  {
    final String THIS_METHOD = "getParticelleFoglio";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      long tempo_iniziale_milli = System.currentTimeMillis();
      
      logger.debug(" *** Inizio query getParticelleFoglio **** ");

      GeoJSONFeatureCollection featureCollection = new GeoJSONFeatureCollection();
      ArrayList<String> listFeaturesString = new ArrayList<String>();

      List<ParticellaDTO> particelle = pianoColturaleDAO.getParticelleFoglio(idEventoLavorazione, cuaa, codiceNazionale, foglio, annoCampagna);
      logger.debug(" *** fine query getParticelleFoglio **** : tempo elaborazione= "+(System.currentTimeMillis()-tempo_iniziale_milli)/1000);

      if(particelle!=null)
      {
        logger.debug(" *** Inizio elaborazione dati query****");
        for(ParticellaDTO particella : particelle)
        {
          try {
            listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON(particella.getGeometriaWkt(),setAttributeParticella(particella),setNvlSRID(particella.getSrid()),"Feature",null));
          }
          catch (IllegalArgumentException e)
          {
            //La funzionalità di conversione fallisce se la geometria è "sporca"
            try {
              
              logger.debug(" *** FixShape idParticella: " + particella.getIdFeature());

              //FIXSHAPE - funzione che pulisce la geometria
              String wktCorretto = pianoColturaleDAO.fixShape(particella.getGeometriaWkt());
              logger.debug(" *** FixShape ESEGUITO idParticella: " + particella.getIdFeature());

              //Riporvo a convertire la geometria pulita
              listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON(wktCorretto,setAttributeParticella(particella),setNvlSRID(particella.getSrid()),"Feature",null));
            }
            catch(IllegalArgumentException e2)
            {
              //Se fallisce di nuovo allora segnalo l'errore.
              logger.debug(" *** FixShape FALLITO idParticella: " + particella.getIdFeature());
              logger.debug("La geometria presenta degli errori.");
              e2.printStackTrace();
              particella.setErrore("La geometria presenta degli errori.");
              //e aggiungo l'attributo "errore" al geoJson, mentre la geometria passata sarà vuota
              listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON("POLYGON EMPTY",setAttributeParticella(particella),setNvlSRID(particella.getSrid()),"Feature",null));
            }

          }
        }
      }
      featureCollection.setFeaturesString(listFeaturesString);
      logger.debug(" *** FINE ELABORAZIONE DATI *****");

      return featureCollection;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  } 


  public List<ClasseEleggibilitaDTO> getClassiEleggibilita()
  {
    final String THIS_METHOD = "getClassiEleggibilita";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getClassiEleggibilita();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  public boolean isEventoBloccato(long idEventoLavorazione, Long idUtenteLogin)
  {
    final String THIS_METHOD = "isEventoBloccato";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.isEventoBloccato(idEventoLavorazione,idUtenteLogin);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public int sbloccoForzato(long idEventoLavorazione, Long idUtenteLogin)
  {
    final String THIS_METHOD = "sbloccoForzato";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      int sblocco = pianoColturaleDAO.sbloccoForzatoFogli(idEventoLavorazione, idUtenteLogin);
      pianoColturaleDAO.sbloccoEvento(idEventoLavorazione, idUtenteLogin);
      return sblocco;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  public void sbloccoForzatoEvento(long idEventoLavorazione, Long idUtenteLogin)
  {
    final String THIS_METHOD = "sbloccoForzatoEvento";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      pianoColturaleDAO.sbloccoEvento(idEventoLavorazione, idUtenteLogin);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public EsitoDTO salvaSuoli(GeoJSONFeatureCollection geoJson, Long idUtenteLogin) throws IOException, ParseException
  {
    final String THIS_METHOD = "salvaSuoli";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    EsitoDTO esitoDTO = new EsitoDTO();
    esitoDTO.setError();
    
    ObjectMapper objectMapper = new ObjectMapper();
    logger_geojson.info(objectMapper.writeValueAsString(geoJson));
    
    try
    {
      ArrayList<SuoloLavoratoDTO> suoliLavorati = new ArrayList<SuoloLavoratoDTO>();
      ArrayList<SuoloParticellaDTO> suoliParticelle = new ArrayList<SuoloParticellaDTO>();
      ArrayList<SuoloCessatoDTO> suoliCessati = new ArrayList<SuoloCessatoDTO>();
      ArrayList<SuoloConfigurazioneDTO> suoliConfigurazione = new ArrayList<SuoloConfigurazioneDTO>();
      ArrayList<ParticellaCessataDTO> particelleCessate = new ArrayList<ParticellaCessataDTO>();
      ArrayList<ParticellaLavorataDTO> particellelavorate = new ArrayList<ParticellaLavorataDTO>();
      ArrayList<ParticellaLavorataDTO> particelleSospese = new ArrayList<ParticellaLavorataDTO>();
      
      List<Long> idsParticelleCessate = new ArrayList<Long>();
      List<Long> idsParticelleInserite = new ArrayList<Long>();
      List<Long> idsSuoliCessati = new ArrayList<Long>();
      List<Long> idsSuoliInseriti = new ArrayList<Long>();
      
      Long idEventoLavorazione = -1l;
      String codiceNazionale = null;
      int foglio = 0;
      
      for(SimpleFeature feature : geoJson.getFeatures())
      {
          Property layer =  feature.getProperty("layer");
          
          if(idEventoLavorazione.longValue()<=0 &&  feature.getProperty("idEventoLavorazione")!=null)
          {
            idEventoLavorazione = (Long) feature.getProperty("idEventoLavorazione").getValue();
            logger_geojson.info("idEventoLavorazione= "+idEventoLavorazione +" - CUAA= "+pianoColturaleDAO.getCuaaFromEventoLavorazione(idEventoLavorazione));
          }
          
          String tipo = (String) layer.getValue();
          switch(tipo) {
            case AgriApiConstants.LAYER.SUOLI_LAVORATI:
              SuoloLavoratoDTO suoloLavorato = creaSuoloLavorato(feature);
              suoliLavorati.add(suoloLavorato);
              idEventoLavorazione = suoloLavorato.getIdEventoLavorazione();
              if(codiceNazionale==null && suoloLavorato.getCodiceNazionale()!=null)
                codiceNazionale = suoloLavorato.getCodiceNazionale();
              if(foglio==0 && suoloLavorato.getFoglio()!=null && suoloLavorato.getFoglio().trim().length()>=0)
                foglio = Integer.parseInt(suoloLavorato.getFoglio());
              break;
            case AgriApiConstants.LAYER.SUOLI_PARTICELLE:
              SuoloParticellaDTO suoloParticella = creaSuoloParticella(feature);
              suoliParticelle.add(suoloParticella);
              if(idEventoLavorazione==-1)
                idEventoLavorazione = suoloParticella.getIdEventoLavorazione();
              if(codiceNazionale==null && suoloParticella.getCodiceNazionale()!=null)
                codiceNazionale = suoloParticella.getCodiceNazionale();
              if(foglio==0 && suoloParticella.getFoglio()!=null && suoloParticella.getFoglio().trim().length()>=0)
                foglio = Integer.parseInt(suoloParticella.getFoglio());
              break;
            case AgriApiConstants.LAYER.SUOLI_CESSATI: 
              if(feature.getProperty("idFeature")!=null) {
                SuoloCessatoDTO suoloCessato = creaSuoloCessato(feature);
                suoliCessati.add(suoloCessato);
                idsSuoliCessati.add(suoloCessato.getIdFeature());
                if(idEventoLavorazione==-1)
                  idEventoLavorazione = suoloCessato.getIdEventoLavorazione();
              }
              break;
            case AgriApiConstants.LAYER.PARTICELLE_CESSATE: 
              if(feature.getProperty("idFeature")!=null) {
                ParticellaCessataDTO particellaCessata = creaParticellaCessata(feature);
                particelleCessate.add(particellaCessata);
                idsParticelleCessate.add(particellaCessata.getIdFeature());
                if(idEventoLavorazione==-1)
                  idEventoLavorazione = particellaCessata.getIdEventoLavorazione();
              }
            break;              
            case AgriApiConstants.LAYER.PARTICELLE_LAVORATE: 
                ParticellaLavorataDTO particellaLavorata = creaParticellaLavorata(feature);
                particellelavorate.add(particellaLavorata);
                if(idEventoLavorazione==-1)
                  idEventoLavorazione = particellaLavorata.getIdEventoLavorazione();
                if(codiceNazionale==null && particellaLavorata.getCodiceNazionale()!=null)
                  codiceNazionale = particellaLavorata.getCodiceNazionale();
                if(foglio==0 && particellaLavorata.getFoglio()!=null && particellaLavorata.getFoglio().trim().length()>=0)
                  foglio = Integer.parseInt(particellaLavorata.getFoglio());
              break;  
            case AgriApiConstants.LAYER.PARTICELLE_SOSPESE: 
                ParticellaLavorataDTO particellaSospesa = creaParticellaLavorata(feature);
                particelleSospese.add(particellaSospesa);
                if(idEventoLavorazione==-1)
                  idEventoLavorazione = particellaSospesa.getIdEventoLavorazione();
                if(codiceNazionale==null && particellaSospesa.getCodiceNazionale()!=null)
                  codiceNazionale = particellaSospesa.getCodiceNazionale();
                if(foglio==0 && particellaSospesa.getFoglio()!=null && particellaSospesa.getFoglio().trim().length()>=0)
                  foglio = Integer.parseInt(particellaSospesa.getFoglio());
              break;   
              
            case AgriApiConstants.LAYER.CONFIGURAZIONE: 
              SuoloConfigurazioneDTO configurazione = creaSuoloConfigurazione(feature);
              suoliConfigurazione.add(configurazione);
              if(idEventoLavorazione==-1)
                idEventoLavorazione = configurazione.getIdEventoLavorazione();
              break;
          }
      }
      
      pianoColturaleDAO.lockEventoLavorazione(idEventoLavorazione);
      pianoColturaleDAO.aggiornaStatoSalvataggioEventoLavorazione(idEventoLavorazione, AgriApiConstants.ESITO.STATO_SALVATAGGIO.SALVATAGGIO_IN_CORSO);
      
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. suoliLavorati: "+suoliLavorati.size());
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. suoliParticelle: "+suoliParticelle.size());
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. suoliCessati: "+suoliCessati.size());
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. particelleCessate: "+particelleCessate.size());
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. particellelavorate: "+particellelavorate.size());
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. particelleSospese: "+particelleSospese.size());
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. suoliConfigurazione: "+suoliConfigurazione.size());
     
      
     if(!pianoColturaleDAO.isEventoBloccato(idEventoLavorazione, null))
      {
        esitoDTO.setEsito(AgriApiConstants.ESITO.NEGATIVO_EVENTO_NON_BLOCCATO);
        esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.EVENTO_NON_BLOCCATO);
        return esitoDTO;
      }
      if(pianoColturaleDAO.isEventoBloccato(idEventoLavorazione, idUtenteLogin))
      {
        esitoDTO.setEsito(AgriApiConstants.ESITO. NEGATIVO_EVENTO_BLOCCATO_DA_ALTRI);
        esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.EVENTO_BLOCCATO_DA_ALTRI);
        return esitoDTO;
      }
      
     
      //controllo se il salvataggio è avvenuto con un bypass da parte dell'operatore e salvo l'operazione
      if(suoliConfigurazione!=null && suoliConfigurazione.size()>0)
      {
        for(SuoloConfigurazioneDTO row: suoliConfigurazione)
        {
          pianoColturaleDAO.insertBypass(row, idUtenteLogin);
        }
      }
      
      //controllo dell'area dei suoli creati rispetto a quella dei suoli cessati, se discostano di un parametro che salverei sul db si blocca il salvataggio.
      BigDecimal areaSuoliCessati = null;
      if(suoliCessati!=null && suoliCessati.size()>0)
      {
        List<Long> ids = new ArrayList<Long>();
        for(SuoloCessatoDTO item: suoliCessati) {
          if(item.getIdFeature()!=null)
            ids.add(item.getIdFeature());
        }
        areaSuoliCessati = pianoColturaleDAO.getAreaSuoliRilevatiByList(ids);
      }
      BigDecimal areaSuoliLavorati = null;
      if(suoliLavorati!=null && suoliLavorati.size()>0)
      {
        areaSuoliLavorati = BigDecimal.ZERO;
        for(SuoloLavoratoDTO item: suoliLavorati) {
          if(item.getIdFeature()==null)
            areaSuoliLavorati = areaSuoliLavorati.add(new BigDecimal(item.getArea()));
        }
      }
      
      ParametroDTO tolleranza = pianoColturaleDAO.getParametroByName("TOLL_SALVA");
      
      if(tolleranza!=null && areaSuoliCessati!=null && areaSuoliLavorati!=null)
      {
        if(areaSuoliCessati.compareTo(areaSuoliLavorati)>0)
        {
          BigDecimal diffArea = areaSuoliLavorati.subtract(areaSuoliCessati);
          //valore assoluto
          //diffArea = new BigDecimal(Math.abs(diffArea.doubleValue()));
          if(diffArea.compareTo(tolleranza.getValoreNumerico()) > 0)
          {
            logger.error("[" + THIS_CLASS + "." + THIS_METHOD + "] La differenza tra le aree dei suoli creati e quelli cessati supera il coefficiente impostato da parametro. parametro('CHKSALVA') :"+tolleranza.getValoreNumerico()+" , areaSuoliLavorati:"+GraficoUtils.NUMBERS.arrotonda(areaSuoliLavorati.doubleValue(), 4) +", areaSuoliCessati:"+GraficoUtils.NUMBERS.arrotonda(areaSuoliCessati.doubleValue(), 4));
            TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
            esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
            esitoDTO.setMessaggio(" La differenza tra le aree dei suoli creati e quelli cessati supera il limite consentito. parametro('TOLL_SALVA') :"+tolleranza.getValoreNumerico()+" , areaSuoliLavorati:"+GraficoUtils.NUMBERS.arrotonda(areaSuoliLavorati.doubleValue(), 4) +", areaSuoliCessati:"+GraficoUtils.NUMBERS.arrotonda(areaSuoliCessati.doubleValue(), 4));
            return esitoDTO;
          }
        }
      }
      
      Date dataAggiornamento = new Date();
      //La data fine validita deve essere la dataAggiornamento meno un secondo
      Calendar cal = Calendar.getInstance();
      cal.setTime(dataAggiornamento);
      cal.add(Calendar.SECOND, -1);
      Date dataFineValidita = cal.getTime();
      //SALVATAGGIO SU DB
      
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] INI lavorazione SUOLI_LAVORATI ");
      for(SuoloLavoratoDTO suolo : suoliLavorati)
      {
          foglio = Integer.parseInt(suolo.getFoglio());
          codiceNazionale = suolo.getCodiceNazionale();
          
          logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] SUOLI_LAVORATO:  foglio="+foglio+", codNazionale:"+codiceNazionale);
          if(suolo.getIdFeature()!=null)
          {
            logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] SUOLI_LAVORATO:  IdFeature="+suolo.getIdFeature());  
          }
          //inserisco su tabella work il log che è stato salvato questo foglio. Viene usato come verifica sui servizi di sblocco foglio
          pianoColturaleDAO.insertWFogliLavorati(idEventoLavorazione,foglio,codiceNazionale);
          
          
          if(suolo.getIdFeature()!=null)
          {
            //Aggiorno la feature solo se è stata variata
            if(suolo.getFlagGeometriaVariata() == 1L)
            {
              pianoColturaleDAO.updateSuoloRilevato(idEventoLavorazione, suolo.getIdFeature(), suolo.getGeometry(), dataAggiornamento, idUtenteLogin, null);
            }
          }
          else 
          {
            //inserire nuovo SUOLO_RILEVATO
            Long idSuoloRilevato = pianoColturaleDAO.insertSuoloRilevato(idEventoLavorazione, suolo, dataAggiornamento, idUtenteLogin);
            idsSuoliInseriti.add(idSuoloRilevato);
            suolo.setIdFeature(idSuoloRilevato);
            //inserire nuova VARIAZIONE_SUOLO_RIL con l'id di ogni idFeaturePadre e l'Id_Suolo_Rilevato appena staccato
            if(suolo.getIdFeaturePadre()!=null)
            {
              for(Long idFeaturePadre : suolo.getIdFeaturePadre())
              {
                if(idFeaturePadre!=null)
                {
                  pianoColturaleDAO.insertVariazioneSuoloRil(idSuoloRilevato, idFeaturePadre, dataAggiornamento);
                  //  QGISAGRI-20
                  // All'inserimento di un nuovo suolo rilevato, si controlla se il suolo padre ha dei 
                  //record attivi nella tabella QGIS_T_SUOLO_UNAR. Se ci sono vengono legati anche al nuovo suolo rilevato.
                  if(pianoColturaleDAO.padreHasSuoloUnar(idFeaturePadre))
                    pianoColturaleDAO.insertSuoloUnarFiglio(idSuoloRilevato, idFeaturePadre);
                }
              
              }
            }
          }
          
          //Aggiorno suoli lavorazione, se esistono, se no li inserisco
          if(!pianoColturaleDAO.esisteSuoloLavorazione(idEventoLavorazione, suolo.getIdFeature()))
            pianoColturaleDAO.insertSuoloLavorazione(idEventoLavorazione, suolo.getIdFeature(), suolo.getTipoSuolo(),idUtenteLogin.longValue());
          
          pianoColturaleDAO.updateSuoloLavorazione(idEventoLavorazione, suolo.getIdFeature(), suolo.getDescrizioneSospensione(), suolo.getFlagSospensione(), suolo.getNoteLavorazione(), suolo.getIdTipoMotivoSospensione(),idUtenteLogin.longValue());
          
          //lo faccio pure per tutti i padri
          if(suolo.getIdFeaturePadre()!=null)
          {
            for(Long idFeature : suolo.getIdFeaturePadre())
            {
              if(!pianoColturaleDAO.esisteSuoloLavorazione(idEventoLavorazione, idFeature))
                pianoColturaleDAO.insertSuoloLavorazione(idEventoLavorazione, idFeature, suolo.getTipoSuolo(),idUtenteLogin.longValue());
              
              pianoColturaleDAO.updateSuoloLavorazione(idEventoLavorazione, idFeature, suolo.getDescrizioneSospensione(), suolo.getFlagSospensione(), suolo.getNoteLavorazione(), suolo.getIdTipoMotivoSospensione(),idUtenteLogin.longValue());
            }
          }

       }
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] FINE lavorazione SUOLI_LAVORATI ");
      
      
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] INI lavorazione PARTICELLE_LAVORATE ");
      pianoColturaleDAO.rimuoviSospendiParticellaLavorata(idEventoLavorazione);
      for(ParticellaLavorataDTO particellaLavorata : particellelavorate)
      {
          try {  
          Long.parseLong(particellaLavorata.getNumeroParticella());
          }catch(Exception e) {
            continue; //un esempio sono le strade
          }
            
          foglio = Integer.parseInt(particellaLavorata.getFoglio());
          codiceNazionale = particellaLavorata.getCodiceNazionale();
          long idVersioneParticella =0;
          if(particellaLavorata.getIdFeature()!=null && particellaLavorata.getIdFeature().longValue()>0)
          {
            idVersioneParticella = particellaLavorata.getIdFeature();
          }
          else
          {
            idVersioneParticella = pianoColturaleDAO.insertVersioneParticella(particellaLavorata, idUtenteLogin);
            idsParticelleInserite.add(idVersioneParticella);
          }
          particellaLavorata.setIdFeature(idVersioneParticella);
          
          if(!pianoColturaleDAO.esisteParticelleLavorazione(particellaLavorata))
            pianoColturaleDAO.insertParticellaLavorata(particellaLavorata);
          else
            pianoColturaleDAO.updateEventoLavorazioneParticellaLavorazione(particellaLavorata);
       }
      
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] FINE lavorazione PARTICELLE_LAVORATE ");
      
      
      
      for(SuoloCessatoDTO suolo : suoliCessati)
      {
        if(suolo.getIdFeature()!=null && suolo.getIdFeature().longValue()>0)
        {
          pianoColturaleDAO.updateSuoloRilevato(idEventoLavorazione, suolo.getIdFeature(), null, dataAggiornamento, idUtenteLogin, dataFineValidita);
          pianoColturaleDAO.updateCessaSuoloLavorazione(idEventoLavorazione, suolo.getIdFeature(),idUtenteLogin);
        }
      }
      
      for(ParticellaCessataDTO particellaCessata : particelleCessate)
      {
        if(particellaCessata.getIdFeature()!=null && particellaCessata.getIdFeature().longValue()>0)
        {
          pianoColturaleDAO.insertParticellaCessata(particellaCessata.getIdEventoLavorazione(), particellaCessata.getIdFeature());
          pianoColturaleDAO.updateVersioneParticellaCessata(particellaCessata.getIdFeature());
        }
      }
      
      for(ParticellaLavorataDTO particellaSospesa : particelleSospese)
      {
          foglio = Integer.parseInt(particellaSospesa.getFoglio());
          codiceNazionale = particellaSospesa.getCodiceNazionale();
          pianoColturaleDAO.sospendiParticellaLavorata(particellaSospesa.getIdParticellaLavorazione().longValue(), particellaSospesa.getDescrizioneSospensione());
      }
      
      
      //Aggiorno registro suoli e particelle
      String campagna = pianoColturaleDAO.getAnnoCampagna(idEventoLavorazione);
      pianoColturaleDAO.callAggiornaRegistroParticelle(campagna, codiceNazionale, foglio, getDistinct(idsParticelleCessate), getDistinct(idsParticelleInserite));
      
      String tableSuoli = pianoColturaleDAO.getTabellaRegistroSuoli(idEventoLavorazione);
      //ATENZIONE!! mettiamo la callAggiornaRegistroSuoli qua perchè se no abbiamo problemi  nella chiamata successiva a getIdVersioneParticella dove non troverebbe nulla
      if(!AgriApiConstants.TABELLA_REGISTRO.CO.equalsIgnoreCase(tableSuoli))
        pianoColturaleDAO.callAggiornaRegistroSuoli(campagna, codiceNazionale, foglio, getDistinct(idsSuoliCessati), getDistinct(idsSuoliInseriti));
      
            
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] INI lavorazione SUOLI_PARTICELLA ");
       int progr = 1;
       for(SuoloParticellaDTO suolo : suoliParticelle)
       {
         //in più bisogna aggiornare cancellare e inserire nuovamente le geometrie ritagliate sulle particelle in QGIS_T_SUOLO_PARTICELLA
         if(suolo.getOgcFidSuolo()!=null)
         {
           logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] SUOLI_PARTICELLA ogcPadre:"+suolo.getOgcFidSuolo());
           //find suolo padre
           for(SuoloLavoratoDTO s : suoliLavorati)
           {
             if(s.getOgcLayerID().longValue() == suolo.getOgcLayerIDSuolo() && suolo.getOgcFidSuolo().equals(s.getOgcFid()))
             {
               
               if(suolo.getIdFeature()==null || s.getIdFeature().longValue()==0)
               {
                 //manca la features fare la insert su versione particelle e poi su suolo rilevato 
                 String annoCampagna = pianoColturaleDAO.getAnnoCampagna(idEventoLavorazione);
                 Long idVersioneParticellaNew = pianoColturaleDAO.getIdVersioneParticella(suolo.getFoglio(),suolo.getCodiceNazionale(),suolo.getNumeroParticella(),suolo.getSubalterno(), annoCampagna);
                 
                 if(idVersioneParticellaNew==null)
                 {
                   logger.error("[" + THIS_CLASS + "." + THIS_METHOD + "] impossibile recuperare la versione particella: codiceNazionale: " + codiceNazionale + ", foglio: " + foglio + ", numeroParticella: " + suolo.getNumeroParticella() +", subalterno: " + suolo.getSubalterno() +", annoCampagna: "+annoCampagna);
                   TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
                   esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
                   esitoDTO.setMessaggio("Attenzione, impossibile recuperare la versione particella");
                   return esitoDTO;
                 }
                 suolo.setIdFeature(idVersioneParticellaNew);
                 suolo.setGeometry(suolo.getGeometry());
                 suolo.setArea(suolo.getArea());
               }
               
               
               //inserisco solo se non c'è già un record a parià di Id_Suolo_Rilevato e Id_Versione_Particella
               if(!pianoColturaleDAO.esisteSuoloParticella(s.getIdFeature(), suolo.getIdFeature()))
               { 
                 logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] inserimento suolo_particella per  ID_SUOLO_RILEVATO:"+s.getIdFeature()+" - ID_VERSIONE_PARTICELLA:"+suolo.getIdFeature());
                 pianoColturaleDAO.insertSuoloParticella(s.getIdFeature(), suolo, dataAggiornamento, idUtenteLogin, progr,idEventoLavorazione);
                 progr++;
               }
               else {
                 logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "]  suolo_particella gia presente per ID_SUOLO_RILEVATO:"+s.getIdFeature()+" - ID_VERSIONE_PARTICELLA:"+suolo.getIdFeature());
               }
             }
           }
         }else {
           logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] SUOLI_PARTICELLA ogcPadre null");
         }
       }
       logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] FINE lavorazione SUOLI_PARTICELLA ");
       
       
       
       //Aggiorno registro suoli e particelle
       if(AgriApiConstants.TABELLA_REGISTRO.CO.equalsIgnoreCase(tableSuoli))
         pianoColturaleDAO.callAggiornaRegistroSuoliCO(campagna, codiceNazionale, foglio, getDistinct(idsSuoliCessati), getDistinct(idsSuoliInseriti));

       
      pianoColturaleDAO.updateLavorazioneFoglio(foglio, codiceNazionale);
      pianoColturaleDAO.updateEventoLavorazione(idEventoLavorazione, dataAggiornamento, idUtenteLogin);
      pianoColturaleDAO.sbloccaFoglio(foglio, codiceNazionale, idUtenteLogin);
      
      Long countFogliNonLavorati = pianoColturaleDAO.countFogliSuoliNonLavorati(idEventoLavorazione);
      
      if(countFogliNonLavorati==null || countFogliNonLavorati.longValue() == 0)
        countFogliNonLavorati = pianoColturaleDAO.countFogliParticelleNonLavorati(idEventoLavorazione);
      
//      if(countFogliNonLavorati==null || countFogliNonLavorati.longValue() == 0)
//      {
//        if(!pianoColturaleDAO.checkControlloControcampo(idEventoLavorazione))
//        {
//          esitoDTO.setEsito(AgriApiConstants.ESITO.ERRORE);
//          esitoDTO.setMessaggio("Attenzione, prima di procedere con il salvataggio occorre compilare e poi consolidare i dati del contraddittorio e/o del sopralluogo");
//          return esitoDTO;
//        }
//      }
      

      
      //Controllo se sbloccare l'evento   --> esistonoFogliParticelleNonLavorati solo se la lavorazione id_tipo_lavorazione == 1 allora particella
      
      long idTipoLista = pianoColturaleDAO.getIdTipoLista(idEventoLavorazione);
      if(idTipoLista == AgriApiConstants.TIPO_LAVORAZIONE.PARTICELLE) {
        if(!pianoColturaleDAO.esistonoFogliParticelleNonLavorati(idEventoLavorazione))
        {
          pianoColturaleDAO.deleteWGestioneFogliLavorati(idEventoLavorazione);
          pianoColturaleDAO.sbloccoEvento(idEventoLavorazione, idUtenteLogin);
          esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FOGLIO_ED_EVENTO_SBLOCCATO);
          esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.FOGLIO_ED_EVENTO_SBLOCCATO);
          return esitoDTO;
        }
      }
      else if(idTipoLista == AgriApiConstants.TIPO_LAVORAZIONE.SUOLI) {
        if(!pianoColturaleDAO.esistonoFogliSuoliNonLavorati(idEventoLavorazione))
        {
          pianoColturaleDAO.deleteWGestioneFogliLavorati(idEventoLavorazione);
          pianoColturaleDAO.sbloccoEvento(idEventoLavorazione, idUtenteLogin);
          esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FOGLIO_ED_EVENTO_SBLOCCATO);
          esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.FOGLIO_ED_EVENTO_SBLOCCATO);
          return esitoDTO;
        }
      }
      
      
      
      
      
      esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FOGLIO_SBLOCCATO);
      esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.FOGLIO_SBLOCCATO);
      return esitoDTO;
    }
    catch (Exception e)
    {
      TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. eccezione: "+e.getMessage());
      e.printStackTrace();
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] .",e);
      }
      
      esitoDTO.setError();
      esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.SALVA_SUOLI_GENERICO);
      return esitoDTO;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  private List<Long> getDistinct(List<Long> values)
  {
    if(values==null)
      return null;
    
    List<Long> elenco = new ArrayList<Long>();
    for(Long val: values) {
      if(!elenco.contains(val))
        elenco.add(val);
    }
    
    return elenco;
  }
  
  public void aggiornaStatoSalvataggioEventoLavorazione(Long idEventoLavorazione, String codiceEsito)
  {
    pianoColturaleDAO.aggiornaStatoSalvataggioEventoLavorazione(idEventoLavorazione, codiceEsito);
  }
  
  @Async
  @Transactional(timeout = 7200) 
  public void callMainSalvaIstanzaAnagrafe(long idEventoLavorazione) {
    final String THIS_METHOD = "callMainSalvaIstanzaAnagrafe";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.  idEventoLavorazione# "+idEventoLavorazione);
    }
    try
    {
      pianoColturaleDAO.aggiornaStatoSalvataggioEventoLavorazione(idEventoLavorazione, AgriApiConstants.ESITO.STATO_SALVATAGGIO.SALVATAGGIO_ISTANZA_IN_CORSO);
      Long nFogli = pianoColturaleDAO.countFogliSuoliNonLavorati(idEventoLavorazione);
      
      if(nFogli==null || nFogli.longValue()==0 )
        nFogli = pianoColturaleDAO.countFogliParticelleNonLavorati(idEventoLavorazione);
      
      if(nFogli==null || nFogli.longValue()==0 )
      {
        if(pianoColturaleDAO.checkAnnoCampagna(idEventoLavorazione))
        {
          //chiudo istanza riesame su anag
          MainControlloDTO controlloDTO = pianoColturaleDAO.callMainSalvaIstanzaAnagrafe(idEventoLavorazione);
          if(controlloDTO==null || (controlloDTO.getRisultato()!=null && !controlloDTO.getRisultato().equals("0"))) {
            logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] pianoColturaleDAO.callMainSalvaIstanzaAnagrafe errore!! idEventoLavorazione = "+idEventoLavorazione+" , risultato: "+controlloDTO.getRisultato() +" - msg:"+controlloDTO.getMessaggio());
            pianoColturaleDAO.aggiornaStatoSalvataggioEventoLavorazione(idEventoLavorazione, AgriApiConstants.ESITO.STATO_SALVATAGGIO.SALVATAGGIO_ISTANZA_TERMINATO_CON_ERRORE);
          }
        }
       }
      
      pianoColturaleDAO.aggiornaStatoSalvataggioEventoLavorazione(idEventoLavorazione, AgriApiConstants.ESITO.STATO_SALVATAGGIO.SALVATAGGIO_TERMINATO);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }


  private SuoloLavoratoDTO creaSuoloLavorato(SimpleFeature feature) throws IOException, ParseException
  {
    SuoloLavoratoDTO suolo = new SuoloLavoratoDTO();
    Long idEventoLavorazione = (Long) feature.getProperty("idEventoLavorazione").getValue();
    Long idFeature = null;
    if(feature.getProperty("idFeature")!=null)
      idFeature = (Long) feature.getProperty("idFeature").getValue();
    
    Long ogcFid = null;
    Long ogcLayerID = null;
    String layer = null;
    String tipoSuolo = null;
    Long flagSospensione = null;
    String codiceEleggibilitaRilevata = null;
    String descrizioneSospensione = "";
    String noteLavorazione = "";
    
    if(feature.getProperty("OGC_FID")!=null)
      ogcFid = (Long) feature.getProperty("OGC_FID").getValue();
    if(feature.getProperty("OGC_LAYERID")!=null)
      ogcLayerID = (Long) feature.getProperty("OGC_LAYERID").getValue();
    if(feature.getProperty("layer")!=null)
      layer = (String) feature.getProperty("layer").getValue();
    if(feature.getProperty("tipoSuolo")!=null)
      tipoSuolo = (String) feature.getProperty("tipoSuolo").getValue();
    
    ArrayList<Long> idFeaturePadre=null;
    try {
      idFeaturePadre = (ArrayList<Long>) feature.getProperty("idFeaturePadre").getValue();
    }catch (Exception e) {
      if(feature.getProperty("idFeaturePadre")!=null)
      {
        String tmp = (String) feature.getProperty("idFeaturePadre").getValue();
        long tmpLong = Long.parseLong(tmp.replace("[", "").replace("]", ""));
        idFeaturePadre = new ArrayList<Long>();
        idFeaturePadre.add(tmpLong);
      }
    }
    
    Double area =  (Double) feature.getProperty("area").getValue();
    String codiceNazionale = (String) feature.getProperty("codiceNazionale").getValue();
    String foglio = (String) feature.getProperty("foglio").getValue();
    Long flagGeometriaVariata = (Long) feature.getProperty("flagGeometriaVariata").getValue();
    
    if(feature.getProperty("codiceEleggibilitaRilevata")!=null && feature.getProperty("codiceEleggibilitaRilevata").getValue()!=null)
      codiceEleggibilitaRilevata = (String) feature.getProperty("codiceEleggibilitaRilevata").getValue();
    
    if(feature.getProperty("flagSospensione")!=null && feature.getProperty("flagSospensione").getValue()!=null)
      flagSospensione = (Long) feature.getProperty("flagSospensione").getValue();
    
    if(feature.getProperty("descrizioneSospensione")!=null && feature.getProperty("descrizioneSospensione").getValue()!=null)
      descrizioneSospensione = (String) feature.getProperty("descrizioneSospensione").getValue();
    
    if(feature.getProperty("noteLavorazione")!=null && feature.getProperty("noteLavorazione").getValue()!=null)
      noteLavorazione = (String) feature.getProperty("noteLavorazione").getValue();
    
    Long idTipoMotivoSospensione = null;
    
    if(feature.getProperty("idTipoMotivoSospensione")!=null && feature.getProperty("idTipoMotivoSospensione").getValue()!=null && (Long) feature.getProperty("idTipoMotivoSospensione").getValue()!=0)
      idTipoMotivoSospensione = (Long) feature.getProperty("idTipoMotivoSospensione").getValue();

    Geometry geometry = (Geometry) feature.getProperty("geometry").getValue();
    suolo.setIdEventoLavorazione(idEventoLavorazione);
    suolo.setIdFeature(idFeature);
    suolo.setOgcFid(ogcFid);
    suolo.setOgcLayerID(ogcLayerID);
    suolo.setTipoSuolo(tipoSuolo);
    suolo.setLayer(layer);
    suolo.setIdFeaturePadre(idFeaturePadre);
    suolo.setArea(area);
    suolo.setCodiceNazionale(codiceNazionale);
    suolo.setFoglio(foglio);
    suolo.setFlagGeometriaVariata(flagGeometriaVariata);
    suolo.setCodiceEleggibilitaRilevata(codiceEleggibilitaRilevata);
    suolo.setFlagSospensione(flagSospensione);
    suolo.setDescrizioneSospensione(descrizioneSospensione);
    suolo.setNoteLavorazione(noteLavorazione);
    suolo.setIdTipoMotivoSospensione(idTipoMotivoSospensione);
    suolo.setGeometry(geometry);
    return suolo;
  }
  
  
  
  private SuoloParticellaDTO creaSuoloParticella(SimpleFeature feature) throws IOException, ParseException
  {
    SuoloParticellaDTO suolo = new SuoloParticellaDTO();
    Long idEventoLavorazione = null;
    Long idFeature = null;
    Long ogcFidSuolo = null;
    Long ogcFidParticella = null;
    
    Long ogcLayerIDSuolo = null;
    Long ogcLayerIDParticella = null;
    
    String layer = null;
    Double area =  null;
    Geometry geometry = null;
    
    String subalterno = null;
    String numeroParticella = null;
    String codiceEleggibilitaRilevata = null;
    String codiceNazionale = null;
    String foglio = null;
    
    if(feature.getProperty("idEventoLavorazione")!=null)
      idEventoLavorazione = (Long) feature.getProperty("idEventoLavorazione").getValue();
    
    if(feature.getProperty("idFeature")!=null)
      idFeature = (Long) feature.getProperty("idFeature").getValue();
    
    if(feature.getProperty("OGC_FID_SUOLO")!=null)
      ogcFidSuolo = (Long) feature.getProperty("OGC_FID_SUOLO").getValue();
    
    if(feature.getProperty("OGC_FID_PARTICELLA")!=null)
      ogcFidParticella = (Long) feature.getProperty("OGC_FID_PARTICELLA").getValue();
    
    if(feature.getProperty("OGC_LAYERID_SUOLO")!=null)
      ogcLayerIDSuolo = (Long) feature.getProperty("OGC_LAYERID_SUOLO").getValue();
    
    if(feature.getProperty("OGC_LAYERID_PARTICELLA")!=null)
      ogcLayerIDParticella = (Long) feature.getProperty("OGC_LAYERID_PARTICELLA").getValue();
    
    if(feature.getProperty("layer")!=null)
      layer = (String) feature.getProperty("layer").getValue();
    
    if(feature.getProperty("area")!=null)
      area =  (Double) feature.getProperty("area").getValue();
    
    if(feature.getProperty("geometry")!=null)
      geometry = (Geometry) feature.getProperty("geometry").getValue();
    
    if(feature.getProperty("subalterno")!=null)
      subalterno = (String) feature.getProperty("subalterno").getValue();
    
    if(feature.getProperty("numeroParticella")!=null)
      numeroParticella = (String) feature.getProperty("numeroParticella").getValue();
    
    if(feature.getProperty("codiceEleggibilitaRilevata")!=null)
      codiceEleggibilitaRilevata = (String) feature.getProperty("codiceEleggibilitaRilevata").getValue();
    
    if(feature.getProperty("codiceNazionale")!=null)
      codiceNazionale = (String) feature.getProperty("codiceNazionale").getValue();
    
    if(feature.getProperty("foglio")!=null)
      foglio = (String) feature.getProperty("foglio").getValue();
    
    suolo.setSubalterno(subalterno);
    suolo.setNumeroParticella(numeroParticella);
    suolo.setCodiceEleggibilitaRilevata(codiceEleggibilitaRilevata);
    suolo.setCodiceNazionale(codiceNazionale);
    suolo.setFoglio(foglio);
    
    suolo.setIdEventoLavorazione(idEventoLavorazione);
    suolo.setIdFeature(idFeature);
    suolo.setOgcFidSuolo(ogcFidSuolo);
    suolo.setOgcFidParticella(ogcFidParticella);
    
    suolo.setOgcLayerIDParticella(ogcLayerIDParticella);
    suolo.setOgcLayerIDSuolo(ogcLayerIDSuolo);
    
    suolo.setLayer(layer);
    suolo.setArea(area);
    suolo.setGeometry(geometry);
    return suolo;
  }

  private ParticellaCessataDTO creaParticellaCessata(SimpleFeature feature) throws IOException, ParseException
  {
    ParticellaCessataDTO particellaCessataDTO = new ParticellaCessataDTO();
    Long idEventoLavorazione = (Long) feature.getProperty("idEventoLavorazione").getValue();
    Long idFeature = (Long) feature.getProperty("idFeature").getValue();
    particellaCessataDTO.setIdEventoLavorazione(idEventoLavorazione);
    particellaCessataDTO.setIdFeature(idFeature);
    return particellaCessataDTO;
  }
  
  private ParticellaLavorataDTO creaParticellaLavorata(SimpleFeature feature) throws IOException, ParseException
  {
    ParticellaLavorataDTO particellaLavorataDTO = new ParticellaLavorataDTO();
    Long idEventoLavorazione = (Long) feature.getProperty("idEventoLavorazione").getValue();
    Long ogcFid =null;
    Long ogcLayerID =null;
    Long idFeature = null;
    Long idParticellaLavorazione = null;
    Long flagSospensione = null;
    String descrizioneSospensione = null;
    String noteLavorazione = null;
    String codiceNazionale = null;
    String foglio = null;
    String numeroParticella = null;
    String flagConduzione  = null;
    String subalterno = null;
    Geometry geometry = null;
    Double area =  null;
    
    if(feature.getProperty("idFeature")!=null && feature.getProperty("idFeature").getValue()!=null && (Long) feature.getProperty("idFeature").getValue()!=0)
      idFeature = (Long) feature.getProperty("idFeature").getValue();
    
    if(feature.getProperty("idParticellaLavorazione")!=null && feature.getProperty("idParticellaLavorazione").getValue()!=null && (Long) feature.getProperty("idParticellaLavorazione").getValue()!=0)
      idParticellaLavorazione = (Long) feature.getProperty("idParticellaLavorazione").getValue();

    if(feature.getProperty("OGC_FID")!=null && feature.getProperty("OGC_FID").getValue()!=null && (Long) feature.getProperty("OGC_FID").getValue()!=0)
      ogcFid = (Long) feature.getProperty("OGC_FID").getValue();
    
    if(feature.getProperty("OGC_LAYERID")!=null && feature.getProperty("OGC_LAYERID").getValue()!=null && (Long) feature.getProperty("OGC_LAYERID").getValue()!=0)
      ogcLayerID = (Long) feature.getProperty("OGC_LAYERID").getValue();
    
    if(feature.getProperty("flagSospensione")!=null && feature.getProperty("flagSospensione").getValue()!=null  && (Long) feature.getProperty("flagSospensione").getValue()!=0)
      flagSospensione = (Long) feature.getProperty("flagSospensione").getValue();
    
    if(feature.getProperty("descrizioneSospensione")!=null)
      descrizioneSospensione = (String) feature.getProperty("descrizioneSospensione").getValue();
    
    if(feature.getProperty("noteLavorazione")!=null)
      noteLavorazione = (String) feature.getProperty("noteLavorazione").getValue();
    
    if(feature.getProperty("codiceNazionale")!=null)
      codiceNazionale = (String) feature.getProperty("codiceNazionale").getValue();
    
    if(feature.getProperty("foglio")!=null)
      foglio = (String) feature.getProperty("foglio").getValue();
    
    if(feature.getProperty("numeroParticella")!=null)
      numeroParticella = (String) feature.getProperty("numeroParticella").getValue();
    
    if(feature.getProperty("flagConduzione")!=null)
      flagConduzione  = (String) feature.getProperty("flagConduzione").getValue();
    
    if(feature.getProperty("subalterno")!=null)
      subalterno = (String) feature.getProperty("subalterno").getValue();
    
    if(feature.getProperty("geometry")!=null)
      geometry = (Geometry) feature.getProperty("geometry").getValue();
    
    if(feature.getProperty("area")!=null)
      area =  (Double) feature.getProperty("area").getValue();
    
    particellaLavorataDTO.setIdEventoLavorazione(idEventoLavorazione);
    particellaLavorataDTO.setIdParticellaLavorazione(idParticellaLavorazione);
    particellaLavorataDTO.setIdFeature(idFeature);
    particellaLavorataDTO.setFlagSospensione(flagSospensione);
    particellaLavorataDTO.setDescrizioneSospensione(descrizioneSospensione);
    particellaLavorataDTO.setNoteLavorazione(noteLavorazione);
    particellaLavorataDTO.setCodiceNazionale(codiceNazionale);
    particellaLavorataDTO.setFoglio(foglio);
    particellaLavorataDTO.setNumeroParticella(numeroParticella);
    particellaLavorataDTO.setSubalterno(subalterno);
    particellaLavorataDTO.setGeometry(geometry);
    particellaLavorataDTO.setOgcFid(ogcFid);
    particellaLavorataDTO.setOgcLayerID(ogcLayerID);
    particellaLavorataDTO.setArea(area);
    particellaLavorataDTO.setFlagConduzione(flagConduzione);
    return particellaLavorataDTO;
  }
  
  private SuoloCessatoDTO creaSuoloCessato(SimpleFeature feature) throws IOException, ParseException
  {
    SuoloCessatoDTO suolo = new SuoloCessatoDTO();
    Long idEventoLavorazione = (Long) feature.getProperty("idEventoLavorazione").getValue();
    Long idFeature = (Long) feature.getProperty("idFeature").getValue();
    String layer = (String) feature.getProperty("layer").getValue();
    String tipoSuolo = (String) feature.getProperty("tipoSuolo").getValue();
    Geometry geometry = (Geometry) feature.getProperty("geometry").getValue();
    suolo.setIdEventoLavorazione(idEventoLavorazione);
    suolo.setIdFeature(idFeature);
    suolo.setTipoSuolo(tipoSuolo);
    suolo.setLayer(layer);
    suolo.setGeometry(geometry);
    return suolo;
  }
  
  private SuoloConfigurazioneDTO creaSuoloConfigurazione(SimpleFeature feature) throws IOException, ParseException
  {
    SuoloConfigurazioneDTO suolo = new SuoloConfigurazioneDTO();
    Long idEventoLavorazione = (Long) feature.getProperty("idEventoLavorazione").getValue();
    String layer = (String) feature.getProperty("layer").getValue();
    Long flagDiffAreaSuoli = (Long) feature.getProperty("flagDiffAreaSuoli").getValue();
    Long flagCessatiSuoli = (Long) feature.getProperty("flagCessatiSuoli").getValue();
    Long flagAreaMinSuoli = (Long) feature.getProperty("flagAreaMinSuoli").getValue();
    Long flagDiffPartSuoli = (Long) feature.getProperty("flagDiffPartSuoli").getValue();
    String anomalia = (String) feature.getProperty("anomalia").getValue();

    suolo.setIdEventoLavorazione(idEventoLavorazione);
    suolo.setAnomalia(anomalia);
    suolo.setFlagCessatiSuoli(flagCessatiSuoli);
    suolo.setFlagDiffAreaSuoli(flagDiffAreaSuoli);
    suolo.setFlagAreaMinSuoli(flagAreaMinSuoli);
    suolo.setFlagDiffPartSuoli(flagDiffPartSuoli);
    suolo.setLayer(layer);
    return suolo;
  }

  public List<MotivoSospensioneDTO> getMotiviSospensione()
  {
    final String THIS_METHOD = "getMotiviSospensione";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getMotiviSospensione();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public boolean isFoglioBloccato(long foglio, String codiceNazionale, Long idUtenteLogin)
  {
    final String THIS_METHOD = "isFoglioBloccato";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.isFoglioBloccato(foglio, codiceNazionale, idUtenteLogin);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public EsitoDTO sbloccoForzatoFoglio(long idEventoLavorazione, int foglio, String codiceNazionale, long idUtenteLogin)
  {
    final String THIS_METHOD = "sbloccoForzatoFoglio";
    EsitoDTO esitoDTO = new EsitoDTO();
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      boolean isFoglioBloccato = pianoColturaleDAO.isFoglioBloccato(foglio, codiceNazionale, -1l);

      boolean isFoglioBloccatoDaAltri = pianoColturaleDAO.isFoglioBloccato(foglio, codiceNazionale,
          idUtenteLogin);

      if (isFoglioBloccato && !isFoglioBloccatoDaAltri) //se è bloccato da me posso sbloccarlo
      {
        pianoColturaleDAO.sbloccaFoglio(foglio, codiceNazionale, idUtenteLogin);
        
        // Se nessun foglio dell'evento è stato lavorato, sblocco pure l'evento
        if(!pianoColturaleDAO.esisteLavorazioneFogliInCorso(idEventoLavorazione))
        {
          pianoColturaleDAO.sbloccoEvento(idEventoLavorazione, idUtenteLogin);
          
          esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FOGLIO_ED_EVENTO_SBLOCCATO);
          esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.FOGLIO_ED_EVENTO_SBLOCCATO);
        }
        else
        {
          esitoDTO.setEsito(AgriApiConstants.ESITO.POSITIVO_FOGLIO_SBLOCCATO);
          esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.FOGLIO_SBLOCCATO);         
        }
        

      }
      else
        if (!isFoglioBloccato)
        {
          esitoDTO.setEsito(AgriApiConstants.ESITO.NEGATIVO_FOGLIO_NON_BLOCCATO);
          esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.NEGATIVO_FOGLIO_NON_BLOCCATO);
        }
        else
          if (isFoglioBloccato && isFoglioBloccatoDaAltri)
          {
            esitoDTO.setEsito(AgriApiConstants.ESITO.NEGATIVO_FOGLIO_BLOCCATO_DA_ALTRI);
            esitoDTO.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.NEGATIVO_FOGLIO_BLOCCATO_DA_ALTRI);
          }
    }
    catch (Exception e)
    {
      TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] n. eccezione: "+e.getMessage());
      e.printStackTrace();
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] .",e);
      }
      
      esitoDTO.setError();
      return esitoDTO;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
    return esitoDTO;
  }
  
  
  
  public boolean esistonoFogliNonLavorati(long idEventoLavorazione)
  {
    final String THIS_METHOD = "esistonoFogliNonLavorati";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.esistonoFogliSuoliNonLavorati(idEventoLavorazione) || pianoColturaleDAO.esistonoFogliParticelleNonLavorati(idEventoLavorazione);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public List<ParametroDTO> getElencoParametri()
  {
    final String THIS_METHOD = "getElencoParametri";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getElencoParametri();
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public GeoJSONFeatureCollection getFoglioRiferimento(long annoCampagna, String codiceNazionale, long foglio) throws IOException, ParseException
  {
    final String THIS_METHOD = "getFoglioRiferimento";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      GeoJSONFeatureCollection featureCollection = new GeoJSONFeatureCollection();
      ArrayList<String> listFeaturesString = new ArrayList<String>();

      List<FoglioRiferimentoDTO> suoli = pianoColturaleDAO.getFoglioRiferimento(annoCampagna, codiceNazionale, foglio);
      if(suoli!=null)
      for(FoglioRiferimentoDTO suolo : suoli)
      {
        listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON(suolo.getGeometriaWkt(),setAttributeFoglioRiferimento(suolo),setNvlSRID(suolo.getSrid()),"Feature",null));
      }
      featureCollection.setFeaturesString(listFeaturesString);
      return featureCollection;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  public String getToken(GestioneCookieDTO cookieDTO)
  {
    final String THIS_METHOD = "getToken";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getToken(cookieDTO);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public GestioneCookieDTO getCookiesFromToken(String token)
  {
    final String THIS_METHOD = "getCookiesFromToken";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      GestioneCookieDTO dto = pianoColturaleDAO.getCookiesFromToken(token);
      //pianoColturaleDAO.deleteWGestioneTokenById(dto.getIdGestioneToken());
      return dto;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public File getGeoPCK(int foglio, String codiceNazionale, Integer annoCampagna, Long idUtenteLogin) throws Exception
  {

    final String THIS_METHOD = "getGeoPCK";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      List<SuoloPropostoDTO> suoli = pianoColturaleDAO.getStoricoSuoliRilevati(codiceNazionale, foglio, annoCampagna);
      

      //String path = "C:\\Users\\massimo.durando\\Desktop";
      //File f = File.createTempFile("geopkg_qgisagri_", ".gpkg", new File(path));
      File f = File.createTempFile("geopkg_qgisagri_", ".gpkg");
      GeoPackage geopkg = new GeoPackage(f);
      geopkg.init();
     
      String codeSrid = (suoli!=null && suoli.get(0).getSrid()!=null) ? suoli.get(0).getSrid() : AgriApiConstants.DEFAULT_CRS_PIEMONTE;
      CRSAuthorityFactory crsAuthorityFactory = ReferencingFactoryFinder.getCRSAuthorityFactory("EPSG", null);
      CoordinateReferenceSystem crs = crsAuthorityFactory.createCoordinateReferenceSystem(codeSrid);
      FeatureEntry entry = new FeatureEntry();
      entry.setBounds(new ReferencedEnvelope(crs));
      entry.setSrid(Integer.parseInt(codeSrid));
      
      entry.setDataType(org.geotools.geopkg.Entry.DataType.Feature); //max
      entry.setGeometryType(Geometries.POLYGON);//max
      
      entry.setTableName("SUOLO");
      entry.setGeometryColumn("geometria");
      entry.setDescription("storico foglio");
      entry.setIdentifier("storico_foglio");
      SimpleFeatureType schema = DataUtilities.createType("SUOLO", "geometria:Polygon,codiceEleggibilitaRilevata:String,descEleggibilitaRilevata:String"
          + ",annoCampagna:String"
          + ",descrTipoSorgenteSuolo:String"
          + ",utente:String"
          + ",dataInizioValidita:String"
          + ",dataFineValidita:String"
          + ",descrListaLavorazione:String"
          + ",descrAzienda:String"
          + ",srid:String"
          + ",dataLavorazione:String");
      
      List<SimpleFeature> elencoFeatures = new ArrayList<SimpleFeature>();
      int count = 1;
      if(suoli!=null)
      {
        for(SuoloPropostoDTO suolo : suoli)
        {
          Geometry g = null;
          try
          {
            g = WKTGeometryConverter.getGeometryFromWKT(suolo.getGeometriaWkt());
            SimpleFeature feature =
                SimpleFeatureBuilder.build(
                        schema, new Object[] {g, suolo.getCodiceEleggibilitaRilevata(), 
                            suolo.getDescEleggibilitaRilevata(),
                            suolo.getAnnoCampagna(),
                            suolo.getDescrTipoSorgenteSuolo(),
                            suolo.getUtente(),
                            GraficoUtils.DATE.formatDate(suolo.getDataInizioValidita()) ,
                            GraficoUtils.DATE.formatDate(suolo.getDataFineValidita()) ,
                            suolo.getDescrListaLavorazione(),
                            suolo.getDescrAzienda(),
                            setNvlSRID(suolo.getSrid()),
                            GraficoUtils.DATE.formatDate(suolo.getDataLavorazione()) 
                            }, "SUOLO."+count);
            elencoFeatures.add(feature);
            count++;
          }catch (Exception e) {
            // TODO gestire il caso che  getGeometryFromWKT non riesce a convertire una geometria da wkt
            continue;
          }
        }
        SimpleFeatureCollection collection = DataUtilities.collection(elencoFeatures);
        geopkg.add(entry,collection);
      }
      return f;
    }
    catch(Exception e)
    {
      EsitoDTO esito = new EsitoDTO();
      esito.setError();
      esito.setMessaggio("ERRORE GENERAZIONE GEOPACKAGE");
      e.printStackTrace();
      return null;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }

  
  }
  
  public DatiSuoloDTO leggiDatiSuolo(long idSuoloRilevato)
  {
    final String THIS_METHOD = "leggiDatiSuolo";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.leggiDatiSuolo(idSuoloRilevato);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
   
  public SuoloRilevatoDTO getSuoloRilevato(long idSuoloRilevato)
  {
    final String THIS_METHOD = "getSuoloRilevato";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getSuoloRilevato(idSuoloRilevato);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  public List<Long> getListIdParticellaCatasto (long foglio,String codiceNazionale,String subalterno,String numeroParticella,String sezione)
  {
    final String THIS_METHOD = "getListIdParticellaAssociataASuolo";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getListIdParticellaCatasto(foglio, codiceNazionale, subalterno, numeroParticella, sezione);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  public List<Long> getListIdParticellaAssociataASuolo(long idSuoloRilevato)
  {
    final String THIS_METHOD = "getListIdParticellaAssociataASuolo";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      return pianoColturaleDAO.getListIdParticellaAssociataASuolo(idSuoloRilevato);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

	public List<UnarAppezzamentoDTO> leggiDatiUnarPoligono(long idSuoloRilevato, Date dataFineValidita)
	{
	    final String THIS_METHOD = "leggiDatiUnarPoligono";
	    if (logger.isDebugEnabled())
	    {
	      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
	    }
	    
	    try
	    {
	    	return pianoColturaleDAO.leggiDatiUnarPoligono(idSuoloRilevato, dataFineValidita);
	    }
	    finally
	    {
	      if (logger.isDebugEnabled())
	      {
	        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
	      }
	    }
	}
  
	public List<UnarAppezzamentoDTO> leggiDatiUnarParticella(Long idSuoloRilevato, Date dataFineValidita, List<Long> particelle)
	{
	    final String THIS_METHOD = "leggiDatiUnarParticella";
	    if (logger.isDebugEnabled())
	    {
	      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
	    }
	    
	    try
	    {
	    	return pianoColturaleDAO.leggiDatiUnarParticella(idSuoloRilevato, dataFineValidita, particelle);
	    }
	    finally
	    {
	      if (logger.isDebugEnabled())
	      {
	        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
	      }
	    }
	}

  public List<UtilizzoParticellaDTO> leggiDatiUtilizzoParticella( int campagna, Date dataFineValidita, List<Long> particelle)
  {
    final String THIS_METHOD = "leggiDatiUtilizzoParticella";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    try
    {
      return pianoColturaleDAO.leggiDatiUtilizzoParticella(campagna, dataFineValidita, particelle);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public String getIdentificativoPraticaOrigine(long idAzienda, long idEventoLavorazione)
  {
    final String THIS_METHOD = "getIdentificativoPraticaOrigine";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    try
    {
      return pianoColturaleDAO.getIdentificativoPraticaOrigine(idAzienda,idEventoLavorazione);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public ImmagineAppezzamentoDTO getImmagineAppezzamentoFromId(
      int idFotoAppezzamentoCons)
  {
    final String THIS_METHOD = "getImmagineAppezzamentoFromId";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    try
    {
      return pianoColturaleDAO.getImmagineAppezzamentoFromId(idFotoAppezzamentoCons);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public boolean verificaAbilitazioneEventoLavorazione(UtenteAbilitazioni utenteAbilitazioni, long idEventoLavorazione)
  {
    final String THIS_METHOD = "verificaAbilitazioneEventoLavorazione";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }

    try
    {
      return pianoColturaleDAO.verificaAbilitazioneEventoLavorazione(utenteAbilitazioni, idEventoLavorazione);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public boolean verificaAbilitazioneListaLavorazione(UtenteAbilitazioni utenteAbilitazioni, long idListaLavorazione)
  {
    final String THIS_METHOD = "verificaAbilitazioneListaLavorazione";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }

    try
    {
      return pianoColturaleDAO.verificaAbilitazioneListaLavorazione(utenteAbilitazioni, idListaLavorazione);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public List<DichiarazioneConsistenzaDTO> leggiValidazioniAzienda(
      long idEventoLavorazione)
  {
    final String THIS_METHOD = "leggiValidazioniAzienda";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    try
    {
      return pianoColturaleDAO.leggiValidazioniAzienda(idEventoLavorazione);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public List<AppezzamentoDTO> leggiAppezzamentiScheda(long idEventoLavorazione, long idDichiarazioneConsistenza, String codNazionale, int foglio)
  {
    final String THIS_METHOD = "leggiAppezzamentiScheda";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    try
    {
      return pianoColturaleDAO.leggiAppezzamentiScheda(idEventoLavorazione, idDichiarazioneConsistenza, codNazionale, foglio);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }  
  
  public List<ParticellaLavorazioneDTO> getParticelleLavorazioni(long idEventoLavorazione,
      String codiceNazionale, Long foglio)
  {
    final String THIS_METHOD = "getParticelleLavorazioni";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    try
    {
      return pianoColturaleDAO.getParticelleLavorazioni(idEventoLavorazione, codiceNazionale, foglio);
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }
  
  
  public GeoJSONFeatureCollection getCxfParticella(String codiceNazionale, Long foglio, Long idUtenteLogin, long idEventoLavorazione) throws Exception
  { 
    final String THIS_METHOD = "getCxfParticella";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    try
    {
      List<CxfParticellaDTO> particelle = pianoColturaleDAO.getCxfParticella(codiceNazionale, foglio,idEventoLavorazione);
      GeoJSONFeatureCollection featureCollection = new GeoJSONFeatureCollection();
      ArrayList<String> listFeaturesString = new ArrayList<String>();

      if(particelle!=null)
      {
        for(CxfParticellaDTO particella : particelle)
        {
          try {
            listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON(particella.getGeometriaWkt(),setAttributeCxf(particella),setNvlSRID(particella.getSrid()),"Feature",null));
          }
          catch (IllegalArgumentException e)
          {
            //La funzionalità di conversione fallisce se la geometria è "sporca"
            try {
              //FIXSHAPE - funzione che pulisce la geometria
              String wktCorretto = pianoColturaleDAO.fixShape(particella.getGeometriaWkt());
              //Riporvo a convertire la geometria pulita
              listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON(wktCorretto,setAttributeCxf(particella),setNvlSRID(particella.getSrid()),"Feature",null));
            }
            catch(IllegalArgumentException e2)
            {
              //Se fallisce di nuovo allora segnalo l'errore.
              logger.debug("La geometria presenta degli errori.");
              e2.printStackTrace();
              particella.setErrore("La geometria presenta degli errori.");
              //e aggiungo l'attributo "errore" al geoJson, mentre la geometria passata sarà vuota
              listFeaturesString.add(GeoJSONGeometryConverter.convertFeatureAndWktElementsToGeoJSON("POLYGON EMPTY",setAttributeCxf(particella),setNvlSRID(particella.getSrid()),"Feature",null));
            }
         }
        }

      }
      featureCollection.setFeaturesString(listFeaturesString);
      return featureCollection ;
    }
    catch (Exception e)
    {
      e.printStackTrace();
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public byte[] geAllegatoFromDoqui(long idEventoLavorazione, long idAllegato)throws Exception
  {
    final String THIS_METHOD = "geAllegatoFromDoqui";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] BEGIN.");
    }
    
    try
    {
       Long idDocIndex = pianoColturaleDAO.getIdDocumentoIndex(idEventoLavorazione, idAllegato);
       DataHandler datah = AgriApiUtils.WS.getSiapComm().leggiFileDocumento(idDocIndex.longValue());
       if(datah == null) {
         throw new Exception("Impossibile procedere: documento non trovato nel documentale SIAP.");
       }
       return org.apache.commons.io.IOUtils.toByteArray(datah.getInputStream());
    }
    catch(Exception e)
    {
      System.out.println(e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + "." + THIS_METHOD + "] END.");
      }
    }
  }

  public Map<String, String> getParametri(String[] paramNames) 
  {
    return pianoColturaleDAO.getParametri(paramNames);
  }
 
  
}
