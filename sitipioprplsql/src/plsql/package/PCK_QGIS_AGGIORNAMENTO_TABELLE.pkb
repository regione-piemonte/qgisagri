CREATE OR REPLACE PACKAGE BODY PCK_QGIS_AGGIORNAMENTO_TABELLE AS

FUNCTION getDataGisCampagna(pCodNazionale     VARCHAR2,
                            pFoglio           NUMBER,
                            pParticella       VARCHAR2,
                            pSub              VARCHAR2,
                            pAnnoRiferimento  NUMBER,
                            pDataInizio       DATE) RETURN DATE IS
  dData  DATE;
  nCont  SIMPLE_INTEGER := 0;
BEGIN
  SELECT COUNT(*)
  INTO   nCont
  FROM   SITISUOLO_ATTIVE
  WHERE  COD_NAZIONALE   = pCodNazionale
  AND    FOGLIO          = pFoglio
  AND    PARTICELLA      = pParticella
  AND    SUB             = pSub
  AND    DATA_INIZIO_VAL > pDataInizio
  AND    CAMPAGNA        = pAnnoRiferimento;
  
  IF nCont != 0 THEN
    RETURN NULL;
  END IF;
  
  BEGIN
    SELECT DATA_FINE_VAL
    INTO   dData
    FROM   (SELECT CAMPAGNA, DATA_FINE_VAL
            FROM   QGIS_W_SITISUOLO
            WHERE  COD_NAZIONALE = pCodNazionale
            AND    FOGLIO        = pFoglio
            AND    PARTICELLA    = pParticella
            AND    SUB           = pSub
            AND    CAMPAGNA     <= pAnnoRiferimento
            ORDER BY CAMPAGNA DESC, DATA_FINE_VAL DESC)
          WHERE ROWNUM = 1;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      dData := TO_DATE('31/12/9999','DD/MM/YYYY');
  END;

  RETURN dData;
END getDataGisCampagna;

FUNCTION TabSitiSuolo(pIdProcessoBatch  QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE) RETURN NUMBER IS

  nCont                SIMPLE_INTEGER := 0;
  nAnno                QGIS_D_PARAMETRO_PLUGIN.VALORE_NUMERICO%TYPE;
  vCodNazionale        SITISUOLO_ATTIVE.COD_NAZIONALE%TYPE;
  nFoglio              SITISUOLO_ATTIVE.FOGLIO%TYPE;
  vParticella          SITISUOLO_ATTIVE.PARTICELLA%TYPE;
  vSub                 SITISUOLO_ATTIVE.SUB%TYPE;
  vDataFineValidita    VARCHAR2(30);
  vDataInizioValidita  VARCHAR2(30);
  dDataInizioVal       DATE;
  dDataAgg             DATE;
BEGIN
  SELECT VALORE_NUMERICO
  INTO   nAnno
  FROM   QGIS_D_PARAMETRO_PLUGIN
  WHERE  CODICE             = 'ANNO_IMP_SUOLO'
  AND    DATA_FINE_VALIDITA IS NOT NULL;
  
  SELECT MIN(DATA_AGGIORNAMENTO)
  INTO   dDataAgg
  FROM   QGIS_W_SITISUOLO;
  
  FOR rec IN (SELECT S.*
              FROM   QGIS_W_SITISUOLO S
              WHERE  S.DATA_INIZIO_VAL < S.DATA_FINE_VAL
              ORDER BY COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_INIZIO_VAL DESC) LOOP
              
    SELECT COUNT(*)
    INTO   nCont
    FROM   SITISUOLO_ATTIVE
    WHERE  COD_NAZIONALE   = rec.COD_NAZIONALE
    AND    FOGLIO          = rec.FOGLIO
    AND    PARTICELLA      = rec.PARTICELLA
    AND    CAMPAGNA        = rec.CAMPAGNA
    AND    DATA_INIZIO_VAL = rec.DATA_INIZIO_VAL
    AND    PROG_POLIGONO   = rec.PROG_POLIGONO
    AND    SUB             = rec.SUB;
    
    vCodNazionale       := rec.COD_NAZIONALE;
    nFoglio             := rec.FOGLIO;
    vParticella         := rec.PARTICELLA;
    vSub                := rec.SUB;
    vDataFineValidita   := TO_CHAR(rec.DATA_FINE_VAL,'DD/MM/YYYY HH24:MI:SS');
    vDataInizioValidita := TO_CHAR(rec.DATA_INIZIO_VAL,'DD/MM/YYYY HH24:MI:SS');
      
    IF nCont = 0 THEN
      IF ((rec.DATA_FINE_VAL < SYSDATE AND ((rec.CAMPAGNA >= nAnno) OR (rec.CAMPAGNA < nAnno AND
                                             rec.DATA_FINE_VAL = getDataGisCampagna(rec.COD_NAZIONALE ,rec.FOGLIO,rec.PARTICELLA,rec.SUB,
                                                                                    rec.CAMPAGNA,rec.DATA_INIZIO_VAL)))) OR
          (rec.DATA_FINE_VAL > SYSDATE)) THEN
        
        BEGIN
          -- allora inserisco
          -- ma prima faccio scadere il record che copre la validita del record da inserire
          UPDATE SITISUOLO_ATTIVE
          SET    DATA_FINE_VAL      = rec.DATA_INIZIO_VAL - INTERVAL '1' SECOND,
                 DATA_AGGIORNAMENTO = rec.DATA_AGGIORNAMENTO
          WHERE  COD_NAZIONALE      = rec.COD_NAZIONALE
          AND    FOGLIO             = rec.FOGLIO
          AND    PARTICELLA         = rec.PARTICELLA
          AND    SUB                = rec.SUB
          AND    DATA_FINE_VAL      > rec.DATA_INIZIO_VAL
          AND    DATA_INIZIO_VAL    < rec.DATA_INIZIO_VAL;
          
          INSERT INTO SITISUOLO_ATTIVE
          (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, PROG_POLIGONO, DATA_FINE_VAL, ALLEGATO, SVILUPPO, CAMPAGNA, UTENTE, DATA_INIZIO_VAL, 
           DATA_LAV, AREA_COLT, COD_COLTURA, SHAPE, ANNO_FOTO, MESE_FOTO, SE_ROW_ID, COD_VARIETA, TARA, ISTATP, COD_UTIL, STATO_COLT, 
           STATO_PROP, UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, 
           DATA_AGGIORNAMENTO, GRUPPO, ID_PARTICELLA, IDFOTO, DXFOTO, DYFOTO, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, ID_CONTROLLO)
          VALUES
          (rec.COD_NAZIONALE, rec.FOGLIO, rec.PARTICELLA, rec.SUB, rec.PROG_POLIGONO, rec.DATA_FINE_VAL, rec.ALLEGATO, rec.SVILUPPO, 
           rec.CAMPAGNA, rec.UTENTE, rec.DATA_INIZIO_VAL,rec.DATA_LAV, rec.AREA_COLT, rec.COD_COLTURA, rec.SHAPE, rec.ANNO_FOTO, 
           rec.MESE_FOTO, rec.SE_ROW_ID, rec.COD_VARIETA, rec.TARA, rec.ISTATP, rec.COD_UTIL, rec.STATO_COLT,rec.STATO_PROP, rec.UTENTE_FINE,
           rec.UTENTE_PROP, rec.UTENTE_PROP_FINE, rec.ID_TRASF, rec.ID_TRASF_FINE, rec.SORGENTE, rec.VALI_PROD, rec.TAVOLA, rec.FLAGCARICO, 
           rec.DATA_AGGIORNAMENTO, rec.GRUPPO, rec.ID_PARTICELLA, rec.IDFOTO, rec.DXFOTO, rec.DYFOTO, rec.ALMOST_DEAD, rec.FLAG_PROVENIENZA, 
           rec.SYNC_SV_ID, rec.ID_CONTROLLO);
        EXCEPTION
          WHEN OTHERS THEN
            UPDATE SITISUOLO_ATTIVE
            SET    DATA_FINE_VAL      = rec.DATA_INIZIO_VAL - INTERVAL '1' SECOND,
                   DATA_AGGIORNAMENTO = rec.DATA_AGGIORNAMENTO
            WHERE  COD_NAZIONALE      = rec.COD_NAZIONALE
            AND    FOGLIO             = rec.FOGLIO
            AND    PARTICELLA         = rec.PARTICELLA
            AND    CAMPAGNA           = rec.CAMPAGNA
            AND    DATA_FINE_VAL      = rec.DATA_FINE_VAL
            AND    SUB                = rec.SUB;
        END;
      END IF;
    ELSE
      UPDATE SITISUOLO_ATTIVE
      SET    DATA_AGGIORNAMENTO   = rec.DATA_AGGIORNAMENTO,
             COD_VARIETA          = rec.COD_VARIETA,
             DATA_FINE_VAL        = rec.DATA_FINE_VAL,
             SHAPE                = rec.SHAPE,
             ID_PARTICELLA        = rec.ID_PARTICELLA,
             AREA_COLT            = rec.AREA_COLT,
             UTENTE               = rec.UTENTE,
             SORGENTE             = rec.SORGENTE,
             ALLEGATO             = rec.ALLEGATO,
             SVILUPPO             = rec.SVILUPPO,
             DATA_LAV             = rec.DATA_LAV,
             COD_COLTURA          = rec.COD_COLTURA,
             ANNO_FOTO            = rec.ANNO_FOTO,
             MESE_FOTO            = rec.MESE_FOTO,
             TARA                 = rec.TARA,
             ISTATP               = rec.ISTATP,
             COD_UTIL             = rec.COD_UTIL,
             STATO_COLT           = rec.STATO_COLT,
             STATO_PROP           = rec.STATO_PROP,
             UTENTE_FINE          = rec.UTENTE_FINE,
             UTENTE_PROP          = rec.UTENTE_PROP,
             UTENTE_PROP_FINE     = rec.UTENTE_PROP_FINE,
             ID_TRASF             = rec.ID_TRASF,
             ID_TRASF_FINE        = rec.ID_TRASF_FINE,
             VALI_PROD            = rec.VALI_PROD,
             TAVOLA               = rec.TAVOLA,
             FLAGCARICO           = rec.FLAGCARICO,
             GRUPPO               = rec.GRUPPO,
             IDFOTO               = rec.IDFOTO,
             DXFOTO               = rec.DXFOTO,
             DYFOTO               = rec.DYFOTO,
             ALMOST_DEAD          = rec.ALMOST_DEAD,
             FLAG_PROVENIENZA     = rec.FLAG_PROVENIENZA,
             SYNC_SV_ID           = rec.SYNC_SV_ID,
             ID_CONTROLLO         = rec.ID_CONTROLLO
      WHERE  COD_NAZIONALE        = rec.COD_NAZIONALE
      AND    FOGLIO               = rec.FOGLIO
      AND    PARTICELLA           = rec.PARTICELLA
      AND    CAMPAGNA             = rec.CAMPAGNA
      AND    DATA_INIZIO_VAL      = rec.DATA_INIZIO_VAL
      AND    PROG_POLIGONO        = rec.PROG_POLIGONO
      AND    SUB                  = rec.SUB;
    END IF;
  END LOOP;
  
  FOR rec IN (SELECT ROWID ROW_ID,COD_NAZIONALE,FOGLIO,PARTICELLA,SUB,DATA_FINE_VAL,DATA_INIZIO_VAL,DATA_AGGIORNAMENTO
              FROM   SITISUOLO_ATTIVE
              WHERE  (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB) IN (SELECT DISTINCT COD_NAZIONALE, FOGLIO, PARTICELLA, SUB
                                                                  FROM   SITISUOLO_ATTIVE
                                                                  WHERE  DATA_AGGIORNAMENTO > dDataAgg)
              ORDER BY COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_INIZIO_VAL) LOOP
              
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
          SET    DATA_FINE_VAL      = dDataInizioVal - INTERVAL '1' SECOND,
                 DATA_AGGIORNAMENTO = rec.DATA_AGGIORNAMENTO
          WHERE  ROWID              = rec.ROW_ID;
        EXCEPTION
          WHEN OTHERS THEN
            PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E002','Errore generico sull''aggiornamento della DATA_FINE_VAL su SITISUOLO_ATTIVE = '||SQLERRM||
                                               ' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE||' - Chiavi = '||vCodNazionale||'-'||
                                               nFoglio||'-'||vParticella||'-'||vSub||'-'||vDataFineValidita||'-'||vDataInizioValidita||'-'||
                                               TO_CHAR(dDataInizioVal,'DD/MM/YYYY HH24:MI:SS'));
            RETURN 1;
        END;
      END IF;
    END IF;
  END LOOP;
  
  RETURN 0;
EXCEPTION
  WHEN OTHERS THEN
    PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E001','Errore grave TabSitiSuolo: '||SQLERRM||' - RIGA = '||
                                       dbms_utility.FORMAT_ERROR_BACKTRACE||' - Chiavi = '||vCodNazionale||'-'||
                                       nFoglio||'-'||vParticella||'-'||vSub||'-'||vDataFineValidita||'-'||vDataInizioValidita||'-'||
                                       TO_CHAR(dDataInizioVal,'DD/MM/YYYY HH24:MI:SS'));
                                      
    RETURN 1;
END TabSitiSuolo;

FUNCTION TabSitiPartFuture(pIdProcessoBatch  QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE) RETURN NUMBER IS

  nCont          SIMPLE_INTEGER := 0;
  vCodNazionale  SITIPART_ATTIVE.COD_NAZIONALE%TYPE;
  nFoglio        SITIPART_ATTIVE.FOGLIO%TYPE;
  vParticella    SITIPART_ATTIVE.PARTICELLA%TYPE;
  vSub           SITIPART_ATTIVE.SUB%TYPE;
  dDataFineVal   SITIPART_ATTIVE.DATA_FINE_VAL%TYPE;
BEGIN
  FOR rec IN (SELECT S.COD_NAZIONALE, S.FOGLIO, S.PARTICELLA, S.SUB, S.DATA_LAV, S.ALLEGATO, S.SVILUPPO, S.UTENTE, 
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
              FROM   QGIS_W_SITIPART S
              WHERE  S.DATA_FINE_VAL                            > SYSDATE
              AND    PCK_SITI_SVECCHIA.IS_NUMERIC(S.PARTICELLA) = 'Y'
              ORDER BY S.COD_NAZIONALE, S.FOGLIO, S.PARTICELLA, S.SUB, S.DATA_INIZIO_VAL) LOOP
    
    vCodNazionale := rec.COD_NAZIONALE;
    nFoglio       := rec.FOGLIO;
    vParticella   := rec.PARTICELLA;
    vSub          := rec.SUB;
    dDataFineVal  := rec.DATA_FINE_VAL;
            
    SELECT COUNT(*)
    INTO   nCont
    FROM   SITIPART_ATTIVE
    WHERE  COD_NAZIONALE   = rec.COD_NAZIONALE
    AND    FOGLIO          = rec.FOGLIO 
    AND    PARTICELLA      = rec.PARTICELLA 
    AND    SUB             = rec.SUB 
    AND    DATA_INIZIO_VAL = rec.DATA_INIZIO_VAL;
    
    IF nCont = 0 THEN
      -- rc 17/06/2022 jira-79
      UPDATE SITIPART_ATTIVE
      SET    DATA_FINE_VAL = rec.DATA_INIZIO_VAL - INTERVAL '1' SECOND
      WHERE  COD_NAZIONALE = rec.COD_NAZIONALE
      AND    FOGLIO        = rec.FOGLIO 
      AND    PARTICELLA    = rec.PARTICELLA 
      AND    SUB           = rec.SUB
      AND    DATA_FINE_VAL > SYSDATE;
      
      INSERT INTO SITIPART_ATTIVE
      (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_LAV, ALLEGATO, SVILUPPO, UTENTE, DATA_INIZIO_VAL, DATA_FINE_VAL, SHAPE, AREA_PART, 
       DELTA_X_FOTO, DELTA_Y_FOTO, CONTRASTO, LUMINOSITA, COD_DIGI, COD_EDIF, FLAG1, FLAG2, FLAG3, SE_ROW_ID, NOTE, ISTATP, STATO_PROP, 
       UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
       ID_PARTICELLA, ID_CATA_PART, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, EXT_ID_PARTICELLA)
      VALUES
      (rec.COD_NAZIONALE, rec.FOGLIO, rec.PARTICELLA, rec.SUB, rec.DATA_LAV, rec.ALLEGATO, rec.SVILUPPO, rec.UTENTE, 
       rec.DATA_INIZIO_VAL,rec.DATA_FINE_VAL, rec.SHAPE, rec.AREA_PART,rec.DELTA_X_FOTO, rec.DELTA_Y_FOTO, rec.CONTRASTO, rec.LUMINOSITA, rec.COD_DIGI, 
       rec.COD_EDIF, rec.FLAG1, rec.FLAG2, rec.FLAG3, rec.SE_ROW_ID,rec.NOTE, rec.ISTATP, rec.STATO_PROP,rec.UTENTE_FINE, rec.UTENTE_PROP, 
       rec.UTENTE_PROP_FINE,rec.ID_TRASF, rec.ID_TRASF_FINE, rec.SORGENTE, rec.VALI_PROD, rec.TAVOLA, rec.FLAGCARICO,rec.DATA_AGGIORNAMENTO,
       rec.ID_PARTICELLA, rec.ID_CATA_PART,rec.ALMOST_DEAD, rec.FLAG_PROVENIENZA, rec.SYNC_SV_ID,rec.MAX_ID_PARTICELLA);
    ELSE
      UPDATE SITIPART_ATTIVE
      SET    DATA_LAV           = rec.DATA_LAV, 
             ALLEGATO           = rec.ALLEGATO, 
             SVILUPPO           = rec.SVILUPPO, 
             UTENTE             = rec.UTENTE, 
             DATA_FINE_VAL      = rec.DATA_FINE_VAL, 
             SHAPE              = rec.SHAPE, 
             AREA_PART          = rec.AREA_PART, 
             DELTA_X_FOTO       = rec.DELTA_X_FOTO, 
             DELTA_Y_FOTO       = rec.DELTA_Y_FOTO, 
             CONTRASTO          = rec.CONTRASTO, 
             LUMINOSITA         = rec.LUMINOSITA, 
             COD_DIGI           = rec.COD_DIGI, 
             COD_EDIF           = rec.COD_EDIF, 
             FLAG1              = rec.FLAG1, 
             FLAG2              = rec.FLAG2, 
             FLAG3              = rec.FLAG3, 
             NOTE               = rec.NOTE, 
             ISTATP             = rec.ISTATP, 
             STATO_PROP         = rec.STATO_PROP, 
             UTENTE_FINE        = rec.UTENTE_FINE, 
             UTENTE_PROP        = rec.UTENTE_PROP, 
             UTENTE_PROP_FINE   = rec.UTENTE_PROP_FINE, 
             ID_TRASF           = rec.ID_TRASF, 
             ID_TRASF_FINE      = rec.ID_TRASF_FINE, 
             SORGENTE           = rec.SORGENTE, 
             VALI_PROD          = rec.VALI_PROD, 
             TAVOLA             = rec.TAVOLA, 
             FLAGCARICO         = rec.FLAGCARICO, 
             DATA_AGGIORNAMENTO = rec.DATA_AGGIORNAMENTO, 
             ID_PARTICELLA      = rec.ID_PARTICELLA, 
             ID_CATA_PART       = rec.ID_CATA_PART, 
             ALMOST_DEAD        = rec.ALMOST_DEAD, 
             FLAG_PROVENIENZA   = rec.FLAG_PROVENIENZA, 
             SYNC_SV_ID         = rec.SYNC_SV_ID, 
             EXT_ID_PARTICELLA  = rec.MAX_ID_PARTICELLA
      WHERE  COD_NAZIONALE      = rec.COD_NAZIONALE
      AND    FOGLIO             = rec.FOGLIO 
      AND    PARTICELLA         = rec.PARTICELLA 
      AND    SUB                = rec.SUB 
      AND    DATA_INIZIO_VAL    = rec.DATA_INIZIO_VAL;
    END IF;
  END LOOP;
 
  RETURN 0;
EXCEPTION
  WHEN OTHERS THEN
    PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E001','Errore grave TabSitiPartFuture: '||SQLERRM||' - RIGA = '||
                                       dbms_utility.FORMAT_ERROR_BACKTRACE||' - COD_NAZIONALE = '||vCodNazionale||' - '||
                                       'FOGLIO = '||nFoglio||' - PARTICELLA = '||vParticella||' - SUB = '||vSub||
                                       ' - DATA_FINE_VAL = '||dDataFineVal);
                                      
    RETURN 1;
END TabSitiPartFuture;

FUNCTION TabSitiPart(pIdProcessoBatch     QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE,
                     pDtUltimaEsecuzione  QGIS_D_NOME_BATCH.DT_ULTIMA_ESECUZIONE%TYPE) RETURN NUMBER IS

  nCont                SIMPLE_INTEGER := 0;
  dDataInizioVal       DATE;
  vCodNazionale        SITISUOLO_ATTIVE.COD_NAZIONALE%TYPE;
  nFoglio              SITISUOLO_ATTIVE.FOGLIO%TYPE;
  vParticella          SITISUOLO_ATTIVE.PARTICELLA%TYPE;
  vSub                 SITISUOLO_ATTIVE.SUB%TYPE;
  vDataFineValidita    VARCHAR2(30);
  vDataInizioValidita  VARCHAR2(30);
BEGIN
  FOR rec IN (SELECT S.*,
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
              FROM   QGIS_W_SITIPART S
              WHERE  S.DATA_FINE_VAL                             < SYSDATE
              AND    PCK_SITI_SVECCHIA.IS_NUMERIC (S.PARTICELLA) = 'Y'
              ORDER BY S.COD_NAZIONALE, S.FOGLIO, S.PARTICELLA, S.SUB, S.DATA_INIZIO_VAL) LOOP
              
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
    AND    DATA_INIZIO_VAL = rec.DATA_INIZIO_VAL;
    
    IF nCont = 0 THEN
       -- faccio scadere il record che copre la validita del record da inserire
      UPDATE SITIPART_ATTIVE
      SET    DATA_FINE_VAL      = rec.DATA_INIZIO_VAL - INTERVAL '1' SECOND,
             DATA_AGGIORNAMENTO = rec.DATA_AGGIORNAMENTO
      WHERE  COD_NAZIONALE      = rec.COD_NAZIONALE
      AND    FOGLIO             = rec.FOGLIO
      AND    PARTICELLA         = rec.PARTICELLA
      AND    SUB                = rec.SUB
      AND    DATA_FINE_VAL      > rec.DATA_INIZIO_VAL
      AND    DATA_INIZIO_VAL    < rec.DATA_INIZIO_VAL;
          
      INSERT INTO SITIPART_ATTIVE
      (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_LAV, ALLEGATO, SVILUPPO, UTENTE, DATA_INIZIO_VAL, DATA_FINE_VAL, SHAPE, AREA_PART, 
       DELTA_X_FOTO, DELTA_Y_FOTO, CONTRASTO, LUMINOSITA, COD_DIGI, COD_EDIF, FLAG1, FLAG2, FLAG3, SE_ROW_ID, NOTE, ISTATP, STATO_PROP, 
       UTENTE_FINE, UTENTE_PROP, UTENTE_PROP_FINE, ID_TRASF, ID_TRASF_FINE, SORGENTE, VALI_PROD, TAVOLA, FLAGCARICO, DATA_AGGIORNAMENTO, 
       ID_PARTICELLA, ID_CATA_PART, ALMOST_DEAD, FLAG_PROVENIENZA, SYNC_SV_ID, EXT_ID_PARTICELLA)
      VALUES
      (rec.COD_NAZIONALE, rec.FOGLIO, rec.PARTICELLA, rec.SUB, rec.DATA_LAV, rec.ALLEGATO, rec.SVILUPPO, rec.UTENTE, 
       rec.DATA_INIZIO_VAL,rec.DATA_FINE_VAL, rec.SHAPE, rec.AREA_PART,rec.DELTA_X_FOTO, rec.DELTA_Y_FOTO, rec.CONTRASTO, rec.LUMINOSITA, rec.COD_DIGI, 
       rec.COD_EDIF, rec.FLAG1, rec.FLAG2, rec.FLAG3, rec.SE_ROW_ID,rec.NOTE, rec.ISTATP, rec.STATO_PROP,rec.UTENTE_FINE, rec.UTENTE_PROP, 
       rec.UTENTE_PROP_FINE,rec.ID_TRASF, rec.ID_TRASF_FINE, rec.SORGENTE, rec.VALI_PROD, rec.TAVOLA, rec.FLAGCARICO,rec.DATA_AGGIORNAMENTO,
       rec.ID_PARTICELLA, rec.ID_CATA_PART,rec.ALMOST_DEAD, rec.FLAG_PROVENIENZA, rec.SYNC_SV_ID,rec.MAX_ID_PARTICELLA);
    ELSE
      UPDATE SITIPART_ATTIVE
      SET    DATA_LAV           = rec.DATA_LAV, 
             ALLEGATO           = rec.ALLEGATO, 
             SVILUPPO           = rec.SVILUPPO, 
             UTENTE             = rec.UTENTE, 
             DATA_FINE_VAL      = rec.DATA_FINE_VAL, 
             SHAPE              = rec.SHAPE, 
             AREA_PART          = rec.AREA_PART, 
             DELTA_X_FOTO       = rec.DELTA_X_FOTO, 
             DELTA_Y_FOTO       = rec.DELTA_Y_FOTO, 
             CONTRASTO          = rec.CONTRASTO, 
             LUMINOSITA         = rec.LUMINOSITA, 
             COD_DIGI           = rec.COD_DIGI, 
             COD_EDIF           = rec.COD_EDIF, 
             FLAG1              = rec.FLAG1, 
             FLAG2              = rec.FLAG2, 
             FLAG3              = rec.FLAG3, 
             NOTE               = rec.NOTE, 
             ISTATP             = rec.ISTATP, 
             STATO_PROP         = rec.STATO_PROP, 
             UTENTE_FINE        = rec.UTENTE_FINE, 
             UTENTE_PROP        = rec.UTENTE_PROP, 
             UTENTE_PROP_FINE   = rec.UTENTE_PROP_FINE, 
             ID_TRASF           = rec.ID_TRASF, 
             ID_TRASF_FINE      = rec.ID_TRASF_FINE, 
             SORGENTE           = rec.SORGENTE, 
             VALI_PROD          = rec.VALI_PROD, 
             TAVOLA             = rec.TAVOLA, 
             FLAGCARICO         = rec.FLAGCARICO, 
             DATA_AGGIORNAMENTO = rec.DATA_AGGIORNAMENTO, 
             ID_PARTICELLA      = rec.ID_PARTICELLA, 
             ID_CATA_PART       = rec.ID_CATA_PART, 
             ALMOST_DEAD        = rec.ALMOST_DEAD, 
             FLAG_PROVENIENZA   = rec.FLAG_PROVENIENZA, 
             SYNC_SV_ID         = rec.SYNC_SV_ID, 
             EXT_ID_PARTICELLA  = rec.MAX_ID_PARTICELLA
      WHERE  COD_NAZIONALE      = rec.COD_NAZIONALE
      AND    FOGLIO             = rec.FOGLIO 
      AND    PARTICELLA         = rec.PARTICELLA 
      AND    SUB                = rec.SUB 
      AND    DATA_INIZIO_VAL    = rec.DATA_INIZIO_VAL;
    END IF;
  END LOOP;
  
  FOR rec IN (SELECT ROWID ROW_ID,COD_NAZIONALE,FOGLIO,PARTICELLA,SUB,DATA_FINE_VAL,DATA_INIZIO_VAL,DATA_AGGIORNAMENTO
              FROM   SITIPART_ATTIVE
              WHERE  (COD_NAZIONALE, FOGLIO, PARTICELLA, SUB) IN (SELECT DISTINCT COD_NAZIONALE, FOGLIO, PARTICELLA, SUB
                                                                  FROM   SITIPART_ATTIVE
                                                                  WHERE  DATA_AGGIORNAMENTO > pDtUltimaEsecuzione)
              ORDER BY COD_NAZIONALE, FOGLIO, PARTICELLA, SUB, DATA_INIZIO_VAL) LOOP
  
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
          SET    DATA_FINE_VAL      = dDataInizioVal - INTERVAL '1' SECOND,
                 DATA_AGGIORNAMENTO = rec.DATA_AGGIORNAMENTO
          WHERE  ROWID              = rec.ROW_ID;
        EXCEPTION
          WHEN OTHERS THEN
            PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E002','Errore generico sull''aggiornamento della DATA_FINE_VAL su SITIPART_ATTIVE = '||SQLERRM||
                                               ' - RIGA = '||DBMS_UTILITY.FORMAT_ERROR_BACKTRACE||' - Chiavi = '||vCodNazionale||'-'||
                                               nFoglio||'-'||vParticella||'-'||vSub||'-'||vDataFineValidita||'-'||vDataInizioValidita||'-'||
                                               TO_CHAR(dDataInizioVal,'DD/MM/YYYY HH24:MI:SS'));
            RETURN 1;
        END;
      END IF;
    END IF;
  END LOOP;  
    
  RETURN 0;
EXCEPTION
  WHEN OTHERS THEN
    PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E001','Errore grave TabSitiPart: '||SQLERRM||' - RIGA = '||
                                       dbms_utility.FORMAT_ERROR_BACKTRACE||' - Chiavi = '||vCodNazionale||'-'||
                                       nFoglio||'-'||vParticella||'-'||vSub||'-'||vDataFineValidita||'-'||vDataInizioValidita);
                                      
    RETURN 1;
END TabSitiPart;

FUNCTION PopolamentoQgis(pIdProcessoBatch     QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE,
                         pDtUltimaEsecuzione  QGIS_D_NOME_BATCH.DT_ULTIMA_ESECUZIONE%TYPE) RETURN NUMBER IS

  nIdVersioneParticella  QGIS_T_VERSIONE_PARTICELLA.ID_VERSIONE_PARTICELLA%TYPE;
  vCodErrore             VARCHAR2(1);
  vDescErrore            VARCHAR2(4000);
  vCodNazionale          SITISUOLO_ATTIVE.COD_NAZIONALE%TYPE;
  nFoglio                SITISUOLO_ATTIVE.FOGLIO%TYPE;
  vParticella            SITISUOLO_ATTIVE.PARTICELLA%TYPE;
  vSub                   SITISUOLO_ATTIVE.SUB%TYPE;
  vDataInizioValidita    VARCHAR2(30);
  bFound                 BOOLEAN := FALSE;
  nCampagna              NUMBER;
  dDataFineValidita      QGIS_T_VERSIONE_PARTICELLA.DATA_FINE_VALIDITA%TYPE;
  anniCampagna           ORA_MINING_NUMBER_NT := ORA_MINING_NUMBER_NT();
  nCont                  SIMPLE_INTEGER := 0;
BEGIN
  FOR recPart IN (SELECT *
                  FROM   SITIPART_ATTIVE
                  WHERE  DATA_AGGIORNAMENTO >= pDtUltimaEsecuzione
                  AND    SHAPE               IS NOT NULL
                  ORDER BY COD_NAZIONALE,FOGLIO,PARTICELLA,SUB,DATA_INIZIO_VAL) LOOP

    anniCampagna.DELETE;
    
    UPDATE QGIS_T_VERSIONE_PARTICELLA
    SET    AREA                           = recPart.AREA_PART,
           DATA_FINE_VALIDITA             = (CASE WHEN recPart.DATA_FINE_VAL = TO_DATE('31/12/9999','dd/mm/yyyy') THEN NULL 
                                             ELSE recPart.DATA_FINE_VAL END),
           DATA_AGGIORNAMENTO             = NVL(recPart.DATA_AGGIORNAMENTO,recPart.DATA_INIZIO_VAL),
           SHAPE                          = recPart.SHAPE,
           EXT_ID_UTENTE_LAVOR_SITICLIENT = recPart.UTENTE,
           ID_TIPO_SORGENTE_SUOLO         = 99
    WHERE  EXT_COD_NAZIONALE              = recPart.COD_NAZIONALE
    AND    DATA_INIZIO_VALIDITA           = recPart.DATA_INIZIO_VAL
    AND    NVL(EXT_ID_PARTICELLA,0)       = NVL(recPart.EXT_ID_PARTICELLA,0)
    AND    FOGLIO                         = recPart.FOGLIO
    AND    PARTICELLA                     = recPart.PARTICELLA
    AND    SUBALTERNO                     = recPart.SUB;
    
    IF SQL%NOTFOUND THEN    
      UPDATE QGIS_T_VERSIONE_PARTICELLA
      SET    DATA_FINE_VALIDITA       = recPart.DATA_INIZIO_VAL - INTERVAL '1' SECOND
      WHERE  EXT_COD_NAZIONALE        = recPart.COD_NAZIONALE
      AND    recPart.DATA_FINE_VAL    BETWEEN DATA_INIZIO_VALIDITA AND NVL(DATA_FINE_VALIDITA,recPart.DATA_FINE_VAL)
      AND    NVL(EXT_ID_PARTICELLA,0) = NVL(recPart.EXT_ID_PARTICELLA,0)
      AND    FOGLIO                   = recPart.FOGLIO
      AND    PARTICELLA               = recPart.PARTICELLA
      AND    SUBALTERNO               = recPart.SUB;

      INSERT INTO QGIS_T_VERSIONE_PARTICELLA
      (ID_VERSIONE_PARTICELLA, AREA, EXT_COD_NAZIONALE, DATA_INIZIO_VALIDITA,
       DATA_FINE_VALIDITA,
       DATA_AGGIORNAMENTO, EXT_ID_PARTICELLA, FOGLIO,PARTICELLA, 
       SHAPE,SUBALTERNO,EXT_ID_UTENTE_LAVOR_SITICLIENT,ID_TIPO_SORGENTE_SUOLO)
      VALUES
      (SEQ_QGIS_T_VERSIONE_PARTICELLA.NEXTVAL,recPart.AREA_PART, recPart.COD_NAZIONALE, recPart.DATA_INIZIO_VAL,
       (CASE WHEN recPart.DATA_FINE_VAL = TO_DATE('31/12/9999','DD/MM/YYYY') THEN NULL ELSE recPart.DATA_FINE_VAL END),
       NVL(recPart.DATA_AGGIORNAMENTO,recPart.DATA_INIZIO_VAL),recPart.EXT_ID_PARTICELLA , recPart.FOGLIO,recPart.PARTICELLA, 
       recPart.SHAPE,recPart.SUB,recPart.UTENTE,99)
      RETURNING ID_VERSIONE_PARTICELLA INTO nIdVersioneParticella;
        
      -- rc 06/05/2022 jira-72
      IF recPart.DATA_FINE_VAL = TO_DATE('31/12/9999','DD/MM/YYYY') THEN
        FOR i IN EXTRACT (YEAR FROM recPart.DATA_INIZIO_VAL)..EXTRACT (YEAR FROM SYSDATE) LOOP
          anniCampagna.EXTEND;
          anniCampagna(anniCampagna.COUNT) := i;
        END LOOP;
      ELSE
        FOR recData IN (SELECT (recPart.DATA_INIZIO_VAL + ROWNUM -1) DATA
                        FROM   ALL_OBJECTS
                        WHERE  ROWNUM <= recPart.DATA_FINE_VAL - recPart.DATA_INIZIO_VAL + 1) LOOP
                        
          IF recData.DATA = TO_DATE('31/12/'||EXTRACT (YEAR FROM recData.DATA),'DD/MM/YYYY') THEN
            anniCampagna.EXTEND;
            anniCampagna(anniCampagna.COUNT) := EXTRACT (YEAR FROM recData.DATA);
          END IF;
        END LOOP;
      END IF;
        
      FOR i IN 1..anniCampagna.COUNT LOOP
      
        SELECT COUNT(*)
        INTO   nCont
        FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_REGISTRO_PARTICELLE RP
        WHERE  VP.EXT_COD_NAZIONALE      = recPart.COD_NAZIONALE
        AND    VP.FOGLIO                 = recPart.FOGLIO  
        AND    VP.PARTICELLA             = recPart.PARTICELLA
        AND    VP.SUBALTERNO             = recPart.SUB
        AND    RP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA
        AND    RP.DATA_FINE_VALIDITA     IS NULL
        AND    RP.CAMPAGNA               = anniCampagna(i);
          
        IF nCont != 0 THEN
          EXIT;
        END IF;
          
        INSERT INTO QGIS_T_REGISTRO_PARTICELLE
        (ID_REGISTRO_PARTICELLE, EXT_COD_NAZIONALE, FOGLIO, CAMPAGNA, ID_VERSIONE_PARTICELLA,DATA_INIZIO_VALIDITA, DATA_FINE_VALIDITA)
        VALUES
        (SEQ_QGIS_T_REGISTRO_PARTICELLE.NEXTVAL,recPart.COD_NAZIONALE,recPart.FOGLIO,anniCampagna(i),nIdVersioneParticella,SYSDATE,NULL);
      END LOOP;
    END IF;
    
    SELECT ID_VERSIONE_PARTICELLA,DATA_FINE_VALIDITA
    INTO   nIdVersioneParticella,dDataFineValidita
    FROM   QGIS_T_VERSIONE_PARTICELLA
    WHERE  EXT_COD_NAZIONALE        = recPart.COD_NAZIONALE
    AND    DATA_INIZIO_VALIDITA     = recPart.DATA_INIZIO_VAL
    AND    NVL(EXT_ID_PARTICELLA,0) = NVL(recPart.EXT_ID_PARTICELLA,0)
    AND    FOGLIO                   = recPart.FOGLIO
    AND    PARTICELLA               = recPart.PARTICELLA
    AND    SUBALTERNO               = recPart.SUB;
      
    -- rc 06/05/2022 jira-72
    IF dDataFineValidita IS NOT NULL AND dDataFineValidita < SYSDATE THEN
      UPDATE QGIS_T_REGISTRO_PARTICELLE
      SET    DATA_FINE_VALIDITA     = TO_DATE('31/12/'||CAMPAGNA,'DD/MM/YYYY')
      WHERE  ID_VERSIONE_PARTICELLA = nIdVersioneParticella
      AND    TO_DATE('31/12/'||CAMPAGNA,'DD/MM/YYYY') > dDataFineValidita;
    END IF; 
  END LOOP;
  
  FOR rec IN (SELECT SA.COD_NAZIONALE,SA.FOGLIO,SA.PARTICELLA,SA.SUB,SA.DATA_INIZIO_VAL,SA.CAMPAGNA,
                     (SELECT CAST(COLLECT(OBJ_SUOLI(SA1.CAMPAGNA,SA1.AREA_COLT,SA1.DATA_FINE_VAL,SA1.COD_VARIETA,99,NULL,
                                                    SA1.SHAPE,SA1.UTENTE,SA1.SE_ROW_ID)) AS LIST_SUOLI)
                      FROM   SITISUOLO_ATTIVE SA1
                      WHERE  SA1.COD_NAZIONALE   = SA.COD_NAZIONALE
                      AND    SA1.FOGLIO          = SA.FOGLIO
                      AND    SA1.PARTICELLA      = SA.PARTICELLA
                      AND    SA1.SUB             = SA.SUB
                      AND    SA1.DATA_INIZIO_VAL = SA.DATA_INIZIO_VAL) ARRAY_SUOLI
              FROM   SITISUOLO_ATTIVE SA
              WHERE  SA.SHAPE               IS NOT NULL
              AND    SA.COD_VARIETA        != 0
              AND    SA.DATA_AGGIORNAMENTO >= pDtUltimaEsecuzione
              --AND    SA.DATA_FINE_VAL       > SYSDATE
              AND    NOT EXISTS             (SELECT 'X'
                                             FROM   QGIS_T_SUOLO_RILEVATO SR
                                             WHERE  SR.SE_ROW_ID = SA.SE_ROW_ID)
              GROUP BY SA.COD_NAZIONALE,SA.FOGLIO,SA.PARTICELLA,SA.SUB,SA.DATA_INIZIO_VAL,SA.CAMPAGNA
              -- rc 11/05/2022
              ORDER BY SA.COD_NAZIONALE,SA.FOGLIO,SA.PARTICELLA,SA.SUB,SA.DATA_INIZIO_VAL,SA.CAMPAGNA) LOOP
              
    vCodNazionale       := rec.COD_NAZIONALE;
    nFoglio             := rec.FOGLIO;
    vParticella         := rec.PARTICELLA;
    vSub                := rec.SUB;
    vDataInizioValidita := TO_CHAR(rec.DATA_INIZIO_VAL,'DD/MM/YYYY HH24:MI:SS');
    nCampagna           := rec.CAMPAGNA;
    
    -- rc 22/10/2021 jira-56
    /*UPDATE QGIS_T_SUOLO_RILEVATO SR
    SET    SR.DATA_FINE_VALIDITA = rec.DATA_INIZIO_VAL - INTERVAL '1' SECOND
    WHERE  SR.DATA_FINE_VALIDITA IS NULL
    AND    EXISTS                (SELECT 'X'
                                  FROM   QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_VERSIONE_PARTICELLA VP
                                  WHERE  SP.ID_SUOLO_RILEVATO      = SR.ID_SUOLO_RILEVATO
                                  AND    SP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA
                                  AND    VP.DATA_FINE_VALIDITA     IS NULL
                                  AND    VP.EXT_COD_NAZIONALE      = rec.COD_NAZIONALE
                                  AND    VP.FOGLIO                 = rec.FOGLIO
                                  AND    VP.PARTICELLA             = rec.PARTICELLA
                                  AND    VP.SUBALTERNO             = rec.SUB);*/
    
    PCK_QGIS_LIBRERIA.InserisciSuoloNuovo(rec.COD_NAZIONALE,rec.FOGLIO,rec.PARTICELLA,rec.SUB,rec.DATA_INIZIO_VAL,rec.ARRAY_SUOLI,
                                          rec.CAMPAGNA,vCodErrore,vDescErrore);
                                          
    IF vCodErrore != 0 THEN
      PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E001','Errore grave PopolamentoQgis: '||vDescErrore||' - Chiavi = '||
                                         vCodNazionale||' - '||nFoglio||' - '||vParticella||' - '||vSub||' - '||vDataInizioValidita||' -'||
                                         nCampagna);
                                      
      RETURN 1;
    END IF;
  END LOOP;
  
  FOR rec IN (SELECT SA.COD_NAZIONALE,SA.FOGLIO,SA.PARTICELLA,SA.SUB,SA.DATA_INIZIO_VAL,SR.ID_SUOLO_RILEVATO,SR.SE_ROW_ID,
                     SA.UTENTE EXT_ID_UTENTE_LAVOR_SITICLIENT,SA.SHAPE,SR.DATA_AGGIORNAMENTO
              FROM   SITISUOLO_ATTIVE SA,QGIS_T_SUOLO_RILEVATO SR
              WHERE  SA.SHAPE               IS NOT NULL
              AND    SA.COD_VARIETA        != 0
              AND    SA.DATA_AGGIORNAMENTO >= pDtUltimaEsecuzione
              AND    SA.DATA_FINE_VAL       > SYSDATE
              AND    SR.SE_ROW_ID           = SA.SE_ROW_ID
              AND    NOT EXISTS             (SELECT 'x' 
                                             FROM   QGIS_T_SUOLO_PARTICELLA SP 
                                             WHERE  SR.ID_SUOLO_RILEVATO = SP.ID_SUOLO_RILEVATO)) LOOP
    
    INSERT INTO QGIS_T_SUOLO_PARTICELLA
    (ID_SUOLO_PARTICELLA, ID_SUOLO_RILEVATO, ID_VERSIONE_PARTICELLA, AREA, 
     DATA_AGGIORNAMENTO, 
     PROG_POLIGONO, SHAPE,EXT_ID_UTENTE_AGGIORNAMENTO, 
     EXT_ID_UTENTE_LAVOR_SITICLIENT, SE_ROW_ID)
    SELECT SEQ_QGIS_T_SUOLO_PARTICELLA.NEXTVAL,rec.ID_SUOLO_RILEVATO,VP.ID_VERSIONE_PARTICELLA,SMRGAA.AABGAD_SDO.SDO_AREA(rec.SHAPE),
           rec.DATA_AGGIORNAMENTO,
           NVL((SELECT MAX(SP1.PROG_POLIGONO) + 1
                FROM   QGIS_T_SUOLO_PARTICELLA SP1
                WHERE  SP1.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA),1),rec.SHAPE,NULL,
           rec.EXT_ID_UTENTE_LAVOR_SITICLIENT,rec.SE_ROW_ID 
    FROM   QGIS_T_VERSIONE_PARTICELLA VP
    WHERE  VP.EXT_COD_NAZIONALE  = rec.COD_NAZIONALE
    AND    VP.FOGLIO             = rec.FOGLIO
    AND    VP.PARTICELLA         = rec.PARTICELLA
    AND    VP.SUBALTERNO         = rec.SUB
    AND    VP.DATA_FINE_VALIDITA IS NULL;
  END LOOP;
  
  -- rc 27/08/2021 jira-46
  FOR rec IN (SELECT SL.ID_EVENTO_LAVORAZIONE,SR.EXT_COD_NAZIONALE,SR.FOGLIO,SR.SHAPE,SL.NOTE_RICHIESTA,SL.IDENTIFICATIVO_PRATICA_ORIGINE,
                     SL.ID_SUOLO_LAVORAZIONE
              FROM   QGIS_T_SUOLO_LAVORAZIONE SL, QGIS_T_EVENTO_LAVORAZIONE EL, QGIS_T_SUOLO_RILEVATO SR
              WHERE  SL.FLAG_LAVORATO          = 'N'
              AND    SL.ID_EVENTO_LAVORAZIONE  = EL.ID_EVENTO_LAVORAZIONE 
              AND    SR.DATA_FINE_VALIDITA     IS NOT NULL
              AND    SR.DATA_FINE_VALIDITA    >= pDtUltimaEsecuzione
              AND    EL.ID_LISTA_LAVORAZIONE   IN (SELECT ID_LISTA_LAVORAZIONE 
                                                   FROM   QGIS_T_LISTA_LAVORAZIONE LL 
                                                   WHERE  LL.CODICE            LIKE 'IS%'
                                                   AND    SL.ID_SUOLO_RILEVATO = SR.ID_SUOLO_RILEVATO)) LOOP
    bFound := FALSE;
    
    FOR recSuolo IN (SELECT SR1.ID_SUOLO_RILEVATO,SR1.SHAPE
                     FROM   QGIS_T_SUOLO_RILEVATO SR1
                     WHERE  SR1.DATA_FINE_VALIDITA IS NULL
                     AND    SR1.EXT_COD_NAZIONALE  = rec.EXT_COD_NAZIONALE
                     AND    SR1.FOGLIO             = rec.FOGLIO
                     AND    SR1.DATA_FINE_VALIDITA IS NULL) LOOP
       
      IF SMRGAA.AABGAD_SDO.SDO_ANYINTERACT(recSuolo.SHAPE,rec.SHAPE) = 1 THEN
        IF SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(recSuolo.SHAPE,rec.SHAPE)) > 0 THEN
          INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
          (ID_SUOLO_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_SUOLO_RILEVATO, FLAG_SOSPENSIONE, FLAG_CESSATO, NOTE_RICHIESTA,
           IDENTIFICATIVO_PRATICA_ORIGINE)
          VALUES
          (SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,rec.ID_EVENTO_LAVORAZIONE,recSuolo.ID_SUOLO_RILEVATO,'N','N',rec.NOTE_RICHIESTA,
           rec.IDENTIFICATIVO_PRATICA_ORIGINE);
           
          bFound := TRUE;
        END IF;
      END IF;
    END LOOP;
    
    IF NOT bFound THEN
      DELETE QGIS_T_SUOLO_LAVORAZIONE 
      WHERE  ID_SUOLO_LAVORAZIONE = rec.ID_SUOLO_LAVORAZIONE;
    END IF;
  END LOOP;
  
  RETURN 0;
EXCEPTION
  WHEN OTHERS THEN
    PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E001','Errore grave PopolamentoQgis: '||SQLERRM||' - RIGA = '||
                                       dbms_utility.FORMAT_ERROR_BACKTRACE||' - Chiavi = '||vCodNazionale||' - '||nFoglio||' - '||
                                       vParticella||' - '||vSub||' - '||vDataInizioValidita);
                                      
    RETURN 1;
END PopolamentoQgis;

FUNCTION ListeLav(pIdProcessoBatch  QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE) RETURN NUMBER IS

  nIdListaLavorazione      QGIS_T_LISTA_LAVORAZIONE.ID_LISTA_LAVORAZIONE%TYPE;
  nIdEventoLavorazione     QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE;
  nContPartAtt             SIMPLE_INTEGER := 0;
  nIdVersioneParticella    QGIS_T_VERSIONE_PARTICELLA.ID_VERSIONE_PARTICELLA%TYPE;
  nContSuoloAtt            SIMPLE_INTEGER := 0;
  nIdLav                   SITIPLAV.ID_LAV%TYPE;
  nIdParticella            SITIPLAV.ID_PARTICELLA%TYPE;
  nExtIdAzienda            QGIS_T_EVENTO_LAVORAZIONE.EXT_ID_AZIENDA%TYPE;
  dDataAgg                 DATE;
  nExtIdParticella         SMRGAA.DB_PARTICELLA_CERTIFICATA.ID_PARTICELLA%TYPE;
BEGIN
  SELECT MIN(DATA_AGGIORNAMENTO)
  INTO   dDataAgg
  FROM   QGIS_W_SITIPLAV;

  FOR rec IN (SELECT *
              FROM   SITILISTALAV
              WHERE  CAMPAGNA >= 2015) LOOP
    
    BEGIN
      SELECT ID_LISTA_LAVORAZIONE
      INTO   nIdListaLavorazione
      FROM   QGIS_T_LISTA_LAVORAZIONE
      WHERE  CAMPAGNA = rec.CAMPAGNA
      AND    CODICE   = rec.PROV_RIF;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        INSERT INTO QGIS_T_LISTA_LAVORAZIONE
        (ID_LISTA_LAVORAZIONE, ID_TIPO_LISTA, CAMPAGNA, CODICE, DESCRIZIONE_LISTA)
        VALUES
        (SEQ_QGIS_T_LISTA_LAVORAZIONE.NEXTVAL,2,rec.CAMPAGNA,rec.PROV_RIF,rec.DESCRIZIONE)
        RETURNING ID_LISTA_LAVORAZIONE INTO nIdListaLavorazione;
    END;
    
    FOR recPLav IN (SELECT P.*
                    FROM   QGIS_W_SITIPLAV P
                    WHERE  P.LAST      = 1
                    AND    P.ID_LAV    = rec.ID_LAV
                    AND    P.DATA_LAV  IS NOT NULL
                    ORDER BY P.COD_NAZIONALE, P.FOGLIO, P.PARTICELLA, P.SUB, P.DATAINS) LOOP
      
      nIdLav        := rec.ID_LAV;
      nIdParticella := recPLav.ID_PARTICELLA;
      nExtIdAzienda := NULL;
      
      SELECT MAX(ID_PARTICELLA)
      INTO   nExtIdParticella
      FROM   SMRGAA.DB_PARTICELLA_CERTIFICATA SP
      WHERE  SP.FOGLIO              = recPLav.FOGLIO
      AND    SP.PARTICELLA          = TO_NUMBER(LTRIM(recPLav.PARTICELLA,'0'))
      AND    SP.DATA_FINE_VALIDITA  IS NULL
      AND    NVL(SP.SUBALTERNO,' ') = recPLav.SUB
      AND    recPLav.COD_NAZIONALE  IN (SELECT COD_NAZIONALE 
                                        FROM   SMRGAA.DB_SITICOMU 
                                        WHERE  ISTAT_COMUNE = SP.COMUNE
                                        AND    ((SP.SEZIONE IS NULL AND ID_SEZC IS NULL) OR 
                                                (SP.SEZIONE IS NOT NULL AND UPPER(ID_SEZC) = UPPER(SP.SEZIONE))));
      
      SELECT COUNT(*)
      INTO   nContPartAtt
      FROM   SITIPART_ATTIVE
      WHERE  ID_PARTICELLA          = recPLav.ID_PARTICELLA
      AND    TRUNC(DATA_INIZIO_VAL) = TRUNC(recPLav.DATA_LAV_P_GIS)
      AND    DATA_FINE_VAL          > SYSDATE;
      
      SELECT COUNT(*)
      INTO   nContSuoloAtt
      FROM   SITISUOLO_ATTIVE 
      WHERE  ID_PARTICELLA          = recPLav.ID_PARTICELLA
      AND    TRUNC(DATA_INIZIO_VAL) = TRUNC(recPLav.DATA_LAV_T_GIS)
      AND    DATA_FINE_VAL          > SYSDATE;
      
      IF nContPartAtt != 0 THEN
        SELECT MAX(VP.ID_VERSIONE_PARTICELLA)
        INTO   nIdVersioneParticella
        FROM   QGIS_T_VERSIONE_PARTICELLA VP,SITIPART_ATTIVE PA,QGIS_T_REGISTRO_PARTICELLE RP
        WHERE  PA.ID_PARTICELLA          = recPLav.ID_PARTICELLA
        AND    VP.DATA_INIZIO_VALIDITA   = PA.DATA_INIZIO_VAL
        AND    VP.EXT_COD_NAZIONALE      = PA.COD_NAZIONALE
        AND    VP.FOGLIO                 = PA.FOGLIO
        AND    VP.PARTICELLA             = PA.PARTICELLA
        AND    VP.SUBALTERNO             = PA.SUB
        -- RC 21/04/2022 JIRA-72
        AND    RP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA
        AND    RP.DATA_FINE_VALIDITA     IS NULL
        AND    RP.CAMPAGNA               = rec.CAMPAGNA;
        
        nExtIdAzienda := PCK_SITI_SVECCHIA.ReturnAzienda(rec.CAMPAGNA,nIdVersioneParticella,rec.PROV_RIF,recPLav.DATAINS);
                                       
        SELECT MAX(ID_EVENTO_LAVORAZIONE)
        INTO   nIdEventoLavorazione
        FROM   QGIS_T_EVENTO_LAVORAZIONE
        WHERE  ID_LISTA_LAVORAZIONE  = nIdListaLavorazione
        AND    NVL(EXT_ID_AZIENDA,0) = NVL(nExtIdAzienda,0)
        AND    DATA_INSERIMENTO      = recPLav.DATAINS
        AND    DATA_LAVORAZIONE      > dDataAgg;
        
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
         FLAG_SOSPENSIONE,FLAG_CESSATO,NOTE_LAVORAZIONE, NOTE_RICHIESTA,EXT_ID_PARTICELLA, EXT_COD_NAZIONALE, FOGLIO, 
         PARTICELLA,SUBALTERNO)
        VALUES
        (SEQ_QGIS_T_PARTICELLA_LAVORAZI.NEXTVAL,nIdEventoLavorazione,nIdVersioneParticella,NVL(recPLav.DESC_MOTI,' '),
         DECODE(recPLav.DATASOSP,NULL,'N','S'),'N',recPLav.NOTE_LAV,recPLav.NOTE,nExtIdParticella,recPLav.COD_NAZIONALE, recPLav.FOGLIO, 
         recPLav.PARTICELLA,recPLav.SUB);
      END IF;
      
      IF nContSuoloAtt != 0 THEN
        SELECT MAX(ID_EVENTO_LAVORAZIONE)
        INTO   nIdEventoLavorazione
        FROM   QGIS_T_EVENTO_LAVORAZIONE
        WHERE  ID_LISTA_LAVORAZIONE  = nIdListaLavorazione
        AND    NVL(EXT_ID_AZIENDA,0) = NVL(nExtIdAzienda,0)
        AND    DATA_INSERIMENTO      = recPLav.DATAINS
        AND    DATA_LAVORAZIONE      > dDataAgg;
        
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
        SELECT MAX(VP.ID_VERSIONE_PARTICELLA)
        INTO   nIdVersioneParticella
        FROM   QGIS_T_VERSIONE_PARTICELLA VP,SITIPART_ATTIVE PA,QGIS_T_REGISTRO_PARTICELLE RP
        WHERE  PA.ID_PARTICELLA        = recPLav.ID_PARTICELLA
        AND    VP.DATA_INIZIO_VALIDITA = PA.DATA_INIZIO_VAL
        AND    VP.EXT_COD_NAZIONALE    = PA.COD_NAZIONALE
        AND    VP.FOGLIO               = PA.FOGLIO
        AND    VP.PARTICELLA           = PA.PARTICELLA
        AND    VP.SUBALTERNO           = PA.SUB
        -- RC 21/04/2022 JIRA-72
        AND    RP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA
        AND    RP.DATA_FINE_VALIDITA     IS NULL
        AND    RP.CAMPAGNA               = rec.CAMPAGNA;
        
        nExtIdAzienda := PCK_SITI_SVECCHIA.ReturnAzienda(rec.CAMPAGNA,nIdVersioneParticella,rec.PROV_RIF,recPLav.DATAINS);
        
        SELECT MAX(ID_EVENTO_LAVORAZIONE)
        INTO   nIdEventoLavorazione
        FROM   QGIS_T_EVENTO_LAVORAZIONE
        WHERE  ID_LISTA_LAVORAZIONE  = nIdListaLavorazione
        AND    NVL(EXT_ID_AZIENDA,0) = NVL(nExtIdAzienda,0)
        AND    DATA_INSERIMENTO      = recPLav.DATAINS
        AND    DATA_LAVORAZIONE      > dDataAgg;

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
         NOTE_LAVORAZIONE, NOTE_RICHIESTA,EXT_ID_PARTICELLA, EXT_COD_NAZIONALE, FOGLIO,PARTICELLA,SUBALTERNO)
        VALUES
        (SEQ_QGIS_T_PARTICELLA_LAVORAZI.NEXTVAL,nIdEventoLavorazione,nIdVersioneParticella,NVL(recPLav.DESC_MOTI,' '),'S','N',
         recPLav.NOTE_LAV,recPLav.NOTE,nExtIdParticella,recPLav.COD_NAZIONALE, recPLav.FOGLIO,recPLav.PARTICELLA,recPLav.SUB);
        
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
         AND    TO_DATE('31/12/'||rec.CAMPAGNA,'DD/MM/YYYY') BETWEEN SR.DATA_INIZIO_VALIDITA AND NVL(SR.DATA_FINE_VALIDITA,TO_DATE('31/12/'||rec.CAMPAGNA,'DD/MM/YYYY')));
      END IF;
    END LOOP;
  END LOOP;

  RETURN 0;
EXCEPTION
  WHEN OTHERS THEN
    PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E001','Errore grave ListeLav: '||SQLERRM||' - RIGA = '||
                                       dbms_utility.FORMAT_ERROR_BACKTRACE||' - ID_LAV = '||nIdLav||' - ID_PARTICELLA = '||
                                       nIdParticella);
                                      
    RETURN 1;
END ListeLav;

-- rc 20/05/2022 jira-74
FUNCTION AggiornaRegistroCO(pIdProcessoBatch  QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE) RETURN NUMBER IS

BEGIN
  FOR rec IN (SELECT SR.CAMPAGNA, SR.EXT_COD_NAZIONALE, SR.FOGLIO, SR.SHAPE,S.DATA_CAMPO,SR.ID_SUOLO_RILEVATO,S.PARTICELLA,S.SUB
              FROM   QGIS_W_SITIPLAV S,SITILISTALAV L,DB_LISTE_CO LC,SITISUOLO_ATTIVE SA,QGIS_T_SUOLO_RILEVATO SR
              WHERE  S.ID_LAV                = L.ID_LAV
              AND    L.PROV_RIF              = LC.PROV_RIF
              AND    S.COD_NAZIONALE         = SA.COD_NAZIONALE
              AND    S.FOGLIO                = SA.FOGLIO
              AND    S.PARTICELLA            = SA.PARTICELLA
              AND    S.SUB                   = SA.SUB
              AND    TRUNC(S.DATA_LAV_T_GIS) = TRUNC(SA.DATA_INIZIO_VAL)
              AND    SA.SE_ROW_ID            = SR.SE_ROW_ID
              ORDER BY SR.EXT_COD_NAZIONALE,SR.FOGLIO,S.PARTICELLA,S.SUB,SR.DATA_INIZIO_VALIDITA) LOOP
  
    FOR recCo IN (SELECT SR.SHAPE,RC.ID_SUOLO_RILEVATO,SR.EXT_COD_NAZIONALE,SR.FOGLIO
                  FROM   QGIS_T_SUOLO_RILEVATO SR,QGIS_T_REGISTRO_CO RC,QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_VERSIONE_PARTICELLA VP,
                         QGIS_T_REGISTRO_PARTICELLE RP
                  WHERE  SR.EXT_COD_NAZIONALE      = RC.EXT_COD_NAZIONALE
                  AND    SR.FOGLIO                 = RC.FOGLIO
                  AND    SR.ID_SUOLO_RILEVATO      = RC.ID_SUOLO_RILEVATO
                  AND    SR.CAMPAGNA               = RC.CAMPAGNA
                  AND    RC.DATA_FINE_VALIDITA     IS NULL
                  AND    SR.ID_SUOLO_RILEVATO      = SP.ID_SUOLO_RILEVATO
                  AND    SP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA
                  AND    VP.EXT_COD_NAZIONALE      = rec.EXT_COD_NAZIONALE
                  AND    VP.FOGLIO                 = rec.FOGLIO
                  AND    VP.PARTICELLA             = rec.PARTICELLA
                  AND    VP.SUBALTERNO             = rec.SUB
                  AND    VP.ID_VERSIONE_PARTICELLA = RP.ID_VERSIONE_PARTICELLA
                  AND    RP.CAMPAGNA               = rec.CAMPAGNA
                  AND    RP.DATA_FINE_VALIDITA     IS NULL) LOOP
      
      IF SMRGAA.AABGAD_SDO.SDO_ANYINTERACT(recCo.SHAPE,rec.SHAPE) = 1 THEN
        IF SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(recCo.SHAPE,rec.SHAPE)) > 0 THEN
          UPDATE QGIS_T_REGISTRO_CO
          SET    DATA_FINE_VALIDITA = SYSDATE
          WHERE  ID_SUOLO_RILEVATO  = recCo.ID_SUOLO_RILEVATO
          AND    CAMPAGNA           = rec.CAMPAGNA;
        END IF;
      END IF;
    END LOOP;
    
    INSERT INTO QGIS_T_REGISTRO_CO
    (ID_REGISTRO_CO, EXT_COD_NAZIONALE, FOGLIO, CAMPAGNA, ID_SUOLO_RILEVATO, DATA_INIZIO_VALIDITA, DATA_FINE_VALIDITA)
    VALUES
    (SEQ_QGIS_T_REGISTRO_CO.NEXTVAL,rec.EXT_COD_NAZIONALE, rec.FOGLIO, rec.CAMPAGNA,rec.ID_SUOLO_RILEVATO,SYSDATE,NULL);
    
    IF rec.DATA_CAMPO IS NOT NULL THEN
      UPDATE QGIS_T_SUOLO_RILEVATO
      SET    ID_TIPO_SORGENTE_SUOLO = 5
      WHERE  ID_SUOLO_RILEVATO      = rec.ID_SUOLO_RILEVATO;
    END IF;
  END LOOP;

  RETURN 0;
EXCEPTION
  WHEN OTHERS THEN
    PCK_QGIS_UTILITY_BATCH.inslogbatch(pIdProcessoBatch,'E001','Errore grave AggiornaRegistroCO: '||SQLERRM||' - RIGA = '||
                                       dbms_utility.FORMAT_ERROR_BACKTRACE);/*||' - ID_LAV = '||nIdLav||' - ID_PARTICELLA = '||
                                       nIdParticella);*/
                                      
    RETURN 1;
END AggiornaRegistroCO;


FUNCTION Main RETURN NUMBER IS

  vNomeBatch           QGIS_D_NOME_BATCH.NOME_BATCH%TYPE := 'AGG';
  nIdProcessoBatch     QGIS_L_PROCESSO_BATCH.ID_PROCESSO_BATCH%TYPE := PCK_QGIS_UTILITY_BATCH.insprocbatch(vNomeBatch);
  dDtUltimaEsecuzione  QGIS_D_NOME_BATCH.DT_ULTIMA_ESECUZIONE%TYPE;
  nFn                  NUMBER;
  ERRORE               EXCEPTION;
  dDataAggSitipart     DATE;
  dDataAggSitisuolo    DATE;
BEGIN
  nFn := TabSitiSuolo(nIdProcessoBatch);

  IF nFn != 0 THEN
    RAISE ERRORE;
  END IF;
  
  SELECT MIN(DATA_AGGIORNAMENTO)
  INTO   dDataAggSitipart
  FROM   QGIS_W_SITIPART;
  
  nFn := TabSitiPart(nIdProcessoBatch,dDataAggSitipart);
  
  IF nFn != 0 THEN
    RAISE ERRORE;
  END IF;
  
  nFn := TabSitiPartFuture(nIdProcessoBatch);
  
  IF nFn != 0 THEN
    RAISE ERRORE;
  END IF;
  
  SELECT MIN(DATA_AGGIORNAMENTO)
  INTO   dDataAggSitisuolo
  FROM   QGIS_W_SITISUOLO;
  
  SELECT CASE WHEN dDataAggSitipart IS NULL THEN dDataAggSitisuolo ELSE nvl(LEAST(dDataAggSitipart,dDataAggSitisuolo),dDataAggSitipart) END
  INTO   dDtUltimaEsecuzione
  FROM   DUAL;
  
  nFn := PopolamentoQgis(nIdProcessoBatch,dDtUltimaEsecuzione);
  
  IF nFn != 0 THEN
    RAISE ERRORE;
  END IF;
  
  nFn := ListeLav(nIdProcessoBatch);
  
  IF nFn != 0 THEN
    RAISE ERRORE;
  END IF;
  
  -- rc 20/05/2022 jira-74
  nFn :=  AggiornaRegistroCO(nIdProcessoBatch);
  
  IF nFn != 0 THEN
    RAISE ERRORE;
  END IF;
    
  UPDATE QGIS_D_NOME_BATCH
  SET    DT_ULTIMA_ESECUZIONE      = SYSDATE,
         DT_ULTIMA_ESECUZIONE_PREC = DT_ULTIMA_ESECUZIONE 
  WHERE  NOME_BATCH                = vNomeBatch;
  
  COMMIT;
  
  PCK_QGIS_UTILITY_BATCH.UpdFineProcBatch(nIdProcessoBatch,'OK');
  
  RETURN 0;
EXCEPTION
  WHEN ERRORE THEN
    ROLLBACK;
    PCK_QGIS_UTILITY_BATCH.UpdFineProcBatch(nIdProcessoBatch,'KO');      
    RETURN 1;
  WHEN OTHERS THEN
    ROLLBACK;
    PCK_QGIS_UTILITY_BATCH.inslogbatch(nIdProcessoBatch,'E001','Errore grave: '||SQLERRM||' - RIGA = '||
                                      dbms_utility.FORMAT_ERROR_BACKTRACE);
    
    PCK_QGIS_UTILITY_BATCH.UpdFineProcBatch(nIdProcessoBatch,'KO');      
    RETURN 1;
END Main; 
  
END PCK_QGIS_AGGIORNAMENTO_TABELLE;

/