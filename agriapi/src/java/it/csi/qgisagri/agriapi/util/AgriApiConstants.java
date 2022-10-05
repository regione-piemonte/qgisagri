package it.csi.qgisagri.agriapi.util;

public class AgriApiConstants
{
  public static final String EPSG_PREFIX = "EPSG:";
  public final static String DEFAULT_CRS_PIEMONTE = "3003";

  public final static int ID_PROCEDIMENTO = 67;
  
  public static class TABELLA_REGISTRO
  {
    public final static String SUOLI = "QGIS_T_REGISTRO_SUOLI";
    public final static String CO = "QGIS_T_REGISTRO_CO";
  }
  
  public static class PARAMETRI
  {
    public final static String TIMEOUT_ASYNC = "TIMEOUT_ASYNC";
    public final static String VERSIONE_PLUGIN = "VERSIONE_PLUGIN";
  }
  
  public static class PROCEDIMENTI
  {
    public static class ID
    {
      public final static int ID_PSRPRATICHE = 46;
      public final static int ID_PSR         = 2;
      public final static int ID_DEMETRAWEB  = 60;
      public final static int ID_RPU         = 12;
      public final static int ID_ANAGRAFE    = 7;
    }
  }  
  
  public static class TIPO_LAVORAZIONE
  {
    public final static long PARTICELLE    = 1;
    public final static long SUOLI         = 2;
  }
  
  public static class SESSION_TOKEN
  {
    public final static String DOCUMENTALE = "D";
    public final static String CONTRADDITORIO = "C";
  }
  
  public static class STATO_FOGLIO
  {
    public final static String LAVORATO = "L";
    public final static String NON_LAVORATO = "N";
    public final static String SOSPESO = "S";
  }
  
  public static class DATABASE
  {
    public final static String JNDINAME = "java:/agriapi/jdbc/agriapiDS";
  }
  
  public static final class URL
  {
    public static final class AGRIWELLWEB
    {
      public static final String BASE_URL_QGIS = "/agriwellweb/secure/qgisagri/accedi.do";
    }
    public static final class CONTRADDITORIO
    {
      public static final String BASE_URL_CONTROCAMPO = "/controcampo/secure/qgisagri/accedi.do";
    }
  }
  
  public static class ESITO
  {
    public static class STATO_SALVATAGGIO
    {
      public final static String SALVATAGGIO_IN_CORSO = "SC";
      public final static String SALVATAGGIO_ISTANZA_IN_CORSO = "SIC";
      public final static String SALVATAGGIO_ISTANZA_TERMINATO_CON_ERRORE = "SITE";
      public final static String SALVATAGGIO_TERMINATO = "ST";
    }
    
    public final static int POSITIVO = 0;
    public final static int POSITIVO_FOGLIO_ED_EVENTO_SBLOCCATO = 100;
    public final static int POSITIVO_FOGLIO_SBLOCCATO = 101;
    public final static int POSITIVO_FILTRI_ERRATI = 1000;
    public final static int POSITIVO_NO_RECORD = 1001;
    public final static int ERRORE = 1;
    public final static int NEGATIVO_EVENTO_NON_BLOCCATO = 200;
    public final static int NEGATIVO_EVENTO_BLOCCATO_DA_ALTRI = 201;
    public final static int EVENTO_NON_COMPLETATO = 202;
    public final static int NEGATIVO_FOGLIO_NON_BLOCCATO = 203;
    public final static int NEGATIVO_FOGLIO_BLOCCATO_DA_ALTRI = 204;
    public final static int NEGATIVO_FOGLIO_NON_COMPLETO = 205;


    public static class MESSAGGIO
    {
      public final static String MESSAGGIO_POSITIVO = null;
      public final static String MESSAGGIO_ERRORE = "Si è verificato un errore nell'accesso del servizio.";      
      public final static String MESSAGGIO_ERRORE_SALVA_SUOLI = "SI è verificare un errore durante l'aggiornamento dell'Istanza di Riesame di Anagrafe, se il problema persiste contattare l'assistenza indicando come codice di errore [RICHIAMO_SALVA_ISTANZA_KO]";  
      public final static String EVENTO_SBLOCCATO = "L'evento lavorazione è stato sbloccato.";
      public static final String EVENTO_NON_COMPLETATO = "Impossibile effettuare lo sblocco, non sono stati lavorati tutti i fogli.";
      public final static String EVENTO_NON_BLOCCATO = "L'evento lavorazione non è bloccato.";
      public final static String EVENTO_BLOCCATO = "L'evento è bloccato.";
      public final static String EVENTO_BLOCCATO_DA_ALTRI = "L'evento non è bloccato dall'utente connesso.";
      
      public final static String FOGLIO_ED_EVENTO_SBLOCCATO = "Il foglio e l'evento di lavorazione sono stati sbloccati";
      public final static String FOGLIO_SBLOCCATO = "Il foglio è stato sbloccato.";
      public final static String NEGATIVO_FOGLIO_NON_BLOCCATO = "Il foglio non è bloccato.";
      public final static String NEGATIVO_FOGLIO_BLOCCATO_DA_ALTRI = "Il foglio non è bloccato dall'utente connesso.";
      public final static String NEGATIVO_FOGLIO_NON_COMPLETO = "Non sono stati salvati tutti i suoli del foglio. Impossibile procedere.";
      public final static String NO_BLOCCO_FOGLIO_UTENTE = "Il foglio non è bloccato dall'utente connesso.";
      public final static String FOGLIO_BLOCCATO = "Il foglio è bloccato.";
      public static final String ACCESS_FORBIDDEN = "L'utente connesso non ha il ruolo configurato per poter accedere ai servizi.";
      public static final String SESSION_EXPIRED = "La sessione è scaduta. Rieffettuare l'accesso per connettersi ai servizi.";
      public static final String ACCESS_ERROR = "Si è verificato un errore durante l'accesso ai servizi di PAPUA.";
   
      public final static String SALVA_SUOLI_GENERICO = "Si è verificato un errore durante il salvataggio dei dati.";
      public final static String ID_SUOLO_RILEVATO_NON_TROVATO = "Non è stato trovato l'ID_SUOLO_RILEVATO richiesto";
    
    }
  }
  public static class ERRORS
  {
    public static final String ACCESS_FORBIDDEN = "L'utente connesso non ha il ruolo configurato per poter accedere ai servizi.";
    public static final String SESSION_EXPIRED = "La sessione è scaduta. Rieffettuare l'accesso per connettersi ai servizi.";
    public static final String ACCESS_ERROR = "Si è verificato un errore durante l'accesso ai servizi di PAPUA.";
 
  }
  
  public static final class LOGGING
  {
    public static final String LOGGER_NAME = "agriapi";
    public static final String LOGGER_GEOJSON_NAME = "agriapi_geojson";
  }
  
  
  public static class LAYER
  {
    public final static String SUOLI_LAVORATI = "SUOLI_LAVORATI";
    public final static String SUOLI_PARTICELLE = "SUOLI_PARTICELLE";
    public final static String SUOLI_CESSATI = "SUOLI_CESSATI";
    
    public final static String PARTICELLE_LAVORATE = "PARTICELLE_LAVORATE";
    public final static String PARTICELLE_SOSPESE = "PARTICELLE_SOSPESE";
    public final static String PARTICELLE_CESSATE = "PARTICELLE_CESSATE";
    
    public final static String CONFIGURAZIONE = "CONFIGURAZIONE";
  }
}
