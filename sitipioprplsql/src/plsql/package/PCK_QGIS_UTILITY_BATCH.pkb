CREATE OR REPLACE PACKAGE BODY PCK_QGIS_UTILITY_BATCH AS

/*******************************************************************************
   NAME:       PCK_QGIS_UTILITY_BATCH
   PURPOSE:    Package di funzioni di utility batch

   REVISIONS:
   Ver        Date        Author           Description
   ---------  ----------  ---------------  ------------------------------------
   1.0.0      03/12/2012  Rocco Cambareri  Created this package.


  LAST MODIFY : 03/12/2012
  AUTHOR      : Rocco Cambareri
  DESCRIPTION : Creazione Package

  LAST MODIFY :
  AUTHOR      :
  DESCRIPTION :
*******************************************************************************/

/************************************************************************
  RecProcBatch : Recupera l'id dell'ultimo processo batch

  Parametri input:  pNomeBatch - nome del batch
  Parametri output: pIdProc    - id processo batch
  *************************************************************************/

FUNCTION RecProcBatch (pNomeBatch IN QGIS_D_NOME_BATCH.NOME_BATCH%TYPE) RETURN QGIS_L_PROCESSO_BATCH.id_processo_batch%TYPE is

  nIdProc  QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE;
BEGIN

  SELECT MAX(ID_PROCESSO_BATCH)
  INTO nIdProc  
  FROM QGIS_L_PROCESSO_BATCH
  WHERE ID_NOME_BATCH = (SELECT ID_NOME_BATCH FROM QGIS_D_NOME_BATCH WHERE NOME_BATCH = pNomeBatch);

  RETURN nIdProc;
  
END RecProcBatch;

/************************************************************************
  InsProcBatch : Inserisce i dati del processo batch in esecuzione

  Parametri input:  pNomeBatch - nome del batch
  Parametri output: pIdProc    - id processo batch
  *************************************************************************/

FUNCTION InsProcBatch (pNomeBatch IN QGIS_D_NOME_BATCH.NOME_BATCH%TYPE) RETURN QGIS_L_PROCESSO_BATCH.id_processo_batch%TYPE is

  PRAGMA   AUTONOMOUS_TRANSACTION;
  nIdProc  QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE;
BEGIN

  INSERT INTO QGIS_L_PROCESSO_BATCH
  (ID_PROCESSO_BATCH,
   ID_NOME_BATCH,
   DT_INIZIO_ELABORAZIONE)
  VALUES
  (SEQ_QGIS_L_PROCESSO_BATCH.NEXTVAL,
   (SELECT ID_NOME_BATCH FROM QGIS_D_NOME_BATCH WHERE NOME_BATCH = pNomeBatch),
   SYSDATE)
  RETURNING ID_PROCESSO_BATCH INTO nIdProc;

  COMMIT;

  RETURN nIdProc;
END InsProcBatch;

  /************************************************************************
  UpdFineProcBatch : Aggiorna la data fine elaborazione
                     del processo batch in esecuzione

  Parametri input:  pIdProc   - id processo batch
                    pEsito    - esito del processo batch OK o KO
  *************************************************************************/

PROCEDURE UpdFineProcBatch (pIdProc IN QGIS_L_PROCESSO_BATCH.id_processo_batch%TYPE,
                            pEsito  IN QGIS_L_PROCESSO_BATCH.flag_esito%TYPE) IS

  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  UPDATE QGIS_L_PROCESSO_BATCH
  SET    DT_FINE_ELABORAZIONE = SYSDATE,
         FLAG_ESITO           = pEsito
  WHERE  ID_PROCESSO_BATCH    = pIdProc;
  COMMIT;
END UpdFineProcBatch;

  /************************************************************************
  InsLogBatch : Popola la Tabella di Log

  Parametri input:  pId         - id identificativo batch
                    pCodErr     - codice errore
                    pMessErr    - messaggio errore
  ***************************************************************************/

PROCEDURE InsLogBatch (pIdProc  IN QGIS_L_LOG_BATCH.id_processo_batch%TYPE,
                       pCodErr  IN QGIS_L_LOG_BATCH.codice_errore%TYPE,
                       pMessErr IN QGIS_L_LOG_BATCH.messaggio_errore%TYPE) is

  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN

  INSERT INTO QGIS_L_LOG_BATCH
  (ID_LOG_BATCH, ID_PROCESSO_BATCH, DT_INSERIMENTO, CODICE_ERRORE, MESSAGGIO_ERRORE)
  VALUES
  (SEQ_QGIS_L_LOG_BATCH.NEXTVAL,pIdProc ,SYSDATE , pCodErr, pMessErr );

  COMMIT;

END InsLogBatch;

PROCEDURE Statistiche IS 
BEGIN
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'SITISUOLO_ATTIVE_PULITE');
  COMMIT;
END Statistiche;

END PCK_QGIS_UTILITY_BATCH;

/