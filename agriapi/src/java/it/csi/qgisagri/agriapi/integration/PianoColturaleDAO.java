package it.csi.qgisagri.agriapi.integration;


import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.sql.DataSource;

import org.locationtech.jts.geom.Geometry;
import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.ResultSetExtractor;
import org.springframework.jdbc.core.SqlOutParameter;
import org.springframework.jdbc.core.SqlParameter;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.simple.SimpleJdbcCall;
import org.springframework.jdbc.core.support.AbstractSqlTypeValue;
import org.springframework.stereotype.Component;

import it.csi.papua.papuaserv.dto.gestioneutenti.Abilitazione;
import it.csi.papua.papuaserv.dto.gestioneutenti.ws.UtenteAbilitazioni;
import it.csi.qgisagri.agriapi.dto.DatiSuoloDTO;
import it.csi.qgisagri.agriapi.dto.FoglioRiferimentoDTO;
import it.csi.qgisagri.agriapi.dto.GestioneCookieDTO;
import it.csi.qgisagri.agriapi.dto.ImmagineAppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.MainControlloDTO;
import it.csi.qgisagri.agriapi.dto.ParametroDTO;
import it.csi.qgisagri.agriapi.dto.SuoloRilevatoDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.AllegatoParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.AziendaListeLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ClasseEleggibilitaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.CoordinateFotoAppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.CxfParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.DichiarazioneConsistenzaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.FoglioAziendaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ListaLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.MotivoSospensioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ParticellaLavorataDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.ParticellaLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloConfigurazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloLavoratoDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloLavorazioneDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloParticellaDTO;
import it.csi.qgisagri.agriapi.dto.listeLavorazione.SuoloPropostoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.AppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.UnarAppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.UtilizzoParticellaDTO;
import it.csi.qgisagri.agriapi.util.AgriApiConstants;
import it.csi.qgisagri.agriapi.util.StringUtils;

@Component
public class PianoColturaleDAO extends BaseDAO
{
  
  public final String           THIS_CLASS = PianoColturaleDAO.class.getSimpleName();

  
  
  private String addSubselectSRID(String shapeField) {
    
    return  " PCK_SMRGAA_STRUMENTI_GRAFICI.getCodiEPSG("+shapeField+") AS SRID   ";
  }
  
  
  public List<ListaLavorazioneDTO> getElencoListeLavorazione(UtenteAbilitazioni utenteAbilitazioni)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getElencoListeLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idUtenteLogin: " + utenteAbilitazioni.getIdUtenteLogin());
    }

    List<String> listIdLivelli = new ArrayList<String>();
    for (Abilitazione abilitazione : utenteAbilitazioni.getAbilitazioni())
    {
      if (abilitazione.getLivello().getCodiceListaSiti() != null)
      {
        listIdLivelli.add(String.valueOf(abilitazione.getLivello().getCodiceListaSiti()));
      }
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = " SELECT                                        \n"
        + "    LL.ID_LISTA_LAVORAZIONE,                                  \n"
        + "    LL.ID_TIPO_LISTA,                                         \n"
        + "    LL.CAMPAGNA,                                              \n"
        + "    LL.CODICE AS CODICE_LISTA,                                \n"
        + "    LL.DESCRIZIONE_LISTA,                                     \n"
        + "    TL.DESCRIZIONE AS DESCRIZIONE_TIPO_LISTA                  \n"
        + "  FROM                                                        \n"
        + "    QGIS_T_LISTA_LAVORAZIONE LL,                              \n"
        + "    QGIS_D_TIPO_LISTA TL                                      \n"
        + "  WHERE                                                       \n"
        + "    TL.ID_TIPO_LISTA = LL.ID_TIPO_LISTA                       \n"
        + getInCondition("LL.CODICE", listIdLivelli,true);

    try
    {
      return queryForList(QUERY, mapSqlParameterSource, ListaLavorazioneDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + 
          " idUtenteLogin: " + utenteAbilitazioni.getIdUtenteLogin()
      , e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }

  }
  
  
  
  

  public List<AziendaListeLavorazioneDTO> getElencoAziende(int idListaLavorazione, String cuaa, String escludiLavorate,
      String escludiBloccate, String escludiSospese)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getElencoAziende]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger
          .debug(THIS_METHOD + " idListaLavorazione: " + idListaLavorazione + ", cuaa: " + cuaa + ", escludiLavorate: "
              + escludiLavorate + ", escludiBloccate: " + escludiBloccate + ", escludiSospese: " + escludiSospese);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    
    final String SUBQUERY_FILTRO_INCLUDI_SOLO_BLOCCATE = 
        " AND EL.ID_EVENTO_LAVORAZIONE IN                                                  \n"
      + " ( SELECT                                                                             \n"
      + "     EB.ID_EVENTO_LAVORAZIONE                                                         \n"
      + "   FROM                                                                               \n"
      + "     QGIS_T_EVENTO_BLOCCATO  EB                                                       \n"
      + "   WHERE                                                                              \n"
      + "     EB.DATA_FINE_VALIDITA IS NULL )                                                  \n";

    
  final String SUBQUERY_FILTRO_ESCLUDI_LAVORATE = " AND EL.DATA_LAVORAZIONE IS  NULL \n";
  final String SUBQUERY_FILTRO_INCLUDI_SOLO_LAVORATE = " AND EL.DATA_LAVORAZIONE IS  NOT NULL \n";
  final String SUBQUERY_FILTRO_INCLUDI_SOLO_SOSPESE = " AND EL.ID_EVENTO_LAVORAZIONE  IN          \n"
    + " ( SELECT                                                                                  \n"
    + "     ID_EVENTO_LAVORAZIONE                                                                 \n"
    + "   FROM                                                                                    \n"
    + "     QGIS_T_SUOLO_LAVORAZIONE                                                              \n"
    + "   WHERE                                                                                   \n"
    + "     FLAG_SOSPENSIONE = 'S'                                                               \n"
    + " UNION SELECT                                                                                  \n"
    + "     ID_EVENTO_LAVORAZIONE                                                                 \n"
    + "   FROM                                                                                    \n"
    + "     QGIS_T_PARTICELLA_LAVORAZIONE                                                              \n"
    + "   WHERE                                                                                   \n"
    + "     FLAG_SOSPENSIONE = 'S')                                                               \n";
  
  
  final String SUBQUERY_FILTRO_ESCLUDI_SOSPESE = " AND EL.ID_EVENTO_LAVORAZIONE  NOT IN \n"
      + " ( SELECT                                                                                  \n"
      + "     ID_EVENTO_LAVORAZIONE                                                                 \n"
      + "   FROM                                                                                    \n"
      + "     QGIS_T_SUOLO_LAVORAZIONE                                                              \n"
      + "   WHERE                                                                                   \n"
      + "     FLAG_SOSPENSIONE = 'S'                                                               \n"
      + " UNION SELECT                                                                                  \n"
      + "     ID_EVENTO_LAVORAZIONE                                                                 \n"
      + "   FROM                                                                                    \n"
      + "     QGIS_T_PARTICELLA_LAVORAZIONE                                                              \n"
      + "   WHERE                                                                                   \n"
      + "     FLAG_SOSPENSIONE = 'S')                                                               \n";
   
  
    
    final StringBuffer QUERY = new StringBuffer(
              " SELECT                                                                                  \n"
            + "   A.*,                                                                                  \n"
            + "   (                                                                                      \n"
            
            
            
           +  "  select count(*)                                                                   \n"
            + "          from (SELECT DISTINCT foglio,ID_EVENTO_LAVORAZIONE                        \n"
            + "                FROM QGIS_T_PARTICELLA_LAVORAZIONE                                  \n"
            + "                WHERE FOGLIO IS NOT NULL                                            \n"
            + "                union                                                               \n"
            + "                SELECT DISTINCT foglio,ID_EVENTO_LAVORAZIONE                        \n"
            + "                FROM QGIS_T_SUOLO_RILEVATO SR,QGIS_T_SUOLO_LAVORAZIONE I            \n"
            + "                WHERE SR.ID_SUOLO_RILEVATO = I.ID_SUOLO_RILEVATO                    \n"
            + "                AND   FOGLIO               IS NOT NULL) fg                          \n"
            + "                where fg.id_evento_lavorazione = a.id_evento_lavorazione            \n"



            
            + "   ) AS NUMERO_FOGLI,                                                                    \n"
            + "   (                                                                                     \n"
            + "     SELECT                                                                              \n"
            + "       COUNT(DISTINCT FOGLIO)                                                            \n"
            + "     FROM                                                                                \n"
            + "       QGIS_T_FOGLIO_BLOCCATO FB,                                                        \n"
            + "       QGIS_T_EVENTO_BLOCCATO EB                                                        \n"
            + "     WHERE                                                                               \n"
            + "       A.ID_EVENTO_LAVORAZIONE = EB.ID_EVENTO_LAVORAZIONE                                \n"
            + "       AND FB.ID_EVENTO_BLOCCATO = EB.ID_EVENTO_BLOCCATO                                 \n"
            + "       AND EB.DATA_FINE_VALIDITA IS NULL                                                 \n"
            + "       AND FB.DATA_FINE_VALIDITA IS NULL                                                 \n"
            + "   ) AS NUMERO_FOGLI_BLOCCATI,"
            + "   ("
            + "     SELECT "
            + "       EXT_ID_UTENTE_AGGIORNAMENTO "
            + "     FROM "
            + "       QGIS_T_EVENTO_BLOCCATO EB"
            + "     WHERE "
            + "       A.ID_EVENTO_LAVORAZIONE = EB.ID_EVENTO_LAVORAZIONE"
            + "       AND EB.DATA_FINE_VALIDITA IS NULL"
            + "   ) ID_UTENTE_BLOCCO,                                                           \n"
            + "   (                                                                                     \n"
            + "     SELECT                                                                              \n"
            + "       UL.CODICE_FISCALE_UTENTE_LOGIN                                                    \n"
            + "       || ' - ' || UL.COGNOME_UTENTE_LOGIN                                               \n"
            + "       || ' ' || UL.NOME_UTENTE_LOGIN                                                    \n"
            + "     FROM                                                                                \n"
            //+ "       QGIS_T_FOGLIO_BLOCCATO FB,                                                        \n"
            + "       QGIS_T_EVENTO_BLOCCATO EB,                                                        \n"
            + "       PAPUA_V_UTENTE_LOGIN UL                                                           \n"
            + "     WHERE                                                                               \n"
            + "       A.ID_EVENTO_LAVORAZIONE = EB.ID_EVENTO_LAVORAZIONE                                \n"
            //+ "       AND FB.ID_EVENTO_BLOCCATO = EB.ID_EVENTO_BLOCCATO                                 \n"
            + "       AND EB.DATA_FINE_VALIDITA IS NULL                                                 \n"
            //+ "       AND FB.DATA_FINE_VALIDITA IS NULL                                                 \n"
            + "       AND EB.EXT_ID_UTENTE_AGGIORNAMENTO = UL.ID_UTENTE_LOGIN                           \n"
            + "       AND ROWNUM=1                                                                      \n"
            + "   ) AS UTENTE_BLOCCO                                                                    \n"
            + " FROM                                                                                    \n"
            + "   (                                                                                     \n"
            + "     SELECT                                                                              \n"
            + "       A.CUAA,                                                                           \n"
            + "       A.DENOMINAZIONE,                                                                  \n"
            + "       A.ID_AZIENDA,                                                                     \n"
             + "       EL.DATA_LAVORAZIONE,                                                                     \n"
            + "       DECODE( (select max(ID_EVENTO_LAVORAZIONE) from QGIS_T_SUOLO_LAVORAZIONE where FLAG_SOSPENSIONE = 'S' and ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE), NULL, 'N', 'S') AS IS_SOSPESA,                                                                   \n"
            + "       EL.ID_EVENTO_LAVORAZIONE,                                                         \n"
            + "       DECODE(EL.DATA_LAVORAZIONE, NULL, 'N', 'S') AS IS_ICONA_LAVORATA,                 \n"
            + "       DECODE(                                                                           \n"
            + "       (                                                                                 \n"
            + "         SELECT                                                                          \n"
            + "           COUNT (*) FROM QGIS_T_SUOLO_LAVORAZIONE WHERE ID_EVENTO_LAVORAZIONE =         \n"
            + "           EL.ID_EVENTO_LAVORAZIONE                                                      \n"
            + "           AND FLAG_SOSPENSIONE = 'S'                                                    \n"
            + "       )                                                                                 \n"
            + "      , 0, 'N', 'S') AS IS_ICONA_SOSPESA,                                                \n"
            + "       (                                                                                 \n"
            + "         SELECT                                                                          \n"
            + "           COUNT(*)                                                                      \n"
            + "         FROM                                                                            \n"
            + "           QGIS_T_PARTICELLA_LAVORAZIONE I                                               \n"
            + "         WHERE                                                                           \n"
            + "           I.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE                            \n"
            + "       ) AS NUMERO_PARTICELLE,                                                           \n"
            + "       (                                                                                 \n"
            + " SELECT  count(distinct  I.ID_SUOLO_RILEVATO)                                                      \n"
            + "  FROM                                                                                              \n"
            + "      QGIS_T_SUOLO_LAVORAZIONE I                                                                   \n"
            + "   WHERE                                                                                            \n"
            + "     I.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE                                          \n"
            + "    and ( I.TIPO_SUOLO_ORIGINE IN ('LAV','LAV_KO','COND_KO', 'KO') or I.TIPO_SUOLO_ORIGINE is null) \n"
            + "       ) AS NUMERO_SUOLI_LAVORAZIONE,                                                    \n"
            + "       (                                                                                 \n"
            + "         SELECT                                                                          \n"
            + "           COUNT(*)                                                                      \n"
            + "         FROM                                                                            \n"
            + "           QGIS_T_SUOLO_PROPOSTO I                                                       \n"
            + "         WHERE                                                                           \n"
            + "           I.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE                            \n"
            + "       ) AS NUMERO_SUOLI_PROPOSTI,                                                       \n"
            + "       DECODE(                                                                           \n"
            + "       (                                                                                 \n"
            + "         SELECT                                                                          \n"
            + "           COUNT(EB.ID_EVENTO_BLOCCATO)                                                  \n"
            + "         FROM                                                                            \n"
            + "           QGIS_T_EVENTO_BLOCCATO EB                                                     \n"
            + "         WHERE                                                                           \n"
            + "           EB.DATA_FINE_VALIDITA IS NULL                                                 \n"
            + "           AND EB.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE                       \n"
            + "       )                                                                                 \n"
            + "      , 0, 'N', 'S') AS IS_AZIENDA_BLOCCATA                                              \n"
            + "     FROM                                                                                \n"
            + "       QGIS_T_EVENTO_LAVORAZIONE EL,                                                     \n"
            + "       QGIS_T_LISTA_LAVORAZIONE LL,                                                      \n"
            + "       SMRGAA.SMRGAA_V_DATI_ANAGRAFICI A                                                 \n"
            + "     WHERE                                                                               \n"
            + "       EL.EXT_ID_AZIENDA           = A.ID_AZIENDA                                        \n"
            + "       AND A.DATA_FINE_VALIDITA   IS NULL                                                \n"
            + "       AND LL.ID_LISTA_LAVORAZIONE = EL.ID_LISTA_LAVORAZIONE                             \n"
            + "       AND EL.ID_LISTA_LAVORAZIONE = :ID_LISTA_LAVORAZIONE                               \n");
    if (cuaa != null && cuaa.trim().length() > 0)
    {
      QUERY.append(" AND A.CUAA = :CUAA ");
    }
    else
    {
      if ("N".equals(escludiBloccate))
      {
        //visualizzo SOLO aziende bloccate - in carico 
        QUERY.append(SUBQUERY_FILTRO_INCLUDI_SOLO_BLOCCATE);
      }
      else if ("N".equals(escludiLavorate))
      {
        //visualizzo SOLO aziende lavorate
        QUERY.append(SUBQUERY_FILTRO_INCLUDI_SOLO_LAVORATE);
        //ESCLUDO LE SOSPESE
        QUERY.append(SUBQUERY_FILTRO_ESCLUDI_SOSPESE);
      }
      else if ("N".equals(escludiSospese))
      {
        //visualizzo SOLO aziende sospese  
        QUERY.append(SUBQUERY_FILTRO_INCLUDI_SOLO_SOSPESE);
      }
      else
      {
        //default: tutti e tre a S
        
        //ESCLUDO LE LAVORATE
        QUERY.append(SUBQUERY_FILTRO_ESCLUDI_LAVORATE);
      }
      
    }
    QUERY.append(" ORDER BY                                                                             \n"
        + "   EL.DATA_INSERIMENTO,                                                                      \n"
        + "   A.DENOMINAZIONE, A.CUAA,                                                                  \n"
        + "   A.ID_AZIENDA,                                                                             \n"
        + "   EL.ID_EVENTO_LAVORAZIONE) A                                                               \n"
        + "  WHERE ROWNUM <= 150                                                                        \n"
        + "                                                                                             \n");

    try
    {
      if (cuaa != null && cuaa.trim().length() > 0)
      {
        mapSqlParameterSource.addValue("CUAA", cuaa, Types.VARCHAR);
      }
      mapSqlParameterSource.addValue("ID_LISTA_LAVORAZIONE", idListaLavorazione, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource,
          new ResultSetExtractor<List<AziendaListeLavorazioneDTO>>()
          {
            @Override
            public List<AziendaListeLavorazioneDTO> extractData(ResultSet rs) throws SQLException, DataAccessException
            {
              ArrayList<AziendaListeLavorazioneDTO> result = new ArrayList<AziendaListeLavorazioneDTO>();
              AziendaListeLavorazioneDTO item = null;
              while (rs.next())
              {
                item = new AziendaListeLavorazioneDTO();
                item.setCuaa(rs.getString("CUAA"));
                item.setDenominazione(rs.getString("DENOMINAZIONE"));
                item.setIdAzienda(rs.getLong("ID_AZIENDA"));
                item.setIdEventoLavorazione(rs.getLong("ID_EVENTO_LAVORAZIONE"));
                item.setIsAziendaBloccata("S".equals(rs.getString("IS_AZIENDA_BLOCCATA")));
                boolean isIconaLavorata = "S".equals(rs.getString("IS_ICONA_LAVORATA"));
                boolean isIconaSospesa = "S".equals(rs.getString("IS_ICONA_SOSPESA"));
                String flagIconaLavorata = "N";
                if (isIconaLavorata && isIconaSospesa)
                  flagIconaLavorata = "S";
                if (isIconaLavorata && !isIconaSospesa)
                  flagIconaLavorata = "L";
                item.setFlagIconaLavorata(flagIconaLavorata);
                item.setNumeroParticelle(rs.getLong("NUMERO_PARTICELLE"));
                item.setNumeroSuoliLavorazione(rs.getLong("NUMERO_SUOLI_LAVORAZIONE"));
                item.setNumeroSuoliProposti(rs.getLong("NUMERO_SUOLI_PROPOSTI"));
                item.setNumeroFogli(rs.getLong("NUMERO_FOGLI"));
                item.setIsSospesa(rs.getString("IS_SOSPESA"));
                item.setDataLavorazione(rs.getDate("DATA_LAVORAZIONE"));
                item.setNumeroFogliBloccati(rs.getLong("NUMERO_FOGLI_BLOCCATI"));
                if(item.getNumeroFogli() != 0 && item.getNumeroFogli()==item.getNumeroFogliBloccati())
                  item.setIsAziendaBloccata(true);
                item.setUtenteBlocco(rs.getString("UTENTE_BLOCCO"));
                item.setIdUtenteBlocco(rs.getLong("ID_UTENTE_BLOCCO"));
                
                //Controllo necessario perché considero bloccate anche le aziende il cui evento lavorazione non è 
                //bloccato, ma tutti i suoi fogli sono bloccati
                 
                if (cuaa != null && cuaa.trim().length() > 0)
                {
                  result.add(item);
                }else
                {
                  if("S".equals(escludiBloccate))
                  {
                    if(!item.getIsAziendaBloccata())
                      result.add(item);
                  }
                  else {
                    result.add(item);
                  }
                }
                
                
                
              }
              return result;
            }
          });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger
          .error(THIS_METHOD + " idListaLavorazione: " + idListaLavorazione + ", cuaa: " + cuaa + ", escludiLavorate: "
              + escludiLavorate + ", escludiBloccate: " + escludiBloccate + ", escludiSospese: " + escludiSospese, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<FoglioAziendaDTO> getElencoFogliAzienda(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getElencoFogliAzienda]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY =             
        " SELECT CODICE_NAZIONALE,                                                          \n"
            + "            FOGLIO,                                                                \n"
            + "            DESCRIZIONE_COMUNE,                                                    \n"
            + "            SEZIONE,                                                               \n"
            + "            (SELECT EXT_ID_UTENTE_AGGIORNAMENTO                                    \n"
            + "               FROM QGIS_T_FOGLIO_BLOCCATO FB                                      \n"
            + "              WHERE     FB.DATA_FINE_VALIDITA IS NULL                              \n"
            + "                    AND FB.FOGLIO = DATI.FOGLIO                                    \n"
            + "                    AND FB.EXT_COD_NAZIONALE = DATI.CODICE_NAZIONALE               \n"
            + "                    AND ROWNUM = 1)                                                \n"
            + "               ID_UTENTE_BLOCCO,                                                   \n"
            + "            (SELECT    UL.CODICE_FISCALE_UTENTE_LOGIN                              \n"
            + "                    || ' - '                                                       \n"
            + "                    || UL.COGNOME_UTENTE_LOGIN                                     \n"
            + "                    || ' '                                                         \n"
            + "                    || UL.NOME_UTENTE_LOGIN                                        \n"
            + "               FROM QGIS_T_FOGLIO_BLOCCATO FB,                                     \n"
            + "                    PAPUA_V_UTENTE_LOGIN UL                                       \n"
           // + "                    QGIS_T_SUOLO_LAVORAZIONE I                                     \n"
            + "              WHERE     FB.DATA_FINE_VALIDITA IS NULL                              \n"
            + "                    AND FB.FOGLIO = DATI.FOGLIO                                    \n"
            + "                    AND FB.EXT_COD_NAZIONALE = DATI.CODICE_NAZIONALE               \n"
            + "                    AND FB.EXT_ID_UTENTE_AGGIORNAMENTO = UL.ID_UTENTE_LOGIN        \n"
            + "                    AND ROWNUM = 1)                                                \n"
            + "               AS UTENTE_BLOCCO,                                                   \n"
            + "            SUM (NUMERO_PARTICELLE) NUMERO_PARTICELLE,                             \n"
            + "            SUM (NUMERO_SUOLI_LAVORAZIONE) NUMERO_SUOLI_LAVORAZIONE,               \n"
            + "            SUM (NUMERO_SUOLI_SOSPESI) NUMERO_SUOLI_SOSPESI,                       \n"
            + "            SUM (NUMERO_SUOLI_PROPOSTI) NUMERO_SUOLI_PROPOSTI,                     \n"
            + "            (SELECT DECODE (                                                       \n"
            + "                       (SELECT MAX (a.identificativo_pratica_origine)              \n"
            + "                          FROM QGIS_T_SUOLO_PROPOSTO a,                            \n"
            + "                               QGIS_T_EVENTO_LAVORAZIONE b                         \n"
            + "                         WHERE     a.ID_EVENTO_LAVORAZIONE =                       \n"
            + "                                      b.ID_EVENTO_LAVORAZIONE                      \n"
            + "                               AND b.ID_EVENTO_LAVORAZIONE =                       \n"
            + "                                      :ID_EVENTO_LAVORAZIONE),                     \n"
            + "                       NULL, 'N',                                                  \n"
            + "                       'S')                                                        \n"
            + "               FROM DUAL)                                                          \n"
            + "               AS IS_DOCUMENTO_PRESENTE                                            \n"
            + "       FROM (                                                                      \n"
            + "       SELECT PL.EXT_COD_NAZIONALE AS CODICE_NAZIONALE,                            \n"
            + "                    PL.FOGLIO,                                                     \n"
            + "                    SC.NOME AS DESCRIZIONE_COMUNE,                                 \n"
            + "                    SC.ID_SEZC AS SEZIONE,                                         \n"
            + "                    (SELECT COUNT (*)                                              \n"
            + "                       FROM QGIS_T_PARTICELLA_LAVORAZIONE I                        \n"
            + "                      WHERE     I.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE \n"
            + "                            AND I.ID_VERSIONE_PARTICELLA IN                        \n"
            + "                                   (SELECT ID_VERSIONE_PARTICELLA                  \n"
            + "                                      FROM QGIS_T_VERSIONE_PARTICELLA              \n"
            + "                                     WHERE     FOGLIO = PL.FOGLIO                  \n"
            + "                                           AND EXT_COD_NAZIONALE =                 \n"
            + "                                                  PL.EXT_COD_NAZIONALE))           \n"
            + "                       AS NUMERO_PARTICELLE,                                       \n"
            + "                    0 NUMERO_SUOLI_LAVORAZIONE,                                    \n"
            + "                    0 NUMERO_SUOLI_SOSPESI,                                        \n"
            + "                    0 NUMERO_SUOLI_PROPOSTI                                        \n"
            + "               FROM QGIS_T_EVENTO_LAVORAZIONE EL,                                  \n"
            + "                    QGIS_T_PARTICELLA_LAVORAZIONE PL,                              \n"
            + "                    QGIS_T_VERSIONE_PARTICELLA VP,                                 \n"
            + "                    DB_SITICOMU SC                                                 \n"
            + "              WHERE     EL.ID_EVENTO_LAVORAZIONE = PL.ID_EVENTO_LAVORAZIONE        \n"
            + "                    AND PL.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA(+)   \n"
            + "                    AND EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE          \n"
            + "                     AND SC.COD_NAZIONALE = PL.EXT_COD_NAZIONALE                   \n"
            + "                    AND ROWNUM < 300                                               \n"
            + "             UNION                                                                 \n"
            + "             SELECT SR.EXT_COD_NAZIONALE AS CODICE_NAZIONALE,                      \n"
            + "                    SR.FOGLIO,                                                     \n"
            + "                    SC.NOME AS DESCRIZIONE_COMUNE,                                 \n"
            + "                    SC.ID_SEZC AS SEZIONE,                                         \n"
            + "                    0 NUMERO_PARTICELLE,                                           \n"
            + "                    (SELECT COUNT (*)                                              \n"
            + "                       FROM TABLE (                                                \n"
            + "                               PCK_QGIS_UTILITY_API.getNumSuoliLavoraz (           \n"
            + "                                  :ID_EVENTO_LAVORAZIONE,                          \n"
            + "                                  SR.EXT_COD_NAZIONALE,                            \n"
            + "                                  SR.FOGLIO))                                      \n"
            + "                      WHERE COLUMN_VALUE IN ('LAV', 'LAV_KO', 'COND_KO', 'KO'))    \n"
            + "                      NUMERO_SUOLI_LAVORAZIONE,                                    \n"
            + "                    (SELECT COUNT (*)                                              \n"
            + "                       FROM QGIS_T_SUOLO_LAVORAZIONE S1                            \n"
            + "                      WHERE     S1.ID_EVENTO_LAVORAZIONE =                         \n"
            + "                                   EL.ID_EVENTO_LAVORAZIONE                        \n"
            + "                            AND S1.FLAG_SOSPENSIONE = 'S'                          \n"
            + "                            AND S1.ID_SUOLO_RILEVATO IN                            \n"
            + "                                   (SELECT SR2.ID_SUOLO_RILEVATO                   \n"
            + "                                      FROM QGIS_T_SUOLO_RILEVATO SR2, "+getTabellaRegistroSuoli(idEventoLavorazione)+" RS , QGIS_T_LISTA_LAVORAZIONE VL              \n"
            + "                                     WHERE     SR2.FOGLIO = SR.FOGLIO  AND RS.DATA_FINE_VALIDITA IS NULL             \n"
            + "                                           AND SR2.EXT_COD_NAZIONALE =             \n"
            + "                                                  SR.EXT_COD_NAZIONALE       AND SR2.FOGLIO = RS.FOGLIO  AND RS.EXT_COD_NAZIONALE = SR2.EXT_COD_NAZIONALE  \n"
            + "                                           AND VL.ID_LISTA_LAVORAZIONE =  EL.ID_LISTA_LAVORAZIONE AND VL.CAMPAGNA = RS.CAMPAGNA AND SR2.ID_SUOLO_RILEVATO = RS.ID_SUOLO_RILEVATO   ))    \n"
            + "                       NUMERO_SUOLI_SOSPESI,                                       \n"
            + "                    0 NUMERO_SUOLI_PROPOSTI                                        \n"
            + "               FROM QGIS_T_EVENTO_LAVORAZIONE EL,                                  \n"
            + "                    QGIS_T_SUOLO_LAVORAZIONE SL,                                   \n"
            + "                    QGIS_T_SUOLO_RILEVATO SR,                                      \n"
            + "                    DB_SITICOMU SC                                                 \n"
            + "              WHERE     EL.ID_EVENTO_LAVORAZIONE = SL.ID_EVENTO_LAVORAZIONE        \n"
            + "                    AND SL.ID_SUOLO_RILEVATO = SR.ID_SUOLO_RILEVATO                \n"
            + "                    AND EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE          \n"
            + "                    AND SC.COD_NAZIONALE = SR.EXT_COD_NAZIONALE                    \n"
            + "                    AND ROWNUM < 300                                               \n"
            + "             UNION                                                                 \n"
            + "             SELECT SP.EXT_COD_NAZIONALE AS CODICE_NAZIONALE,                      \n"
            + "                    SP.FOGLIO,                                                     \n"
            + "                    SC.NOME AS DESCRIZIONE_COMUNE,                                 \n"
            + "                    SC.ID_SEZC AS SEZIONE,                                         \n"
            + "                    0 NUMERO_PARTICELLE,                                           \n"
            + "                    0 NUMERO_SUOLI_LAVORAZIONE,                                    \n"
            + "                    0 NUMERO_SUOLI_SOSPESI,                                        \n"
            + "                    (SELECT COUNT (*)                                              \n"
            + "                       FROM QGIS_T_SUOLO_PROPOSTO I                                \n"
            + "                      WHERE     I.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE \n"
            + "                            AND I.FOGLIO = SP.FOGLIO                               \n"
            + "                            AND I.EXT_COD_NAZIONALE = SP.EXT_COD_NAZIONALE)        \n"
            + "                       NUMERO_SUOLI_PROPOSTI                                       \n"
            + "               FROM QGIS_T_EVENTO_LAVORAZIONE EL,                                  \n"
            + "                    QGIS_T_SUOLO_PROPOSTO SP,                                      \n"
            + "                    DB_SITICOMU SC                                                 \n"
            + "              WHERE     EL.ID_EVENTO_LAVORAZIONE = SP.ID_EVENTO_LAVORAZIONE        \n"
            + "                    AND EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE          \n"
            + "                    AND SC.COD_NAZIONALE = SP.EXT_COD_NAZIONALE                    \n"
            + "                    AND ROWNUM < 300) DATI                                         \n"
            + "      WHERE ROWNUM < 300                                                           \n"
            + "   GROUP BY CODICE_NAZIONALE,                                                      \n"
            + "            FOGLIO,                                                                \n"
            + "            DESCRIZIONE_COMUNE,                                                    \n"
            + "            SEZIONE                                                                \n"
            + "   ORDER BY CODICE_NAZIONALE,                                                      \n"
            + "            FOGLIO,                                                                \n"
            + "            DESCRIZIONE_COMUNE,                                                    \n"
            + "            SEZIONE                                                                \n";

    
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      return queryForList(QUERY, mapSqlParameterSource, FoglioAziendaDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<SuoloLavorazioneDTO> getSuoliFoglio(long idEventoLavorazione,
      String codiceNazionale, Long foglio, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getSuoliFoglio]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", codiceNazionale: "
          + codiceNazionale + ", foglio:" + foglio + ", idUtenteLogin:" + idUtenteLogin);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuilder QUERY = new StringBuilder(
        " SELECT * FROM TABLE(PCK_QGIS_UTILITY_API.getSuoliInLavorazione(:ID_EVENTO_LAVORAZIONE,:CODICE_NAZIONALE,:FOGLIO))          \n");
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("CODICE_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_UTENTE_LOGIN", idUtenteLogin, Types.NUMERIC);

      return queryForList(QUERY.toString(), mapSqlParameterSource, SuoloLavorazioneDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", codiceNazionale: "
          + codiceNazionale + ", foglio:" + foglio + ", idUtenteLogin:" + idUtenteLogin, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

 
  public List<SuoloPropostoDTO> getSuoliProposti(long idEventoLavorazione,
      String codiceNazionale, Long foglio)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getSuoliProposti]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio: " + foglio
          + ", idEventoLavorazione:" + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                                     \n"
            + "   SP.ID_SUOLO_PROPOSTO AS ID_FEATURE,                                \n"
            + "   SP.FOGLIO AS FOGLIO,                                               \n"
            + "   SP.IDENTIFICATIVO_PRATICA_ORIGINE AS IDENTIFICATIVO_PRATICA_ORIGINE,                                               \n"
            + "   SP.EXT_COD_NAZIONALE AS CODICE_NAZIONALE,                          \n"
            + "   SP.EXT_ID_ISTA_RIES AS ID_ISTANZA_RIESAME,                          \n"
            + "   SDO_UTIL.TO_WKTGEOMETRY(SP.SHAPE) AS GEOMETRIA_WKT,                \n"
            + addSubselectSRID("SP.SHAPE") +", \n"
            + "   TER.ID_ELEGGIBILITA_RILEVATA,                                      \n"
            + "   TER.CODI_RILE_PROD AS CODICE_ELEGGIBILITA_RILEVATA,                \n"
            + "   TER.DESC_RILE_PROD AS DESC_ELEGGIBILITA_RILEVATA,                   \n"
            + "   FOTO.ID_FOTO_APPEZZAMENTO_CONS,                   \n"
            + "   NVL(FOTO.LATITUDINE_MAN, FOTO.LATITUDINE) AS LATITUDINE,           \n"
            + "   NVL(FOTO.LONGITUDINE_MAN, FOTO.LONGITUDINE) AS LONGITUDINE,          \n"
            + "   NVL(FOTO.DIREZIONE_GPS_MAN, FOTO.DIREZIONE_GPS ) AS DIREZIONE_GPS ,           \n"
            + "  NVL(FOTO.DIREZIONE_GPS_REF_MAN, FOTO.DIREZIONE_GPS_REF ) AS DIREZIONE_GPS_REF          \n"
            + " FROM                                                                 \n"
            + "   QGIS_T_SUOLO_PROPOSTO SP,                                          \n"
            + "   DB_FOTO_APPEZZAMENTO_CONS FOTO,                                          \n"
            + "   SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA TER                           \n"
            + " WHERE                                                                \n"
            + "   SP.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                  \n"
            + "   AND FOTO.ID_ISTANZA_APPEZZAMENTO(+) = SP.EXT_ID_ISTA_RIES                  \n");
    if (codiceNazionale != null)
      QUERY.append("   AND SP.EXT_COD_NAZIONALE = :CODICE_NAZIONALE                       \n");
    if (foglio != null)
      QUERY.append("   AND SP.FOGLIO = :FOGLIO                                            \n");
    QUERY.append("   AND SP.EXT_ID_ELEGGIBILITA_RILEVATA = TER.ID_ELEGGIBILITA_RILEVATA \n"
        + " ORDER BY                                                             \n"
        + "    TER.CODI_RILE_PROD,                                              \n"
        + "    TER.DESC_RILE_PROD                                                \n");
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      if (codiceNazionale != null)
        mapSqlParameterSource.addValue("CODICE_NAZIONALE", codiceNazionale, Types.VARCHAR);
      if (foglio != null)
        mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      //return queryForList(QUERY.toString(), mapSqlParameterSource, SuoloPropostoDTO.class);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource,
          new ResultSetExtractor<List<SuoloPropostoDTO>>()
          {
            @Override
            public List<SuoloPropostoDTO> extractData(ResultSet rs) throws SQLException, DataAccessException
            {
              ArrayList<SuoloPropostoDTO> result = new ArrayList<SuoloPropostoDTO>();
              ArrayList<CoordinateFotoAppezzamentoDTO> coordinateFotoAppezzamento = null;
              SuoloPropostoDTO item = null;
              long idFeature = 0;
              long idFeatureLast = 0;
              
              while (rs.next())
              {
                idFeatureLast = rs.getLong("ID_FEATURE");
                if(idFeatureLast!=idFeature)
                {
                  idFeature = idFeatureLast;
                  item = new SuoloPropostoDTO();
                  item.setIdFeature(rs.getLong("ID_FEATURE"));
                  item.setFoglio(rs.getString("FOGLIO"));
                  item.setIdentificativoPraticaOrigine(rs.getString("IDENTIFICATIVO_PRATICA_ORIGINE"));
                  item.setCodiceNazionale(rs.getString("CODICE_NAZIONALE"));
                  if(item.getIdentificativoPraticaOrigine()!=null && item.getIdentificativoPraticaOrigine().trim().length()>0)
                    item.setIdIstanzaRiesame(rs.getString("ID_ISTANZA_RIESAME"));
                  item.setGeometriaWkt(rs.getString("GEOMETRIA_WKT"));
                  item.setSrid(rs.getString("SRID"));
                  item.setIdEleggibilitaRilevata(rs.getLong("ID_ELEGGIBILITA_RILEVATA"));
                  item.setCodiceEleggibilitaRilevata(rs.getString("CODICE_ELEGGIBILITA_RILEVATA"));
                  item.setDescEleggibilitaRilevata(rs.getString("DESC_ELEGGIBILITA_RILEVATA"));
                  
                  coordinateFotoAppezzamento = new ArrayList<CoordinateFotoAppezzamentoDTO>();
                  item.setCoordinateFotoAppezzamento(coordinateFotoAppezzamento);
                  result.add(item);
                }
                
                CoordinateFotoAppezzamentoDTO foto = new CoordinateFotoAppezzamentoDTO();
                foto.setIdFotoAppezzamento(rs.getString("ID_FOTO_APPEZZAMENTO_CONS"));
                foto.setLatitudine(rs.getString("LATITUDINE"));
                foto.setLongitudine(rs.getString("LONGITUDINE"));
                
                String direzioneRef = rs.getString("DIREZIONE_GPS_REF");
                String direzione = rs.getString("DIREZIONE_GPS");
                if(direzioneRef!=null)
                {
                  // T nord geografico , M magnetico (da convertire)
                  foto.setDirezione(("T".equals(direzioneRef) ? direzione : convertMagneticNorthToTrueNorth(Double.parseDouble(direzione))+""));
                }
                else
                  foto.setDirezione(null);
                coordinateFotoAppezzamento.add(foto);
              }
              return result;
            }
          });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio: " + foglio
          + ", idEventoLavorazione:" + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public double convertMagneticNorthToTrueNorth(double degree)
  {
     double delta = 8.0;
     if(degree>=(360.0-delta) && degree<=360.0)
     {
       return (degree + delta - 360);
     }
     else if(degree > 360)
     {
       return convertMagneticNorthToTrueNorth(degree % 360);
     }
     else
     {
       return (degree + delta);
     }
  }
  
  public List<ParticellaDTO> getParticelleFoglio(long idEventoLavorazione, String cuaa,
      String codiceNazionale, long foglio, long annoCampagna)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getParticelleFoglio]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio: " + foglio + ", cuaa:" + cuaa
          + ", annoCampagna:" + annoCampagna + " ,idEventoLavorazione:"+idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    
   String QUERY =     
             " WITH                                                                                                                                                     \n"
           + "     DATI_AZIENDA AS ( SELECT Ext_Id_Azienda AS ID_AZIENDA from QGIS_T_EVENTO_LAVORAZIONE where ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE )                                                                                                                                        \n"
           + "     SELECT                                                                                                                                               \n"
           + "     VPC.ID_VERSIONE_PARTICELLA ID_FEATURE,                                                                                                               \n"
           + "     VPC.PARTICELLA NUMERO_PARTICELLA,                                                                                                                    \n"
           + "     VPC.SUBALTERNO AS SUBALTERNO,                                                                                                                        \n"
           + "     'B' AS FLAG_PART_LAV_CONF,                                                                                                                           \n"
           + "     SDO_UTIL.TO_WKTGEOMETRY(VPC.SHAPE) AS GEOMETRIA_WKT_CONF,                                                                                            \n"
           + "     PCK_SMRGAA_STRUMENTI_GRAFICI.GETCODIEPSG( VPC.SHAPE) AS SRID ,                                                                                       \n"
           + "     SMRGAA.PCK_SMRGAA_UTILITY_QGIS.ISPARTICELLACONDOTTA(VPC.EXT_ID_PARTICELLA,DA.ID_AZIENDA,:ANNO_CAMPAGNA) AS FLAG_CONDUZIONE_CONF,                     \n"
           + "     (SELECT DECODE (PL.FLAG_SOSPENSIONE, NULL, 'N', 'S' ) FROM QGIS_T_PARTICELLA_LAVORAZIONE PL WHERE PL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE  \n"
           + "         AND PL.EXT_COD_NAZIONALE(+) = VPC.EXT_COD_NAZIONALE                                                                                              \n"
           + "         AND PL.FOGLIO(+) = VPC.FOGLIO                                                                                                                    \n"
           + "         AND VPC.PARTICELLA = PL.PARTICELLA(+) AND VPC.ID_VERSIONE_PARTICELLA = PL.ID_VERSIONE_PARTICELLA                                                 \n"
           + "     ) AS FLAG_SOSPENSIONE,                                                                                                                               \n"
           + "     (SELECT PL.DESCRIZIONE_SOSPENSIONE FROM QGIS_T_PARTICELLA_LAVORAZIONE PL WHERE PL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                     \n"
           + "         AND PL.EXT_COD_NAZIONALE(+) = VPC.EXT_COD_NAZIONALE                                                                                              \n"
           + "         AND PL.FOGLIO(+) = VPC.FOGLIO                                                                                                                    \n"
           + "         AND VPC.PARTICELLA = PL.PARTICELLA(+)     AND VPC.ID_VERSIONE_PARTICELLA = PL.ID_VERSIONE_PARTICELLA                                             \n"
           + "     ) AS DESCRIZIONE_SOSPENSIONE                                                                                                                         \n"
           + "     FROM QGIS_T_VERSIONE_PARTICELLA VPC, DATI_AZIENDA DA  , QGIS_T_REGISTRO_PARTICELLE RP                                                                                               \n"
           + "     WHERE                                                                                                                                                \n"
           + "     VPC.FOGLIO = :FOGLIO                                                                                                                                 \n"
           + "     AND VPC.EXT_COD_NAZIONALE = :CODICE_NAZIONALE                                                                                                        \n"
           + "     AND RP.DATA_FINE_VALIDITA IS NULL AND RP.FOGLIO = VPC.FOGLIO AND RP.EXT_COD_NAZIONALE = VPC.EXT_COD_NAZIONALE AND RP.CAMPAGNA= :ANNO_CAMPAGNA AND RP.ID_VERSIONE_PARTICELLA = VPC.ID_VERSIONE_PARTICELLA                                                                                                               \n"
           + "  order by VPC.PARTICELLA ,VPC.SUBALTERNO                                                                                                                 \n";

    try
    {
      mapSqlParameterSource.addValue("CUAA", cuaa, Types.VARCHAR);
      mapSqlParameterSource.addValue("CODICE_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ANNO_CAMPAGNA", annoCampagna, Types.NUMERIC);

      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource,
          new ResultSetExtractor<List<ParticellaDTO>>()
          {
            @Override
            public List<ParticellaDTO> extractData(ResultSet rs) throws SQLException, DataAccessException
            {
              List<ParticellaDTO> particelle = new ArrayList<ParticellaDTO>();
              ParticellaDTO particella = null;
             
              rs.setFetchSize(500);
              while (rs.next())
              {
                particella = new ParticellaDTO();
                particella.setFlagConduzione(rs.getString("FLAG_CONDUZIONE_CONF"));
                particella.setFlagPartLav(rs.getString("FLAG_PART_LAV_CONF"));
                particella.setGeometriaWkt(rs.getString("GEOMETRIA_WKT_CONF"));
                particella.setSrid(rs.getString("SRID"));
                particella.setSubalterno(rs.getString("SUBALTERNO"));
                particella.setIdFeature(rs.getLong("ID_FEATURE"));
                particella.setNumeroParticella(rs.getString("NUMERO_PARTICELLA"));
                particelle.add(particella);
              }
              
              
              return particelle;
            }
          });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio: " + foglio + ", cuaa:" + cuaa
          + ", annoCampagna:" + annoCampagna, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<ClasseEleggibilitaDTO> getClassiEleggibilita()
  {
    String THIS_METHOD = "getClassiEleggibilita]";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_METHOD + " BEGIN.");
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = " SELECT                                                \n"
        + "   TER.CODI_RILE_PROD AS CODICE_ELEGGIBILITA_RILEVATA,                \n"
        + "   TER.DESC_RILE_PROD AS DESC_ELEGGIBILITA_RILEVATA,                  \n"
        + "   TER.FLAG_ASSEGNABILE_QGIS AS FLAG_ASSEGNABILE_QGIS                 \n"
        + " FROM                                                                 \n"
        + "   SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA TER                           \n"
        + " ORDER BY                                                             \n"
        + "    TER.CODI_RILE_PROD,                                               \n"
        + "    TER.DESC_RILE_PROD                                                \n";
    try
    {
      return queryForList(QUERY, mapSqlParameterSource, ClasseEleggibilitaDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void assegnaEventoAllUtente(long idEventoLavorazione,
      Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::assegnaEventoAllUtente]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " ,idUtenteLogin: " + idUtenteLogin);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String UPDATE = " UPDATE QGIS_T_EVENTO_LAVORAZIONE                      \n"
        + " SET EXT_ID_UTENTE_LAVORAZIONE = :ID_UTENTE                            \n"
        + " WHERE ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                  \n";
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_UTENTE", idUtenteLogin, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " ,idUtenteLogin: " + idUtenteLogin, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void insertSuoloBloccato(long idEventoLavorazione,
      SuoloLavorazioneDTO suolo, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertSuoloBloccato]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione
          + " ,idUtenteLogin: " + idUtenteLogin);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String UPDATE = " INSERT INTO QGIS_T_SUOLO_BLOCCATO (                   \n"
        + " ID_SUOLO_BLOCCATO,                                  \n"
        + " ID_EVENTO_LAVORAZIONE,                              \n"
        + " ID_SUOLO_RILEVATO,                                  \n"
        + " DATA_INIZIO_BLOCCO,                                 \n"
        + " DATA_FINE_BLOCCO,                                   \n"
        + " EXT_ID_UTENTE_BLOCCO                                \n"
        + ")                                                    \n"
        + " VALUES  (                                           \n"
        + " :ID_SUOLO_BLOCCATO,                                 \n"
        + " :ID_EVENTO_LAVORAZIONE,                             \n"
        + " :ID_SUOLO_RILEVATO,                                 \n"
        + " SYSDATE,                                            \n"
        + " NULL,                                               \n"
        + " :EXT_ID_UTENTE_BLOCCO                               \n"
        + ")                                                    \n";
    try
    {
      Long idSuoloBloccato = getNextSequenceValue("SEQ_QGIS_T_SUOLO_BLOCCATO");
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_SUOLO_BLOCCATO", idSuoloBloccato, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", suolo.getIdFeature(), Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_BLOCCO", idUtenteLogin, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " ,idUtenteLogin: " + idUtenteLogin
          + " ,ID_SUOLO_RILEVATO: " + suolo.getIdFeature()
          + " ,idUtenteLogin: " + idUtenteLogin
          + " ,idUtenteLogin: " + idUtenteLogin
          ,
          e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public boolean isEventoBloccato(long idEventoLavorazione, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::isEventoBloccato]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idUtenteLogin: " + idUtenteLogin);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                                   \n"
            + "   COUNT(*) N_BLOCCATI                                                  \n"
            + " FROM                                                                   \n"
            + "   QGIS_T_EVENTO_BLOCCATO                                               \n"
            + " WHERE                                                                  \n"
            + "   ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                       \n"
            + "   AND DATA_FINE_VALIDITA IS NULL                                       \n");
    if (idUtenteLogin != null)
      QUERY.append(" AND EXT_ID_UTENTE_AGGIORNAMENTO <> :ID_UTENTE_LOGIN                \n");
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_UTENTE_LOGIN", idUtenteLogin, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nBloccati = rs.getInt("N_BLOCCATI");
            if (nBloccati > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idUtenteLogin: " + idUtenteLogin, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public int sbloccoForzatoFogli(long idEventoLavorazione, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::sbloccoForzatoFogli]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione
          + " ,idUtenteLogin: " + idUtenteLogin);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " UPDATE QGIS_T_FOGLIO_BLOCCATO               \n"
        + " SET DATA_FINE_VALIDITA = SYSDATE,                     \n"
        + " EXT_ID_UTENTE_AGGIORNAMENTO = :ID_UTENTE_LOGIN        \n"
        + " WHERE                                                 \n"
        + " EXT_ID_UTENTE_AGGIORNAMENTO = :ID_UTENTE_LOGIN        \n"
        + " AND ID_EVENTO_BLOCCATO IN (                           \n"
        + "   SELECT                                              \n"
        + "     ID_EVENTO_BLOCCATO                                \n"
        + "   FROM                                                \n"
        + "     QGIS_T_EVENTO_BLOCCATO                            \n"
        + "   WHERE                                               \n"
        + "     ID_EVENTO_LAVORAZIONE=:ID_EVENTO_LAVORAZIONE      \n"
        + ")                                                      \n";

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_UTENTE_LOGIN", idUtenteLogin, Types.NUMERIC);

      return namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " ,idUtenteLogin: " + idUtenteLogin,
          e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public void sbloccoEvento(long idEventoLavorazione, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::sbloccoEvento]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione
          + " ,idUtenteLogin: " + idUtenteLogin);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " UPDATE                                        \n"
        + "   QGIS_T_EVENTO_BLOCCATO                                \n"
        + " SET                                                     \n"
        + "   DATA_FINE_VALIDITA = SYSDATE,                         \n"
        + "   EXT_ID_UTENTE_AGGIORNAMENTO = :ID_UTENTE_LOGIN        \n"
        + " WHERE                                                   \n"
        + "   EXT_ID_UTENTE_AGGIORNAMENTO = :ID_UTENTE_LOGIN        \n"
        + "   AND ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE    \n";

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_UTENTE_LOGIN", idUtenteLogin, Types.NUMERIC);

      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " ,idUtenteLogin: " + idUtenteLogin,
          e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  

  public void updateSuoloRilevato(Long idEventoLavorazione, Long idFeature,
      Geometry geometry, Date dataAggiornamento, Long idUtenteLogin, Date dataFineValidita)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::updateSuoloRilevato]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " ,idUtenteLogin: " + idUtenteLogin
          + ", idFeature: " + idFeature);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = 
        " DECLARE GEOM clob:= '"+geometry+"';    BEGIN   "
        +" UPDATE QGIS_T_SUOLO_RILEVATO                            \n"
        + " SET                                                               \n";
    if (geometry != null)
      UPDATE += " SHAPE =  SDO_UTIL.FROM_WKTGEOMETRY(:SHAPE),                 \n"
          + " DATA_AGGIORNAMENTO = :DATA_AGGIORNAMENTO,                       \n";
    else
      UPDATE += " DATA_FINE_VALIDITA = :DATA_FINE_VALIDITA,                   \n";

    UPDATE += " EXT_ID_UTENTE_AGGIORNAMENTO = :EXT_ID_UTENTE_AGGIORNAMENTO    \n"
        + " WHERE                                                             \n"
        + " ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO   ; END;                         \n";

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteLogin, Types.NUMERIC);
      mapSqlParameterSource.addValue("DATA_AGGIORNAMENTO", dataAggiornamento, Types.TIMESTAMP);
      mapSqlParameterSource.addValue("DATA_FINE_VALIDITA", dataFineValidita, Types.TIMESTAMP);
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idFeature, Types.NUMERIC);
      //mapSqlParameterSource.addValue("SHAPE", geometry, Types.CLOB);

      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idUtenteLogin: " + idUtenteLogin
          + ", idFeature: " + idFeature);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void storicizzaSuoliPadre(ArrayList<Long> idFeaturePadre, Date dataFineValidita)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::storicizzaSuoliPadre]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idFeaturePadre: " + idFeaturePadre);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " UPDATE QGIS_T_SUOLO_RILEVATO  SET                           \n"
        + " DATA_FINE_VALIDITA = :DATA_FINE_VALIDITA                    \n"
        + " WHERE                                                       \n"
        + " 1=1                                                         \n"
        + getInCondition("ID_SUOLO_RILEVATO", idFeaturePadre,true);

    try
    {
      mapSqlParameterSource.addValue("DATA_FINE_VALIDITA", dataFineValidita, Types.TIMESTAMP);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public Long insertSuoloRilevato(Long idEventoLavorazione, SuoloLavoratoDTO suolo,
      Date dataAggiornamento, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertSuoloRilevato]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD +  "-  elenco variabili: idEventoLavorazione: " + idEventoLavorazione + ", idFeature: " + suolo.getIdFeature()
      + ", AREA: " +  suolo.getArea()
      + ", FOGLIO: " + suolo.getFoglio()
      + ", EXT_COD_NAZIONALE: " + suolo.getCodiceNazionale()
      + ", COD_ELEGGIBILITA_RILEVATA: " + suolo.getCodiceEleggibilitaRilevata()
      + ", EXT_ID_UTENTE_AGGIORNAMENTO: " + idUtenteLogin
      + ", SHAPE: " + suolo.getGeometry()
      + ", DATA_INSERIMENTO: " + idUtenteLogin);

    }
    
    String idTipoSorgente = "1";
    Long id = getIdTipoSorgenteSuoli(idEventoLavorazione);
    if(id!=null && (id.longValue() == 4 || id.longValue() == 5) )
      idTipoSorgente = Long.toString(id);
    
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " DECLARE GEOM clob:=  '';    BEGIN   " +StringUtils.splitSQLStringWidthVar(suolo.getGeometry().toString(), 20000, "GEOM")+" \n"
        + "  INSERT INTO QGIS_T_SUOLO_RILEVATO                       \n"           
        + "  (                                                                 \n"
        + "  ID_SUOLO_RILEVATO,                                                \n"
        + "  AREA,                                                             \n"
        + "  CAMPAGNA,                                                         \n"
        + "  EXT_COD_NAZIONALE,                                                \n"
        + "  FOGLIO,                                                           \n"
        + "  DATA_INIZIO_VALIDITA,                                             \n"
        + "  DATA_FINE_VALIDITA,                                               \n"
        + "  DATA_AGGIORNAMENTO,                                               \n"
        + "  EXT_ID_ELEGGIBILITA_RILEVATA,                                     \n"
        + "  EXT_ID_UTENTE_AGGIORNAMENTO,                                      \n"
        + "  ID_TIPO_SORGENTE_SUOLO,                                           \n"
        + "  SHAPE                                                             \n"
        + " )                                                                  \n"
        + "  VALUES                                                            \n"
        + "  (                                                                 \n"
        + "  :ID_SUOLO_RILEVATO,                                               \n"
        + "  :AREA,                                                            \n"
        + "  ( SELECT                                                          \n"
        + "      L.CAMPAGNA                                                    \n"
        + "    FROM                                                            \n"
        + "      QGIS_T_EVENTO_LAVORAZIONE E,                                  \n"
        + "      QGIS_T_LISTA_LAVORAZIONE L                                    \n"
        + "    WHERE                                                           \n"
        + "      E.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE              \n"
        + "      AND E.ID_LISTA_LAVORAZIONE = L.ID_LISTA_LAVORAZIONE),         \n"                              
        + "  :EXT_COD_NAZIONALE,                                               \n"
        + "  :FOGLIO,                                                          \n"
        + "  :DATA_INSERIMENTO,                                                \n"
        + "  NULL,                                                             \n"
        + "  SYSDATE,                                                          \n"
        + "  (SELECT                                                           \n"
        + "      MAX(ID_ELEGGIBILITA_RILEVATA)                                      \n"
        + "   FROM                                                             \n"
        + "      SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA                          \n"
        + "   WHERE                                                            \n"
        + "      CODI_RILE_PROD = :COD_ELEGGIBILITA_RILEVATA                   \n"
        + "      ) ,                             \n"
        + "  :EXT_ID_UTENTE_AGGIORNAMENTO,                                     \n"
        + "  :ID_TIPO_SORGENTE_SUOLO,                                     \n"
        + "  SDO_UTIL.FROM_WKTGEOMETRY(GEOM) ) ; END;                              \n";


    try
    { 
      Long idSuoloRilevato = getNextSequenceValue("SEQ_QGIS_T_SUOLO_RILEVATO");
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idSuoloRilevato, Types.NUMERIC);
      mapSqlParameterSource.addValue("AREA", suolo.getArea(), Types.DECIMAL);
      mapSqlParameterSource.addValue("FOGLIO", suolo.getFoglio(), Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", suolo.getCodiceNazionale(), Types.VARCHAR);
      mapSqlParameterSource.addValue("COD_ELEGGIBILITA_RILEVATA", suolo.getCodiceEleggibilitaRilevata(), Types.VARCHAR);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteLogin, Types.NUMERIC);
      mapSqlParameterSource.addValue("DATA_INSERIMENTO", dataAggiornamento, Types.TIMESTAMP);
      mapSqlParameterSource.addValue("ID_TIPO_SORGENTE_SUOLO", idTipoSorgente, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      //mapSqlParameterSource.addValue("SHAPE", suolo.getGeometry(), Types.CLOB);

      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
      return idSuoloRilevato;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idFeature: " + suolo.getIdFeature()
          + ", AREA: " +  suolo.getArea()
          + ", FOGLIO: " + suolo.getFoglio()
          + ", EXT_COD_NAZIONALE: " + suolo.getCodiceNazionale()
          + ", COD_ELEGGIBILITA_RILEVATA: " + suolo.getCodiceEleggibilitaRilevata()
          + ", EXT_ID_UTENTE_AGGIORNAMENTO: " + idUtenteLogin
          + ", SHAPE: " + suolo.getGeometry()
          + ", DATA_INSERIMENTO: " + idUtenteLogin
          , e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void updateEventoLavorazione(Long idEventoLavorazione,
      Date dataAggiornamento, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::updateEventoLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idUtenteLogin: " + idUtenteLogin);
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " UPDATE QGIS_T_EVENTO_LAVORAZIONE SET                            \n"
        + " EXT_ID_UTENTE_LAVORAZIONE = :EXT_ID_UTENTE_LAVORAZIONE,         \n"
        + " DATA_LAVORAZIONE = :DATA_LAVORAZIONE                            \n"
        + " WHERE                                                           \n"
        + " ID_EVENTO_LAVORAZIONE=:ID_EVENTO_LAVORAZIONE                    \n";

    mapSqlParameterSource.addValue("EXT_ID_UTENTE_LAVORAZIONE", idUtenteLogin, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
    mapSqlParameterSource.addValue("DATA_LAVORAZIONE", dataAggiornamento, Types.TIMESTAMP);

    try
    {
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idUtenteLogin: " + idUtenteLogin,
          e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void insertVariazioneSuoloRil(Long idSuoloRilevato,
      Long idFeaturePadre, Date dataAggiornamento)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertVariazioneSuoloRil]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idSuoloRilevato" + idSuoloRilevato + ", idFeaturePadre: " + idFeaturePadre);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " INSERT INTO QGIS_T_VARIAZIONE_SUOLO_RIL             \n"
        + " (                                                   \n"
        + " ID_VARIAZIONE_SUOLO_RIL,                            \n"
        + " ID_SUOLO_RILEVATO_PADRE,                            \n"
        + " ID_SUOLO_RILEVATO_FIGLIO,                           \n"
        + " DATA_VARIAZIONE                                     \n"
        + ")                                                    \n"
        + " VALUES                                              \n"
        + " (                                                   \n"
        + " :ID_VARIAZIONE_SUOLO_RIL,                           \n"
        + " :ID_SUOLO_RILEVATO_PADRE,                           \n"
        + " :ID_SUOLO_RILEVATO_FIGLIO,                          \n"
        + " :DATA_VARIAZIONE                                    \n"
        + ")                                                    \n";

    try
    {
      Long idVariazione = getNextSequenceValue("SEQ_QGIS_T_VARIAZION_SUOLO_RIL");
      mapSqlParameterSource.addValue("ID_VARIAZIONE_SUOLO_RIL", idVariazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO_FIGLIO", idSuoloRilevato, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO_PADRE", idFeaturePadre, Types.NUMERIC);
      mapSqlParameterSource.addValue("DATA_VARIAZIONE", dataAggiornamento, Types.TIMESTAMP);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + ": idSuoloRilevato" + idSuoloRilevato + ", idFeaturePadre: " + idFeaturePadre);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void updateSuoloLavorazione(Long idEventoLavorazione, Long idFeature,
      String descrizioneSospensione, Long flagSospensione,
      String noteLavorazione, Long idTipoMotivoSospensione, long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::updateSuoloLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idFeature: " + idFeature
          + ", flagSospensione: " + flagSospensione + ", idTipoMotivoSospensione: " + idTipoMotivoSospensione);
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " UPDATE QGIS_T_SUOLO_LAVORAZIONE                                 \n"
        + " SET                                                             \n"
        + " DESCRIZIONE_SOSPENSIONE = :DESCRIZIONE_SOSPENSIONE,             \n"
        + " FLAG_SOSPENSIONE = :FLAG_SOSPENSIONE,                           \n"
        + " FLAG_LAVORATO = 'S',                                            \n"
        + " NOTE_LAVORAZIONE = :NOTE_LAVORAZIONE,                           \n"
        + " ID_TIPO_MOTIVO_SOSPENSIONE = :ID_TIPO_MOTIVO_SOSPENSIONE,        \n"
        + " EXT_ID_UTENTE_LAVORAZIONE = :EXT_ID_UTENTE_LAVORAZIONE,        \n"
        + " DATA_LAVORAZIONE  = SYSDATE        \n"
        + " WHERE                                                           \n"
        + " ID_EVENTO_LAVORAZIONE=:ID_EVENTO_LAVORAZIONE                    \n"
        + " AND ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                      \n";

    mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idFeature, Types.NUMERIC);
    mapSqlParameterSource.addValue("DESCRIZIONE_SOSPENSIONE", descrizioneSospensione, Types.VARCHAR);
    mapSqlParameterSource.addValue("FLAG_SOSPENSIONE", flagSospensione == 1L ? "S" : "N", Types.VARCHAR);
    mapSqlParameterSource.addValue("NOTE_LAVORAZIONE", noteLavorazione, Types.VARCHAR);
    mapSqlParameterSource.addValue("ID_TIPO_MOTIVO_SOSPENSIONE", idTipoMotivoSospensione, Types.NUMERIC);
    mapSqlParameterSource.addValue("EXT_ID_UTENTE_LAVORAZIONE", idUtenteLogin, Types.NUMERIC);
    
    try
    {
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + "idEventoLavorazione: " + idEventoLavorazione + ", idFeature: " + idFeature
          + ", flagSospensione: " + flagSospensione + ", idTipoMotivoSospensione: " + idTipoMotivoSospensione);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  
  public void updateLavorazioneFoglio(long foglio, String codiceNazionale)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::updateLavorazioneFoglio]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " foglio: " + foglio + ", codiceNazionale: " + codiceNazionale);
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE =     " update qgis_t_suolo_lavorazione                     \n"
        + " set flag_lavorato = 'S'                             \n"
        + " where id_suolo_rilevato in (                        \n"
        + " select id_suolo_rilevato from QGIS_T_SUOLO_rilevato \n"
        + " where                                               \n"
        + "     FOGLIO = :FOGLIO                                \n"
        + "     AND EXT_COD_NAZIONALE = :EXT_COD_NAZIONALE      \n"
        + " )                                                   \n";

    mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
    mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
    
    try
    {
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + "foglio: " + foglio + ", codiceNazionale: " + codiceNazionale);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public boolean esisteSuoloLavorazione(Long idEventoLavorazione,
      Long idFeature)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::esisteSuoloLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione
          + ", idFeature: " + idFeature);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT COUNT(*) N_SUOLI                                        \n"
            + " FROM QGIS_T_SUOLO_LAVORAZIONE                                  \n"
            + " WHERE ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE           \n"
            + " AND ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                     \n");

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idFeature, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nSuoli = rs.getInt("N_SUOLI");
            if (nSuoli > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione
          + ", idFeature: " + idFeature, e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void insertSuoloLavorazione(Long idEventoLavorazione, Long idFeature, String tipoSuolo, long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertSuoloLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione" + idEventoLavorazione + ", idFeature: " + idFeature);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " INSERT INTO QGIS_T_SUOLO_LAVORAZIONE                   \n"
        + " (                                                   \n"
        + " ID_SUOLO_LAVORAZIONE,                               \n"
        + " ID_EVENTO_LAVORAZIONE,                              \n"
        + " ID_SUOLO_RILEVATO,                                  \n"
        + " FLAG_SOSPENSIONE,                                   \n"
        + " FLAG_LAVORATO,                                      \n"
        + " TIPO_SUOLO_ORIGINE,                                 \n"
        + " FLAG_CESSATO,                                        \n"
        + " EXT_ID_UTENTE_LAVORAZIONE,                                        \n"
        + " DATA_LAVORAZIONE                                        \n"
        + ")                                                    \n"
        + " VALUES                                              \n"
        + " (                                                   \n"
        + " :ID_SUOLO_LAVORAZIONE,                              \n"
        + " :ID_EVENTO_LAVORAZIONE,                             \n"
        + " :ID_SUOLO_RILEVATO,                                 \n"
        + " 'N',                                                \n"
        + " 'S',                                                \n"
        + " :TIPO_SUOLO_ORIGINE,                                \n"
        + " 'N',                                                 \n"
        + " :EXT_ID_UTENTE_LAVORAZIONE ,                               \n"
        + " SYSDATE                                \n"
        + ")                                                    \n";

    try
    {
      Long idSuoloLavorazione = getNextSequenceValue("SEQ_QGIS_T_SUOLO_LAVORAZIONE");
      mapSqlParameterSource.addValue("ID_SUOLO_LAVORAZIONE", idSuoloLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idFeature, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_LAVORAZIONE", idUtenteLogin, Types.NUMERIC);
      mapSqlParameterSource.addValue("TIPO_SUOLO_ORIGINE", tipoSuolo, Types.VARCHAR);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + ": idEventoLavorazione" + idEventoLavorazione + ", idFeature: " + idFeature);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void updateCessaSuoloLavorazione(Long idEventoLavorazione,
      Long idFeature, long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::updateCessaSuoloLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idFeature: " + idFeature);
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " UPDATE QGIS_T_SUOLO_LAVORAZIONE                                 \n"
        + " SET                                                             \n"
        + " FLAG_CESSATO = 'S',                                              \n"
        + " EXT_ID_UTENTE_LAVORAZIONE = :EXT_ID_UTENTE_LAVORAZIONE,        \n"
        + " DATA_LAVORAZIONE  = SYSDATE        \n"
        + " WHERE                                                           \n"
        + " ID_EVENTO_LAVORAZIONE=:ID_EVENTO_LAVORAZIONE                    \n"
        + " AND ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                      \n"
        ;

    mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idFeature, Types.NUMERIC);
    mapSqlParameterSource.addValue("EXT_ID_UTENTE_LAVORAZIONE", idUtenteLogin, Types.NUMERIC);
    
    try
    {
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + ": idEventoLavorazione" + idEventoLavorazione + ", idFeature: " + idFeature);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public boolean esisteSuoloParticella(Long idSuoloRilevato, Long idVersioneParticella)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::esisteSuoloParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.error(THIS_METHOD + " idSuoloRilevato: " + idSuoloRilevato + ", idSuoloParticella: "
          + idVersioneParticella);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
            " SELECT COUNT(*) N_SUOLI                                               \n"
                + " FROM QGIS_T_SUOLO_PARTICELLA                                    \n"
                + " WHERE ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                    \n"
                + " AND ID_VERSIONE_PARTICELLA = :ID_VERSIONE_PARTICELLA                  \n");

    try
    {
      mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", idVersioneParticella, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idSuoloRilevato, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nSuoli = rs.getInt("N_SUOLI");
            if (nSuoli > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idSuoloRilevato: " + idSuoloRilevato + ", idVersioneParticella: "
          + idVersioneParticella);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public boolean esisteSuoloParticellaByArea(Long idVersioneParticella , double area, long idUtenteAggiornamento)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::esisteSuoloParticellaByArea]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.error(THIS_METHOD + " idVersioneParticella: " + idVersioneParticella + ", idUtenteAggiornamento: "
          + idUtenteAggiornamento+ ", area: "
          + area);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
            " SELECT COUNT(*) N_SUOLI                                               \n"
                + " FROM QGIS_T_SUOLO_PARTICELLA                                    \n"
                + " WHERE AREA = :AREA                    \n"
                + " AND ID_VERSIONE_PARTICELLA = :ID_VERSIONE_PARTICELLA   AND EXT_ID_UTENTE_AGGIORNAMENTO = :EXT_ID_UTENTE_AGGIORNAMENTO               \n");

    try
    {
      mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", idVersioneParticella, Types.NUMERIC);
      mapSqlParameterSource.addValue("AREA", area, Types.DECIMAL);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteAggiornamento, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nSuoli = rs.getInt("N_SUOLI");
            if (nSuoli > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idVersioneParticella: " + idVersioneParticella + ", idUtenteAggiornamento: "
          + idUtenteAggiornamento+ ", area: "
          + area);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void updateSuoloParticella(Long idFeature, SuoloParticellaDTO suolo,
      Date dataAggiornamento, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::updateSuoloParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idSuoloRilevato: " + idFeature + ", idSuoloParticella: " + suolo.getIdFeature()
          + ", idUtenteLogin: " + idUtenteLogin+", area:"+suolo.getArea() + ", SHAPE "+suolo.getGeometry());
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE =
        " DECLARE GEOM clob:=  '';    BEGIN   " +StringUtils.splitSQLStringWidthVar(suolo.getGeometry().toString(), 20000, "GEOM")+"  \n"
        +" UPDATE QGIS_T_SUOLO_PARTICELLA                                  \n"
        + " SET                                                             \n"
        + " AREA = :AREA,                                                   \n"
        + " SHAPE = SDO_UTIL.FROM_WKTGEOMETRY(GEOM),                      \n"
        + " DATA_AGGIORNAMENTO = :DATA_AGGIORNAMENTO,                       \n"
        + " EXT_ID_UTENTE_AGGIORNAMENTO = :EXT_ID_UTENTE_AGGIORNAMENTO      \n"
        + " WHERE                                                           \n"
        + " ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                      \n"
        + " AND ID_VERSIONE_PARTICELLA = :ID_VERSIONE_PARTICELLA ; END;                     \n";

    mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", suolo.getIdFeature(), Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idFeature, Types.NUMERIC);
    mapSqlParameterSource.addValue("AREA", suolo.getArea(), Types.DECIMAL);
    mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteLogin, Types.NUMERIC);
    mapSqlParameterSource.addValue("DATA_AGGIORNAMENTO", dataAggiornamento, Types.TIMESTAMP);
    //mapSqlParameterSource.addValue("SHAPE", suolo.getGeometry(), Types.CLOB);

    try
    {
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + " idSuoloRilevato: " + idFeature + ", idSuoloParticella: " + suolo.getIdFeature()
          + ", idUtenteLogin: " + idUtenteLogin+", area:"+suolo.getArea() + ", SHAPE "+suolo.getGeometry());
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void insertSuoloParticella(Long idFeature, SuoloParticellaDTO suolo,
      Date dataAggiornamento, Long idUtenteLogin, int progr, long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertSuoloParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idSuoloRilevato: " + idFeature + ", ID_VERSIONE_PARTICELLA: " + suolo.getIdFeature()
          + ", idUtenteLogin: " + idUtenteLogin + ", progr: " + progr+", area"+suolo.getArea()+ ", SHAPE "+suolo.getGeometry());
    }
    
     String annoCampagna = getAnnoCampagna(idEventoLavorazione);
     Long idVersioneParticellaNew = getIdVersioneParticella(suolo.getFoglio(),suolo.getCodiceNazionale(),suolo.getNumeroParticella(),suolo.getSubalterno(), annoCampagna);
     logger.debug(THIS_METHOD + " inserita versione particella #"+idVersioneParticellaNew);
     
    
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = 
            " DECLARE GEOM clob:=  '';    BEGIN   " +StringUtils.splitSQLStringWidthVar(suolo.getGeometry().toString(), 20000, "GEOM")+"  \n"
        +" INSERT INTO QGIS_T_SUOLO_PARTICELLA                            \n"
        + " (ID_SUOLO_PARTICELLA, ID_SUOLO_RILEVATO, ID_VERSIONE_PARTICELLA, AREA,DATA_AGGIORNAMENTO, PROG_POLIGONO, SHAPE,EXT_ID_UTENTE_AGGIORNAMENTO)"
        + "VALUES"
        + " (:ID_SUOLO_PARTICELLA, :ID_SUOLO_RILEVATO, :ID_VERSIONE_PARTICELLA, :AREA, :DATA_AGGIORNAMENTO, :PROG_POLIGONO,  SDO_UTIL.FROM_WKTGEOMETRY(GEOM), :EXT_ID_UTENTE_AGGIORNAMENTO)"
        + " ; END; ";

    mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idFeature, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_SUOLO_PARTICELLA", getNextSequenceValue("SEQ_QGIS_T_SUOLO_PARTICELLA"),
        Types.NUMERIC);
    mapSqlParameterSource.addValue("AREA", suolo.getArea(), Types.DECIMAL);
    mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteLogin, Types.NUMERIC);
    mapSqlParameterSource.addValue("DATA_AGGIORNAMENTO", dataAggiornamento, Types.TIMESTAMP);
    mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", idVersioneParticellaNew    , Types.NUMERIC);
    mapSqlParameterSource.addValue("PROG_POLIGONO", progr, Types.NUMERIC);

    try
    {
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + " idSuoloRilevato: " + idFeature + ", idSuoloParticella: " + suolo.getIdFeature()
          + ", idUtenteLogin: " + idUtenteLogin + ", progr: " + progr+", area"+suolo.getArea()+ ", SHAPE "+suolo.getGeometry());
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public String fixShape(String geometriaWkt)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::fixShape]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " shape: " + geometriaWkt);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT  SDO_UTIL.TO_WKTGEOMETRY(SITIPIOPR.FIXSHAPE(SDO_UTIL.FROM_WKTGEOMETRY(:SHAPE)))   GEOM                    \n"
            + "     FROM DUAL                                                                           \n");
    try
    {
      mapSqlParameterSource.addValue("SHAPE", geometriaWkt, Types.CLOB);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<String>()
      {
        @Override
        public String extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          if (rs.next())
          {
            return rs.getString("GEOM");
          }
          return null;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<MotivoSospensioneDTO> getMotiviSospensione()
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getMotiviSospensione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = " SELECT                                 \n"
        + "   DESC_TIPO_MOTIVO_SOSPENSIONE DESCRIZIONE,           \n"
        + "   ID_TIPO_MOTIVO_SOSPENSIONE                          \n"
        + " FROM                                                  \n"
        + "   QGIS_D_TIPO_MOTIVO_SOSPENSIONE                      \n"
        + " WHERE                                                 \n"
        + "   DATA_FINE_VALIDITA IS NULL                          \n"
        + " ORDER BY                                              \n"
        + "    DESC_TIPO_MOTIVO_SOSPENSIONE                       \n";
    try
    {
      return queryForList(QUERY, mapSqlParameterSource, MotivoSospensioneDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public boolean isFoglioBloccato(long foglio, String codiceNazionale, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::isFoglioBloccato]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " foglio: " + foglio + " codiceNazionale:" + codiceNazionale + " idUtenteLogin: "
          + idUtenteLogin);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                                \n"
            + "   COUNT(*) N_BLOCCATI                                           \n"
            + " FROM                                                            \n"
            + "   QGIS_T_FOGLIO_BLOCCATO FB                                     \n"
            + " WHERE                                                           \n"
            + "   FB.FOGLIO = :FOGLIO                                           \n"
            + "   AND FB.EXT_COD_NAZIONALE = :CODICE_NAZIONALE                  \n"
            + "   AND DATA_FINE_VALIDITA IS NULL                                \n"
            + "   AND EXT_ID_UTENTE_AGGIORNAMENTO <> :ID_UTENTE_LOGIN           \n");
    try
    {
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("CODICE_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("ID_UTENTE_LOGIN", idUtenteLogin, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nBloccati = rs.getInt("N_BLOCCATI");
            if (nBloccati > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " foglio: " + foglio + " codiceNazionale:" + codiceNazionale + " idUtenteLogin: "
          + idUtenteLogin, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public Long getIdBloccoEvento(long idEventoLavorazione, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getIdBloccoEvento]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " idUtenteLogin: " + idUtenteLogin);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                         \n"
            + "   ID_EVENTO_BLOCCATO                                           \n"
            + " FROM                                                           \n"
            + "   QGIS_T_EVENTO_BLOCCATO                                       \n"
            + " WHERE                                                          \n"
            + "   ID_EVENTO_LAVORAZIONE=:ID_EVENTO_LAVORAZIONE                 \n"
            + "   AND DATA_FINE_VALIDITA IS NULL                               \n"
            + "   AND EXT_ID_UTENTE_AGGIORNAMENTO = :ID_UTENTE_LOGIN           \n");
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_UTENTE_LOGIN", idUtenteLogin, Types.NUMERIC);
      return namedParameterJdbcTemplate.queryForObject(QUERY.toString(), mapSqlParameterSource, Long.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " idUtenteLogin: " + idUtenteLogin, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public Long insertBloccoEvento(long idEventoLavorazione, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertBloccoEvento]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idUtenteLogin: " + idUtenteLogin);
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " INSERT INTO QGIS_T_EVENTO_BLOCCATO      \n"
        + " (                                                 \n"
        + " ID_EVENTO_BLOCCATO,                               \n"
        + " ID_EVENTO_LAVORAZIONE,                            \n"
        + " DATA_INIZIO_VALIDITA,                             \n"
        + " DATA_FINE_VALIDITA,                               \n"
        + " EXT_ID_UTENTE_AGGIORNAMENTO                       \n"
        + ")                                                  \n"
        + " VALUES                                            \n"
        + " (                                                 \n"
        + " :ID_EVENTO_BLOCCATO,                              \n"
        + " :ID_EVENTO_LAVORAZIONE,                           \n"
        + " SYSDATE,                                          \n"
        + " NULL,                                             \n"
        + " :EXT_ID_UTENTE_AGGIORNAMENTO                      \n"
        + ")                                                  \n";

    try
    {
      Long idEventoBloccato = getNextSequenceValue("SEQ_QGIS_T_EVENTO_BLOCCATO");
      mapSqlParameterSource.addValue("ID_EVENTO_BLOCCATO", idEventoBloccato, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteLogin, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
      return idEventoBloccato;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", idUtenteLogin: " + idUtenteLogin, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void insertBloccoFoglio(Long idEventoBloccato, Long foglio, String codiceNazionale, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertBloccoFoglio]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoBloccato: " + idEventoBloccato + ", foglio: " + foglio + ", codiceNazionale: " + codiceNazionale
          + ", idUtenteLogin: " + idUtenteLogin);
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " INSERT INTO QGIS_T_FOGLIO_BLOCCATO      \n"
        + " (                                                 \n"
        + " ID_EVENTO_BLOCCATO,                               \n"
        + " ID_FOGLIO_BLOCCATO,                               \n"
        + " FOGLIO,                                           \n"
        + " EXT_COD_NAZIONALE,                                \n"
        + " DATA_INIZIO_VALIDITA,                             \n"
        + " DATA_FINE_VALIDITA,                               \n"
        + " EXT_ID_UTENTE_AGGIORNAMENTO                       \n"
        + ")                                                  \n"
        + " VALUES                                            \n"
        + " (                                                 \n"
        + " :ID_EVENTO_BLOCCATO,                              \n"
        + " :ID_FOGLIO_BLOCCATO,                              \n"
        + " :FOGLIO,                                          \n"
        + " :EXT_COD_NAZIONALE,                               \n"
        + " SYSDATE,                                          \n"
        + " NULL,                                             \n"
        + " :EXT_ID_UTENTE_AGGIORNAMENTO                      \n"
        + ")                                                  \n";

    try
    {
      Long idFoglioBloccato = getNextSequenceValue("SEQ_QGIS_T_FOGLIO_BLOCCATO");
      mapSqlParameterSource.addValue("ID_FOGLIO_BLOCCATO", idFoglioBloccato, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_BLOCCATO", idEventoBloccato, Types.NUMERIC);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteLogin, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoBloccato: " + idEventoBloccato + ", foglio: " + foglio + ", codiceNazionale: " + codiceNazionale
          + ", idUtenteLogin: " + idUtenteLogin, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void sbloccaFoglio(int foglio, String codiceNazionale, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::sbloccaFoglio]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " foglio: " + foglio + " ,codiceNazionale: " + codiceNazionale + " ,idUtenteLogin: " + idUtenteLogin);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " UPDATE                                      \n"
        + "   QGIS_T_FOGLIO_BLOCCATO                              \n"
        + " SET                                                   \n"
        + "   DATA_FINE_VALIDITA = SYSDATE,                       \n"
        + "   EXT_ID_UTENTE_AGGIORNAMENTO = :ID_UTENTE_LOGIN      \n"
        + " WHERE                                                 \n"
        + "   EXT_ID_UTENTE_AGGIORNAMENTO = :ID_UTENTE_LOGIN      \n"
        + "   AND FOGLIO = :FOGLIO                                \n"
        + "   AND EXT_COD_NAZIONALE=:EXT_COD_NAZIONALE            \n";

    try
    {
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("ID_UTENTE_LOGIN", idUtenteLogin, Types.NUMERIC);

      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " foglio: " + foglio + " ,codiceNazionale: " + codiceNazionale + " ,idUtenteLogin: " + idUtenteLogin,
          e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public String getTabellaRegistroSuoli(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getTabellaRegistroSuoli]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " select LL.ID_TIPO_SORGENTE_SUOLO from QGIS_T_LISTA_LAVORAZIONE LL , QGIS_T_EVENTO_LAVORAZIONE EL where EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE \n"
      + " and EL.ID_LISTA_LAVORAZIONE = LL.ID_LISTA_LAVORAZIONE                                                                                                    \n"
    );
    
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<String>()
      {
        @Override
        public String extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            Long idTipoSorgSuolo = rs.getLong("ID_TIPO_SORGENTE_SUOLO");
            if(idTipoSorgSuolo!=null && (idTipoSorgSuolo==4L || idTipoSorgSuolo==5L) )
              return AgriApiConstants.TABELLA_REGISTRO.CO;
          }
          return AgriApiConstants.TABELLA_REGISTRO.SUOLI;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public Long getIdTipoSorgenteSuoli(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getIdTipoSorgenteSuoli]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
              " select LL.ID_TIPO_SORGENTE_SUOLO from QGIS_T_LISTA_LAVORAZIONE LL , QGIS_T_EVENTO_LAVORAZIONE EL where EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE \n"
            + " and EL.ID_LISTA_LAVORAZIONE = LL.ID_LISTA_LAVORAZIONE                                                                                                    \n"
          );

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Long>()
      {
        @Override
        public Long extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            return  rs.getLong("ID_TIPO_SORGENTE_SUOLO");
          }
          return null;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public boolean esistonoFogliSuoliNonLavorati(Long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::esistonoFogliSuoliNonLavorati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                                   \n"
            + "   COUNT(*) NUM_FOGLI_NON_LAVORATI                                      \n"
            + " FROM                                                                   \n"
            + "   QGIS_T_SUOLO_LAVORAZIONE SR                                            \n"
            + " WHERE                                                                  \n"
            + "   SR.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                       \n"
            + "   AND SR.FLAG_CESSATO = 'N'                                               \n"
            + "   AND SR.FLAG_LAVORATO = 'N'                                              \n");
//            + "   AND  NOT exists (SELECT 'X' FROM "+getTabellaRegistroSuoli(idEventoLavorazione)+" SR2, QGIS_T_EVENTO_LAVORAZIONE EL, QGIS_T_LISTA_LAVORAZIONE LL WHERE  "
//            + "   SR.ID_SUOLO_RILEVATO = SR2.ID_SUOLO_RILEVATO AND  EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE AND LL.ID_LISTA_LAVORAZIONE =  EL.ID_LISTA_LAVORAZIONE "
//            + "   AND SR2.CAMPAGNA = LL.CAMPAGNA  AND SR2.DATA_FINE_VALIDITA IS NULL"
//            + " ) ");


    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nBloccati = rs.getInt("NUM_FOGLI_NON_LAVORATI");
            if (nBloccati > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public boolean esistonoFogliParticelleNonLavorati(Long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::esistonoFogliParticelleNonLavorati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT COUNT (*)                                                                                                \n"
            + "  NUM_FOGLI_NON_LAVORATI                                                                                         \n"
            + "   FROM QGIS_T_PARTICELLA_LAVORAZIONE pl , QGIS_T_VERSIONE_PARTICELLA SR                                                                        \n"
            + "  WHERE     pl.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                                                                           \n"
            + "        AND pl.FLAG_CESSATO = 'N'   AND  SR.ID_VERSIONE_PARTICELLA         = pl.ID_VERSIONE_PARTICELLA                                                                                \n"
            + "        AND pl.FLAG_LAVORATO = 'N'                                                                                  \n"
//            + "        AND  NOT exists                                                                                          \n"
//            + "               (SELECT 'X' FROM QGIS_T_REGISTRO_PARTICELLE SR2, QGIS_T_EVENTO_LAVORAZIONE EL, QGIS_T_LISTA_LAVORAZIONE LL WHERE  \n" + 
//            "               SR.ID_VERSIONE_PARTICELLA = SR2.ID_VERSIONE_PARTICELLA AND  EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE AND LL.ID_LISTA_LAVORAZIONE =  EL.ID_LISTA_LAVORAZIONE \n" + 
//            "               AND SR2.CAMPAGNA = LL.CAMPAGNA AND SR2.DATA_FINE_VALIDITA IS NULL                                                                                                                              \n" + 
//            "             )                                                                                                                                                             \n"
);

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nBloccati = rs.getInt("NUM_FOGLI_NON_LAVORATI");
            if (nBloccati > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public Long countFogliSuoliNonLavorati(Long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::countFogliSuoliNonLavorati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
              "             SELECT                                                                                                                           \n"
            + "                 COUNT(DISTINCT FOGLIO)  AS NUM_FOGLI_NON_LAVORATI                                                                                                     \n"
            + "              FROM                                                                                                                            \n"
            + "                  QGIS_T_SUOLO_RILEVATO SR,                                                                                                   \n"
            + "                 QGIS_T_SUOLO_LAVORAZIONE SL                                                                                                  \n"
            + "              WHERE                                                                                                                           \n"
            + "                SL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                                                                             \n"
            + "               AND  SR.ID_SUOLO_RILEVATO         = SL.ID_SUOLO_RILEVATO                                                                       \n"
            + "                AND SL.FLAG_CESSATO = 'N'                                                                                                     \n"
            + "                AND SL.FLAG_LAVORATO = 'N'                                                                                                    \n"
            + "   AND  NOT exists (SELECT 'X' FROM "+getTabellaRegistroSuoli(idEventoLavorazione)+" SR2, QGIS_T_EVENTO_LAVORAZIONE EL, QGIS_T_LISTA_LAVORAZIONE LL WHERE  "
            + "   SR.ID_SUOLO_RILEVATO = SR2.ID_SUOLO_RILEVATO AND  EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE AND LL.ID_LISTA_LAVORAZIONE =  EL.ID_LISTA_LAVORAZIONE "
            + "   AND SR2.CAMPAGNA = LL.CAMPAGNA AND SR2.DATA_FINE_VALIDITA IS NOT  NULL "
            + " ) ");

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      Long count = namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Long>()
      {
        @Override
        public Long extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            return rs.getLong("NUM_FOGLI_NON_LAVORATI");
          }
          return null;
        }
      });
      
      logger.debug(THIS_METHOD + " #count: " + (count!=null ? count.longValue() : "NULL"));
      return count;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public Long countFogliParticelleNonLavorati(Long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::countFogliParticelleNonLavorati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
              "             SELECT                                                                                                                           \n"
            + "                 COUNT(DISTINCT SR.FOGLIO)  AS NUM_FOGLI_NON_LAVORATI                                                                                                     \n"
            + "              FROM                                                                                                                            \n"
            + "                  QGIS_T_VERSIONE_PARTICELLA SR,                                                                                                   \n"
            + "                 QGIS_T_PARTICELLA_LAVORAZIONE SL                                                                                                  \n"
            + "              WHERE                                                                                                                           \n"
            + "                SL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                                                                             \n"
            + "               AND  SR.ID_VERSIONE_PARTICELLA         = SL.ID_VERSIONE_PARTICELLA                                                                       \n"
            + "                AND SL.FLAG_CESSATO = 'N'                                                                                                     \n"
            + "                AND SL.FLAG_LAVORATO = 'N'                                                                                                    \n"
            + "        AND  NOT exists                                                                                          \n"
            + "               (SELECT 'X' FROM QGIS_T_REGISTRO_PARTICELLE SR2, QGIS_T_EVENTO_LAVORAZIONE EL, QGIS_T_LISTA_LAVORAZIONE LL WHERE  \n" + 
            "               SR.ID_VERSIONE_PARTICELLA = SR2.ID_VERSIONE_PARTICELLA AND  EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE AND LL.ID_LISTA_LAVORAZIONE =  EL.ID_LISTA_LAVORAZIONE \n" + 
            "               AND SR2.CAMPAGNA = LL.CAMPAGNA  AND SR2.DATA_FINE_VALIDITA IS NOT NULL                                                                                                                            \n" + 
            "             )                                                                                                                                                             \n");

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      Long count = namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Long>()
      {
        @Override
        public Long extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            return rs.getLong("NUM_FOGLI_NON_LAVORATI");
          }
          return null;
        }
      });
      
      logger.debug(THIS_METHOD + " #count: " + (count!=null ? count.longValue() : "NULL"));
      return count;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public boolean esistonoFogliSuoloLavorati(Long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::esistonoFogliSuoloLavorati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                                   \n"
            + "   COUNT(*) NUM_FOGLI_LAVORATI                                      \n"
            + " FROM                                                                   \n"
            + "   QGIS_T_SUOLO_LAVORAZIONE                                             \n"
            + " WHERE                                                                  \n"
            + "   ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                       \n"
            + "   AND FLAG_LAVORATO = 'S'                                              \n");

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nBloccati = rs.getInt("NUM_FOGLI_LAVORATI");
            if (nBloccati > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public boolean hoLavoratoTuttiISuoliDelFoglioaa(Long idEventoLavorazione, int foglio, String codiceNazionale)
  {

    String THIS_METHOD = "[" + THIS_CLASS + "::esistonoFogliLavorati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                                       \n"
            + "   COUNT(*) NUM_SUOLI_NON_LAVORATI                                      \n"
            + " FROM                                                                   \n"
            + "   QGIS_T_SUOLO_LAVORAZIONE SL,                                         \n"
            + "   QGIS_T_SUOLO_RILEVATO SR                                             \n"
            + " WHERE                                                                  \n"
            + "   SL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                    \n"
            + "   AND SR.ID_SUOLO_RILEVATO = SL.ID_SUOLO_RILEVATO                      \n"
            + "   AND SR.FOGLIO = :FOGLIO                                              \n"
            + "   AND SR.EXT_COD_NAZIONALE = :EXT_COD_NAZIONALE                        \n"
            + "   AND SR.DATA_FINE_VALIDITA IS NULL                                    \n"
            + "   AND FLAG_CESSATO = 'N'                                               \n"
            + "   AND SL.FLAG_LAVORATO = 'N'                                           \n");

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", codiceNazionale, Types.VARCHAR);

      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nBloccati = rs.getInt("NUM_SUOLI_NON_LAVORATI");
            if (nBloccati > 0)
              return false;
            else
              return true;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void deleteSuoloParticella(Long idFeature, SuoloParticellaDTO suolo)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::deleteSuoloParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }

    final String QUERY = " DELETE                                  \n"
        + " FROM                                                   \n"
        + "   QGIS_T_SUOLO_PARTICELLA                              \n"
        + " WHERE                                                  \n"
        + "   ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                  "
        + "   AND ID_VERSIONE_PARTICELLA = :ID_VERSIONE_PARTICELLA            \n";

    MapSqlParameterSource mapParameterSource = new MapSqlParameterSource();
    try
    {
      mapParameterSource.addValue("ID_SUOLO_RILEVATO", idFeature, Types.VARCHAR);
      mapParameterSource.addValue("ID_VERSIONE_PARTICELLA", suolo.getIdFeature(), Types.VARCHAR);
      namedParameterJdbcTemplate.update(QUERY, mapParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idSuoloRilevato: " + idFeature + " idSuoloParticella: " + suolo.getIdFeature(), e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<ParametroDTO> getElencoParametri()
  {
    String THIS_METHOD = "getElencoParametri]";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_METHOD + " BEGIN.");
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = " SELECT                                                           \n"
        + "     ID_PARAMETRO_PLUGIN,                                                        \n"
        + "     CODICE,                                                                     \n"
        + "     DESCRIZIONE,                                                                \n"
        + "     TIPO,                                                                       \n"
        + "     VALORE_STRINGA,                                                             \n"
        + "     VALORE_NUMERICO,                                                            \n"
        + "     VALORE_DATA                                                                 \n"
        + " FROM                                                                            \n"
        + "     QGIS_D_PARAMETRO_PLUGIN                                                     \n"
        + " WHERE                                                                           \n"
        + "     (DATA_FINE_VALIDITA IS NULL OR DATA_FINE_VALIDITA>SYSDATE)                  \n"
        + "     AND DATA_INIZIO_VALIDITA <= SYSDATE                                         \n";
    try
    {
      return queryForList(QUERY, mapSqlParameterSource, ParametroDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public ParametroDTO getParametroByName(String codice)
  {
    String THIS_METHOD = "getParametroByName]";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_METHOD + " BEGIN.");
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = " SELECT                                                           \n"
        + "     ID_PARAMETRO_PLUGIN,                                                        \n"
        + "     CODICE,                                                                     \n"
        + "     DESCRIZIONE,                                                                \n"
        + "     TIPO,                                                                       \n"
        + "     VALORE_STRINGA,                                                             \n"
        + "     VALORE_NUMERICO,                                                            \n"
        + "     VALORE_DATA                                                                 \n"
        + " FROM                                                                            \n"
        + "     QGIS_D_PARAMETRO_PLUGIN                                                     \n"
        + " WHERE                                                                           \n"
        + "     (DATA_FINE_VALIDITA IS NULL OR DATA_FINE_VALIDITA>SYSDATE)                  \n"
        + "     AND DATA_INIZIO_VALIDITA <= SYSDATE                                         \n"
        + "    AND  CODICE = :CODICE                 \n";
    try
    {
      mapSqlParameterSource.addValue("CODICE", codice, Types.VARCHAR);
      return queryForObject(QUERY, mapSqlParameterSource, ParametroDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<FoglioRiferimentoDTO> getFoglioRiferimento(long annoCampagna, String codiceNazionale, long foglio)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getFoglioRiferimento]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio: " + foglio
          + ", annoCampagna:" + annoCampagna);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String QUERY =   "   SELECT                                                            \n"
        + "      EXT_COD_NAZIONALE,                                                        \n"
        + "      CAMPAGNA_INIZIO,                                                          \n"
        + "      CAMPAGNA_FINE,                                                            \n"
        + "      ID_FOGLIO_RIFERIMENTO,                                                    \n"
        + "      ID_GEO_FOGLIO,                                                            \n"
        + "      COD_COM_BELFIORE,                                                         \n"
        + "      COD_COM_ISTAT,                                                            \n"
        + "      COMUNE,                                                                   \n"
        + "      SEZIONE,                                                                  \n"
        + "      FOGLIO,                                                                   \n"
        + "      ALLEGATO,                                                                 \n"
        + "      SVILUPPO,                                                                 \n"
        + "      AGGIORNATO_AL,                                                            \n"
        + "      STATO,                                                                    \n"
        + "      COD_COM_ISTAT_BDTRE,                                                      \n"
        + "      SDO_UTIL.TO_WKTGEOMETRY(SHAPE) AS GEOMETRIA_WKT,                           \n"
        + addSubselectSRID("SHAPE")+"  \n"
        
        + "    FROM                                                                        \n"
        + "      QGIS_T_FOGLIO_RIFERIMENTO                                                 \n"
        + "    WHERE                                                                       \n"
        + "      EXT_COD_NAZIONALE = :CODICE_NAZIONALE                                     \n"
        + "      AND FOGLIO = :FOGLIO                                                      \n"
        + "      AND :ANNO_CAMPAGNA BETWEEN CAMPAGNA_INIZIO AND CAMPAGNA_FINE              \n"
        + "      AND DATA_FINE_VALIDITA IS NULL                                            \n";
    
    try
    
    {
      mapSqlParameterSource.addValue("ANNO_CAMPAGNA", annoCampagna, Types.NUMERIC);
      mapSqlParameterSource.addValue("CODICE_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      return queryForList(QUERY.toString(), mapSqlParameterSource, FoglioRiferimentoDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio: " + foglio
          + ", annoCampagna:" + annoCampagna, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public String getToken(GestioneCookieDTO cookieDTO)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getToken]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String UPDATE = " INSERT INTO QGIS_W_GESTIONE_COOKIE (                   \n"
        + " ID_GESTIONE_COOKIE,                                  \n"
        + " COOKIE_1,                              \n"
        + " COOKIE_2,                                  \n"
        + " COOKIE_3,                                 \n"
        + " COOKIE_4,                                   \n"
        + " COOKIE_5,                                \n"
        + " PARAMETRO                                \n"
        + ")                                                    \n"
        + " VALUES  (                                           \n"
        + " :ID_GESTIONE_COOKIE,                                  \n"
        + " :COOKIE_1,                              \n"
        + " :COOKIE_2,                                  \n"
        + " :COOKIE_3,                                 \n"
        + " :COOKIE_4,                                   \n"
        + " :COOKIE_5,                                \n"
        + " :PARAMETRO                                \n"
        + ")                                                    \n";
    try
    {
      Long id = getNextSequenceValue("SEQ_QGIS_W_GESTIONE_COOKIE");
      mapSqlParameterSource.addValue("ID_GESTIONE_COOKIE", id, Types.NUMERIC);
      mapSqlParameterSource.addValue("COOKIE_1", cookieDTO.getCookie1(), Types.VARCHAR);
      mapSqlParameterSource.addValue("COOKIE_2", cookieDTO.getCookie2(), Types.VARCHAR);
      mapSqlParameterSource.addValue("COOKIE_3", cookieDTO.getCookie3(), Types.VARCHAR);
      mapSqlParameterSource.addValue("COOKIE_4", cookieDTO.getCookie4(), Types.VARCHAR);
      mapSqlParameterSource.addValue("COOKIE_5", cookieDTO.getCookie5(), Types.VARCHAR);
      mapSqlParameterSource.addValue("PARAMETRO", cookieDTO.getParametro(), Types.VARCHAR);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
      return id+"";
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public GestioneCookieDTO getCookiesFromToken(String token)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getCookiesFromToken]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " token: " + token);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
              " SELECT                                                             \n"
            + "  ID_GESTIONE_COOKIE, COOKIE_1,COOKIE_2,COOKIE_3,COOKIE_4,COOKIE_5,PARAMETRO  \n"
            + " FROM                                                               \n"
            + "   QGIS_W_GESTIONE_COOKIE                                           \n"
            + " WHERE                                                              \n"
            + "   ID_GESTIONE_COOKIE=:ID_GESTIONE_COOKIE                           \n");
    try
    {
      mapSqlParameterSource.addValue("ID_GESTIONE_COOKIE", token, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource,
          new ResultSetExtractor<GestioneCookieDTO>()
          {
            @Override
            public GestioneCookieDTO extractData(ResultSet rs) throws SQLException, DataAccessException
            {
              GestioneCookieDTO result = new GestioneCookieDTO();
              if (rs.next())
              {
                result.setIdGestioneToken(rs.getLong("ID_GESTIONE_COOKIE"));
                result.setCookie1(rs.getString("COOKIE_1"));
                result.setCookie2(rs.getString("COOKIE_2"));   
                result.setCookie3(rs.getString("COOKIE_3"));
                result.setCookie4(rs.getString("COOKIE_4"));
                result.setCookie5(rs.getString("COOKIE_5"));
                result.setParametro(rs.getString("PARAMETRO"));
              }
              return result;
            }
          });
      
      
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " token: " + token , e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public void deleteWGestioneTokenById(long idGestioneToken)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::deleteWGestioneTokenById]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }

    final String QUERY = " DELETE                                  \n"
        + " FROM                                                   \n"
        + "   QGIS_W_GESTIONE_COOKIE                              \n"
        + " WHERE                                                  \n"
        + "   ID_GESTIONE_COOKIE = :ID_GESTIONE_COOKIE               \n";

    MapSqlParameterSource mapParameterSource = new MapSqlParameterSource();
    try
    {
      mapParameterSource.addValue("ID_GESTIONE_COOKIE", idGestioneToken, Types.VARCHAR);
      namedParameterJdbcTemplate.update(QUERY, mapParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idGestioneToken: " + idGestioneToken, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  
  public List<SuoloPropostoDTO> getStoricoSuoliRilevati(String codiceNazionale, int foglio, Integer annoCampagna)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getStoricoSuoliRilevati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio: " + foglio
          + ", annoCampagna:" + annoCampagna);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
            " select   \n"
            + " SDO_UTIL.TO_WKTGEOMETRY(sr.SHAPE) AS GEOMETRIA_WKT,  \n"
            + addSubselectSRID("sr.SHAPE") +", \n"
            + " sr.campagna as anno_campagna,  \n"
            + " ter.codi_rile_prod AS CODICE_ELEGGIBILITA_RILEVATA,  \n"
            + " ter.desc_rile_prod AS DESC_ELEGGIBILITA_RILEVATA, \n"
            + " tss.descrizione AS DESCR_TIPO_SORGENTE_SUOLO, \n"
            + " nvl(ul.COGNOME_UTENTE_LOGIN ||' '||ul.NOME_UTENTE_LOGIN,sr.ext_id_utente_lavor_siticlient) as utente, \n"
            + " sr.data_inizio_validita,  \n"
            + " NVL(SR.DATA_FINE_VALIDITA, TO_DATE('31/12/9999','DD/MM/YYYY'))   AS DATA_FINE_VALIDITA,       \n"                              
            + " ll.codice||'-'|| ll.descrizione_lista AS DESCR_LISTA_LAVORAZIONE,  \n"
            + " da.CUAA||'-'||da.DENOMINAZIONE as DESCR_AZIENDA, \n"
            + " el.data_lavorazione   \n"
            
            + " from qgis_t_suolo_rilevato sr, QGIS_D_TIPO_SORGENTE_SUOLO tss, papua_v_utente_login ul,               \n"
            + " qgis_t_suolo_lavorazione sl, QGIS_T_LISTA_LAVORAZIONE ll, QGIS_T_EVENTO_LAVORAZIONE el,               \n"
            + " smrgaa.DB_TIPO_ELEGGIBILITA_RILEVATA ter, smrgaa.smrgaa_v_dati_anagrafici da,papua_v_utente_login ul1 \n"
            + " where sr.ext_cod_nazionale = :CODICE_NAZIONALE                                                                    \n"
            + " and foglio = :FOGLIO                                                                                       \n"
            + " and tss.id_tipo_sorgente_suolo = sr.id_tipo_sorgente_suolo                                            \n"
            + " and sr.ext_id_utente_aggiornamento= ul.ID_UTENTE_login (+)                                            \n"
            + " and sr.id_suolo_rilevato = sl.id_suolo_rilevato (+)                                                   \n"
            + " and sl.id_evento_lavorazione = el.id_evento_lavorazione(+)                                            \n"
            + " and el.id_lista_lavorazione = ll.id_lista_lavorazione(+)                                              \n"
            + " and el.ext_id_azienda = da.ID_AZIENDA(+)                                                              \n"
            + " and sr.ext_id_eleggibilita_rilevata= ter.id_eleggibilita_rilevata                                     \n"
            + " and el.ext_id_utente_lavorazione = ul1.ID_UTENTE_LOGIN (+)                                            \n");
    
     
    if (annoCampagna != null)
      QUERY.append("   AND sr.campagna = :ANNO_CAMPAGNA                       \n");
    
        QUERY.append(" ORDER BY                                                             \n"
        + "    sr.campagna DESC                                            \n");
    try
    {
        mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
        mapSqlParameterSource.addValue("CODICE_NAZIONALE", codiceNazionale, Types.VARCHAR);
      if (annoCampagna != null)
        mapSqlParameterSource.addValue("ANNO_CAMPAGNA", annoCampagna, Types.NUMERIC);
      return queryForList(QUERY.toString(), mapSqlParameterSource, SuoloPropostoDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio: " + foglio
          + ", annoCampagna:" + annoCampagna, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public DatiSuoloDTO leggiDatiSuolo(long idSuoloRilevato)
  {
    String THIS_METHOD = "leggiDatiSuolo]";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_METHOD + " BEGIN.");
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = 
   			 " WITH TMP_EVENTO_LAVORAZIONE AS (                                                                                                              \n"
		   + "         SELECT                                                                                                                                \n"
		   + "             :ID_SUOLO_RILEVATO AS ID_SUOLO_RILEVATO,                                                                                          \n"
		   + "             LL.CODICE || ' - ' || LL.DESCRIZIONE_LISTA AS LISTA_DI_LAVORAZIONE,                                                               \n"
		   + "             EL.EXT_ID_AZIENDA,                                                                                                                \n"
		   + "             EL.DATA_LAVORAZIONE AS DATA_LAVORAZIONE,                                                                                          \n"
		   + "             (                                                                                                                                 \n"
		   + "                 SELECT                                                                                                                        \n"
		   + "                     VDA.DENOMINAZIONE                                                                                                         \n"
		   + "                 FROM                                                                                                                          \n"
		   + "                     SMRGAA_V_DATI_ANAGRAFICI VDA                                                                                              \n"
		   + "                 WHERE                                                                                                                         \n"
		   + "                      EL.EXT_ID_AZIENDA = VDA.ID_AZIENDA                                                                                       \n"
		   + "                      AND VDA.DATA_FINE_VALIDITA IS NULL AND VDA.data_cessazione is null                                                                                      \n"
		   + "             ) AS AZIENDA_LAVORAZIONE,                                                                                                         \n"
		   + "             (                                                                                                                                 \n"
		   + "                 SELECT UL.COGNOME_UTENTE_LOGIN || ' ' || UL.NOME_UTENTE_LOGIN AS UTENTE_SUOLO                                                 \n"
		   + "                 FROM PAPUA_V_UTENTE_LOGIN UL                                                                                                  \n"
		   + "                 WHERE EL.EXT_ID_UTENTE_LAVORAZIONE = UL.ID_UTENTE_LOGIN                                                                       \n"
		   + "             ) AS UTENTE_LAVORAZIONE                                                                                                           \n"
		   + "         FROM                                                                                                                                  \n"
		   + "             QGIS_T_SUOLO_LAVORAZIONE SL,                                                                                                      \n"
		   + "             QGIS_T_EVENTO_LAVORAZIONE EL,                                                                                                     \n"
		   + "             QGIS_T_LISTA_LAVORAZIONE LL                                                                                                       \n"
		   + "         WHERE                                                                                                                                 \n"
		   + "             SL.ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                                                                                         \n"
		   + "             AND SL.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE                                                                           \n"
		   + "             AND EL.ID_LISTA_LAVORAZIONE = LL.ID_LISTA_LAVORAZIONE                                                                             \n"
		   + "             AND SL.ID_EVENTO_LAVORAZIONE =                                                                                                    \n"
		   + "             (                                                                                                                                 \n"
		   + "                 -- estraggo l'evento_lavorazione associato al suolo_rilevato tale per cui tale evento sia il meno recente di tutti gli eventi \n"
		   + "                 SELECT                                                                                                                        \n"
		   + "                     EL3.ID_EVENTO_LAVORAZIONE                                                                                                 \n"
		   + "                 FROM                                                                                                                          \n"
		   + "                     QGIS_T_SUOLO_LAVORAZIONE SL3,                                                                                             \n"
		   + "                     QGIS_T_EVENTO_LAVORAZIONE EL3                                                                                             \n"
		   + "                 WHERE                                                                                                                         \n"
		   + "                     SL3.ID_EVENTO_LAVORAZIONE = EL3.ID_EVENTO_LAVORAZIONE                                                                     \n"
		   + "                     AND SL3.ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                                                                            \n"
		   + "                     AND EL3.DATA_INSERIMENTO = (                                                                                              \n"
		   + "                         SELECT                                                                                                                \n"
		   + "                             MIN(EL2.DATA_INSERIMENTO)                                                                                         \n"
		   + "                         FROM                                                                                                                  \n"
		   + "                             QGIS_T_SUOLO_LAVORAZIONE SL2,                                                                                     \n"
		   + "                             QGIS_T_EVENTO_LAVORAZIONE EL2                                                                                     \n"
		   + "                         WHERE                                                                                                                 \n"
		   + "                             SL2.ID_EVENTO_LAVORAZIONE = EL2.ID_EVENTO_LAVORAZIONE                                                             \n"
		   + "                             AND SL2.ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                                                                    \n"
		   + "                     )                                                                                                                         \n"
		   + "                     AND ROWNUM < 2                                                                                                            \n"
		   + "             )                                                                                                                                 \n"
		   + " )                                                                                                                                             \n"
		   + " SELECT                                                                                                                                        \n"
		   + "     SR.CAMPAGNA AS ANNO_CAMPAGNA,                                                                                                             \n"
		   + "     SR.AREA,                                                                                                                                  \n"
		   + "     TSS.DESCRIZIONE AS TIPO_SUOLO,                                                                                                            \n"
		   + "     (                                                                                                                                         \n"
		   + "         SELECT UL.COGNOME_UTENTE_LOGIN || ' ' || UL.NOME_UTENTE_LOGIN || ' - ' || UL.DENOMINAZIONE AS UTENTE_SUOLO                                                         \n"
		   + "         FROM PAPUA_V_UTENTE_LOGIN UL                                                                                                          \n"
		   + "         WHERE NVL(TO_CHAR(SR.EXT_ID_UTENTE_AGGIORNAMENTO), SR.EXT_ID_UTENTE_LAVOR_SITICLIENT) = TO_CHAR(UL.ID_UTENTE_LOGIN)                                         \n"
		   + "     ) AS UTENTE_SUOLO,                                                                                                                        \n"
		   + "     SR.DATA_INIZIO_VALIDITA AS DATA_VALIDITA,                                                                                                 \n"
		   + "   NVL(SR.DATA_FINE_VALIDITA, TO_DATE('31/12/9999','DD/MM/YYYY'))   AS DATA_FINE_VALIDITA,                                                                                                 \n"
       + "     TMPEL.LISTA_DI_LAVORAZIONE,                                                                                                               \n"
		   + "     TMPEL.AZIENDA_LAVORAZIONE,                                                                                                                \n"
		   + "     TMPEL.UTENTE_LAVORAZIONE,																												 \n"
		   + "	   TMPEL.DATA_LAVORAZIONE,	                                                                                                                 \n"
		   + "     TER.CODI_RILE_PROD || ' - ' || TER.DESC_RILE_PROD AS CODICE_VARIETA                                                                       \n"
		   + " FROM                                                                                                                                          \n"
		   + "     QGIS_T_SUOLO_RILEVATO SR,                                                                                                                 \n"
		   + "     QGIS_D_TIPO_SORGENTE_SUOLO TSS,                                                                                                           \n"
		   + "     DB_TIPO_ELEGGIBILITA_RILEVATA TER,                                                                                                        \n"
		   + "     TMP_EVENTO_LAVORAZIONE TMPEL                                                                                                              \n"
		   + " WHERE                                                                                                                                         \n"
		   + "     SR.ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO                                                                                                 \n"
		   + "     AND SR.ID_TIPO_SORGENTE_SUOLO = TSS.ID_TIPO_SORGENTE_SUOLO                                                                                \n"
		   + "     AND TMPEL.ID_SUOLO_RILEVATO(+) = SR.ID_SUOLO_RILEVATO                                                                                        \n"
		   + "     AND SR.EXT_ID_ELEGGIBILITA_RILEVATA = TER.ID_ELEGGIBILITA_RILEVATA                                                                        \n"

    		;
    try
    {
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idSuoloRilevato);
      return queryForObject(QUERY, mapSqlParameterSource, DatiSuoloDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.\n"
      		+ " idSuoloRilevato: " + idSuoloRilevato
      		, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public boolean padreHasSuoloUnar(Long idFeaturePadre)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::padreHasSuoloUnar]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idFeaturePadre: " + idFeaturePadre);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                               \n"
            + "   COUNT(ID_SUOLO_UNAR)                                         \n"
            + " FROM                                                           \n"
            + "   QGIS_T_SUOLO_UNAR                                            \n"
            + " WHERE                                                          \n"
            + "   ID_SUOLO_RILEVATO = :ID_FEATURE_PADRE                        \n");
    try
    {
      mapSqlParameterSource.addValue("ID_FEATURE_PADRE", idFeaturePadre, Types.NUMERIC);

      Long n = namedParameterJdbcTemplate.queryForObject(QUERY.toString(), mapSqlParameterSource, Long.class);
      if(n==null || n==0)
        return false;
      else 
        return true;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idFeaturePadre: " + idFeaturePadre, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public void insertSuoloUnarFiglio(Long idSuoloRilevato, Long idFeaturePadre)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertSuoloUnarFiglio]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idSuoloRilevato: " + idSuoloRilevato + ", idFeaturePadre: " +  idFeaturePadre);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String UPDATE = " INSERT INTO QGIS_T_SUOLO_UNAR (     \n"
        + " ID_SUOLO_UNAR,                                      \n"
        + " ID_SUOLO_RILEVATO,                                  \n"
        + " EXT_ID_UNITA_ARBOREA,                               \n"
        + " DATA_INIZIO_VALIDITA,                               \n"
        + " DATA_FINE_VALIDITA                                  \n"
        + ")                                                    \n"
        + " VALUES  (                                           \n"
        + " :ID_SUOLO_UNAR,                                     \n"
        + " :ID_SUOLO_RILEVATO,                                 \n"
        + " (SELECT DISTINCT EXT_ID_UNITA_ARBOREA FROM QGIS_T_SUOLO_UNAR WHERE ID_SUOLO_UNAR = :ID_FEATURE_PADRE),                              \n"
        + " SYSDATE,                                            \n"
        + " NULL                                                \n"
        + ")                                                    \n";
    try
    {
      Long idSuoloUnar = getNextSequenceValue("SEQ_QGIS_T_SUOLO_UNAR");
      mapSqlParameterSource.addValue("ID_SUOLO_UNAR", idSuoloUnar, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idSuoloRilevato, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_FEATURE_PADRE", idFeaturePadre, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idSuoloRilevato: " + idSuoloRilevato + ", idFeaturePadre: " +  idFeaturePadre, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public SuoloRilevatoDTO getSuoloRilevato(long idSuoloRilevato)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getSuoloRilevato]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idSuoloRilevato: " + idSuoloRilevato );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = 
   	     " SELECT                                        \n"
	   + "     SR.*,                                     \n"
	   + "     SR.SHAPE.GET_WKT() AS GEOMETRY ,           \n"
	   + addSubselectSRID("sr.SHAPE") +" \n"
	   + " FROM                                          \n"
	   + "     QGIS_T_SUOLO_RILEVATO SR                  \n"
	   + " WHERE                                         \n"
	   + "     SR.ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO \n"
	   ;
	try
    {
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idSuoloRilevato, Types.NUMERIC);
      return queryForObject(QUERY.toString(), mapSqlParameterSource, SuoloRilevatoDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idSuoloRilevato: " + idSuoloRilevato, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public List<Long> getListIdParticellaAssociataASuolo (long idSuoloRilevato)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getListIdParticellaAssociataASuolo]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idSuoloRilevato: " + idSuoloRilevato );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = 
    	 " SELECT                                                        \n"
	   + "     VP.EXT_ID_PARTICELLA                                      \n"
	   + " FROM                                                          \n"
	   + "     QGIS_T_SUOLO_RILEVATO SR,                                 \n"
	   + "     QGIS_T_SUOLO_PARTICELLA SP,                               \n"
	   + "     QGIS_T_VERSIONE_PARTICELLA VP                             \n"
	   + " WHERE                                                         \n"
	   + "     SR.ID_SUOLO_RILEVATO = SP.ID_SUOLO_RILEVATO               \n"
	   + "     AND SP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA \n"
	   + "     AND SR.ID_SUOLO_RILEVATO = :ID_SUOLO_RILEVATO             \n"
	   ;
	try
    {
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idSuoloRilevato, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY, mapSqlParameterSource, new ResultSetExtractor<List<Long>>() {

		@Override
		public List<Long> extractData(ResultSet rs) throws SQLException, DataAccessException
		{
			List<Long> lista = new ArrayList<Long>();
			while(rs.next())
			{
				lista.add(rs.getLong(1));
			}
			return lista;
		}
    	  
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idSuoloRilevato: " + idSuoloRilevato, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public List<Long> getListIdParticellaCatasto (long foglio,String codiceNazionale,String subalterno,String numeroParticella,String sezione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getListIdParticellaCatasto]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " foglio: " + foglio+ " codiceNazionale: " + codiceNazionale+ " subalterno: " + subalterno+ " numeroParticella: " + numeroParticella+ " sezione: " + sezione );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
     String QUERY = 
        " SELECT                                          \n"
            + "   sp.id_particella                              \n"
            + " FROM                                            \n"
            + "   SMRGAA_V_STORICO_PARTICELLA SP,               \n"
            + "   DB_SITICOMU SC                                \n"
            + " WHERE                                           \n"
            + "   SP.foglio = :FOGLIO                       \n"
            + "   AND SC.COD_NAZIONALE = :EXT_COD_NAZIONALE     \n"
            + "   and SP.PARTICELLA = :NUMEROPARTICELLA         \n"
            + "   and nvl(SP.sezione,'-') = nvl(SC.id_sezc,'-') \n"
            + "    and SC.istat_comune = SP.istat_comune \n"
            + "   AND sp.DATA_FINE_VALIDITA_PART IS NULL        \n";
    
    if(subalterno==null || subalterno.equals(" "))
      QUERY += " and sp.subalterno is null ";
    else
      QUERY += " and sp.subalterno = :SUBALTERNO  ";
    
    if(sezione==null || sezione.equals("0"))
      QUERY += " and sp.sezione is null ";
    else
      QUERY += " and sp.sezione = :SEZIONE  ";
    
  try
    {
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("NUMEROPARTICELLA", numeroParticella, Types.VARCHAR);
      mapSqlParameterSource.addValue("SUBALTERNO",  subalterno==null ? " " : subalterno, Types.VARCHAR);
      mapSqlParameterSource.addValue("SEZIONE", sezione, Types.VARCHAR);
      return namedParameterJdbcTemplate.query(QUERY, mapSqlParameterSource, new ResultSetExtractor<List<Long>>() {

    @Override
    public List<Long> extractData(ResultSet rs) throws SQLException, DataAccessException
    {
      List<Long> lista = new ArrayList<Long>();
      while(rs.next())
      {
        lista.add(rs.getLong(1));
      }
      return lista;
    }
        
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " foglio: " + foglio+ " codiceNazionale: " + codiceNazionale+ " subalterno: " + subalterno+ " numeroParticella: " + numeroParticella+ " sezione: " + sezione );
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public List<UnarAppezzamentoDTO> leggiDatiUnarPoligono (long idSuoloRilevato, Date dataFineValidita)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getListUnarAppezzamento]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " Parametri: \n"+ 
    		  "idSuoloRilevato: " + idSuoloRilevato + "\n" +
    		  "dataFineValidita: " + dataFineValidita + "\n");
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String QUERY = 
		     " SELECT                                                                                                                        \n"
		   + "     TIPO,                                                                                                                     \n"
		   + "     SUPERFICIE,                                                                                                               \n"
		   + "     ANNO_IMPIANTO,                                                                                                            \n"
		   + "     VARIETA,                                                                                                                  \n"
		   + "     ID_UNITA_ARBOREA,                                                                                                         \n"
		   + "     VARIETA_FAG,                                                                                                         \n"
		   + "     DATA_AGGIORNAMENTO                                                                                                        \n"
		   + " FROM                                                                                                                          \n"
		   + "   TABLE(SMRGAA.PCK_SMRGAA_UTILITY_QGIS.getSchedeUnarPoligono(:ID_SUOLO_RILEVATO,NVL(:DATA_FINE_VALIDITA,date'9999-12-31'))) T1                      \n"
	   ;
	try
    {
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idSuoloRilevato, Types.NUMERIC);
      mapSqlParameterSource.addValue("DATA_FINE_VALIDITA", dataFineValidita, Types.DATE);
      return queryForList(QUERY, mapSqlParameterSource, UnarAppezzamentoDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " Parametri: \n " + 
    		  "\nidSuoloRilevato: " + idSuoloRilevato +
    		  "\ndataFineValidita: " + dataFineValidita
    		  , e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public List<UnarAppezzamentoDTO> leggiDatiUnarParticella (Long idSuoloRilevato, Date dataFineValidita, List<Long> particelle)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getListUnarAppezzamento]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " Parametri: \n"+ 
    		  "idSuoloRilevato: " + idSuoloRilevato + "\n" +
    		  "dataFineValidita: " + dataFineValidita + "\n" + 
    		  "particelle: " + particelle + "\n");
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String QUERY = 
		     " SELECT                                                                                                                        \n"
		   + "     COMUNE,                                                                                                                     \n"
		   + "     SEZIONE,                                                                                                                     \n"
		   + "     FOGLIO,                                                                                                                     \n"
		   + "     PARTICELLA,                                                                                                                     \n"
		   + "     SUBALTERNO,                                                                                                                     \n"
		   + "     TIPO,                                                                                                                     \n"
		   + "     SUPERFICIE,                                                                                                               \n"
		   + "     ANNO_IMPIANTO,                                                                                                            \n"
		   + "     VARIETA,                                                                                                                  \n"
		   + "     ID_UNITA_ARBOREA,                                                                                                         \n"
		   + "     VARIETA_FAG,                                                                                                         \n"
		   + "     DATA_AGGIORNAMENTO                                                                                                        \n"
		   + " FROM                                                                                                                          \n"
		   + "   TABLE(SMRGAA.PCK_SMRGAA_UTILITY_QGIS.getSchedeUnarParticella(:ID_SUOLO_RILEVATO, :LIST_PARTICELLE, NVL(:DATA_FINE_VALIDITA,date'9999-12-31'))) T1 \n"
	   ;
	try
    {
      mapSqlParameterSource.addValue("ID_SUOLO_RILEVATO", idSuoloRilevato, Types.NUMERIC);
      mapSqlParameterSource.addValue("DATA_FINE_VALIDITA", dataFineValidita, Types.DATE);
      
      StringBuilder oraMiningNumberNt = new StringBuilder("ORA_MINING_NUMBER_NT(");
      boolean first = true;
      for(Long idParticella : particelle)
      {
    	  if(first)
    	  {
    		  first = false;
    	  }
    	  else
    	  {
    		  oraMiningNumberNt.append(",");
    	  }
    	  oraMiningNumberNt.append(idParticella.toString());
      }
      oraMiningNumberNt.append(")");
      QUERY = QUERY.replace(":LIST_PARTICELLE", oraMiningNumberNt);
      return queryForList(QUERY, mapSqlParameterSource, UnarAppezzamentoDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " Parametri: \n " + 
    		  "\nidSuoloRilevato: " + idSuoloRilevato +
    		  "\ndataFineValidita: " + dataFineValidita +
    		  "\nparticelle: " + particelle 
    		  , e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<UtilizzoParticellaDTO> leggiDatiUtilizzoParticella( int campagna, Date dataFineValidita, List<Long> particelle)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::leggiDatiUtilizzoParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " Parametri: \n"+ 
          "campagna: " + campagna + "\n" + 
          "dataFineValidita: " + dataFineValidita + "\n" + 
          "particelle: " + particelle + "\n");
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String QUERY = 
         " SELECT                                                                                                                         \n"
       + "     SUPERFICIE,                                                                                                                \n"
       + "     UTILIZZO,                                                                                                                  \n"
       + "     DESTINAZIONE,                                                                                                              \n"
       + "     DETTAGLIO_USO,                                                                                                             \n"
       + "     QUALITA,                                                                                                                   \n"
       + "     VARIETA                                                                                                                    \n"
       + " FROM                                                                                                                           \n"
       + "   TABLE(SMRGAA.PCK_SMRGAA_UTILITY_QGIS.getUtilizzoParticella(:LIST_PARTICELLE, NVL(:DATA_FINE_VALIDITA, TO_DATE('31/12/9999','DD/MM/YYYY')), :CAMPAGNA)) T1 \n"
     ;
  try
    {
      mapSqlParameterSource.addValue("DATA_FINE_VALIDITA", dataFineValidita, Types.DATE);
      mapSqlParameterSource.addValue("CAMPAGNA", campagna, Types.NUMERIC);
      
      StringBuilder oraMiningNumberNt = new StringBuilder("ORA_MINING_NUMBER_NT(");
      boolean first = true;
      for(Long idParticella : particelle)
      {
        if(first)
        {
          first = false;
        }
        else
        {
          oraMiningNumberNt.append(",");
        }
        oraMiningNumberNt.append(idParticella.toString());
      }
      oraMiningNumberNt.append(")");
      QUERY = QUERY.replace(":LIST_PARTICELLE", oraMiningNumberNt);
      return queryForList(QUERY, mapSqlParameterSource, UtilizzoParticellaDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " Parametri: \n " +
          "\ndataFineValidita: " + dataFineValidita +
          "\nparticelle: " + particelle 
          , e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public String getIdentificativoPraticaOrigine(long idAzienda, long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getIdentificativoPraticaOrigine]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idAzienda: " + idAzienda + " idEventoLavorazione: " + idEventoLavorazione );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " select distinct b.identificativo_pratica_origine                                                                         \n"
            + " from QGIS_T_EVENTO_LAVORAZIONE z, QGIS_T_SUOLO_PROPOSTO b                                                          \n"
            + " where z.ID_EVENTO_LAVORAZIONE = b.ID_EVENTO_LAVORAZIONE    and b.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE    \n"
            + " and z.ext_id_azienda = :ID_AZIENDA  order by b.identificativo_pratica_origine                                      \n");
    try
    {
      mapSqlParameterSource.addValue("ID_AZIENDA", idAzienda, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<String>()
      {
        @Override
        public String extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          while (rs.next())
          {
            String id = rs.getString("identificativo_pratica_origine");
            if(id!=null)
              return id;
          }
          return null;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public boolean checkAnnoCampagna(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::checkAnnoCampagna]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }
    final String QUERY =     
          " select CAMPAGNA  from QGIS_T_EVENTO_LAVORAZIONE EL , QGIS_T_LISTA_LAVORAZIONE LL \n"
        + " WHERE EL.ID_LISTA_LAVORAZIONE = LL.ID_LISTA_LAVORAZIONE                          \n"
        + " AND EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                            \n" ;

    try
    {
      MapSqlParameterSource mapParameterSource = new MapSqlParameterSource();
      mapParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione,Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          if (rs.next())
          {
            int campagna = rs.getInt("CAMPAGNA");
            return campagna >= 2021;
          }
          return false;
        }
      });
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public String getAnnoCampagna(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getAnnoCampagna]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }
    final String QUERY =     
          " select CAMPAGNA  from QGIS_T_EVENTO_LAVORAZIONE EL , QGIS_T_LISTA_LAVORAZIONE LL \n"
        + " WHERE EL.ID_LISTA_LAVORAZIONE = LL.ID_LISTA_LAVORAZIONE                          \n"
        + " AND EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                            \n" ;

    try
    {
      MapSqlParameterSource mapParameterSource = new MapSqlParameterSource();
      mapParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione,Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapParameterSource, new ResultSetExtractor<String>()
      {
        @Override
        public String extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          if (rs.next())
          {
            return rs.getString("CAMPAGNA");
          }
          return "";
        }
      });
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public MainControlloDTO callMainSalvaIstanzaAnagrafe(long idEventoLavorazione)
  {
    String THIS_METHOD = "callMainSalvaIstanzaAnagrafe";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + ":: " + THIS_METHOD + "] BEGIN.");
    }
    try 
    {
      MapSqlParameterSource parameterSource = new MapSqlParameterSource();
      parameterSource.addValue("PIDEVENTOLAVORAZIONE", idEventoLavorazione,Types.NUMERIC);

      SimpleJdbcCall call = new SimpleJdbcCall(
          (DataSource) appContext.getBean("dataSource"))
              .withCatalogName("PCK_QGIS_LIBRERIA")
              .withProcedureName("SalvaIstanza")
              .withoutProcedureColumnMetaDataAccess();

      call.addDeclaredParameter(
          new SqlParameter("PIDEVENTOLAVORAZIONE", java.sql.Types.NUMERIC));
      call.addDeclaredParameter(
          new SqlOutParameter("PCODERRORE", java.sql.Types.VARCHAR));
      call.addDeclaredParameter(
          new SqlOutParameter("PDESCERRORE", java.sql.Types.VARCHAR));

      
      Map<String, String> mapParametri = getParametri(new String[]
          { AgriApiConstants.PARAMETRI.TIMEOUT_ASYNC});

      String queryTimeout = mapParametri.get(AgriApiConstants.PARAMETRI.TIMEOUT_ASYNC);
      call.getJdbcTemplate().setQueryTimeout(Integer.parseInt(queryTimeout)); 
      
      Map<String, Object> results = call.execute(parameterSource);

      MainControlloDTO dto = new MainControlloDTO();
      dto.setRisultato(((String) results.get("PCODERRORE")));
      dto.setMessaggio(safeMessaggioPLSQL((String) results.get("PDESCERRORE")));
      return dto;

    }
    catch (Throwable e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + ":: " + THIS_METHOD + "] END.");
      }
    }
  }
  
  


  public ImmagineAppezzamentoDTO getImmagineAppezzamentoFromId(
      int idFotoAppezzamentoCons)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::checkAnnoCampagna]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }
    final String QUERY =     
          " SELECT NOME_FISICO_FOTO, NOME_LOGICO_FOTO, FOTO FROM DB_FOTO_APPEZZAMENTO_CONS WHERE ID_FOTO_APPEZZAMENTO_CONS = :ID_FOTO_APPEZZAMENTO_CONS \n" ;

    try
    {
      MapSqlParameterSource mapParameterSource = new MapSqlParameterSource();
      mapParameterSource.addValue("ID_FOTO_APPEZZAMENTO_CONS", idFotoAppezzamentoCons,Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapParameterSource, new ResultSetExtractor<ImmagineAppezzamentoDTO>()
      {
        @Override
        public ImmagineAppezzamentoDTO extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          ImmagineAppezzamentoDTO item = null;
          if (rs.next())
          {
            item = new ImmagineAppezzamentoDTO();
            item.setContent(rs.getBytes("FOTO"));
            item.setNomeFisicoFile(rs.getString("NOME_FISICO_FOTO"));
            item.setNomeLogicoFile(rs.getString("NOME_LOGICO_FOTO"));
          }
          return item;
        }
      });
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }


  public void insertWFogliLavorati(Long idEventoLavorazione, int foglio,String codiceNazionale)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertWFogliLavorati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", foglio: " + foglio + ", codiceNazionale: " + codiceNazionale);
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " INSERT INTO QGIS_W_FOGLI_LAVORATI      \n"
        + " (                                                 \n"
        + " ID_EVENTO_LAVORAZIONE,                               \n"
        + " FOGLIO,                                           \n"
        + " EXT_COD_NAZIONALE                                \n"
        + ")                                                  \n"
        + " VALUES                                            \n"
        + " (                                                 \n"
        + " :ID_EVENTO_LAVORAZIONE,                              \n"
        + " :FOGLIO,                                          \n"
        + " :EXT_COD_NAZIONALE                               \n"
        + ")                                                  \n";

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", foglio: " + foglio + ", codiceNazionale: " + codiceNazionale);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public void deleteWGestioneFogliLavorati(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::deleteWGestioneFogliLavorati]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }

    final String QUERY = " DELETE                                  \n"
        + " FROM                                                   \n"
        + "   QGIS_W_FOGLI_LAVORATI                              \n"
        + " WHERE                                                  \n"
        + "   ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE               \n";

    MapSqlParameterSource mapParameterSource = new MapSqlParameterSource();
    try
    {
      mapParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.VARCHAR);
      namedParameterJdbcTemplate.update(QUERY, mapParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public boolean esisteLavorazioneFogliInCorso(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::esisteLavorazioneFogliInCorso]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT COUNT(*) N_FOGLI                                        \n"
            + " FROM QGIS_W_FOGLI_LAVORATI                                  \n"
            + " WHERE ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE           \n");

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nSuoli = rs.getInt("N_FOGLI");
            if (nSuoli > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }


  public BigDecimal getAreaSuoliRilevatiByList(List<Long> ids)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getAreaSuoliRilevatiByList]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN. ids: " + Arrays.toString(ids.toArray()));
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT SUM(AREA) AS AREA  FROM QGIS_T_SUOLO_RILEVATO      WHERE             " +getInCondition("ID_SUOLO_RILEVATO", ids, false));

    try
    {
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<BigDecimal>()
      {
        @Override
        public BigDecimal extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          BigDecimal area = null;
          while (rs.next())
          {
            area = rs.getBigDecimal("AREA");

          }
          return area;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " ids: " + Arrays.toString(ids.toArray()), e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }


  public boolean isFoglioLavorato(Long idEventoLavorazione, int foglio)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::isFoglioNonLavorato]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT                                                                   \n"
            + "   COUNT(*) NUM_FOGLI_LAVORATI                                      \n"
            + " FROM                                                                   \n"
            + "   QGIS_T_SUOLO_LAVORAZIONE                                             \n"
            + " WHERE                                                                  \n"
            + "   ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                       \n"
            + "   AND FLAG_LAVORATO = 'S'                                              \n"
            + "   AND ID_SUOLO_RILEVATO IN (SELECT ID_SUOLO_RILEVATO FROM QGIS_T_SUOLO_RILEVATO WHERE DATA_FINE_VALIDITA IS NOT NULL AND FOGLIO = :FOGLIO )");

    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {

          while (rs.next())
          {
            int nBloccati = rs.getInt("NUM_FOGLI_LAVORATI");
            if (nBloccati > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }


  public void insertBypass(SuoloConfigurazioneDTO row, long idUtenteAggiornamento)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertBypass]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + row.getIdEventoLavorazione().longValue());

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String UPDATE = " INSERT INTO QGIS_T_LAVORAZ_BYPASS (                   \n"
        + " ID_LAVORAZ_BYPASS,                                  \n"
        + " ID_EVENTO_LAVORAZIONE,                                  \n"
        + " FLAG_DIFF_AREA_SUOLI,                              \n"
        + " FLAG_CESSATI_SUOLI,                                  \n"
        + " FLAG_AREA_MIN_SUOLI,                                  \n"
        + " FLAG_DIFF_PART_SUOLI,                                  \n"
        + " DATA_AGGIORNAMENTO,                                  \n"
        + " EXT_ID_UTENTE_AGGIORNAMENTO,                                  \n"
        + " ANOMALIA                                 \n"
        + ")                                                    \n"
        + " VALUES  (                                           \n"
        + " :ID_LAVORAZ_BYPASS,                                  \n"
        + " :ID_EVENTO_LAVORAZIONE,                                  \n"
        + " :FLAG_DIFF_AREA_SUOLI,                              \n"
        + " :FLAG_CESSATI_SUOLI,                                 \n"
        + " :FLAG_AREA_MIN_SUOLI,                                  \n"
        + " :FLAG_DIFF_PART_SUOLI,                                  \n"
        + " SYSDATE,                                  \n"
        + " :EXT_ID_UTENTE_AGGIORNAMENTO,                                  \n"
        + " :ANOMALIA                                 \n"
        + ")                                                    \n";
    try
    {
      Long id = getNextSequenceValue("SEQ_QGIS_T_LAVORAZ_BYPASS");
      mapSqlParameterSource.addValue("ID_LAVORAZ_BYPASS", id, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteAggiornamento, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", row.getIdEventoLavorazione(), Types.NUMERIC);
      mapSqlParameterSource.addValue("FLAG_DIFF_AREA_SUOLI", row.getFlagDiffAreaSuoli()== 1L ? "S" : "N", Types.VARCHAR);
      mapSqlParameterSource.addValue("FLAG_CESSATI_SUOLI", row.getFlagCessatiSuoli()== 1L ? "S" : "N", Types.VARCHAR);
      mapSqlParameterSource.addValue("FLAG_AREA_MIN_SUOLI", row.getFlagAreaMinSuoli()== 1L ? "S" : "N", Types.VARCHAR);
      mapSqlParameterSource.addValue("FLAG_DIFF_PART_SUOLI", row.getFlagDiffPartSuoli()== 1L ? "S" : "N", Types.VARCHAR);
      mapSqlParameterSource.addValue("ANOMALIA", row.getAnomalia(), Types.VARCHAR);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + row.getIdEventoLavorazione() + " ,FLAG_DIFF_AREA_SUOLI: " + row.getFlagDiffAreaSuoli()
          + " ,FLAG_CESSATI_SUOLI: " + row.getFlagCessatiSuoli()
          ,
          e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public String getCuaaFromEventoLavorazione(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getCuaaFromEventoLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
              " select VDA.cuaa from smrgaa.SMRGAA_V_DATI_ANAGRAFICI VDA, qgis_t_evento_lavorazione el \n"
            + " where VDA.DATA_FINE_VALIDITA IS NULL  AND VDA.data_cessazione is null                                                  \n"
            + " and EL.EXT_ID_AZIENDA = VDA.ID_AZIENDA                                                 \n"
            + " and el.id_evento_lavorazione = :ID_EVENTO_LAVORAZIONE                                  \n");
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<String>()
      {
        @Override
        public String extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          while (rs.next())
          {
            String id = rs.getString("cuaa");
            if(id!=null)
              return rs.getString("cuaa");
          }
          return null;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public void lockEventoLavorazione(long idEventoLavorazione)
  {
    final String QUERY = " SELECT ID_EVENTO_LAVORAZIONE FROM qgis_t_evento_lavorazione WHERE ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE FOR UPDATE ";
    MapSqlParameterSource mapParameterSource = new MapSqlParameterSource();
    mapParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
    namedParameterJdbcTemplate.queryForList(QUERY, mapParameterSource);
  }
  
  public void aggiornaStatoSalvataggioEventoLavorazione(Long idEventoLavorazione, String codiceEsito)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::aggiornaStatoSalvataggioEventoLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", codiceEsito: " + codiceEsito);
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " UPDATE qgis_t_evento_lavorazione SET ID_ESITO = (SELECT ID_ESITO FROM QGIS_D_ESITO WHERE CODICE = :CODICE)  WHERE ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE    ";

    try
    {
      mapSqlParameterSource.addValue("CODICE", codiceEsito, Types.VARCHAR);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", codiceEsito: " + codiceEsito);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<DichiarazioneConsistenzaDTO> leggiValidazioniAzienda(
      long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::leggiValidazioniAzienda]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }

    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_DEMETRAWEB", AgriApiConstants.PROCEDIMENTI.ID.ID_DEMETRAWEB, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_RPU", AgriApiConstants.PROCEDIMENTI.ID.ID_RPU, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_PSRPRATICHE", AgriApiConstants.PROCEDIMENTI.ID.ID_PSRPRATICHE, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_PSR", AgriApiConstants.PROCEDIMENTI.ID.ID_PSR, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_ANAGRAFE", AgriApiConstants.PROCEDIMENTI.ID.ID_ANAGRAFE, Types.NUMERIC);
    final String QUERY = ""
        + " SELECT                                                                                                           \n"
        + "   DC.ID_DICHIARAZIONE_CONSISTENZA,                                                                               \n"
        + "   DC.DATA_INSERIMENTO_DICHIARAZIONE    AS DATA,                                                                  \n"
        + "   DC.ANNO_CAMPAGNA,                                                                                              \n"
        + "   DC.DESCRIZIONE                       AS MOTIVO,                                                                \n"
        + "   CASE                                                                                                           \n"
        + "     WHEN SUM(DECODE(PA.ID_PROCEDIMENTO, :ID_DEMETRAWEB, 1, :ID_RPU, 1,                                           \n"
        + "                       0)) > 0                                                                                    \n"
        + "          AND SUM(DECODE(PA.ID_PROCEDIMENTO, :ID_PSRPRATICHE, 1, :ID_PSR, 1,                                      \n"
        + "                         0)) > 0 THEN                                                                             \n"
        + "       'DU - PSR'                                                                                                 \n"
        + "     ELSE                                                                                                         \n"
        + "       CASE                                                                                                       \n"
        + "         WHEN SUM(DECODE(PA.ID_PROCEDIMENTO, :ID_DEMETRAWEB, 1, :ID_RPU, 1,                                       \n"
        + "                         0)) > 0 THEN                                                                             \n"
        + "             'DU'                                                                                                 \n"
        + "         ELSE                                                                                                     \n"
        + "           CASE                                                                                                   \n"
        + "             WHEN SUM(DECODE(PA.ID_PROCEDIMENTO, :ID_PSRPRATICHE, 1, :ID_PSR, 1,                                  \n"
        + "                             0)) > 0 THEN                                                                         \n"
        + "                   'PSR'                                                                                          \n"
        + "             ELSE                                                                                                 \n"
        + "               NULL                                                                                               \n"
        + "           END                                                                                                    \n"
        + "       END                                                                                                        \n"
        + "   END AS PRATICHE                                                                                                \n"
        + " FROM                                                                                                             \n"
        + "        QGIS_T_EVENTO_LAVORAZIONE EL                                                                              \n"
        + "   JOIN SMRGAA_V_DICH_CONSISTENZA       DC ON DC.ID_AZIENDA = EL.EXT_ID_AZIENDA                                   \n"
        + "                                        AND DC.ID_PROCEDIMENTO = :ID_ANAGRAFE                                     \n"
        + "   JOIN SMRGAA_V_ACCESSO_PIANO_GRAFICO  APG ON APG.ID_DICHIARAZIONE_CONSISTENZA = DC.ID_DICHIARAZIONE_CONSISTENZA \n"
        + "   LEFT JOIN DB_PROCEDIMENTO_AZIENDA    PA ON PA.ID_AZIENDA = DC.ID_AZIENDA                                       \n"
        + "                                        AND PA.ANNO_CAMPAGNA = DC.ANNO_CAMPAGNA                                   \n"
        + " WHERE                                                                                                            \n"
        + "   EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                                                              \n"
        + "   AND DC.NUMERO_PROTOCOLLO IS NOT NULL                                                                           \n"
        + " GROUP BY                                                                                                         \n"
        + "   DC.ID_DICHIARAZIONE_CONSISTENZA,                                                                               \n"
        + "   DC.DATA_INSERIMENTO_DICHIARAZIONE,                                                                             \n"
        + "   DC.ANNO_CAMPAGNA,                                                                                              \n"
        + "   DC.DESCRIZIONE                                                                                                 \n";

    try
    {
      return queryForList(QUERY, mapSqlParameterSource, DichiarazioneConsistenzaDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD +
          " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public boolean verificaAbilitazioneListaLavorazione(UtenteAbilitazioni utenteAbilitazioni, long idListaLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + ".verificaAbilitazioneListaLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idUtenteLogin: " + utenteAbilitazioni.getIdUtenteLogin()+ ", idListaLavorazione: " + idListaLavorazione);
    }

    Map<String, String> mapLivelli = new HashMap<String, String>();
    for (Abilitazione abilitazione : utenteAbilitazioni.getAbilitazioni())
    {
      if (abilitazione.getLivello().getCodiceListaSiti() != null)
      {
        String codiceListaSiti = abilitazione.getLivello().getCodiceListaSiti();
        mapLivelli.put(codiceListaSiti, codiceListaSiti);
      }
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    mapSqlParameterSource.addValue("ID_LISTA_LAVORAZIONE", idListaLavorazione, Types.NUMERIC);
    final String QUERY = ""
        + " SELECT                                            \n"
        + "   LL.CODICE                                       \n"
        + " FROM                                              \n"
        + "   QGIS_T_LISTA_LAVORAZIONE LL                     \n"
        + " WHERE                                             \n"
        + "   LL.ID_LISTA_LAVORAZIONE = :ID_LISTA_LAVORAZIONE \n";
    try
    {
      String codice = queryForNullableString(QUERY, mapSqlParameterSource);
      boolean abilitato = mapLivelli.get(codice)!=null;
      if (logger.isDebugEnabled())
      {
        if (abilitato)
        {
          logger.debug(THIS_METHOD + "L'utente con ID #" + utenteAbilitazioni.getIdUtenteLogin() + " è abilitato sulla lista con ID #" + idListaLavorazione);
        }
        else
        {
          logger
              .debug(THIS_METHOD + "L'utente con ID #" + utenteAbilitazioni.getIdUtenteLogin() + " NON è abilitato sulla lista con ID #" + idListaLavorazione);
        }
      }
      return abilitato;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idUtenteLogin: " + utenteAbilitazioni.getIdUtenteLogin() + ", idListaLavorazione = " + idListaLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
    
  }
  
  public boolean verificaAbilitazioneEventoLavorazione(UtenteAbilitazioni utenteAbilitazioni, long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + ".verificaAbilitazioneEventoLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idUtenteLogin: " + utenteAbilitazioni.getIdUtenteLogin()+ ", idEventoLavorazione: " + idEventoLavorazione);
    }
    
    Map<String, String> mapLivelli = new HashMap<String, String>();
    for (Abilitazione abilitazione : utenteAbilitazioni.getAbilitazioni())
    {
      if (abilitazione.getLivello().getCodiceListaSiti() != null)
      {
        String codiceListaSiti = abilitazione.getLivello().getCodiceListaSiti();
        mapLivelli.put(codiceListaSiti, codiceListaSiti);
      }
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
    final String QUERY = ""
        + " SELECT                                                                                    \n"
        + "   LL.CODICE                                                                               \n"
        + " FROM                                                                                      \n"
        + "   QGIS_T_LISTA_LAVORAZIONE   LL                                                           \n"
        + "   JOIN QGIS_T_EVENTO_LAVORAZIONE  EL ON EL.ID_LISTA_LAVORAZIONE = LL.ID_LISTA_LAVORAZIONE \n"
        + " WHERE                                                                                     \n"
        + "  EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                                        \n";
    try
    {
      String codice = queryForNullableString(QUERY, mapSqlParameterSource);
      boolean abilitato = mapLivelli.get(codice)!=null;
      if (logger.isDebugEnabled())
      {
        if (abilitato)
        {
          logger.debug(THIS_METHOD + "L'utente con ID #" + utenteAbilitazioni.getIdUtenteLogin() + " è abilitato sull'evento con ID #" + idEventoLavorazione);
        }
        else
        {
          logger
          .debug(THIS_METHOD + "L'utente con ID #" + utenteAbilitazioni.getIdUtenteLogin() + " NON è abilitato sull'evento con ID #" + idEventoLavorazione);
        }
      }
      return abilitato;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idUtenteLogin: " + utenteAbilitazioni.getIdUtenteLogin() + ", idEventoLavorazione = " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }


  public List<AppezzamentoDTO> leggiAppezzamentiScheda(long idEventoLavorazione, long idDichiarazioneConsistenza, String codNazionale, int foglio)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::leggiAppezzamentiScheda]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione+ ", idDichiarazioneConsistenza: " + idDichiarazioneConsistenza+",codNazionale: "+codNazionale+", foglio: "+foglio);
    }
    
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
    mapSqlParameterSource.addValue("ID_DICHIARAZIONE_CONSISTENZA", idDichiarazioneConsistenza, Types.NUMERIC);
    mapSqlParameterSource.addValue("COD_NAZIONALE", codNazionale, Types.VARCHAR);
    mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
    mapSqlParameterSource.addValue("DEFAULT_CRS_PIEMONTE", AgriApiConstants.DEFAULT_CRS_PIEMONTE, Types.VARCHAR);
    final String QUERY = ""
        + " SELECT                                                    \n"
        + " TREAT( (TREAT(VALUE(A) AS APPEZZAMENTO_REC).SUOLO_GIS) AS AABGSUOL_GRAF_REC).CODI_RILE CODI_RILE,            \n"
        + " TREAT( (TREAT(VALUE(A) AS APPEZZAMENTO_REC).SUOLO_GIS) AS AABGSUOL_GRAF_REC).CODI_PROD_RILE CODI_PROD_RILE,  \n"
        + " TREAT( (TREAT(VALUE(A) AS APPEZZAMENTO_REC).SUOLO_GIS) AS AABGSUOL_GRAF_REC).SUPE_SUOL_GRAF SUPE_APPE,       \n"
        + " TREAT( (TREAT(VALUE(A) AS APPEZZAMENTO_REC).SUOLO_GIS) AS AABGSUOL_GRAF_REC).CODI_EPSG CODI_EPSG,            \n"
        + " TREAT( (TREAT(VALUE(A) AS APPEZZAMENTO_REC).SUOLO_GIS) AS AABGSUOL_GRAF_REC).SHAPE_SUOL.GET_WKT() AS SHAPE,  \n"
        + " 'EPSG:' || NVL(PCK_SMRGAA_STRUMENTI_GRAFICI.getCodiEPSG(                                                     \n"
        + "       TREAT( (TREAT(VALUE(A) AS APPEZZAMENTO_REC).SUOLO_GIS) AS AABGSUOL_GRAF_REC).SHAPE_SUOL),              \n"
        + "       :DEFAULT_CRS_PIEMONTE) AS SRID,                                                                        \n"
        + " A.*                                                       \n"
        + " FROM                                                      \n"
        + "   TABLE ( PCK_SMRGAA_UTILITY_QGIS.LEGGIAPPEZZAMENTIQGIS(( \n"
        + "     SELECT                                                \n"
        + "       EL.EXT_ID_AZIENDA                                   \n"
        + "     FROM                                                  \n"
        + "       QGIS_T_EVENTO_LAVORAZIONE EL                        \n"
        + "     WHERE                                                 \n"
        + "       EL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE   \n"
        + "   ),                                                      \n"
        + "   :ID_DICHIARAZIONE_CONSISTENZA,                          \n"
        + "   :COD_NAZIONALE,                                         \n"
        + "   :FOGLIO) ) A                                            \n";

    try
    {
      return namedParameterJdbcTemplate.query(QUERY, mapSqlParameterSource,
          new ResultSetExtractorAppezzamento());
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD +
          " idEventoLavorazione: " + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public boolean checkControlloControcampo(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::checkControlloControcampo]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
    }
    final String QUERY =  " SELECT PCK_SMRGAA_UTILITY_QGIS.CONTROLLOCONTROCAMPO(:ID_EVENTO_LAVORAZIONE) RESULT FROM DUAL " ;

    try
    {
      MapSqlParameterSource mapParameterSource = new MapSqlParameterSource();
      mapParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione,Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          if (rs.next())
          {
            int result = rs.getInt("RESULT");
            return result  == 0;
          }
          return false;
        }
      });
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public List<ParticellaLavorazioneDTO> getParticelleLavorazioni(long idEventoLavorazione,
      String codiceNazionale, Long foglio)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getParticelleLavorazioni]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", codiceNazionale: "
          + codiceNazionale + ", foglio:" + foglio );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = 
        " SELECT                                                                                                                                                                                                                                           \n"
            + "      ID_PARTICELLA_LAVORAZIONE,                                                                                                                                                                                                                  \n"
            + "      ID_EVENTO_LAVORAZIONE,                                                                                                                                                                                                                      \n"
            + "      ID_VERSIONE_PARTICELLA,                                                                                                                                                                                                                     \n"
            + "      DESCRIZIONE_SOSPENSIONE,                                                                                                                                                                                                                    \n"
            + "      FLAG_SOSPENSIONE,                                                                                                                                                                                                                           \n"
            + "      NOTE_RICHIESTA,                                                                                                                                                                                                                             \n"
            + "      NOTE_LAVORAZIONE,                                                                                                                                                                                                                           \n"
            + "      FLAG_LAVORATO,                                                                                                                                                                                                                              \n"
            + "      EXT_ID_PARTICELLA AS ID_PARTICELLA,                                                                                                                                                                                                         \n"
            + "      EXT_COD_NAZIONALE AS CODICE_NAZIONALE,                                                                                                                                                                                                      \n"
            + "      FOGLIO,                                                                                                                                                                                                                                     \n"
            + "      PARTICELLA AS NUMERO_PARTICELLA,                                                                                                                                                                                                            \n"
            + "      SUBALTERNO,                                                                                                                                                                                                                                 \n"
            + "      IDENTIFICATIVO_PRATICA_ORIGINE AS ID_PRATICA_ORIGINE,                                                                                                                                                                                       \n"
            + "      DECODE (                                                                                                                                                                                                                                    \n"
            + "      (SELECT COUNT(*) FROM QGIS_T_CXF_PARTICELLA P WHERE P.FOGLIO= PL.FOGLIO AND P.EXT_COD_NAZIONALE = PL.EXT_COD_NAZIONALE AND  DATA_FINE_VALIDITA IS NULL   ),                                                                                 \n"
            + "      0, 'N', 'S'                                                                                                                                                                                                                                 \n"
            + "      ) AS FLAG_PRESENZA_CXF,                                                                                                                                                                                                                     \n"
            + "      DECODE(                                                                                                                                                                                                                                     \n"
            + "      (                                                                                                                                                                                                                                           \n"
            + "                                                                                                                                                                                                                                                  \n"
            + "      SELECT                                                                                                                                                                                                                                      \n"
            + "     count(*)                                                                                                                                                                                                                                     \n"
            + "  FROM                                                                                                                                                                                                                                            \n"
            + "    DB_R_ALLEGATO_POLIGONAZIONE AP,                                                                                                                                                                                                               \n"
            + "    SMRGAA_V_STORICO_PARTICELLA SP,                                                                                                                                                                                                               \n"
            + "    DB_ALLEGATO A,                                                                                                                                                                                                                                \n"
            + "    DB_TIPO_DOCUMENTO TD,                                                                                                                                                                                                                         \n"
            + "    DB_SITICOMU SC                                                                                                                                                                                                                                \n"
            + "  WHERE                                                                                                                                                                                                                                           \n"
            + "    ap.id_particella = SP.ID_PARTICELLA                                                                                                                                                                                                           \n"
            + "    AND sp.DATA_FINE_VALIDITA_PART IS NULL                                                                                                                                                                                                        \n"
            + "    AND AP.ID_ALLEGATO = A.ID_ALLEGATO                                                                                                                                                                                                            \n"
            + "    AND TD.ID_DOCUMENTO = AP.ID_TIPO_DOCUMENTO                                                                                                                                                                                                    \n"
            + "    and SC.istat_comune = SP.istat_comune                                                                                                                                                                                                         \n"
            + "    and nvl(SP.sezione,'-') = nvl(SC.id_sezc,'-')                                                                                                                                                                                                 \n"
            + "    and SP.foglio = :FOGLIO                                                                                                                                                                                                                       \n"
            + "    AND AP.EXT_ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                                                                                                                                                                                     \n"
            + "    AND SC.COD_NAZIONALE = :EXT_COD_NAZIONALE                                                                                                                                                                                                     \n"
            + "      )                                                                                                                                                                                                                                           \n"
            + "      , 0, 'N', 'S') AS FLAG_PRESENZA_ALLEGATI                                                                                                                                                                                                    \n"
            + "  FROM                                                                                                                                                                                                                                            \n"
            + "      QGIS_T_PARTICELLA_LAVORAZIONE PL                                                                                                                                                                                                            \n"
            + "  WHERE                                                                                                                                                                                                                                           \n"
            + "      PL.ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE                                                                                                                                                                                           \n"
            + "      AND FLAG_CESSATO <> 'S'                                                                                                                                                                                                                     \n"
            + "      and                                                                                                                                                                                                                                         \n"
            + "      (                                                                                                                                                                                                                                           \n"
            + "          ( PL.FOGLIO = :FOGLIO AND PL.EXT_COD_NAZIONALE = :EXT_COD_NAZIONALE )                                                                                                                                                                   \n"
            + "          OR                                                                                                                                                                                                                                      \n"
            + "          ( PL.ID_VERSIONE_PARTICELLA = (SELECT VP.ID_VERSIONE_PARTICELLA FROM QGIS_T_VERSIONE_PARTICELLA VP WHERE VP.ID_VERSIONE_PARTICELLA = PL.ID_VERSIONE_PARTICELLA AND VP.FOGLIO = :FOGLIO AND VP.EXT_COD_NAZIONALE = :EXT_COD_NAZIONALE) ) \n"
            + "      )                                                                                                                                                                                                                                           \n"
            + "  ORDER BY ID_PARTICELLA_LAVORAZIONE                                                                                                                                                                                                              \n"

        ;
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);

      return queryForList(QUERY, mapSqlParameterSource, ParticellaLavorazioneDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + ", codiceNazionale: "
          + codiceNazionale + ", foglio:" + foglio, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public List<CxfParticellaDTO> getCxfParticella(
      String codiceNazionale, long foglio, long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getCxfParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: "
          + codiceNazionale + ", foglio:" + foglio+ ", idEventoLavorazione:" + idEventoLavorazione );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = 
              " SELECT                                            \n"
            + "   ID_CXF_PARTICELLA,                              \n"
            + "   EXT_COD_NAZIONALE,                              \n"
            + "   FOGLIO,                                         \n"
            + "   PARTICELLA,                                     \n"
            + "   SUBALTERNO,                                     \n"
            + "   ALLEGATO,                                       \n"
            + "   SVILUPPO,                                       \n"
            + addSubselectSRID("SHAPE") +", \n"
            + "   SDO_UTIL.TO_WKTGEOMETRY(SHAPE) AS GEOMETRIA_WKT \n"
            + " FROM                                              \n"
            + "   QGIS_T_CXF_PARTICELLA                           \n"
            + " WHERE                                             \n"
            + "   FOGLIO = :FOGLIO                                \n"
            + "   AND EXT_COD_NAZIONALE = :COD_NAZIONALE          \n"
            + "   AND DATA_FINE_VALIDITA IS NULL                  \n"
            + " ORDER BY   ID_CXF_PARTICELLA                      \n";
    try
    {
      mapSqlParameterSource.addValue("COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      return queryForList(QUERY, mapSqlParameterSource, CxfParticellaDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio:" + foglio+ ", idEventoLavorazione:" + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public List<AllegatoParticellaDTO> getElencoAllegatiParticella(
      String codiceNazionale, long foglio, long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getElencoAllegatiParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: "
          + codiceNazionale + ", foglio:" + foglio + ", idEventoLavorazione:" + idEventoLavorazione);
    }
    
    //9614868 54  D205
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = 
        " SELECT                                                      \n"
            + "    AP.ID_ALLEGATO,                                          \n"
            + "    A.NOME_LOGICO,                                           \n"
            + "    A.NOME_FISICO,                                           \n"
            + "    TD.DESCRIZIONE                                           \n"
            + " FROM                                                        \n"
            + "   DB_R_ALLEGATO_POLIGONAZIONE AP,                           \n"
            + "   SMRGAA_V_STORICO_PARTICELLA SP,                           \n"
            + "   DB_ALLEGATO A,                                            \n"
            + "   DB_TIPO_DOCUMENTO TD,                                     \n"
            + "   DB_SITICOMU SC                                            \n"
            + " WHERE                                                       \n"
            + "   ap.id_particella = SP.ID_PARTICELLA                       \n"
            + "   AND sp.DATA_FINE_VALIDITA_PART IS NULL                    \n"
            + "   AND AP.ID_ALLEGATO = A.ID_ALLEGATO                        \n"
            + "   AND TD.ID_DOCUMENTO = AP.ID_TIPO_DOCUMENTO                \n"
            + "   and SC.istat_comune = SP.istat_comune                     \n"
            + "   and nvl(SP.sezione,'-') = nvl(SC.id_sezc,'-')             \n"
            + "   and SP.foglio = :FOGLIO                                   \n"
            + "   AND AP.EXT_ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE \n"
            + "   AND SC.COD_NAZIONALE = :COD_NAZIONALE                     \n";
    try
    {
      mapSqlParameterSource.addValue("COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);

      return queryForList(QUERY, mapSqlParameterSource, AllegatoParticellaDTO.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " codiceNazionale: " + codiceNazionale + ", foglio:" + foglio+ ", idEventoLavorazione:" + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }


  public Long getIdDocumentoIndex(long idEventoLavorazione, long idAllegato)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getIdDocumentoIndex]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD +  ", idAllegato:" + idAllegato + ", idEventoLavorazione:" + idEventoLavorazione);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String QUERY = 
        " SELECT                                                      \n"
            + "   A.EXT_ID_DOCUMENTO_INDEX                                  \n"
            + " FROM                                                        \n"
            + "   DB_R_ALLEGATO_POLIGONAZIONE AP,                           \n"
            + "   DB_ALLEGATO A                                             \n"
            + " WHERE                                                       \n"
            + "   AP.ID_ALLEGATO = A.ID_ALLEGATO                            \n"
            + "   AND AP.EXT_ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE \n"
            + "   AND A.ID_ALLEGATO = :ID_ALLEGATO                          \n";
    try
    {
      mapSqlParameterSource.addValue("ID_ALLEGATO", idAllegato, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      return namedParameterJdbcTemplate.queryForObject(QUERY.toString(), mapSqlParameterSource, Long.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD +  "idAllegato:" + idAllegato+ ", idEventoLavorazione:" + idEventoLavorazione, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }


  public void insertParticellaCessata(Long idEventoLavorazione, Long idVersioneParticella)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertParticellaCessata]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione
          + " ,idVersioneParticella: " + idVersioneParticella);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String UPDATE =     " INSERT INTO QGIS_T_PARTICELLA_LAVORAZIONE \n"
        + " (                                         \n"
        + " ID_PARTICELLA_LAVORAZIONE,                \n"
        + " ID_EVENTO_LAVORAZIONE,                    \n"
        + " ID_VERSIONE_PARTICELLA,                   \n"
        + " FLAG_SOSPENSIONE,                         \n"
        + " FLAG_LAVORATO,                         \n"
        + " FLAG_CESSATO                              \n"
        + " )                                         \n"
        + " VALUES(                                   \n"
        + " SEQ_QGIS_T_PARTICELLA_LAVORAZI.nextval,   \n"
        + " :ID_EVENTO_LAVORAZIONE,                   \n"
        + " :ID_VERSIONE_PARTICELLA,                  \n"
        + " 'N',                                      \n"
        + " 'S',                                       \n"
        + " 'S'                                       \n"
        + " )                                         \n";
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", idVersioneParticella, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione + " ,idVersioneParticella: " + idVersioneParticella ,e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public void insertParticellaLavorata(ParticellaLavorataDTO particellaLavorata)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertParticellaLavorata]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + particellaLavorata.getIdEventoLavorazione()
          + " ,idVersioneParticella: " + particellaLavorata.getIdFeature()+ "flagSospensione: "+particellaLavorata.getFlagSospensione()
          + ", descrizioneSospensione:"+ particellaLavorata.getDescrizioneSospensione()+ ", noteLavorazione:"+ particellaLavorata.getNoteLavorazione());

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String UPDATE =     " INSERT INTO QGIS_T_PARTICELLA_LAVORAZIONE \n"
        + " (                                         \n"
        + " ID_PARTICELLA_LAVORAZIONE,                \n"
        + " ID_EVENTO_LAVORAZIONE,                    \n"
        + " ID_VERSIONE_PARTICELLA,                   \n"
        + " FLAG_CESSATO,                              \n"
        + " NOTE_LAVORAZIONE,                              \n"
        + " FLAG_SOSPENSIONE,                              \n"
        + " FLAG_LAVORATO,                              \n"
        + " EXT_COD_NAZIONALE,                              \n"
        + " FOGLIO,                              \n"
        + " PARTICELLA,                              \n"
        + " SUBALTERNO,                              \n"
        + " DESCRIZIONE_SOSPENSIONE,                              \n"
        + " FLAG_PARTICELLA_CONDUZIONE                              \n"
        + " )                                         \n"
        + " VALUES(                                   \n"
        + " SEQ_QGIS_T_PARTICELLA_LAVORAZI.nextval,   \n"
        + " :ID_EVENTO_LAVORAZIONE,                   \n"
        + " :ID_VERSIONE_PARTICELLA,                  \n"
        + " 'N',                                       \n"
        + " :NOTE_LAVORAZIONE,                  \n"
        + " :FLAG_SOSPENSIONE,                  \n"
        + " 'S',                  \n"
        + " :EXT_COD_NAZIONALE,                              \n"
        + " :FOGLIO,                              \n"
        + " :PARTICELLA,                              \n"
        + " :SUBALTERNO,                              \n"
        + " :DESCRIZIONE_SOSPENSIONE,                  \n"
        + " :FLAG_PARTICELLA_CONDUZIONE                  \n"
        + " )                                         \n";
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", particellaLavorata.getIdEventoLavorazione(), Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", particellaLavorata.getIdFeature(), Types.NUMERIC);
      mapSqlParameterSource.addValue("NOTE_LAVORAZIONE", particellaLavorata.getNoteLavorazione(), Types.VARCHAR);
      mapSqlParameterSource.addValue("FLAG_SOSPENSIONE", (particellaLavorata.getFlagSospensione()!=null && particellaLavorata.getFlagSospensione() == 1L) ? "S" : "N", Types.VARCHAR);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", particellaLavorata.getCodiceNazionale(), Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", particellaLavorata.getFoglio(), Types.VARCHAR);
      mapSqlParameterSource.addValue("PARTICELLA", particellaLavorata.getNumeroParticella(), Types.VARCHAR);
      mapSqlParameterSource.addValue("SUBALTERNO", (particellaLavorata.getSubalterno()!=null && particellaLavorata.getSubalterno().trim().length()>0) ? particellaLavorata.getSubalterno() : " ", Types.VARCHAR);
      mapSqlParameterSource.addValue("FLAG_PARTICELLA_CONDUZIONE", particellaLavorata.getFlagConduzione(), Types.VARCHAR);
      mapSqlParameterSource.addValue("DESCRIZIONE_SOSPENSIONE", particellaLavorata.getDescrizioneSospensione(), Types.VARCHAR);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + particellaLavorata.getIdEventoLavorazione()
      + " ,idVersioneParticella: " + particellaLavorata.getIdFeature()+ "flagSospensione: "+particellaLavorata.getFlagSospensione()
      + ", descrizioneSospensione:"+ particellaLavorata.getDescrizioneSospensione()+ ", noteLavorazione:"+ particellaLavorata.getNoteLavorazione(), e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }


  public void updateVersioneParticellaCessata(long idVersioneParticella)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::updateVersioneParticellaCessata]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idVersioneParticella: " + idVersioneParticella);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final String UPDATE = " UPDATE QGIS_T_VERSIONE_PARTICELLA                     \n"
        + " SET DATA_FINE_VALIDITA = SYSDATE                            \n"
        + " WHERE ID_VERSIONE_PARTICELLA = :ID_VERSIONE_PARTICELLA                  \n";
    try
    {
      mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", idVersioneParticella, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idVersioneParticella: " + idVersioneParticella, e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public Long insertVersioneParticella(ParticellaLavorataDTO particella, Long idUtenteLogin)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::insertVersioneParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD +  "-  elenco variabili: "
      + ", AREA: " +  particella.getArea()
      + ", FOGLIO: " + particella.getFoglio()
      + ", EXT_COD_NAZIONALE: " + particella.getCodiceNazionale()
      + ", SUBALTERNO: " + particella.getSubalterno()
      + ", PARTICELLA: " + particella.getNumeroParticella()
      + ", EXT_ID_UTENTE_AGGIORNAMENTO: " + idUtenteLogin
      + ", SHAPE: " + particella.getGeometry()
      + ", DATA_INSERIMENTO: " + idUtenteLogin);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE = " DECLARE GEOM clob:=  '';    BEGIN   " +StringUtils.splitSQLStringWidthVar(particella.getGeometry().toString(), 20000, "GEOM")+" \n"
        + " INSERT INTO QGIS_T_VERSIONE_PARTICELLA \n"
        + " (                                      \n"
        + " ID_VERSIONE_PARTICELLA,                \n"
        + " EXT_ID_PARTICELLA,                \n"
        + " EXT_COD_NAZIONALE,                     \n"
        + " FOGLIO,                                \n"
        + " PARTICELLA,                            \n"
        + " SUBALTERNO,                            \n"
        + " DATA_INIZIO_VALIDITA,                  \n"
        + " DATA_FINE_VALIDITA,                    \n"
        + " AREA,                                  \n"
        + " SHAPE,                                 \n"
        + " DATA_AGGIORNAMENTO,                    \n"
        + " EXT_ID_UTENTE_AGGIORNAMENTO            \n"
        + " )                                      \n"
        + " values                                 \n"
        + " (                                      \n"
        + " :ID_VERSIONE_PARTICELLA,               \n"
        + "    (  SELECT SP.ID_PARTICELLA FROM SMRGAA_V_STORICO_PARTICELLA SP, DB_SITICOMU SC \n"
        + "           WHERE sp.DATA_FINE_VALIDITA_PART IS NULL               \n"
        + "                 and SC.istat_comune = SP.istat_comune            \n"
        + "                 and nvl(SP.sezione,'-') = nvl(SC.id_sezc,'-')    \n"
        + "                 and SP.foglio = :FOGLIO                          \n"
        + "                 AND SC.COD_NAZIONALE = :EXT_COD_NAZIONALE        \n"
        + "                 AND sp.particella = :PARTICELLA   and nvl(sp.subalterno, ' ') =  nvl(:SUBALTERNO, ' ')              \n"
        + "     ) ,                                                          \n"
        + " :EXT_COD_NAZIONALE,                    \n"
        + " :FOGLIO,                               \n"
        + " :PARTICELLA,                           \n"
        + " :SUBALTERNO,                           \n"
        + " SYSDATE,                               \n"
        + " NULL,                                  \n"
        + " :AREA,                                 \n"
        + " SDO_UTIL.FROM_WKTGEOMETRY(GEOM),       \n"
        + " SYSDATE,                               \n"
        + " :EXT_ID_UTENTE_AGGIORNAMENTO           \n"
        + " )                                      \n"
        + " ; END;                                 \n"
;


    try
    { 
      Long idVersioneParticella = getNextSequenceValue("SEQ_QGIS_T_VERSIONE_PARTICELLA");
      mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", idVersioneParticella, Types.NUMERIC);
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", particella.getCodiceNazionale(), Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", particella.getFoglio(), Types.NUMERIC);
      mapSqlParameterSource.addValue("PARTICELLA", particella.getNumeroParticella(), Types.VARCHAR);
      mapSqlParameterSource.addValue("SUBALTERNO", (particella.getSubalterno()!=null && particella.getSubalterno().trim().length()>0) ? particella.getSubalterno() : " " , Types.VARCHAR);
      mapSqlParameterSource.addValue("AREA", particella.getArea(), Types.DECIMAL);
      mapSqlParameterSource.addValue("EXT_ID_UTENTE_AGGIORNAMENTO", idUtenteLogin, Types.NUMERIC);

      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
      return idVersioneParticella;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + "elenco variabili: "
          + ", AREA: " +  particella.getArea()
          + ", FOGLIO: " + particella.getFoglio()
          + ", EXT_COD_NAZIONALE: " + particella.getCodiceNazionale()
          + ", SUBALTERNO: " + particella.getSubalterno()
          + ", PARTICELLA: " + particella.getNumeroParticella()
          + ", EXT_ID_UTENTE_AGGIORNAMENTO: " + idUtenteLogin
          + ", SHAPE: " + particella.getGeometry()
          + ", DATA_INSERIMENTO: " + idUtenteLogin
          , e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  

  public void sospendiParticellaLavorata(long idParticellaLavorazione, String descrizioneSospensione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::sospendiParticellaLavorata]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + "elenco variabili: "
          + ", idParticellaLavorazione: " +  idParticellaLavorazione);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE =     " UPDATE QGIS_T_PARTICELLA_LAVORAZIONE  SET FLAG_LAVORATO = 'S', FLAG_SOSPENSIONE = 'S', DESCRIZIONE_SOSPENSIONE= :DESCRIZIONE_SOSPENSIONE WHERE ID_PARTICELLA_LAVORAZIONE = :ID_PARTICELLA_LAVORAZIONE  ";
    try
    {
      mapSqlParameterSource.addValue("ID_PARTICELLA_LAVORAZIONE", idParticellaLavorazione, Types.NUMERIC);
      mapSqlParameterSource.addValue("DESCRIZIONE_SOSPENSIONE", descrizioneSospensione, Types.VARCHAR);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + "elenco variabili: "
          + ", idParticellaLavorazione: " + idParticellaLavorazione
          , e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public void rimuoviSospendiParticellaLavorata(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::rimuoviSospendiParticellaLavorata]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + "elenco variabili: "
          + ", idEventoLavorazione: " +  idEventoLavorazione);

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    String UPDATE =     " UPDATE QGIS_T_PARTICELLA_LAVORAZIONE  SET FLAG_SOSPENSIONE = 'N', DESCRIZIONE_SOSPENSIONE = ' ' WHERE ID_EVENTO_LAVORAZIONE = :ID_EVENTO_LAVORAZIONE  ";
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + "elenco variabili: "
          + ", idEventoLavorazione: " + idEventoLavorazione
          , e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public void updateEventoLavorazioneParticellaLavorazione(ParticellaLavorataDTO particellaLavorata)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::updateEventoLavorazioneParticellaLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: " + particellaLavorata.getCodiceNazionale()
      + ", foglio: " + particellaLavorata.getFoglio()
      + ", numeroParticella: " + particellaLavorata.getNumeroParticella()
      + ", subalterno: " + particellaLavorata.getSubalterno()
      + ", idVersioneParticella: " + particellaLavorata.getIdFeature()  
      );

    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
     String UPDATE =     
       " UPDATE QGIS_T_PARTICELLA_LAVORAZIONE  SET  FLAG_LAVORATO = 'S',  ID_VERSIONE_PARTICELLA = :ID_VERSIONE_PARTICELLA, FLAG_SOSPENSIONE = :FLAG_SOSPENSIONE, DESCRIZIONE_SOSPENSIONE = :DESCRIZIONE_SOSPENSIONE \n"
     + " WHERE EXT_COD_NAZIONALE = :EXT_COD_NAZIONALE                                             \n"
     + " AND FOGLIO = :FOGLIO                                                                     \n"
     + " AND PARTICELLA = :PARTICELLA                                                             \n";
     
     if(particellaLavorata.getSubalterno()!=null && particellaLavorata.getSubalterno().trim().length()>0)
       UPDATE += " AND SUBALTERNO = :SUBALTERNO                                                             \n";
     else
       UPDATE += " AND SUBALTERNO = ' '                                                             \n";

    try
    {
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", particellaLavorata.getCodiceNazionale(), Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", particellaLavorata.getFoglio(), Types.NUMERIC);
      mapSqlParameterSource.addValue("ID_VERSIONE_PARTICELLA", particellaLavorata.getIdFeature(), Types.NUMERIC);
      mapSqlParameterSource.addValue("PARTICELLA", particellaLavorata.getNumeroParticella(), Types.VARCHAR);
      mapSqlParameterSource.addValue("DESCRIZIONE_SOSPENSIONE", particellaLavorata.getDescrizioneSospensione(), Types.VARCHAR);
      mapSqlParameterSource.addValue("FLAG_SOSPENSIONE", (particellaLavorata.getFlagSospensione()!=null && particellaLavorata.getFlagSospensione() == 1L) ? "S" : "N", Types.VARCHAR);
      
      if(particellaLavorata.getSubalterno()!=null && particellaLavorata.getSubalterno().trim().length()>0)
        mapSqlParameterSource.addValue("SUBALTERNO",  particellaLavorata.getSubalterno()  , Types.VARCHAR);
      int row = namedParameterJdbcTemplate.update(UPDATE, mapSqlParameterSource);
      logger.debug("aggiornati #"+row+" record");
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " codiceNazionale: " + particellaLavorata.getCodiceNazionale()
          + ", foglio: " + particellaLavorata.getFoglio()
          + ", numeroParticella: " + particellaLavorata.getNumeroParticella()
          + ", subalterno: " + particellaLavorata.getSubalterno()
          + ", idVersioneParticella: " + particellaLavorata.getIdFeature()
          , e);

      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public boolean esisteParticelleLavorazione(ParticellaLavorataDTO particellaLavorata)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::esisteParticelleLavorazione]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: " + particellaLavorata.getCodiceNazionale()
          + ", foglio: " + particellaLavorata.getFoglio()
          + ", numeroParticella: " + particellaLavorata.getNumeroParticella()
          + ", subalterno: " + particellaLavorata.getSubalterno()          
          );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
              " SELECT COUNT(*) N_SUOLI                         \n"
            + " FROM QGIS_T_PARTICELLA_LAVORAZIONE              \n"
            + " WHERE EXT_COD_NAZIONALE = :EXT_COD_NAZIONALE    \n"
            + " AND FOGLIO = :FOGLIO                            \n"
            + " AND PARTICELLA = :PARTICELLA                    \n"
            + " AND SUBALTERNO = :SUBALTERNO                    \n"
        );

    try
    {
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", particellaLavorata.getCodiceNazionale(), Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", particellaLavorata.getFoglio(), Types.NUMERIC);
      mapSqlParameterSource.addValue("PARTICELLA", particellaLavorata.getNumeroParticella(), Types.VARCHAR);
      mapSqlParameterSource.addValue("SUBALTERNO", (particellaLavorata.getSubalterno()!=null && particellaLavorata.getSubalterno().trim().length()>0) ? particellaLavorata.getSubalterno() : " " , Types.VARCHAR);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Boolean>()
      {
        @Override
        public Boolean extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          while (rs.next())
          {
            int nSuoli = rs.getInt("N_SUOLI");
            if (nSuoli > 0)
              return true;
            else
              return false;
          }
          return false;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " codiceNazionale: " + particellaLavorata.getCodiceNazionale()
      + ", foglio: " + particellaLavorata.getFoglio()
      + ", numeroParticella: " + particellaLavorata.getNumeroParticella()
      + ", subalterno: " + particellaLavorata.getSubalterno() , e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  
  public Long getIdVersioneParticella(String foglio, String codiceNazionale,
      String numeroParticella, String subalterno, String annoCampagna)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getIdVersioneParticella]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " codiceNazionale: " + codiceNazionale
      + ", foglio: " + foglio
      + ", numeroParticella: " + numeroParticella
      + ", subalterno: " + subalterno          
      );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(

    "             SELECT                                                                                                                           \n"
  + "                 VP.ID_VERSIONE_PARTICELLA                                                                                                    \n"
  + "              FROM                                                                                                                            \n"
  + "                  Qgis_t_Versione_Particella VP , QGIS_T_REGISTRO_PARTICELLE RP                                                                                                  \n"
  + " WHERE VP.EXT_COD_NAZIONALE = :EXT_COD_NAZIONALE    \n"
  + " AND VP.FOGLIO = :FOGLIO                            \n"
  + " AND VP.PARTICELLA = :PARTICELLA                    \n"
  + " AND VP.SUBALTERNO = :SUBALTERNO    AND RP.CAMPAGNA = :ANNO_CAMPAGNA  AND RP.FOGLIO =  VP.FOGLIO  "
  + " AND VP.EXT_COD_NAZIONALE=RP.EXT_COD_NAZIONALE  AND VP.ID_VERSIONE_PARTICELLA = RP.ID_VERSIONE_PARTICELLA AND RP.DATA_FINE_VALIDITA IS NULL    \n");

    
    
    try
    {
      mapSqlParameterSource.addValue("EXT_COD_NAZIONALE", codiceNazionale, Types.VARCHAR);
      mapSqlParameterSource.addValue("FOGLIO", foglio, Types.NUMERIC);
      mapSqlParameterSource.addValue("PARTICELLA", numeroParticella, Types.VARCHAR);
      mapSqlParameterSource.addValue("ANNO_CAMPAGNA", annoCampagna, Types.VARCHAR);
      mapSqlParameterSource.addValue("SUBALTERNO", (subalterno!=null && subalterno.trim().length()>0) ? subalterno : " " , Types.VARCHAR);

      Long count = namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<Long>()
      {
        @Override
        public Long extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          while (rs.next())
          {
            return rs.getLong("ID_VERSIONE_PARTICELLA");
          }
          return null;
        }
      });
      
      logger.debug(THIS_METHOD + " #count: " + (count!=null ? count.longValue() : "NULL"));
      return count;
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.debug(THIS_METHOD + " codiceNazionale: " + codiceNazionale
          + ", foglio: " + foglio
          + ", numeroParticella: " + numeroParticella
          + ", subalterno: " + subalterno          
          );
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }

  public MainControlloDTO callAggiornaRegistroSuoli(String campagna, String codNazionale, long foglio, List<Long> idsSuoliCessati, List<Long> idsSuoliInseriti  )
  {
    String THIS_METHOD = "callAggiornaRegistroSuoli";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + ":: " + THIS_METHOD + "] BEGIN. campagna: "+campagna+", codNazionale: "+codNazionale+", foglio: "+foglio+", idsSuoliCessati: "+idsSuoliCessati.toString()+", idsSuoliInseriti: "+idsSuoliInseriti.toString());
    }
    try 
    {
      MapSqlParameterSource parameterSource = new MapSqlParameterSource();
      parameterSource.addValue("PCAMPAGNA", campagna,Types.NUMERIC);
      parameterSource.addValue("PEXTCODNAZIONALE", codNazionale,Types.VARCHAR);
      parameterSource.addValue("PFOGLIO", foglio,Types.NUMERIC);
      parameterSource.addValue("PARRAYCESSATO", new AbstractSqlTypeValue()
      {
        public Object createTypeValue(Connection con, int sqlType,
            String typeName) throws SQLException
        {
          Method method;
          try
          {
            method = con.getClass().getMethod("getUnderlyingConnection");
            con = (Connection) method.invoke(con, (Object[]) null);
          }
          catch (Exception e)
          {
            throw new SQLException(
                "Impossibile ottenere la connessione originale");
          }
          Long[] array = idsSuoliCessati.toArray(new Long[idsSuoliCessati.size()]);
          oracle.sql.ArrayDescriptor arrDesc = new oracle.sql.ArrayDescriptor(
              "ORA_MINING_NUMBER_NT", con);
          return new oracle.sql.ARRAY(arrDesc, con, array);
        }
      }, Types.ARRAY);
      
      parameterSource.addValue("PARRAYINSERITO", new AbstractSqlTypeValue()
      {
        public Object createTypeValue(Connection con, int sqlType,
            String typeName) throws SQLException
        {
          Method method;
          try
          {
            method = con.getClass().getMethod("getUnderlyingConnection");
            con = (Connection) method.invoke(con, (Object[]) null);
          }
          catch (Exception e)
          {
            throw new SQLException(
                "Impossibile ottenere la connessione originale");
          }
          Long[] array = idsSuoliInseriti.toArray(new Long[idsSuoliInseriti.size()]);
          oracle.sql.ArrayDescriptor arrDesc = new oracle.sql.ArrayDescriptor(
              "ORA_MINING_NUMBER_NT", con);
          return new oracle.sql.ARRAY(arrDesc, con, array);
        }
      }, Types.ARRAY);

      SimpleJdbcCall call = new SimpleJdbcCall(
          (DataSource) appContext.getBean("dataSource"))
              .withCatalogName("PCK_QGIS_LIBRERIA")
              .withProcedureName("AggiornaRegistroSuoli")
              .withoutProcedureColumnMetaDataAccess();

      call.addDeclaredParameter(new SqlParameter("PCAMPAGNA", java.sql.Types.NUMERIC));
      call.addDeclaredParameter(new SqlParameter("PEXTCODNAZIONALE", java.sql.Types.VARCHAR));
      call.addDeclaredParameter(new SqlParameter("PFOGLIO", java.sql.Types.NUMERIC));
      call.addDeclaredParameter(new SqlParameter("PARRAYCESSATO", Types.ARRAY));
      call.addDeclaredParameter(new SqlParameter("PARRAYINSERITO", Types.ARRAY));
      
      call.addDeclaredParameter(new SqlOutParameter("PCODERRORE", java.sql.Types.VARCHAR));
      call.addDeclaredParameter(new SqlOutParameter("PDESCERRORE", java.sql.Types.VARCHAR));

      
      Map<String, String> mapParametri = getParametri(new String[]
          { AgriApiConstants.PARAMETRI.TIMEOUT_ASYNC});

      String queryTimeout = mapParametri.get(AgriApiConstants.PARAMETRI.TIMEOUT_ASYNC);
      call.getJdbcTemplate().setQueryTimeout(Integer.parseInt(queryTimeout)); 
      
      Map<String, Object> results = call.execute(parameterSource);

      MainControlloDTO dto = new MainControlloDTO();
      dto.setRisultato(((String) results.get("PCODERRORE")));
      dto.setMessaggio(safeMessaggioPLSQL((String) results.get("PDESCERRORE")));
      return dto;

    }
    catch (Throwable e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + ":: " + THIS_METHOD + "] END.");
      }
    }
  }
  
  public MainControlloDTO callAggiornaRegistroSuoliCO(String campagna, String codNazionale, long foglio, List<Long> idsSuoliCessati, List<Long> idsSuoliInseriti  )
  {
    String THIS_METHOD = "callAggiornaRegistroSuoliCO";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + ":: " + THIS_METHOD + "] BEGIN. campagna: "+campagna+", codNazionale: "+codNazionale+", foglio: "+foglio+", idsSuoliCessati: "+idsSuoliCessati.toString()+", idsSuoliInseriti: "+idsSuoliInseriti.toString());
    }
    try 
    {
      MapSqlParameterSource parameterSource = new MapSqlParameterSource();
      parameterSource.addValue("PCAMPAGNA", campagna,Types.NUMERIC);
      parameterSource.addValue("PEXTCODNAZIONALE", codNazionale,Types.VARCHAR);
      parameterSource.addValue("PFOGLIO", foglio,Types.NUMERIC);
      parameterSource.addValue("PARRAYCESSATO", new AbstractSqlTypeValue()
      {
        public Object createTypeValue(Connection con, int sqlType,
            String typeName) throws SQLException
        {
          Method method;
          try
          {
            method = con.getClass().getMethod("getUnderlyingConnection");
            con = (Connection) method.invoke(con, (Object[]) null);
          }
          catch (Exception e)
          {
            throw new SQLException(
                "Impossibile ottenere la connessione originale");
          }
          Long[] array = idsSuoliCessati.toArray(new Long[idsSuoliCessati.size()]);
          oracle.sql.ArrayDescriptor arrDesc = new oracle.sql.ArrayDescriptor(
              "ORA_MINING_NUMBER_NT", con);
          return new oracle.sql.ARRAY(arrDesc, con, array);
        }
      }, Types.ARRAY);
      
      parameterSource.addValue("PARRAYINSERITO", new AbstractSqlTypeValue()
      {
        public Object createTypeValue(Connection con, int sqlType,
            String typeName) throws SQLException
        {
          Method method;
          try
          {
            method = con.getClass().getMethod("getUnderlyingConnection");
            con = (Connection) method.invoke(con, (Object[]) null);
          }
          catch (Exception e)
          {
            throw new SQLException(
                "Impossibile ottenere la connessione originale");
          }
          Long[] array = idsSuoliInseriti.toArray(new Long[idsSuoliInseriti.size()]);
          oracle.sql.ArrayDescriptor arrDesc = new oracle.sql.ArrayDescriptor(
              "ORA_MINING_NUMBER_NT", con);
          return new oracle.sql.ARRAY(arrDesc, con, array);
        }
      }, Types.ARRAY);

      SimpleJdbcCall call = new SimpleJdbcCall(
          (DataSource) appContext.getBean("dataSource"))
              .withCatalogName("PCK_QGIS_LIBRERIA")
              .withProcedureName("AggiornaRegistroCO")
              .withoutProcedureColumnMetaDataAccess();

      call.addDeclaredParameter(new SqlParameter("PCAMPAGNA", java.sql.Types.NUMERIC));
      call.addDeclaredParameter(new SqlParameter("PEXTCODNAZIONALE", java.sql.Types.VARCHAR));
      call.addDeclaredParameter(new SqlParameter("PFOGLIO", java.sql.Types.NUMERIC));
      call.addDeclaredParameter(new SqlParameter("PARRAYCESSATO", Types.ARRAY));
      call.addDeclaredParameter(new SqlParameter("PARRAYINSERITO", Types.ARRAY));
      
      call.addDeclaredParameter(new SqlOutParameter("PCODERRORE", java.sql.Types.VARCHAR));
      call.addDeclaredParameter(new SqlOutParameter("PDESCERRORE", java.sql.Types.VARCHAR));

      
      Map<String, String> mapParametri = getParametri(new String[]
          { AgriApiConstants.PARAMETRI.TIMEOUT_ASYNC});

      String queryTimeout = mapParametri.get(AgriApiConstants.PARAMETRI.TIMEOUT_ASYNC);
      call.getJdbcTemplate().setQueryTimeout(Integer.parseInt(queryTimeout)); 
      
      Map<String, Object> results = call.execute(parameterSource);

      MainControlloDTO dto = new MainControlloDTO();
      dto.setRisultato(((String) results.get("PCODERRORE")));
      dto.setMessaggio(safeMessaggioPLSQL((String) results.get("PDESCERRORE")));
      return dto;

    }
    catch (Throwable e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + ":: " + THIS_METHOD + "] END.");
      }
    }
  }
  
  public MainControlloDTO callAggiornaRegistroParticelle(String campagna, String codNazionale, long foglio, List<Long> idsParticelleCessate, List<Long> idsParticelleInserite  )
  {
    String THIS_METHOD = "AggiornaRegistroParticelle";
    if (logger.isDebugEnabled())
    {
      logger.debug("[" + THIS_CLASS + ":: " + THIS_METHOD + "] BEGIN. campagna: "+campagna+", codNazionale: "+codNazionale+", foglio: "+foglio+", idsParticelleCessate: "+idsParticelleCessate.toString()+", idsParticelleInserite: "+idsParticelleInserite.toString());
    }
    try 
    {
      MapSqlParameterSource parameterSource = new MapSqlParameterSource();
      parameterSource.addValue("PCAMPAGNA", campagna,Types.NUMERIC);
      parameterSource.addValue("PEXTCODNAZIONALE", codNazionale,Types.VARCHAR);
      parameterSource.addValue("PFOGLIO", foglio,Types.NUMERIC);
      
      parameterSource.addValue("PARRAYCESSATO", new AbstractSqlTypeValue()
      {
        public Object createTypeValue(Connection con, int sqlType,
            String typeName) throws SQLException
        {
          Method method;
          try
          {
            method = con.getClass().getMethod("getUnderlyingConnection");
            con = (Connection) method.invoke(con, (Object[]) null);
          }
          catch (Exception e)
          {
            throw new SQLException(
                "Impossibile ottenere la connessione originale");
          }
          Long[] array = idsParticelleCessate.toArray(new Long[idsParticelleCessate.size()]);
          oracle.sql.ArrayDescriptor arrDesc = new oracle.sql.ArrayDescriptor(
              "ORA_MINING_NUMBER_NT", con);
          return new oracle.sql.ARRAY(arrDesc, con, array);
        }
      }, Types.ARRAY);
      
      parameterSource.addValue("PARRAYINSERITO", new AbstractSqlTypeValue()
      {
        public Object createTypeValue(Connection con, int sqlType,
            String typeName) throws SQLException
        {
          Method method;
          try
          {
            method = con.getClass().getMethod("getUnderlyingConnection");
            con = (Connection) method.invoke(con, (Object[]) null);
          }
          catch (Exception e)
          {
            throw new SQLException(
                "Impossibile ottenere la connessione originale");
          }
          Long[] array = idsParticelleInserite.toArray(new Long[idsParticelleInserite.size()]);
          oracle.sql.ArrayDescriptor arrDesc = new oracle.sql.ArrayDescriptor(
              "ORA_MINING_NUMBER_NT", con);
          return new oracle.sql.ARRAY(arrDesc, con, array);
        }
      }, Types.ARRAY);
      

      SimpleJdbcCall call = new SimpleJdbcCall(
          (DataSource) appContext.getBean("dataSource"))
              .withCatalogName("PCK_QGIS_LIBRERIA")
              .withProcedureName("AggiornaRegistroParticelle")
              .withoutProcedureColumnMetaDataAccess();

      call.addDeclaredParameter(new SqlParameter("PCAMPAGNA", java.sql.Types.NUMERIC));
      call.addDeclaredParameter(new SqlParameter("PEXTCODNAZIONALE", java.sql.Types.VARCHAR));
      call.addDeclaredParameter(new SqlParameter("PFOGLIO", java.sql.Types.NUMERIC));
      call.addDeclaredParameter(new SqlParameter("PARRAYCESSATO",  Types.ARRAY));
      call.addDeclaredParameter(new SqlParameter("PARRAYINSERITO",  Types.ARRAY));
      
      call.addDeclaredParameter(new SqlOutParameter("PCODERRORE", java.sql.Types.VARCHAR));
      call.addDeclaredParameter(new SqlOutParameter("PDESCERRORE", java.sql.Types.VARCHAR));

      
      Map<String, String> mapParametri = getParametri(new String[]
          { AgriApiConstants.PARAMETRI.TIMEOUT_ASYNC});

      String queryTimeout = mapParametri.get(AgriApiConstants.PARAMETRI.TIMEOUT_ASYNC);
      call.getJdbcTemplate().setQueryTimeout(Integer.parseInt(queryTimeout)); 
      
      Map<String, Object> results = call.execute(parameterSource);

      MainControlloDTO dto = new MainControlloDTO();
      dto.setRisultato(((String) results.get("PCODERRORE")));
      dto.setMessaggio(safeMessaggioPLSQL((String) results.get("PDESCERRORE")));
      return dto;

    }
    catch (Throwable e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug("[" + THIS_CLASS + ":: " + THIS_METHOD + "] END.");
      }
    }
  }


  public String getDecodificaTipoSorgenteSuolo(String idTipoSorgenteSuolo)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::fixShape]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idTipoSorgenteSuolo: " + idTipoSorgenteSuolo);
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
        " SELECT  FLAG_SOPRALLUOGO FROM  QGIS_D_TIPO_SORGENTE_SUOLO WHERE ID_TIPO_SORGENTE_SUOLO = :ID_TIPO_SORGENTE_SUOLO  \n");
    try
    {
      mapSqlParameterSource.addValue("ID_TIPO_SORGENTE_SUOLO", idTipoSorgenteSuolo, Types.NUMERIC);
      return namedParameterJdbcTemplate.query(QUERY.toString(), mapSqlParameterSource, new ResultSetExtractor<String>()
      {
        @Override
        public String extractData(ResultSet rs) throws SQLException, DataAccessException
        {
          if (rs.next())
          {
            return rs.getString("FLAG_SOPRALLUOGO");
          }
          return null;
        }
      });
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
  public Long getIdTipoLista(long idEventoLavorazione)
  {
    String THIS_METHOD = "[" + THIS_CLASS + "::getIdTipoLista]";
    if (logger.isDebugEnabled())
    {
      logger.debug(THIS_METHOD + " BEGIN.");
      logger.debug(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione );
    }
    MapSqlParameterSource mapSqlParameterSource = new MapSqlParameterSource();
    final StringBuffer QUERY = new StringBuffer(
              " select  LL.ID_TIPO_LISTA                                        \n"
            + " from QGIS_T_LISTA_LAVORAZIONE LL , qgis_t_evento_lavorazione el \n"
            + " where                                                           \n"
            + " el.id_evento_lavorazione = :ID_EVENTO_LAVORAZIONE               \n"
            + " and el.id_lista_lavorazione = ll.id_lista_lavorazione           \n");
    try
    {
      mapSqlParameterSource.addValue("ID_EVENTO_LAVORAZIONE", idEventoLavorazione, Types.NUMERIC);
      return namedParameterJdbcTemplate.queryForObject(QUERY.toString(), mapSqlParameterSource, Long.class);
    }
    catch (RuntimeException e)
    {
      logger.error(THIS_METHOD + " Errore nel richiamo del metodo.", e);
      logger.error(THIS_METHOD + " idEventoLavorazione: " + idEventoLavorazione , e);
      throw e;
    }
    finally
    {
      if (logger.isDebugEnabled())
      {
        logger.debug(THIS_METHOD + " END.");
      }
    }
  }
  
}
