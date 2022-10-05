CREATE OR REPLACE PACKAGE BODY PCK_SITI_SVECCHIA AS

function is_numeric(str in varchar2) return char is
begin
  for i in 1..length(str) loop
    if instr('0123456789', substr(str, i, 1)) = 0 then
      return 'N';
    end if;
  end loop;

  return 'Y';
end is_numeric;

PROCEDURE CreateIndex IS
  vErr  VARCHAR2(32627);
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio creazione indici');
  COMMIT;

  EXECUTE IMMEDIATE ('CREATE UNIQUE INDEX SITISUOLO_PK ON SITISUOLO (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_FINE_VAL, PROG_POLIGONO) TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE INDEX SITIPART_AU ON SITIPART (COD_NAZIONALE, TAVOLA, PARTICELLA, SUB, DATA_FINE_VAL) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE UNIQUE INDEX ELENCHI_HEADER_PK ON ELENCHI_HEADER (ID_ELENCO) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE INDEX RF_QUADRO_DIFF_IX1 ON RF_QUADRO_DIFF (NUM_ELENCO, GRID_ID) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE UNIQUE INDEX RF_QUADRO_PK1 ON RF_QUADRO (NUM_ELENCO, GRID_ID) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE UNIQUE INDEX RF_QUADRO_ALT_CPK ON RF_QUADRO_ALT (GRID_ID, NUM_ELENCO) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE INDEX IE1_RF_QUADRO_SUOLO ON RF_QUADRO_SUOLO (NUM_ELENCO) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE INDEX TMP_SITIPLAV_IL_LAST ON SITIPLAV (ID_LAV, LAST) TABLESPACE SITIPIOPR_IDX');

  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine creazione indici');
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job creazione indici',
                message    => 'ok');
  
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErr := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su CreateIndex = '||vErr||' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job creazione indici',
                  message    => 'ko');
END CreateIndex;


PROCEDURE TabSitiSuolo(pSiglaProv   SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE,
                       pNoPiemonte  VARCHAR2) IS
  
  CURSOR recSitisuolo is SELECT S.*
                         FROM   SITISUOLO S;
  
  TYPE Refcursor    IS REF CURSOR;
  
  rec    Refcursor;
  Suolo  recSitisuolo%ROWTYPE;
  nCont  SIMPLE_INTEGER := 0;
  vErr   VARCHAR2(32627);
  nAnno  QGIS_D_PARAMETRO_PLUGIN.VALORE_NUMERICO%TYPE;
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio insert SITISUOLO_ATTIVE. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte);
  COMMIT;
  
  SELECT VALORE_NUMERICO
  INTO   nAnno
  FROM   QGIS_D_PARAMETRO_PLUGIN
  WHERE  CODICE             = 'ANNO_IMP_SUOLO'
  AND    DATA_FINE_VALIDITA IS NOT NULL;
  
  -- ci sono dei record che non hanno corrispondeza su SMRGAA.DB_SITICOMU
  IF pSiglaProv IS NULL AND pNoPiemonte IS NULL THEN
    INSERT /*+ PARALLEL (SITISUOLO_ATTIVE)*/ INTO SITISUOLO_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, PROG_POLIGONO, DATA_FINE_VAL, ALLEGATO, SVILUPPO, CAMPAGNA, UTENTE, DATA_INIZIO_VAL, DATA_LAV,
     AREA_COLT, COD_COLTURA, SHAPE, ANNO_FOTO, MESE_FOTO, SE_ROW_ID, COD_VARIETA, TARA, ISTATP, COD_UTIL, STATO_COLT, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     GRUPPO, ID_PARTICELLA, IDFOTO, DXFOTO, DYFOTO, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, ID_CONTROLLO)
    SELECT /*+ PARALLEL (SITISUOLO)*/ COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, PROG_POLIGONO, DATA_FINE_VAL, ALLEGATO, SVILUPPO, CAMPAGNA, 
           UTENTE, DATA_INIZIO_VAL, DATA_LAV,AREA_COLT, COD_COLTURA, SHAPE, ANNO_FOTO, MESE_FOTO, SE_ROW_ID, COD_VARIETA, TARA, ISTATP, 
           COD_UTIL, STATO_COLT, STATO_PROP,UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, 
           TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO,GRUPPO, ID_PARTICELLA, IDFOTO, DXFOTO, DYFOTO, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID,
           ID_CONTROLLO
    FROM   SITISUOLO S
    WHERE  S.DATA_FINE_VAL      > SYSDATE
    AND    S.DATA_INIZIO_VAL    < S.DATA_FINE_VAL
    AND    S.DATA_AGGIORNAMENTO IS NOT NULL
    AND    S.DATA_INIZIO_VAL    > TO_DATE('01/01/1970','DD/MM/YYYY')
    AND    NOT EXISTS           (SELECT 'X'
                                 FROM   SMRGAA.DB_SITICOMU SC
                                 WHERE  S.COD_NAZIONALE = SC.COD_NAZIONALE);
                                 
    COMMIT;                                 
  ELSIF pSiglaProv IS NULL AND pNoPiemonte IS NOT NULL THEN                                     
    -- elaboro i record fuori piemonte
    INSERT /*+ PARALLEL (SITISUOLO_ATTIVE)*/ INTO SITISUOLO_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, PROG_POLIGONO, DATA_FINE_VAL, ALLEGATO, SVILUPPO, CAMPAGNA, UTENTE, DATA_INIZIO_VAL, DATA_LAV,
     AREA_COLT, COD_COLTURA, SHAPE, ANNO_FOTO, MESE_FOTO, SE_ROW_ID, COD_VARIETA, TARA, ISTATP, COD_UTIL, STATO_COLT, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     GRUPPO, ID_PARTICELLA, IDFOTO, DXFOTO, DYFOTO, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, ID_CONTROLLO)
    SELECT /*+ PARALLEL (SITISUOLO)*/ S.COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, PROG_POLIGONO, DATA_FINE_VAL, ALLEGATO, SVILUPPO, CAMPAGNA, 
           UTENTE, DATA_INIZIO_VAL, DATA_LAV,AREA_COLT, COD_COLTURA, SHAPE, ANNO_FOTO, MESE_FOTO, SE_ROW_ID, COD_VARIETA, TARA, S.ISTATP, 
           COD_UTIL, STATO_COLT, STATO_PROP,UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, 
           TAVOLA, FLAGCARICO, S.DATA_AGGIORNAMENTO,GRUPPO, ID_PARTICELLA, IDFOTO, DXFOTO, DYFOTO, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID,
           ID_CONTROLLO
    FROM   SITISUOLO S,SMRGAA.DB_SITICOMU SC
    WHERE  S.COD_NAZIONALE      = SC.COD_NAZIONALE
    AND    S.DATA_FINE_VAL      > SYSDATE
    AND    S.DATA_INIZIO_VAL    < S.DATA_FINE_VAL
    AND    S.DATA_AGGIORNAMENTO IS NOT NULL
    AND    S.DATA_INIZIO_VAL    > TO_DATE('01/01/1970','DD/MM/YYYY')
    AND    ISTATR               != '01';
    
    COMMIT;
  ELSIF pSiglaProv IS NOT NULL THEN                                     
    -- elaboro i record per provincia
    INSERT /*+ PARALLEL (SITISUOLO_ATTIVE)*/ INTO SITISUOLO_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, PROG_POLIGONO, DATA_FINE_VAL, ALLEGATO, SVILUPPO, CAMPAGNA, UTENTE, DATA_INIZIO_VAL, DATA_LAV,
     AREA_COLT, COD_COLTURA, SHAPE, ANNO_FOTO, MESE_FOTO, SE_ROW_ID, COD_VARIETA, TARA, ISTATP, COD_UTIL, STATO_COLT, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     GRUPPO, ID_PARTICELLA, IDFOTO, DXFOTO, DYFOTO, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, ID_CONTROLLO)
    SELECT /*+ PARALLEL (SITISUOLO)*/ S.COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, PROG_POLIGONO, DATA_FINE_VAL, ALLEGATO, SVILUPPO, CAMPAGNA, 
           UTENTE, DATA_INIZIO_VAL, DATA_LAV,AREA_COLT, COD_COLTURA, SHAPE, ANNO_FOTO, MESE_FOTO, SE_ROW_ID, COD_VARIETA, TARA, S.ISTATP, 
           COD_UTIL, STATO_COLT, STATO_PROP,UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, 
           TAVOLA, FLAGCARICO, S.DATA_AGGIORNAMENTO,GRUPPO, ID_PARTICELLA, IDFOTO, DXFOTO, DYFOTO, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID,
           ID_CONTROLLO
    FROM   SITISUOLO S,SMRGAA.DB_SITICOMU SC
    WHERE  S.COD_NAZIONALE      = SC.COD_NAZIONALE
    AND    S.DATA_FINE_VAL      > SYSDATE
    AND    S.DATA_INIZIO_VAL    < S.DATA_FINE_VAL
    AND    SIGLA_PROV           = pSiglaProv
    AND    S.DATA_INIZIO_VAL    > TO_DATE('01/01/1970','DD/MM/YYYY')
    AND    S.DATA_AGGIORNAMENTO IS NOT NULL;
    
    COMMIT;
  END IF;
  
  IF pSiglaProv IS NULL AND pNoPiemonte IS NULL THEN
    open rec for SELECT S.*
                 FROM   SITISUOLO S
                 WHERE  S.DATA_FINE_VAL      < SYSDATE
                 AND    S.DATA_INIZIO_VAL    < S.DATA_FINE_VAL
                 AND    S.DATA_AGGIORNAMENTO IS NOT NULL
                 AND    S.DATA_INIZIO_VAL    > TO_DATE('01/01/1970','DD/MM/YYYY')
                 AND    NOT EXISTS           (SELECT 'X'
                                              FROM   SMRGAA.DB_SITICOMU SC
                                              WHERE  S.COD_NAZIONALE = SC.COD_NAZIONALE);
  ELSIF pSiglaProv IS NULL AND pNoPiemonte IS NOT NULL THEN
    open rec for SELECT S.*
                 FROM   SITISUOLO S,SMRGAA.DB_SITICOMU SC
                 WHERE  S.DATA_FINE_VAL       < SYSDATE
                 AND    S.DATA_INIZIO_VAL     < S.DATA_FINE_VAL
                 AND    S.COD_NAZIONALE       = SC.COD_NAZIONALE
                 AND    S.DATA_AGGIORNAMENTO  IS NOT NULL
                 AND    S.DATA_INIZIO_VAL     > TO_DATE('01/01/1970','DD/MM/YYYY')
                 AND    ISTATR               != '01';
  ELSIF pSiglaProv IS NOT NULL THEN
    open rec for SELECT S.*
                 FROM   SITISUOLO S,SMRGAA.DB_SITICOMU SC
                 WHERE  S.DATA_FINE_VAL      < SYSDATE
                 AND    S.DATA_INIZIO_VAL    < S.DATA_FINE_VAL
                 AND    S.COD_NAZIONALE      = SC.COD_NAZIONALE
                 AND    S.DATA_AGGIORNAMENTO IS NOT NULL
                 AND    S.DATA_INIZIO_VAL    > TO_DATE('01/01/1970','DD/MM/YYYY')
                 AND    SIGLA_PROV           = pSiglaProv;
  END IF;
  
  LOOP
    FETCH rec INTO Suolo;
    EXIT WHEN rec%NOTFOUND;
              
      SELECT COUNT(*)
      INTO   nCont
      FROM   SITISUOLO_ATTIVE
      WHERE  COD_NAZIONALE = Suolo.COD_NAZIONALE
      AND    FOGLIO        = Suolo.FOGLIO
      AND    PARTICELLA    = Suolo.PARTICELLA
      AND    CAMPAGNA      = Suolo.CAMPAGNA
      AND    DATA_FINE_VAL = Suolo.DATA_FINE_VAL
      AND    PROG_POLIGONO = Suolo.PROG_POLIGONO;
      
      IF nCont = 0 THEN
        IF ((Suolo.CAMPAGNA >= nAnno) OR (Suolo.CAMPAGNA      < nAnno AND
                                          Suolo.DATA_FINE_VAL = get_data_gis_campagna(Suolo.COD_NAZIONALE ,Suolo.FOGLIO,
                                                                                      Suolo.PARTICELLA,Suolo.SUB,Suolo.CAMPAGNA))) THEN
        
          -- allora inserisco
          INSERT INTO SITISUOLO_ATTIVE
          (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, PROG_POLIGONO, DATA_FINE_VAL, ALLEGATO, SVILUPPO, CAMPAGNA, UTENTE, DATA_INIZIO_VAL, 
           DATA_LAV,AREA_COLT, COD_COLTURA, SHAPE, ANNO_FOTO, MESE_FOTO, SE_ROW_ID, COD_VARIETA, TARA, ISTATP, COD_UTIL, STATO_COLT, 
           STATO_PROP,UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, 
           DATA_AGGIORNAMENTO,GRUPPO, ID_PARTICELLA, IDFOTO, DXFOTO, DYFOTO, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, ID_CONTROLLO)
          VALUES
          (Suolo.COD_NAZIONALE, Suolo.FOGLIO, Suolo.PARTICELLA, Suolo.SUB, Suolo.PROG_POLIGONO, Suolo.DATA_FINE_VAL, Suolo.ALLEGATO, 
           Suolo.SVILUPPO, Suolo.CAMPAGNA,Suolo.UTENTE, Suolo.DATA_INIZIO_VAL, Suolo.DATA_LAV,Suolo.AREA_COLT, Suolo.COD_COLTURA, 
           Suolo.SHAPE, Suolo.ANNO_FOTO, Suolo.MESE_FOTO, Suolo.SE_ROW_ID, Suolo.COD_VARIETA, Suolo.TARA, Suolo.ISTATP,Suolo.COD_UTIL, 
           Suolo.STATO_COLT, Suolo.STATO_PROP,Suolo.UTENTE_FINE, Suolo.UTENTE_PROP, Suolo.UTENTE_PROP_FINE, Suolo.ID_TRASF, 
           Suolo.ID_TRASF_FINE, Suolo.SORGENTE, Suolo.VALI_PROD,Suolo.TAVOLA, Suolo.FLAGCARICO, Suolo.DATA_AGGIORNAMENTO,Suolo.GRUPPO, 
           Suolo.ID_PARTICELLA, Suolo.IDFOTO, Suolo.DXFOTO, Suolo.DYFOTO, Suolo.ALMOST_DEAD, Suolo.FLAG_PROVENIENZA, Suolo.SYNC_SV_ID,
           Suolo.ID_CONTROLLO);
         
          COMMIT;
        END IF;
      END IF;
  END LOOP;
                           
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine insert su SITISUOLO_ATTIVE. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte);
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job TabSitiSuolo. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte,
                message    => 'ok');
  
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErr := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su SITISUOLO_ATTIVE. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||
                                         pNoPiemonte||' = '||vErr||' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job TabSitiSuolo. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte,
                  message    => 'ko');
END TabSitiSuolo;

PROCEDURE IndSitisuolo IS
  nCont                SIMPLE_INTEGER := 0;
  dDataInizioVal       DATE;
  vErr                 VARCHAR2(32627);
  vCodNazionale        SITISUOLO_ATTIVE.COD_NAZIONALE%TYPE;
  nFoglio              SITISUOLO_ATTIVE.FOGLIO%TYPE;
  vParticella          SITISUOLO_ATTIVE.PARTICELLA%TYPE;
  vSub                 SITISUOLO_ATTIVE.SUB%TYPE;
  vDataFineValidita    VARCHAR2(30);
  vDataInizioValidita  VARCHAR2(30);
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio creazione indici su SITISUOLO_ATTIVE');
  COMMIT;
  
  EXECUTE IMMEDIATE ('CREATE UNIQUE INDEX SITISUOLO_ATTIVE_ID ON SITISUOLO_ATTIVE (SE_ROW_ID) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE UNIQUE INDEX SITISUOLO_ATTIVE_PK ON SITISUOLO_ATTIVE (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_FINE_VAL,PROG_POLIGONO) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE INDEX SITISUOLO_ATTIVE_PK_IDP ON SITISUOLO_ATTIVE (ID_PARTICELLA) PARALLEL TABLESPACE SITIPIOPR_IDX');
  
  DELETE USER_SDO_GEOM_METADATA
  WHERE  TABLE_NAME  = 'SITISUOLO_ATTIVE'
  AND    COLUMN_NAME = 'SHAPE';
  
  INSERT INTO USER_SDO_GEOM_METADATA
  (TABLE_NAME, COLUMN_NAME, DIMINFO, 
   SRID)
  VALUES
  ('SITISUOLO_ATTIVE','SHAPE',SDO_DIM_ARRAY(SDO_DIM_ELEMENT ('X', 1310000, 2820000, 100),SDO_DIM_ELEMENT ('Y', 3930000, 5220000, 100)),
   NULL);

  COMMIT;

  EXECUTE IMMEDIATE ('ALTER TABLE SITISUOLO_ATTIVE ADD (CONSTRAINT SITISUOLO_ATTIVE_PK PRIMARY KEY (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_FINE_VAL, PROG_POLIGONO) USING INDEX SITISUOLO_ATTIVE_PK ENABLE VALIDATE)');

  EXECUTE IMMEDIATE ('GRANT SELECT ON SITISUOLO_ATTIVE TO SMRGAA');
  
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'SITISUOLO_ATTIVE');
  
  FOR rec IN (SELECT ROWID ROW_ID,COD_NAZIONALE,FOGLIO,PARTICELLA,SUB,DATA_FINE_VAL,DATA_INIZIO_VAL
              FROM   SITISUOLO_ATTIVE
              WHERE  DATA_FINE_VAL < TO_DATE('31/12/9999','DD/MM/YYYY')) LOOP
    
    vCodNazionale       := rec.COD_NAZIONALE;
    nFoglio             := rec.FOGLIO;
    vParticella         := rec.PARTICELLA;
    vSub                := rec.SUB;
    vDataFineValidita   := TO_CHAR(rec.DATA_FINE_VAL,'DD/MM/YYYY HH24:MI:SS');
    vDataInizioValidita := TO_CHAR(rec.DATA_INIZIO_VAL,'DD/MM/YYYY HH24:MI:SS');
  
    SELECT COUNT(*)
    INTO   nCont
    FROM   SITISUOLO_ATTIVE
    WHERE  COD_NAZIONALE   = rec.COD_NAZIONALE
    AND    FOGLIO          = rec.FOGLIO   
    AND    PARTICELLA      = rec.PARTICELLA   
    AND    SUB             = rec.SUB
    AND    DATA_INIZIO_VAL = rec.DATA_FINE_VAL + INTERVAL '1' SECOND;
    
    IF nCont = 0 THEN
      SELECT MIN(DATA_INIZIO_VAL)
      INTO   dDataInizioVal
      FROM   SITISUOLO_ATTIVE
      WHERE  COD_NAZIONALE   = rec.COD_NAZIONALE
      AND    FOGLIO          = rec.FOGLIO   
      AND    PARTICELLA      = rec.PARTICELLA   
      AND    SUB             = rec.SUB
      AND    DATA_INIZIO_VAL > rec.DATA_INIZIO_VAL;
      
      IF dDataInizioVal IS NOT NULL THEN
        BEGIN
          UPDATE SITISUOLO_ATTIVE
          SET    DATA_FINE_VAL = dDataInizioVal - INTERVAL '1' SECOND
          WHERE  ROWID         = rec.ROW_ID;
        EXCEPTION
          WHEN OTHERS THEN
            vErr := SQLERRM;
            INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su creazione indici SITISUOLO_ATTIVE = '||vErr||' - RIGA = '||
                                                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE||' - Chiavi = '||vCodNazionale||'-'||nFoglio||'-'||
                                                vParticella||'-'||vSub||'-'||vDataFineValidita||'-'||vDataInizioValidita||'-'||
                                                TO_CHAR(dDataInizioVal,'DD/MM/YYYY HH24:MI:SS'));
            COMMIT;
        END;
      END IF;
    END IF;
  END LOOP;
  
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine creazione indici su SITISUOLO_ATTIVE');
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job Indici SITISUOLO_ATTIVE',
                message    => 'ok');
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErr := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su creazione indici SITISUOLO_ATTIVE = '||vErr||' - RIGA = '||
                                        DBMS_UTILITY.FORMAT_ERROR_BACKTRACE||' - Chiavi = '||vCodNazionale||'-'||nFoglio||'-'||
                                        vParticella||'-'||vSub||'-'||vDataFineValidita||'-'||vDataInizioValidita||'-'||
                                        TO_CHAR(dDataInizioVal,'DD/MM/YYYY HH24:MI:SS'));
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job Indici SITISUOLO_ATTIVE',
                  message    => 'ko');
END IndSitisuolo;

PROCEDURE TabSitiPartFuture(pSiglaProv  SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE,
                            pNoPiemonte  VARCHAR2) IS
  vErr  VARCHAR2(32627);
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio TabSitiPartFuture. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte);
  COMMIT;
  
  IF pSiglaProv IS NULL AND pNoPiemonte IS NULL THEN
    INSERT /*+ PARALLEL (SITIPART_ATTIVE)*/ INTO SITIPART_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_LAV, ALLEGATO, SVILUPPO, UTENTE, DATA_INIZIO_VAL, DATA_FINE_VAL, SHAPE, AREA_PART, 
     DELTA_X_FOTO, DELTA_Y_FOTO, CONTRASTO, LUMINOSITA, COD_DIGI, COD_EDIF, FLAG1, FLAG2, FLAG3, SE_ROW_ID, NOTE, ISTATP, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     ID_PARTICELLA, ID_CATA_PART, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, EXT_ID_PARTICELLA)
    (SELECT /*+ PARALLEL (SITIPART)*/ S.COD_NAZIONALE, S.FOGLIO, S.PARTICELLA, S.SUB, S.DATA_LAV, S.ALLEGATO, S.SVILUPPO, S.UTENTE, 
            S.DATA_INIZIO_VAL,S.DATA_FINE_VAL, S.SHAPE, S.AREA_PART,S.DELTA_X_FOTO, S.DELTA_Y_FOTO, S.CONTRASTO, S.LUMINOSITA, S.COD_DIGI, 
            S.COD_EDIF, S.FLAG1, S.FLAG2, S.FLAG3, S.SE_ROW_ID,S.NOTE, S.ISTATP, S.STATO_PROP,S.UTENTE_FINE, S.UTENTE_PROP, 
            S.UTENTE_PROP_FINE,S.ID_TRASF, S.ID_TRASF_FINE, SORGENTE, S.VALI_PROD, S.TAVOLA, S.FLAGCARICO,S.DATA_AGGIORNAMENTO,
            S.ID_PARTICELLA, S.ID_CATA_PART,S.ALMOST_DEAD, S.FLAG_PROVENIENZA, S.SYNC_SV_ID,
            (SELECT MAX(ID_PARTICELLA)
             FROM   SMRGAA.DB_PARTICELLA_CERTIFICATA SP
             WHERE  SP.FOGLIO              = S.FOGLIO
             AND    SP.PARTICELLA          = TO_NUMBER(LTRIM(S.PARTICELLA,'0'))
             AND    SP.DATA_FINE_VALIDITA  IS NULL
             AND    NVL(SP.SUBALTERNO,' ') = S.SUB
             AND    S.COD_NAZIONALE        IN (SELECT COD_NAZIONALE 
                                               FROM   SMRGAA.DB_SITICOMU 
                                               WHERE  ISTAT_COMUNE = SP.COMUNE
                                               AND    ((SP.SEZIONE IS NULL AND ID_SEZC IS NULL) OR 
                                                       (SP.SEZIONE IS NOT NULL AND UPPER(ID_SEZC) = UPPER(SP.SEZIONE))))) MAX_ID_PARTICELLA
     FROM   SITIPART S
     WHERE  S.DATA_FINE_VAL           > SYSDATE
     AND    IS_NUMERIC (S.PARTICELLA) = 'Y'
     AND    S.DATA_INIZIO_VAL         > TO_DATE('01/01/1970','DD/MM/YYYY')
     AND    NOT EXISTS                (SELECT 'X'
                                       FROM   SMRGAA.DB_SITICOMU SC
                                       WHERE  S.COD_NAZIONALE = SC.COD_NAZIONALE));
  ELSIF pSiglaProv IS NULL AND pNoPiemonte IS NOT NULL THEN
    INSERT /*+ PARALLEL (SITIPART_ATTIVE)*/ INTO SITIPART_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_LAV, ALLEGATO, SVILUPPO, UTENTE, DATA_INIZIO_VAL, DATA_FINE_VAL, SHAPE, AREA_PART, 
     DELTA_X_FOTO, DELTA_Y_FOTO, CONTRASTO, LUMINOSITA, COD_DIGI, COD_EDIF, FLAG1, FLAG2, FLAG3, SE_ROW_ID, NOTE, ISTATP, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     ID_PARTICELLA, ID_CATA_PART, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, EXT_ID_PARTICELLA)
    (SELECT /*+ PARALLEL (SITIPART)*/ S.COD_NAZIONALE, S.FOGLIO, S.PARTICELLA, S.SUB, S.DATA_LAV, S.ALLEGATO, S.SVILUPPO, S.UTENTE, 
            S.DATA_INIZIO_VAL,S.DATA_FINE_VAL, S.SHAPE, S.AREA_PART,S.DELTA_X_FOTO, S.DELTA_Y_FOTO, S.CONTRASTO, S.LUMINOSITA, S.COD_DIGI, 
            S.COD_EDIF, S.FLAG1, S.FLAG2, S.FLAG3, S.SE_ROW_ID,S.NOTE, S.ISTATP, S.STATO_PROP,S.UTENTE_FINE, S.UTENTE_PROP, 
            S.UTENTE_PROP_FINE,S.ID_TRASF, S.ID_TRASF_FINE, SORGENTE, S.VALI_PROD, S.TAVOLA, S.FLAGCARICO,S.DATA_AGGIORNAMENTO,
            S.ID_PARTICELLA, S.ID_CATA_PART,S.ALMOST_DEAD, S.FLAG_PROVENIENZA, S.SYNC_SV_ID,
            (SELECT MAX(ID_PARTICELLA)
             FROM   SMRGAA.DB_PARTICELLA_CERTIFICATA SP
             WHERE  SP.FOGLIO              = S.FOGLIO
             AND    SP.PARTICELLA          = TO_NUMBER(LTRIM(S.PARTICELLA,'0'))
             AND    SP.DATA_FINE_VALIDITA  IS NULL
             AND    NVL(SP.SUBALTERNO,' ') = S.SUB
             AND    S.COD_NAZIONALE        IN (SELECT COD_NAZIONALE 
                                               FROM   SMRGAA.DB_SITICOMU 
                                               WHERE  ISTAT_COMUNE = SP.COMUNE
                                               AND    ((SP.SEZIONE IS NULL AND ID_SEZC IS NULL) OR 
                                                       (SP.SEZIONE IS NOT NULL AND UPPER(ID_SEZC) = UPPER(SP.SEZIONE))))) MAX_ID_PARTICELLA
            FROM   SITIPART S,SMRGAA.DB_SITICOMU SC
            WHERE  S.DATA_FINE_VAL           > SYSDATE
            AND    IS_NUMERIC (S.PARTICELLA) = 'Y'
            AND    S.DATA_INIZIO_VAL         > TO_DATE('01/01/1970','DD/MM/YYYY')
            AND    S.COD_NAZIONALE           = SC.COD_NAZIONALE
            AND    ISTATR                   != '01');
  ELSIF pSiglaProv IS NOT NULL THEN
    INSERT /*+ PARALLEL (SITIPART_ATTIVE)*/ INTO SITIPART_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_LAV, ALLEGATO, SVILUPPO, UTENTE, DATA_INIZIO_VAL, DATA_FINE_VAL, SHAPE, AREA_PART, 
     DELTA_X_FOTO, DELTA_Y_FOTO, CONTRASTO, LUMINOSITA, COD_DIGI, COD_EDIF, FLAG1, FLAG2, FLAG3, SE_ROW_ID, NOTE, ISTATP, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     ID_PARTICELLA, ID_CATA_PART, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, EXT_ID_PARTICELLA)
    (SELECT /*+ PARALLEL (SITIPART)*/ S.COD_NAZIONALE, S.FOGLIO, S.PARTICELLA, S.SUB, S.DATA_LAV, S.ALLEGATO, S.SVILUPPO, S.UTENTE, 
            S.DATA_INIZIO_VAL,S.DATA_FINE_VAL, S.SHAPE, S.AREA_PART,S.DELTA_X_FOTO, S.DELTA_Y_FOTO, S.CONTRASTO, S.LUMINOSITA, S.COD_DIGI, 
            S.COD_EDIF, S.FLAG1, S.FLAG2, S.FLAG3, S.SE_ROW_ID,S.NOTE, S.ISTATP, S.STATO_PROP,S.UTENTE_FINE, S.UTENTE_PROP, 
            S.UTENTE_PROP_FINE,S.ID_TRASF, S.ID_TRASF_FINE, SORGENTE, S.VALI_PROD, S.TAVOLA, S.FLAGCARICO,S.DATA_AGGIORNAMENTO,
            S.ID_PARTICELLA, S.ID_CATA_PART,S.ALMOST_DEAD, S.FLAG_PROVENIENZA, S.SYNC_SV_ID,
            (SELECT MAX(ID_PARTICELLA)
             FROM   SMRGAA.DB_PARTICELLA_CERTIFICATA SP
             WHERE  SP.FOGLIO              = S.FOGLIO
             AND    SP.PARTICELLA          = TO_NUMBER(LTRIM(S.PARTICELLA,'0'))
             AND    SP.DATA_FINE_VALIDITA  IS NULL
             AND    NVL(SP.SUBALTERNO,' ') = S.SUB
             AND    S.COD_NAZIONALE        IN (SELECT COD_NAZIONALE 
                                               FROM   SMRGAA.DB_SITICOMU 
                                               WHERE  ISTAT_COMUNE = SP.COMUNE
                                               AND    ((SP.SEZIONE IS NULL AND ID_SEZC IS NULL) OR 
                                                       (SP.SEZIONE IS NOT NULL AND UPPER(ID_SEZC) = UPPER(SP.SEZIONE))))) MAX_ID_PARTICELLA
            FROM   SITIPART S,SMRGAA.DB_SITICOMU SC
            WHERE  S.DATA_FINE_VAL           > SYSDATE
            AND    IS_NUMERIC (S.PARTICELLA) = 'Y'
            AND    S.COD_NAZIONALE           = SC.COD_NAZIONALE
            AND    S.DATA_INIZIO_VAL         > TO_DATE('01/01/1970','DD/MM/YYYY')
            AND    SIGLA_PROV                = pSiglaProv);
  END IF;
   
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine TabSitiPartFuture. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte);
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job TabSitiPartFuture. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte,
                message    => 'ok');
                
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErr := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su TabSitiPartFuture. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||
                                         pNoPiemonte||' = '||vErr||' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job TabSitiPartFuture. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte,
                  message    => 'ko');                
END TabSitiPartFuture;

PROCEDURE TabSitiPart(pSiglaProv  SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE,
                      pNoPiemonte  VARCHAR2) IS
                      
  vErr  VARCHAR2(32627);
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio SITIPART_ATTIVE. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte);
  COMMIT;
  
  IF pSiglaProv IS NULL AND pNoPiemonte IS NULL THEN
    INSERT /*+ PARALLEL (SITIPART_ATTIVE)*/ INTO SITIPART_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_LAV, ALLEGATO, SVILUPPO, UTENTE, DATA_INIZIO_VAL, DATA_FINE_VAL, SHAPE, AREA_PART, 
     DELTA_X_FOTO,DELTA_Y_FOTO, CONTRASTO, LUMINOSITA, COD_DIGI, COD_EDIF, FLAG1, FLAG2, FLAG3, SE_ROW_ID, NOTE, ISTATP, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP,UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     ID_PARTICELLA, ID_CATA_PART,ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID,EXT_ID_PARTICELLA)
    (SELECT /*+ PARALLEL (SITIPART)*/ S.*,
            (SELECT MAX(ID_PARTICELLA)
             FROM   SMRGAA.DB_PARTICELLA_CERTIFICATA SP
             WHERE  SP.FOGLIO              = S.FOGLIO
             AND    SP.PARTICELLA          = TO_NUMBER(LTRIM(S.PARTICELLA,'0'))
             AND    SP.DATA_FINE_VALIDITA  IS NULL
             AND    NVL(SP.SUBALTERNO,' ') = S.SUB
             AND    S.COD_NAZIONALE        IN (SELECT COD_NAZIONALE 
                                               FROM   SMRGAA.DB_SITICOMU 
                                               WHERE  ISTAT_COMUNE = SP.COMUNE
                                               AND    ((SP.SEZIONE IS NULL AND ID_SEZC IS NULL) OR 
                                                       (SP.SEZIONE IS NOT NULL AND UPPER(ID_SEZC) = UPPER(SP.SEZIONE))))) MAX_ID_PARTICELLA
     FROM   SITIPART S
     WHERE  S.DATA_FINE_VAL           < SYSDATE
     AND    IS_NUMERIC (S.PARTICELLA) = 'Y'
     AND    S.DATA_INIZIO_VAL         > TO_DATE('01/01/1970','DD/MM/YYYY')
     AND    NOT EXISTS                (SELECT 'X'
                                       FROM   SMRGAA.DB_SITICOMU SC
                                       WHERE  S.COD_NAZIONALE = SC.COD_NAZIONALE)
     AND    EXISTS                    (SELECT 'X'
                                       FROM   SITISUOLO_ATTIVE SA
                                       WHERE  SA.COD_NAZIONALE     = S.COD_NAZIONALE
                                       AND    SA.FOGLIO            = S.FOGLIO
                                       AND    SA.PARTICELLA        = S.PARTICELLA
                                       AND    SA.SUB               = S.SUB
                                       AND    SA.DATA_FINE_VAL     < SYSDATE
                                       AND    ((SA.DATA_INIZIO_VAL BETWEEN S.DATA_INIZIO_VAL AND S.DATA_FINE_VAL) OR 
                                               (SA.DATA_FINE_VAL   BETWEEN S.DATA_INIZIO_VAL AND S.DATA_FINE_VAL))));
  ELSIF pSiglaProv IS NULL AND pNoPiemonte IS NOT NULL THEN         
    INSERT /*+ PARALLEL (SITIPART_ATTIVE)*/ INTO SITIPART_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_LAV, ALLEGATO, SVILUPPO, UTENTE, DATA_INIZIO_VAL, DATA_FINE_VAL, SHAPE, AREA_PART, 
     DELTA_X_FOTO,DELTA_Y_FOTO, CONTRASTO, LUMINOSITA, COD_DIGI, COD_EDIF, FLAG1, FLAG2, FLAG3, SE_ROW_ID, NOTE, ISTATP, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP,UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     ID_PARTICELLA, ID_CATA_PART,ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID,EXT_ID_PARTICELLA)
    (SELECT /*+ PARALLEL (SITIPART)*/ S.*,
            (SELECT MAX(ID_PARTICELLA)
             FROM   SMRGAA.DB_PARTICELLA_CERTIFICATA SP
             WHERE  SP.FOGLIO              = S.FOGLIO
             AND    SP.PARTICELLA          = TO_NUMBER(LTRIM(S.PARTICELLA,'0'))
             AND    SP.DATA_FINE_VALIDITA  IS NULL
             AND    NVL(SP.SUBALTERNO,' ') = S.SUB
             AND    S.COD_NAZIONALE        IN (SELECT COD_NAZIONALE 
                                               FROM   SMRGAA.DB_SITICOMU 
                                               WHERE  ISTAT_COMUNE = SP.COMUNE
                                               AND    ((SP.SEZIONE IS NULL AND ID_SEZC IS NULL) OR 
                                                       (SP.SEZIONE IS NOT NULL AND UPPER(ID_SEZC) = UPPER(SP.SEZIONE))))) MAX_ID_PARTICELLA
     FROM   SITIPART S,SMRGAA.DB_SITICOMU SC
     WHERE  S.DATA_FINE_VAL           < SYSDATE
     AND    IS_NUMERIC (S.PARTICELLA) = 'Y'
     AND    S.COD_NAZIONALE           = SC.COD_NAZIONALE
     AND    ISTATR                   != '01'
     AND    S.DATA_INIZIO_VAL         > TO_DATE('01/01/1970','DD/MM/YYYY')
     AND    EXISTS                    (SELECT 'X'
                                       FROM   SITISUOLO_ATTIVE SA
                                       WHERE  SA.COD_NAZIONALE     = S.COD_NAZIONALE
                                       AND    SA.FOGLIO            = S.FOGLIO
                                       AND    SA.PARTICELLA        = S.PARTICELLA
                                       AND    SA.SUB               = S.SUB
                                       AND    SA.DATA_FINE_VAL     < SYSDATE
                                       AND    ((SA.DATA_INIZIO_VAL BETWEEN S.DATA_INIZIO_VAL AND S.DATA_FINE_VAL) OR 
                                               (SA.DATA_FINE_VAL   BETWEEN S.DATA_INIZIO_VAL AND S.DATA_FINE_VAL))));
  ELSIF pSiglaProv IS NOT NULL THEN     
    INSERT /*+ PARALLEL (SITIPART_ATTIVE)*/ INTO SITIPART_ATTIVE
    (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_LAV, ALLEGATO, SVILUPPO, UTENTE, DATA_INIZIO_VAL, DATA_FINE_VAL, SHAPE, AREA_PART, 
     DELTA_X_FOTO,DELTA_Y_FOTO, CONTRASTO, LUMINOSITA, COD_DIGI, COD_EDIF, FLAG1, FLAG2, FLAG3, SE_ROW_ID, NOTE, ISTATP, STATO_PROP, 
     UTENTE_FINE, UTENTE_PROP,UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
     ID_PARTICELLA, ID_CATA_PART,ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID,EXT_ID_PARTICELLA)
    (SELECT /*+ PARALLEL (SITIPART)*/ S.*,
            (SELECT MAX(ID_PARTICELLA)
             FROM   SMRGAA.DB_PARTICELLA_CERTIFICATA SP
             WHERE  SP.FOGLIO              = S.FOGLIO
             AND    SP.PARTICELLA          = TO_NUMBER(LTRIM(S.PARTICELLA,'0'))
             AND    SP.DATA_FINE_VALIDITA  IS NULL
             AND    NVL(SP.SUBALTERNO,' ') = S.SUB
             AND    S.COD_NAZIONALE        IN (SELECT COD_NAZIONALE 
                                               FROM   SMRGAA.DB_SITICOMU 
                                               WHERE  ISTAT_COMUNE = SP.COMUNE
                                               AND    ((SP.SEZIONE IS NULL AND ID_SEZC IS NULL) OR 
                                                       (SP.SEZIONE IS NOT NULL AND UPPER(ID_SEZC) = UPPER(SP.SEZIONE))))) MAX_ID_PARTICELLA
     FROM   SITIPART S,SMRGAA.DB_SITICOMU SC
     WHERE  S.DATA_FINE_VAL           < SYSDATE
     AND    IS_NUMERIC (S.PARTICELLA) = 'Y'
     AND    S.COD_NAZIONALE           = SC.COD_NAZIONALE
     AND    SIGLA_PROV                = pSiglaProv
     AND    S.DATA_INIZIO_VAL         > TO_DATE('01/01/1970','DD/MM/YYYY')
     AND    EXISTS                    (SELECT 'X'
                                       FROM   SITISUOLO_ATTIVE SA
                                       WHERE  SA.COD_NAZIONALE     = S.COD_NAZIONALE
                                       AND    SA.FOGLIO            = S.FOGLIO
                                       AND    SA.PARTICELLA        = S.PARTICELLA
                                       AND    SA.SUB               = S.SUB
                                       AND    SA.DATA_FINE_VAL     < SYSDATE
                                       AND    ((SA.DATA_INIZIO_VAL BETWEEN S.DATA_INIZIO_VAL AND S.DATA_FINE_VAL) OR 
                                               (SA.DATA_FINE_VAL   BETWEEN S.DATA_INIZIO_VAL AND S.DATA_FINE_VAL))));
  END IF;
  
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine SITIPART_ATTIVE. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte);
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job TabSitiPart. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte,
                message    => 'ok');
  
EXCEPTION
  WHEN OTHERS THEN
    vErr := SQLERRM;
    ROLLBACK;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su SITIPART_ATTIVE. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||
                                         pNoPiemonte||' = '||vErr||' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job TabSitiPart. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte,
                  message    => 'ko');
END TabSitiPart;

PROCEDURE IndSitiPart IS

  nCont                SIMPLE_INTEGER := 0;
  dDataInizioVal       DATE;
  vErr                 VARCHAR2(32627);
  vCodNazionale        SITIPART_ATTIVE.COD_NAZIONALE%TYPE;
  nFoglio              SITIPART_ATTIVE.FOGLIO%TYPE;
  vParticella          SITIPART_ATTIVE.PARTICELLA%TYPE;
  vSub                 SITIPART_ATTIVE.SUB%TYPE;
  vDataFineValidita    VARCHAR2(30);
  vDataInizioValidita  VARCHAR2(30);
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio creazione indici su SITIPART_ATTIVE');
  COMMIT;
  
  EXECUTE IMMEDIATE ('CREATE INDEX SITIPART_ATTIVE_AU ON SITIPART_ATTIVE (COD_NAZIONALE, TAVOLA, PARTICELLA, SUB, DATA_FINE_VAL) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE UNIQUE INDEX SITIPART_ATTIVE_ID ON SITIPART_ATTIVE (SE_ROW_ID) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE UNIQUE INDEX SITIPART_ATTIVE_PK ON SITIPART_ATTIVE (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_FINE_VAL) PARALLEL TABLESPACE SITIPIOPR_IDX');

  EXECUTE IMMEDIATE ('CREATE INDEX SITIPART_ATTIVE_PK_IDP ON SITIPART_ATTIVE (ID_PARTICELLA) PARALLEL TABLESPACE SITIPIOPR_IDX');
  
  DELETE USER_SDO_GEOM_METADATA
  WHERE  TABLE_NAME  = 'SITIPART_ATTIVE'
  AND    COLUMN_NAME = 'SHAPE';
  
  INSERT INTO USER_SDO_GEOM_METADATA
  (TABLE_NAME, COLUMN_NAME, DIMINFO, 
   SRID)
  VALUES
  ('SITIPART_ATTIVE','SHAPE',SDO_DIM_ARRAY(SDO_DIM_ELEMENT ('X', 1310000, 2820000, 100),SDO_DIM_ELEMENT ('Y', 3930000, 5220000, 100)),
   NULL);

  COMMIT;

  --EXECUTE IMMEDIATE ('CREATE INDEX SITIPART_ATTIVE_SHAPE_SDX ON SITIPART_ATTIVE (SHAPE) INDEXTYPE IS MDSYS.SPATIAL_INDEX PARAMETERS(''tablespace=SITIPIOPR_IDX'')');

  EXECUTE IMMEDIATE ('ALTER TABLE SITIPART_ATTIVE ADD (CONSTRAINT SITIPART_ATTIVE_PK PRIMARY KEY(COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_FINE_VAL) USING INDEX SITIPART_ATTIVE_PK ENABLE VALIDATE)');

  EXECUTE IMMEDIATE ('GRANT SELECT ON SITIPART_ATTIVE TO SMRGAA');
  
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'SITIPART_ATTIVE');
  
  FOR rec IN (SELECT ROWID ROW_ID,COD_NAZIONALE,FOGLIO,PARTICELLA,SUB,DATA_FINE_VAL,DATA_INIZIO_VAL
              FROM   SITIPART_ATTIVE
              WHERE  DATA_FINE_VAL < TO_DATE('31/12/9999','DD/MM/YYYY')) LOOP
  
    vCodNazionale       := rec.COD_NAZIONALE;
    nFoglio             := rec.FOGLIO;
    vParticella         := rec.PARTICELLA;
    vSub                := rec.SUB;
    vDataFineValidita   := TO_CHAR(rec.DATA_FINE_VAL,'DD/MM/YYYY HH24:MI:SS');
    vDataInizioValidita := TO_CHAR(rec.DATA_INIZIO_VAL,'DD/MM/YYYY HH24:MI:SS');
  
    SELECT COUNT(*)
    INTO   nCont
    FROM   SITIPART_ATTIVE
    WHERE  COD_NAZIONALE   = rec.COD_NAZIONALE
    AND    FOGLIO          = rec.FOGLIO   
    AND    PARTICELLA      = rec.PARTICELLA   
    AND    SUB             = rec.SUB
    AND    DATA_INIZIO_VAL = rec.DATA_FINE_VAL + INTERVAL '1' SECOND;
    
    IF nCont = 0 THEN
      SELECT MIN(DATA_INIZIO_VAL)
      INTO   dDataInizioVal
      FROM   SITIPART_ATTIVE
      WHERE  COD_NAZIONALE   = rec.COD_NAZIONALE
      AND    FOGLIO          = rec.FOGLIO   
      AND    PARTICELLA      = rec.PARTICELLA   
      AND    SUB             = rec.SUB
      AND    DATA_INIZIO_VAL > rec.DATA_INIZIO_VAL;
      
      IF dDataInizioVal IS NOT NULL THEN
        BEGIN
          UPDATE SITIPART_ATTIVE
          SET    DATA_FINE_VAL = dDataInizioVal - INTERVAL '1' SECOND
          WHERE  ROWID         = rec.ROW_ID;
        EXCEPTION
          WHEN OTHERS THEN
            vErr := SQLERRM;
            INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su creazione indici SITIPART_ATTIVE = '||vErr||' - RIGA = '||
                                                DBMS_UTILITY.FORMAT_ERROR_BACKTRACE||' - Chiavi = '||vCodNazionale||'-'||nFoglio||'-'||
                                                vParticella||'-'||vSub||'-'||vDataFineValidita||'-'||vDataInizioValidita||'-'||
                                                TO_CHAR(dDataInizioVal,'DD/MM/YYYY HH24:MI:SS'));
            COMMIT;
        END;
      END IF;
    END IF;
  END LOOP;
  
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine creazione indici su SITIPART_ATTIVE');
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job Indici SITIPART_ATTIVE',
                message    => 'ok');
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErr := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su creazione indici SITIPART_ATTIVE = '||vErr||' - RIGA = '||
                                        DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job Indici SITIPART_ATTIVE',
                  message    => 'ko');
END IndSitiPart;  

PROCEDURE Rf IS

  TYPE tblNumElenco IS TABLE OF ELENCHI_HEADER.NUM_ELENCO%TYPE;
  
  NumElenco  tblNumElenco;
  vErr       VARCHAR2(32627);
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio pulizia tabelle RF');
  COMMIT;
  
  SELECT NUM_ELENCO
  BULK COLLECT INTO NumElenco
  FROM   ELENCHI_HEADER
  WHERE  ID_ELENCO IN ('REF2012','REF2015');
  
  IF NumElenco.FIRST IS NOT NULL THEN
    FOR i IN NumElenco.FIRST..NumElenco.LAST LOOP
      DELETE RF_QUADRO_DIFF WHERE NUM_ELENCO = NumElenco(i);
      
      DBMS_OUTPUT.PUT_LINE('NUM REC CANCELLATI SU RF_QUADRO_DIFF = '||SQL%ROWCOUNT||' PER NUM_ELENCO = '||NumElenco(i));
      
      DELETE RF_QUADRO WHERE NUM_ELENCO = NumElenco(i);
      
      DBMS_OUTPUT.PUT_LINE('NUM REC CANCELLATI SU RF_QUADRO = '||SQL%ROWCOUNT||' PER NUM_ELENCO = '||NumElenco(i));
      
      DELETE RF_QUADRO_ALT WHERE NUM_ELENCO = NumElenco(i);
      
      DBMS_OUTPUT.PUT_LINE('NUM REC CANCELLATI SU RF_QUADRO_ALT = '||SQL%ROWCOUNT||' PER NUM_ELENCO = '||NumElenco(i));
      
      DELETE RF_QUADRO_SUOLO WHERE NUM_ELENCO = NumElenco(i);
      
      DBMS_OUTPUT.PUT_LINE('NUM REC CANCELLATI SU RF_QUADRO_SUOLO = '||SQL%ROWCOUNT||' PER NUM_ELENCO = '||NumElenco(i));
    END LOOP;
  END IF;
  
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine pulizia tabelle RF');
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job pulizia tabelle RF',
                message    => 'ok');
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErr := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico pulizia tabelle RF = '||vErr||' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job pulizia tabelle RF',
                  message    => 'ko');                
END Rf;

PROCEDURE PopolamentoQgis(pSiglaProv  SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE,
                          pNoPiemonte  VARCHAR2) IS
                          
  TYPE Refcursor IS REF CURSOR;

  nIdEleggibilitaRilevata  SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA.ID_ELEGGIBILITA_RILEVATA%TYPE;
  nIdSuoloRilevato         QGIS_T_SUOLO_RILEVATO.ID_SUOLO_RILEVATO%TYPE;
  --nIdParticella            SMRGAA.DB_PARTICELLA_CERTIFICATA.ID_PARTICELLA%TYPE;
  nIdVersioneParticella    QGIS_T_VERSIONE_PARTICELLA.ID_VERSIONE_PARTICELLA%TYPE;
  vErrSql                  VARCHAR2(4000);
  nFoglio                  SITIPART_ATTIVE.FOGLIO%TYPE;
  vParticella              SITIPART_ATTIVE.PARTICELLA%TYPE;
  vCodNazionale            SITIPART_ATTIVE.COD_NAZIONALE%TYPE;
  --nParticella              SMRGAA.DB_PARTICELLA_CERTIFICATA.PARTICELLA%TYPE;
  nNumRec                  SIMPLE_INTEGER := 0;
  recRefCursor             Refcursor;
  rec                      SITISUOLO_ATTIVE_PULITE%ROWTYPE;
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio PopolamentoQgis. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte);
  COMMIT;
  
  -- ci sono dei record che non hanno corrispondeza su SMRGAA.DB_SITICOMU
  IF pSiglaProv IS NULL AND pNoPiemonte IS NULL THEN
    OPEN recRefCursor FOR SELECT S.*
                          FROM   SITISUOLO_ATTIVE_PULITE S
                          WHERE  S.SHAPE        IS NOT NULL
                          AND    S.COD_VARIETA != 0
                          AND    NOT EXISTS     (SELECT 'X'
                                                 FROM   SMRGAA.DB_SITICOMU SC
                                                 WHERE  S.COD_NAZIONALE = SC.COD_NAZIONALE);
  ELSIF pSiglaProv IS NULL AND pNoPiemonte IS NOT NULL THEN                                     
    -- elaboro i record fuori piemonte
    OPEN recRefCursor FOR SELECT S.*
                          FROM   SITISUOLO_ATTIVE_PULITE S,SMRGAA.DB_SITICOMU SC
                          WHERE  S.COD_NAZIONALE  = SC.COD_NAZIONALE
                          AND    SHAPE            IS NOT NULL
                          AND    COD_VARIETA     != 0
                          AND    ISTATR          != '01';
  ELSIF pSiglaProv IS NOT NULL THEN                                     
    -- elaboro i record per provincia
    OPEN recRefCursor FOR SELECT S.*
                          FROM   SITISUOLO_ATTIVE_PULITE S,SMRGAA.DB_SITICOMU SC
                          WHERE  S.COD_NAZIONALE  = SC.COD_NAZIONALE
                          AND    SHAPE            IS NOT NULL
                          AND    COD_VARIETA     != 0
                          AND    SIGLA_PROV       = pSiglaProv;
  END IF;                                        
  
  LOOP
    FETCH recRefCursor INTO rec;
    EXIT WHEN recRefCursor%NOTFOUND;
    
    nNumRec := nNumRec + 1;
    
    nFoglio       := rec.FOGLIO;
    vParticella   := rec.PARTICELLA;
    vCodNazionale := rec.COD_NAZIONALE;
           
    BEGIN
      SELECT ID_ELEGGIBILITA_RILEVATA
      INTO   nIdEleggibilitaRilevata
      FROM   SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA
      WHERE  CODI_RILE_PROD     = rec.COD_VARIETA
      AND    DATA_FINE_VALIDITA IS NULL;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        BEGIN
          SELECT ID_ELEGGIBILITA_RILEVATA
          INTO   nIdEleggibilitaRilevata
          FROM   SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA
          WHERE  CODI_RILE_PROD = rec.COD_VARIETA; 
        EXCEPTION
          WHEN OTHERS THEN
            nIdEleggibilitaRilevata := 7513;
        END;
    END;
  
    BEGIN
      INSERT INTO QGIS_T_SUOLO_RILEVATO
      (ID_SUOLO_RILEVATO, AREA, CAMPAGNA, EXT_COD_NAZIONALE, DATA_INIZIO_VALIDITA, 
       DATA_FINE_VALIDITA,
       DATA_AGGIORNAMENTO,EXT_ID_ELEGGIBILITA_RILEVATA,FOGLIO, ID_TIPO_SORGENTE_SUOLO, SHAPE,EXT_ID_UTENTE_LAVOR_SITICLIENT,SE_ROW_ID)
      VALUES
      (SEQ_QGIS_T_SUOLO_RILEVATO.NEXTVAL,SMRGAA.AABGAD_SDO.SDO_AREA(rec.SHAPE),rec.CAMPAGNA,rec.COD_NAZIONALE,rec.DATA_INIZIO_VAL,
       (CASE WHEN rec.DATA_FINE_VAL = TO_DATE('31/12/9999','dd/mm/yyyy') THEN NULL ELSE rec.DATA_FINE_VAL END),
       NVL(rec.DATA_AGGIORNAMENTO,rec.DATA_INIZIO_VAL),nIdEleggibilitaRilevata,rec.FOGLIO,99,rec.SHAPE,rec.UTENTE,rec.SE_ROW_ID)
      RETURNING ID_SUOLO_RILEVATO INTO nIdSuoloRilevato;
    EXCEPTION
      WHEN OTHERS THEN
        vErrSql := SQLERRM;
        INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su QGIS_T_SUOLO_RILEVATO. Foglio = '||nFoglio||' - Particella = '||
                                            vParticella||' - Codice Nazionale = '||vCodNazionale||' = '||vErrSql||' - RIGA = '||
                                            DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
        COMMIT;
        CONTINUE;
    END;
    
    FOR recPart IN (SELECT *
                    FROM   SITIPART_ATTIVE
                    WHERE  COD_NAZIONALE          = rec.COD_NAZIONALE
                    AND    FOGLIO                 = rec.FOGLIO
                    AND    PARTICELLA             = rec.PARTICELLA 
                    AND    SUB                    = rec.SUB 
                    --AND    rec.DATA_FINE_VALIDITA BETWEEN (DATA_INIZIO_VAL - INTERVAL '10' SECOND) AND (DATA_FINE_VAL + INTERVAL '10' SECOND)
                    AND    ((rec.DATA_FINE_VAL   BETWEEN (DATA_INIZIO_VAL - INTERVAL '10' SECOND) AND (DATA_FINE_VAL + INTERVAL '10' SECOND)) OR
                            (rec.DATA_INIZIO_VAL BETWEEN (DATA_INIZIO_VAL - INTERVAL '10' SECOND) AND (DATA_FINE_VAL + INTERVAL '10' SECOND)))
                    AND    SHAPE                  IS NOT NULL) LOOP
      
      BEGIN
        SELECT ID_VERSIONE_PARTICELLA
        INTO   nIdVersioneParticella
        FROM   QGIS_T_VERSIONE_PARTICELLA
        WHERE  EXT_COD_NAZIONALE        = recPart.COD_NAZIONALE
        AND    DATA_INIZIO_VALIDITA     = recPart.DATA_INIZIO_VAL
        AND    NVL(EXT_ID_PARTICELLA,0) = NVL(recPart.EXT_ID_PARTICELLA,0) --NVL(nIdParticella,0)
        AND    FOGLIO                   = recPart.FOGLIO
        AND    PARTICELLA               = recPart.PARTICELLA
        AND    SUBALTERNO               = recPart.SUB;
      EXCEPTION
        WHEN NO_DATA_FOUND THEN
          INSERT INTO QGIS_T_VERSIONE_PARTICELLA
          (ID_VERSIONE_PARTICELLA, AREA, EXT_COD_NAZIONALE, DATA_INIZIO_VALIDITA,
           DATA_FINE_VALIDITA,
           DATA_AGGIORNAMENTO, EXT_ID_PARTICELLA, FOGLIO, 
           PARTICELLA, SHAPE,SUBALTERNO,EXT_ID_UTENTE_LAVOR_SITICLIENT,ID_TIPO_SORGENTE_SUOLO)
          VALUES
          (SEQ_QGIS_T_VERSIONE_PARTICELLA.NEXTVAL,recPart.AREA_PART, recPart.COD_NAZIONALE, recPart.DATA_INIZIO_VAL,
           (CASE WHEN recPart.DATA_FINE_VAL = TO_DATE('31/12/9999','dd/mm/yyyy') THEN NULL ELSE recPart.DATA_FINE_VAL END),
           NVL(recPart.DATA_AGGIORNAMENTO,recPart.DATA_INIZIO_VAL),recPart.EXT_ID_PARTICELLA , recPart.FOGLIO, 
           recPart.PARTICELLA, recPart.SHAPE,recPart.SUB,recPart.UTENTE,99)
          RETURNING ID_VERSIONE_PARTICELLA INTO nIdVersioneParticella;
      END;
      
      INSERT INTO QGIS_T_SUOLO_PARTICELLA
      (ID_SUOLO_PARTICELLA, ID_SUOLO_RILEVATO, ID_VERSIONE_PARTICELLA, AREA, 
       DATA_AGGIORNAMENTO, 
       PROG_POLIGONO, SHAPE,EXT_ID_UTENTE_LAVOR_SITICLIENT,SE_ROW_ID)
      VALUES
      (SEQ_QGIS_T_SUOLO_PARTICELLA.NEXTVAL,nIdSuoloRilevato,nIdVersioneParticella,rec.AREA_COLT,
       NVL(rec.DATA_AGGIORNAMENTO,rec.DATA_INIZIO_VAL),
       rec.PROG_POLIGONO, rec.SHAPE,recPart.UTENTE,recPart.SE_ROW_ID);
    END LOOP;
    
    IF nNumRec = 10000 THEN
      COMMIT;
      nNumRec := 0;
    END IF;
  END LOOP;
  
  CLOSE recRefCursor;
  
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine insert su PopolamentoQgis. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||
                                      pNoPiemonte);
  COMMIT;
  
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'QGIS_T_VERSIONE_PARTICELLA');
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job PopolamentoQgis. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte,
                message    => 'ok');

EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErrSql := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su PopolamentoQgis. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||
                                         pNoPiemonte||' = '||vErrSql||' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    INSERT INTO TMP_ROCCO (COL1) VALUES(nFoglio||' - '||vParticella||' - '||vCodNazionale);
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job PopolamentoQgis. Sigla Prov = '||pSiglaProv||' - pNoPiemonte = '||pNoPiemonte,
                  message    => 'ko');
END PopolamentoQgis;

FUNCTION ReturnAzienda(pAnnoCampagna          NUMBER,
                       pIdVersioneParticella  QGIS_T_VERSIONE_PARTICELLA.ID_VERSIONE_PARTICELLA%TYPE,
                       pProvRif               SITILISTALAV.PROV_RIF%TYPE,
                       pDatains               SITIPLAV.DATAINS%TYPE) RETURN QGIS_T_EVENTO_LAVORAZIONE.EXT_ID_AZIENDA%TYPE IS

  nExtIdAzienda  QGIS_T_EVENTO_LAVORAZIONE.EXT_ID_AZIENDA%TYPE;
BEGIN
  IF pIdVersioneParticella IS NULL THEN
    RETURN NULL;
  END IF;
  
  IF UPPER(pProvRif) LIKE 'IS%' THEN
    SELECT MAX(IR.ID_AZIENDA)
    INTO   nExtIdAzienda
    FROM   QGIS_T_VERSIONE_PARTICELLA VP,SMRGAA.DB_ISTANZA_RIESAME IR
    WHERE  VP.ID_VERSIONE_PARTICELLA  = pIdVersioneParticella
    AND    VP.EXT_ID_PARTICELLA       = IR.ID_PARTICELLA
    AND    IR.ANNO                    = pAnnoCampagna
    AND    IR.DATA_ANNULLAMENTO       IS NULL
    AND    IR.ID_FASE_ISTANZA_RIESAME = 1;
  ELSIF UPPER(pProvRif) LIKE 'UE%' OR UPPER(pProvRif) LIKE 'UI%' OR UPPER(pProvRif) LIKE 'BOUE%' OR UPPER(pProvRif) LIKE 'BOUI%' THEN
    SELECT MAX(SUA.ID_AZIENDA)
    INTO   nExtIdAzienda
    FROM   QGIS_T_VERSIONE_PARTICELLA VP,SMRGAA.DB_STORICO_UNITA_ARBOREA SUA
    WHERE  VP.ID_VERSIONE_PARTICELLA = pIdVersioneParticella
    AND    SUA.ID_PARTICELLA         = VP.EXT_ID_PARTICELLA
    AND    SUA.ID_TIPOLOGIA_UNAR     = 2
    AND    pDatains                  BETWEEN SUA.DATA_INIZIO_VALIDITA AND NVL(SUA.DATA_FINE_VALIDITA,pDatains);
  ELSE
    RETURN NULL;
  END IF;

  RETURN nExtIdAzienda;
END ReturnAzienda;    

PROCEDURE ListeLav(pAnnoCampagna  NUMBER,
                   pSiglaProv     SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE) IS

  nIdListaLavorazione      QGIS_T_LISTA_LAVORAZIONE.ID_LISTA_LAVORAZIONE%TYPE;
  nIdEventoLavorazione     QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE;
  nContPartAtt             SIMPLE_INTEGER := 0;
  nIdVersioneParticella    QGIS_T_VERSIONE_PARTICELLA.ID_VERSIONE_PARTICELLA%TYPE;
  nContSuoloAtt            SIMPLE_INTEGER := 0;
  nNumRec                  SIMPLE_INTEGER := 0;
  vErrSql                  VARCHAR2(4000);
  nIdLav                   SITIPLAV.ID_LAV%TYPE;
  nIdParticella            SITIPLAV.ID_PARTICELLA%TYPE;
  nExtIdAzienda            QGIS_T_EVENTO_LAVORAZIONE.EXT_ID_AZIENDA%TYPE;
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio liste lavorazioni x anno_campagna = '||pAnnoCampagna||' e provincia = '||pSiglaProv);
  COMMIT;
  
  FOR rec IN (SELECT *
              FROM   SITILISTALAV
              WHERE  CAMPAGNA >= 2015
              AND    CAMPAGNA  = pAnnoCampagna) LOOP
    
    BEGIN
      SELECT ID_LISTA_LAVORAZIONE
      INTO   nIdListaLavorazione
      FROM   QGIS_T_LISTA_LAVORAZIONE
      WHERE  CAMPAGNA = rec.CAMPAGNA
      AND    CODICE   = rec.PROV_RIF;
    EXCEPTION
      WHEN OTHERS THEN
        ROLLBACK;
        vErrSql := SQLERRM;
        INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su ListeLav '||pSiglaProv||' '||pAnnoCampagna||' = '||vErrSql||
                                            ' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE||
                                            ' - CAMPAGNA = '||rec.CAMPAGNA||' - PROV_RIF = '||rec.PROV_RIF);
        COMMIT;
        
        UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                      recipients => '<EMAIL_ADDRESS>',
                      subject    => 'job liste lavorazione provincia '||pSiglaProv||' '||pAnnoCampagna,
                      message    => 'ko');
        RETURN;
    END;
    
    FOR recPLav IN (SELECT P.*
                    FROM   SITIPLAV P,SMRGAA.DB_SITICOMU S
                    WHERE  P.COD_NAZIONALE = S.COD_NAZIONALE
                    AND    S.SIGLA_PROV    = pSiglaProv
                    AND    P.LAST          = 1
                    AND    P.ID_LAV        = rec.ID_LAV
                    AND    P.DATA_LAV      IS NOT NULL) LOOP
      
      nNumRec       := nNumRec + 1;
      nIdLav        := rec.ID_LAV;
      nIdParticella := recPLav.ID_PARTICELLA;
      nExtIdAzienda := NULL;
      
      SELECT COUNT(*)
      INTO   nContPartAtt
      FROM   SITIPART_ATTIVE
      WHERE  ID_PARTICELLA          = recPLav.ID_PARTICELLA
      AND    TRUNC(DATA_INIZIO_VAL) = TRUNC(recPLav.DATA_LAV_P_GIS);
      
      SELECT COUNT(*)
      INTO   nContSuoloAtt
      FROM   SITISUOLO_ATTIVE_PULITE 
      WHERE  ID_PARTICELLA          = recPLav.ID_PARTICELLA
      AND    TRUNC(DATA_INIZIO_VAL) = TRUNC(recPLav.DATA_LAV_T_GIS);
      
      IF nContPartAtt != 0 THEN
        SELECT MAX(ID_VERSIONE_PARTICELLA)
        INTO   nIdVersioneParticella
        FROM   QGIS_T_VERSIONE_PARTICELLA VP,SITIPART_ATTIVE PA
        WHERE  PA.ID_PARTICELLA        = recPLav.ID_PARTICELLA
        AND    VP.DATA_INIZIO_VALIDITA = PA.DATA_INIZIO_VAL
        AND    VP.EXT_COD_NAZIONALE    = PA.COD_NAZIONALE
        AND    VP.FOGLIO               = PA.FOGLIO
        AND    VP.PARTICELLA           = PA.PARTICELLA
        AND    VP.SUBALTERNO           = PA.SUB
        AND    TO_DATE('31/12/'||pAnnoCampagna,'DD/MM/YYYY') BETWEEN VP.DATA_INIZIO_VALIDITA AND NVL(VP.DATA_FINE_VALIDITA,TO_DATE('31/12/'||pAnnoCampagna,'DD/MM/YYYY'));
        
        nExtIdAzienda := ReturnAzienda(pAnnoCampagna,
                                       nIdVersioneParticella,
                                       rec.PROV_RIF,
                                       recPLav.DATAINS);
                                       
        SELECT MAX(ID_EVENTO_LAVORAZIONE)
        INTO   nIdEventoLavorazione
        FROM   QGIS_T_EVENTO_LAVORAZIONE
        WHERE  ID_LISTA_LAVORAZIONE = nIdListaLavorazione
        AND    EXT_ID_AZIENDA       = nExtIdAzienda;
        
        IF nIdEventoLavorazione IS NULL THEN
          INSERT INTO QGIS_T_EVENTO_LAVORAZIONE
          (ID_EVENTO_LAVORAZIONE, ID_LISTA_LAVORAZIONE, DATA_LAVORAZIONE, DATA_INSERIMENTO,EXT_ID_UTENTE_INSER_SITICLIENT, 
           EXT_ID_UTENTE_LAVOR_SITICLIENT,EXT_ID_AZIENDA)
          VALUES
          (SEQ_QGIS_T_EVENTO_LAVORAZIONE.NEXTVAL,nIdListaLavorazione,recPLav.DATA_LAV,recPLav.DATAINS,recPLav.UTENTEINS,
           recPLav.UTENTE,nExtIdAzienda)
          RETURNING ID_EVENTO_LAVORAZIONE INTO nIdEventoLavorazione;
        END IF;
        
        INSERT INTO QGIS_T_PARTICELLA_LAVORAZIONE
        (ID_PARTICELLA_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_VERSIONE_PARTICELLA, DESCRIZIONE_SOSPENSIONE, 
         FLAG_SOSPENSIONE,FLAG_CESSATO,NOTE_LAVORAZIONE, NOTE_RICHIESTA)
        VALUES
        (SEQ_QGIS_T_PARTICELLA_LAVORAZI.NEXTVAL,nIdEventoLavorazione,nIdVersioneParticella,NVL(recPLav.DESC_MOTI,' '),
         DECODE(recPLav.DATASOSP,NULL,'N','S'),'N',recPLav.NOTE_LAV,recPLav.NOTE);
      END IF;
      
      IF nContSuoloAtt != 0 THEN
        SELECT MAX(ID_EVENTO_LAVORAZIONE)
        INTO   nIdEventoLavorazione
        FROM   QGIS_T_EVENTO_LAVORAZIONE
        WHERE  ID_LISTA_LAVORAZIONE = nIdListaLavorazione
        AND    EXT_ID_AZIENDA       = nExtIdAzienda;
        
        IF nIdEventoLavorazione IS NULL THEN
          INSERT INTO QGIS_T_EVENTO_LAVORAZIONE
          (ID_EVENTO_LAVORAZIONE, ID_LISTA_LAVORAZIONE, DATA_LAVORAZIONE, DATA_INSERIMENTO,EXT_ID_UTENTE_INSER_SITICLIENT, 
           EXT_ID_UTENTE_LAVOR_SITICLIENT,EXT_ID_AZIENDA)
          VALUES
          (SEQ_QGIS_T_EVENTO_LAVORAZIONE.NEXTVAL,nIdListaLavorazione,recPLav.DATA_LAV,recPLav.DATAINS,recPLav.UTENTEINS,
           recPLav.UTENTE,NULL)
          RETURNING ID_EVENTO_LAVORAZIONE INTO nIdEventoLavorazione;
        END IF;
        
        INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
        (ID_SUOLO_LAVORAZIONE,ID_EVENTO_LAVORAZIONE, ID_SUOLO_RILEVATO, DESCRIZIONE_SOSPENSIONE, 
         FLAG_SOSPENSIONE,FLAG_CESSATO,NOTE_LAVORAZIONE, NOTE_RICHIESTA)
        (SELECT SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,nIdEventoLavorazione,SP.ID_SUOLO_RILEVATO,NVL(recPLav.DESC_MOTI,' '),
                DECODE(recPLav.DATASOSP,NULL,'N','S'),'N',recPLav.NOTE_LAV,recPLav.NOTE
         FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_SUOLO_RILEVATO SR
         WHERE  VP.EXT_COD_NAZIONALE      = recPLav.COD_NAZIONALE
         AND    VP.FOGLIO                 = recPLav.FOGLIO
         AND    VP.PARTICELLA             = recPLav.PARTICELLA
         AND    VP.SUBALTERNO             = recPLav.SUB
         AND    VP.ID_VERSIONE_PARTICELLA = SP.ID_VERSIONE_PARTICELLA
         AND    SP.ID_SUOLO_RILEVATO      = SR.ID_SUOLO_RILEVATO
         AND    SR.DATA_INIZIO_VALIDITA   = (SELECT MAX(SR1.DATA_INIZIO_VALIDITA)
                                             FROM   QGIS_T_VERSIONE_PARTICELLA VP1,QGIS_T_SUOLO_PARTICELLA SP1,
                                                    QGIS_T_SUOLO_RILEVATO SR1
                                             WHERE  VP1.EXT_COD_NAZIONALE           = VP.EXT_COD_NAZIONALE
                                             AND    VP1.FOGLIO                      = VP.FOGLIO
                                             AND    VP1.PARTICELLA                  = VP.PARTICELLA
                                             AND    VP1.SUBALTERNO                  = VP.SUBALTERNO
                                             AND    VP1.ID_VERSIONE_PARTICELLA      = SP1.ID_VERSIONE_PARTICELLA
                                             AND    SP1.ID_SUOLO_RILEVATO           = SR1.ID_SUOLO_RILEVATO
                                             AND    TRUNC(SR1.DATA_INIZIO_VALIDITA) = TRUNC(recPLav.DATA_LAV_T_GIS)));
      END IF;
      
      -- Lavorazioni sospese
      IF recPLav.DATA_LAV_T_GIS IS NULL AND recPLav.DATA_LAV_P_GIS IS NULL AND recPLav.DATASOSP IS NOT NULL THEN
        SELECT MAX(ID_VERSIONE_PARTICELLA)
        INTO   nIdVersioneParticella
        FROM   QGIS_T_VERSIONE_PARTICELLA VP,SITIPART_ATTIVE PA
        WHERE  PA.ID_PARTICELLA        = recPLav.ID_PARTICELLA
        AND    VP.DATA_INIZIO_VALIDITA = PA.DATA_INIZIO_VAL
        AND    VP.EXT_COD_NAZIONALE    = PA.COD_NAZIONALE
        AND    VP.FOGLIO               = PA.FOGLIO
        AND    VP.PARTICELLA           = PA.PARTICELLA
        AND    VP.SUBALTERNO           = PA.SUB
        AND    TO_DATE('31/12/'||pAnnoCampagna,'DD/MM/YYYY') BETWEEN VP.DATA_INIZIO_VALIDITA AND NVL(VP.DATA_FINE_VALIDITA,TO_DATE('31/12/'||pAnnoCampagna,'DD/MM/YYYY'));
        
        nExtIdAzienda := ReturnAzienda(pAnnoCampagna,
                                       nIdVersioneParticella,
                                       rec.PROV_RIF,
                                       recPLav.DATAINS);
        
        SELECT MAX(ID_EVENTO_LAVORAZIONE)
        INTO   nIdEventoLavorazione
        FROM   QGIS_T_EVENTO_LAVORAZIONE
        WHERE  ID_LISTA_LAVORAZIONE = nIdListaLavorazione
        AND    EXT_ID_AZIENDA       = nExtIdAzienda;

        IF nIdEventoLavorazione IS NULL THEN
          INSERT INTO QGIS_T_EVENTO_LAVORAZIONE
          (ID_EVENTO_LAVORAZIONE, ID_LISTA_LAVORAZIONE, DATA_LAVORAZIONE, DATA_INSERIMENTO,EXT_ID_UTENTE_INSER_SITICLIENT, 
           EXT_ID_UTENTE_LAVOR_SITICLIENT,EXT_ID_AZIENDA)
          VALUES
          (SEQ_QGIS_T_EVENTO_LAVORAZIONE.NEXTVAL,nIdListaLavorazione,recPLav.DATA_LAV,recPLav.DATAINS,recPLav.UTENTEINS,
           recPLav.UTENTE,nExtIdAzienda)
          RETURNING ID_EVENTO_LAVORAZIONE INTO nIdEventoLavorazione;
        END IF;
        
        INSERT INTO QGIS_T_PARTICELLA_LAVORAZIONE
        (ID_PARTICELLA_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_VERSIONE_PARTICELLA, DESCRIZIONE_SOSPENSIONE, FLAG_SOSPENSIONE,FLAG_CESSATO,
         NOTE_LAVORAZIONE, NOTE_RICHIESTA)
        VALUES
        (SEQ_QGIS_T_PARTICELLA_LAVORAZI.NEXTVAL,nIdEventoLavorazione,nIdVersioneParticella,NVL(recPLav.DESC_MOTI,' '),'S','N',
         recPLav.NOTE_LAV,recPLav.NOTE);
        
        INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
        (ID_SUOLO_LAVORAZIONE,ID_EVENTO_LAVORAZIONE, ID_SUOLO_RILEVATO, DESCRIZIONE_SOSPENSIONE, FLAG_SOSPENSIONE, FLAG_CESSATO,
         NOTE_LAVORAZIONE, NOTE_RICHIESTA)
        (SELECT SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,nIdEventoLavorazione,SP.ID_SUOLO_RILEVATO,NVL(recPLav.DESC_MOTI,' '),'S','N',
                recPLav.NOTE_LAV,recPLav.NOTE
         FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_SUOLO_RILEVATO SR
         WHERE  VP.EXT_COD_NAZIONALE      = recPLav.COD_NAZIONALE
         AND    VP.FOGLIO                 = recPLav.FOGLIO
         AND    VP.PARTICELLA             = recPLav.PARTICELLA
         AND    VP.SUBALTERNO             = recPLav.SUB 
         AND    VP.ID_VERSIONE_PARTICELLA = SP.ID_VERSIONE_PARTICELLA
         AND    SP.ID_SUOLO_RILEVATO      = SR.ID_SUOLO_RILEVATO
         AND    TO_DATE('31/12/'||pAnnoCampagna,'DD/MM/YYYY') BETWEEN SR.DATA_INIZIO_VALIDITA AND NVL(SR.DATA_FINE_VALIDITA,TO_DATE('31/12/'||pAnnoCampagna,'DD/MM/YYYY')));
      END IF;
    END LOOP;
    
    FOR recPLav IN (SELECT P.*
                    FROM   SITIPLAV P,SMRGAA.DB_SITICOMU S
                    WHERE  P.COD_NAZIONALE = S.COD_NAZIONALE
                    AND    S.SIGLA_PROV    = pSiglaProv
                    AND    P.LAST          = 1
                    AND    P.ID_LAV        = rec.ID_LAV
                    AND    rec.CAMPAGNA   >= 2020
                    AND    P.DATA_LAV      IS NULL) LOOP
      
      nNumRec       := nNumRec + 1;
      nIdLav        := rec.ID_LAV;
      nIdParticella := recPLav.ID_PARTICELLA;
      
      SELECT MAX(ID_VERSIONE_PARTICELLA)
      INTO   nIdVersioneParticella
      FROM   QGIS_T_VERSIONE_PARTICELLA VP,SITIPART_ATTIVE PA
      WHERE  PA.ID_PARTICELLA        = recPLav.ID_PARTICELLA
      AND    VP.EXT_COD_NAZIONALE    = PA.COD_NAZIONALE
      AND    VP.DATA_INIZIO_VALIDITA = PA.DATA_INIZIO_VAL
      AND    recPLav.DATAINS         BETWEEN VP.DATA_INIZIO_VALIDITA AND NVL(VP.DATA_FINE_VALIDITA,recPLav.DATAINS)
      AND    VP.FOGLIO               = PA.FOGLIO
      AND    VP.PARTICELLA           = PA.PARTICELLA
      AND    VP.SUBALTERNO           = PA.SUB;
      
      nExtIdAzienda := ReturnAzienda(pAnnoCampagna,
                                     nIdVersioneParticella,
                                     rec.PROV_RIF,
                                     recPLav.DATAINS);
      
      SELECT MAX(ID_EVENTO_LAVORAZIONE)
      INTO   nIdEventoLavorazione
      FROM   QGIS_T_EVENTO_LAVORAZIONE
      WHERE  ID_LISTA_LAVORAZIONE = nIdListaLavorazione
      AND    EXT_ID_AZIENDA       = nExtIdAzienda
      AND    DATA_LAVORAZIONE     IS NULL;
      
      IF nIdEventoLavorazione IS NULL THEN
        INSERT INTO QGIS_T_EVENTO_LAVORAZIONE
        (ID_EVENTO_LAVORAZIONE, ID_LISTA_LAVORAZIONE, DATA_LAVORAZIONE, DATA_INSERIMENTO,EXT_ID_UTENTE_INSER_SITICLIENT, EXT_ID_UTENTE_LAVOR_SITICLIENT,
         EXT_ID_AZIENDA)
        VALUES
        (SEQ_QGIS_T_EVENTO_LAVORAZIONE.NEXTVAL,nIdListaLavorazione,recPLav.DATA_LAV,recPLav.DATAINS,recPLav.UTENTEINS,recPLav.UTENTE,
         nExtIdAzienda)
        RETURNING ID_EVENTO_LAVORAZIONE INTO nIdEventoLavorazione;
      END IF;
      
      IF nIdVersioneParticella IS NOT NULL THEN
        INSERT INTO QGIS_T_PARTICELLA_LAVORAZIONE
        (ID_PARTICELLA_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_VERSIONE_PARTICELLA, DESCRIZIONE_SOSPENSIONE, 
         FLAG_SOSPENSIONE,FLAG_CESSATO,NOTE_LAVORAZIONE, NOTE_RICHIESTA)
        VALUES
        (SEQ_QGIS_T_PARTICELLA_LAVORAZI.NEXTVAL,nIdEventoLavorazione,nIdVersioneParticella,NVL(recPLav.DESC_MOTI,' '),
         DECODE(recPLav.DATASOSP,NULL,'N','S'),'N',recPLav.NOTE_LAV,recPLav.NOTE);
      
        INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
        (ID_SUOLO_LAVORAZIONE,ID_EVENTO_LAVORAZIONE, ID_SUOLO_RILEVATO, DESCRIZIONE_SOSPENSIONE, FLAG_SOSPENSIONE, FLAG_CESSATO,
         NOTE_LAVORAZIONE, NOTE_RICHIESTA)
        (SELECT SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,nIdEventoLavorazione,SP.ID_SUOLO_RILEVATO,NULL,'N','N',
                NULL,NULL
         FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_SUOLO_RILEVATO SR
         WHERE  VP.EXT_COD_NAZIONALE      = recPLav.COD_NAZIONALE
         AND    VP.FOGLIO                 = recPLav.FOGLIO
         AND    VP.PARTICELLA             = recPLav.PARTICELLA
         AND    VP.SUBALTERNO             = recPLav.SUB
         AND    VP.ID_VERSIONE_PARTICELLA = SP.ID_VERSIONE_PARTICELLA
         AND    SP.ID_SUOLO_RILEVATO      = SR.ID_SUOLO_RILEVATO
         AND    SR.DATA_FINE_VALIDITA     IS NULL);
      END IF;
    END LOOP;
    
    IF nNumRec = 1000 THEN
      COMMIT;
      nNumRec := 0;
    END IF;
  END LOOP;
  
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine liste lavorazioni x anno_campagna = '||pAnnoCampagna||' e provincia = '||pSiglaProv);
  
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job liste lavorazione provincia '||pSiglaProv||' '||pAnnoCampagna,
                message    => 'ok');
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErrSql := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES('Errore generico su ListeLav '||pSiglaProv||' '||pAnnoCampagna||' = '||vErrSql||' - RIGA = '||
                                        DBMS_UTILITY.FORMAT_ERROR_BACKTRACE||' - ID_LAV = '||nIdLav||' - ID_PARTICELLA = '||
                                        nIdParticella);
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job liste lavorazione provincia '||pSiglaProv||' '||pAnnoCampagna,
                  message    => 'ko');
END ListeLav;

PROCEDURE StatListeLav IS 
BEGIN
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'QGIS_T_PARTICELLA_LAVORAZIONE');
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'QGIS_T_SUOLO_LAVORAZIONE');
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'QGIS_T_EVENTO_LAVORAZIONE');
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'QGIS_T_LISTA_LAVORAZIONE');
  DBMS_STATS.gather_table_stats('SITIPIOPR', 'QGIS_T_SUOLO_PROPOSTO');
END StatListeLav;

PROCEDURE SuoloProposto IS

  nIdAzienda  NUMBER;
  vErrSql     VARCHAR2(4000);
BEGIN
  INSERT INTO TMP_ROCCO (COL1) VALUES('Inizio SuoloProposto');
  COMMIT;
  
  FOR rec IN (SELECT EV.EXT_ID_AZIENDA,LL.CAMPAGNA,EV.ID_EVENTO_LAVORAZIONE
              FROM   QGIS_T_EVENTO_LAVORAZIONE EV,QGIS_T_LISTA_LAVORAZIONE LL
              WHERE  EV.EXT_ID_AZIENDA        IS NOT NULL
              AND    EV.ID_LISTA_LAVORAZIONE  = LL.ID_LISTA_LAVORAZIONE
              AND    LL.CODICE                LIKE 'IS%'
              AND    LL.CAMPAGNA             >= 2020) LOOP
              
    nIdAzienda := rec.EXT_ID_AZIENDA;          
  
    FOR recIst IN (SELECT DISTINCT IA.ID_ISTANZA_APPEZZAMENTO,VP.EXT_COD_NAZIONALE,VP.FOGLIO,TER.ID_ELEGGIBILITA_RILEVATA
                   FROM   SMRGAA.DB_ISTANZA_APPEZZAMENTO IA,SMRGAA.DB_ISTANZA_RIESAME_AZIENDA IRA,QGIS_T_VERSIONE_PARTICELLA VP,
                          QGIS_T_PARTICELLA_LAVORAZIONE PL,SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA TER
                   WHERE  IRA.ID_ISTANZA_RIESAME_AZIENDA = IA.ID_ISTANZA_RIESAME_AZIENDA
                   AND    IRA.ID_AZIENDA                 = rec.EXT_ID_AZIENDA
                   AND    IRA.ANNO_ISTANZA               = rec.CAMPAGNA
                   AND    VP.ID_VERSIONE_PARTICELLA      = PL.ID_VERSIONE_PARTICELLA
                   AND    PL.ID_EVENTO_LAVORAZIONE       = rec.ID_EVENTO_LAVORAZIONE
                   AND    TER.CODI_RILE_PROD             = IA.CODI_PROD_RILE
                   AND    TER.DATA_FINE_VALIDITA         IS NULL
                   AND    SDO_GEOM.RELATE(VP.SHAPE,'ANYINTERACT',IA.SHAPE_POLIGONO, 0.005) = 'TRUE'
                   AND    SDO_GEOM.SDO_AREA(SDO_GEOM.SDO_INTERSECTION(VP.SHAPE,IA.SHAPE_POLIGONO, 0.005),0.005) > 0) LOOP
                   
      INSERT INTO QGIS_T_SUOLO_PROPOSTO
      (ID_SUOLO_PROPOSTO, ID_EVENTO_LAVORAZIONE, EXT_ID_ELEGGIBILITA_RILEVATA, EXT_ID_ISTA_RIES, 
       SHAPE,
       EXT_COD_NAZIONALE, FOGLIO)
      VALUES
      (SEQ_QGIS_T_SUOLO_PROPOSTO.NEXTVAL,rec.ID_EVENTO_LAVORAZIONE,recIst.ID_ELEGGIBILITA_RILEVATA,recIst.ID_ISTANZA_APPEZZAMENTO,
       (SELECT SHAPE_POLIGONO FROM SMRGAA.DB_ISTANZA_APPEZZAMENTO WHERE ID_ISTANZA_APPEZZAMENTO = recIst.ID_ISTANZA_APPEZZAMENTO),
       recIst.EXT_COD_NAZIONALE, recIst.FOGLIO);               
    END LOOP;
  END LOOP;
  
  INSERT INTO TMP_ROCCO (COL1) VALUES('Fine SuoloProposto');
  COMMIT;
  
  UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                recipients => '<EMAIL_ADDRESS>',
                subject    => 'job SuoloProposto',
                message    => 'ok');
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    vErrSql := SQLERRM;
    INSERT INTO TMP_ROCCO (COL1) VALUES ('Errore generico su SuoloProposto = '||vErrSql||' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE||
                                         ' - ID_AZIENDA = '||nIdAzienda);    
    COMMIT;
    
    UTL_MAIL.SEND(sender     => 'JOB@JOB.IT',
                  recipients => '<EMAIL_ADDRESS>',
                  subject    => 'job SuoloProposto',
                  message    => 'ko');
END SuoloProposto;

FUNCTION Cdt(pStr  VARCHAR2) RETURN INTEGER IS
BEGIN
  DBMS_OUTPUT.PUT_LINE('Esecuzione stringa SQL : '||SUBSTR(pStr,1,200));
  DBMS_OUTPUT.PUT_LINE('Inizio : '||TO_CHAR(SYSDATE,'DD/MM/YYYY HH24:MI:SS'));

  EXECUTE IMMEDIATE pStr;
  COMMIT;
  DBMS_OUTPUT.PUT_LINE('Fine : '||TO_CHAR(SYSDATE,'DD/MM/YYYY HH24:MI:SS'));
  DBMS_OUTPUT.PUT_LINE('Esecuzione OK');
  RETURN 0;

EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE(TO_CHAR(SQLCODE)||' - '||SUBSTR(SQLERRM,1,150));
    DBMS_OUTPUT.PUT_LINE('Fine : ' || TO_CHAR(SYSDATE,'DD/MM/YYYY HH24:MI:SS'));
    DBMS_OUTPUT.PUT_LINE('Esecuzione KO');
    RETURN 1;
END Cdt;

END PCK_SITI_SVECCHIA;

/