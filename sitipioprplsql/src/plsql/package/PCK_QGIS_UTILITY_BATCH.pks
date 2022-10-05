CREATE OR REPLACE PACKAGE PCK_QGIS_UTILITY_BATCH AS

  /************************************************************************
  RecProcBatch : Recupera l'id dell'ultimo processo batch

  Parametri input:  pNomeBatch - nome del batch
  Parametri output: pIdProc    - id processo batch
  *************************************************************************/

  FUNCTION RecProcBatch (pNomeBatch IN QGIS_D_NOME_BATCH.NOME_BATCH%TYPE) RETURN QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE ;

  /************************************************************************
  InsProcBatch : Inserisce i dati del processo batch in esecuzione

  Parametri input:  pNomeBatch - nome del batch
  Parametri output: pIdProc    - id processo batch
  *************************************************************************/

  FUNCTION InsProcBatch (pNomeBatch IN QGIS_D_NOME_BATCH.NOME_BATCH%TYPE) RETURN QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE ;

  /************************************************************************
  UpdFineProcBatch : Aggiorna la data fine elaborazione
                     del processo batch in esecuzione

  Parametri input:  pIdProc   - id processo batch
                    pEsito    - esito del processo batch OK o KO
  *************************************************************************/

  PROCEDURE UpdFineProcBatch (pIdProc IN QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE,
                              pEsito  IN QGIS_L_PROCESSO_BATCH.FLAG_ESITO%TYPE);

  /************************************************************************
  InsLogBatch : Popola la Tabella di Log

  Parametri input:  pId         - id identificativo batch
                    pCodErr     - codice errore
                    pMessErr    - messaggio errore
  ***************************************************************************/

  PROCEDURE InsLogBatch (pIdProc  IN QGIS_L_LOG_BATCH.ID_PROCESSO_BATCH%TYPE,
                         pCodErr  IN QGIS_L_LOG_BATCH.CODICE_ERRORE%TYPE,
                         pMessErr IN QGIS_L_LOG_BATCH.MESSAGGIO_ERRORE%TYPE);

  PROCEDURE Statistiche;
  
END PCK_QGIS_UTILITY_BATCH;

/