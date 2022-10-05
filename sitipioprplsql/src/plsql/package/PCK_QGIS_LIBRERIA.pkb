CREATE OR REPLACE PACKAGE BODY PCK_QGIS_LIBRERIA AS

-- rc 27/11/2020 jira-29
PROCEDURE InserisciListaLavorazione(pTipoModalita                  VARCHAR2,
                                    pIdAzienda                     NUMBER,
                                    pIdIstanzaAppezzamento         NUMBER,   
                                    pIdParticella                  NUMBER,
                                    pExtIdentificativoPratica      VARCHAR2,
                                    pExtIdUtenteAggiornamento      NUMBER,
                                    pNoteRichiestaParticella       VARCHAR2,
                                    pCampagna                      NUMBER,  -- RC 11/01/2022 JIRA-ANAG-5052
                                    pCodErrore                 OUT VARCHAR2,
                                    pDescErrore                OUT VARCHAR2,
                                    -- rc 04/01/2021 jira-63
                                    pIdEventoLavorazione       OUT QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE) IS

  vSwapSemina              VARCHAR2(50);
  nCampagna                NUMBER;
  nIdListaLavorazione      QGIS_T_LISTA_LAVORAZIONE.ID_LISTA_LAVORAZIONE%TYPE;
  vNoteRichiesta           SMRGAA.DB_ISTANZA_APPEZZAMENTO.NOTE_RICHIESTA%TYPE;
  nIdEleggibilitaRilevata  SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA.ID_ELEGGIBILITA_RILEVATA%TYPE;
  sShapePoligono           SMRGAA.DB_ISTANZA_APPEZZAMENTO.SHAPE_POLIGONO%TYPE;
  nCont                    SIMPLE_INTEGER := 0;
  bFound                   BOOLEAN := FALSE;
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  -- RC 11/01/2022 JIRA-ANAG-5052
  IF pCampagna IS NOT NULL THEN
    nCampagna := pCampagna;
  ELSE
    SMRGAA.PCK_SMRGAA_UTILITY_QGIS.RitornaDatiCampagna(vSwapSemina,nCampagna);
  END IF;
  
  BEGIN
    SELECT LL.ID_LISTA_LAVORAZIONE
    INTO   nIdListaLavorazione
    FROM   QGIS_T_LISTA_LAVORAZIONE LL
    WHERE  LL.CODICE   LIKE pTipoModalita||'%'
    AND    LL.CAMPAGNA = nCampagna;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      INSERT INTO QGIS_T_LISTA_LAVORAZIONE
      (ID_LISTA_LAVORAZIONE, 
       ID_TIPO_LISTA, 
       CAMPAGNA, CODICE, 
       DESCRIZIONE_LISTA, 
       ID_TIPO_SORGENTE_SUOLO)
      VALUES
      (SEQ_QGIS_T_LISTA_LAVORAZIONE.NEXTVAL,
       CASE WHEN pTipoModalita = 'PO' THEN 1 ELSE 2 END,
       nCampagna,pTipoModalita||nCampagna,
       CASE WHEN pTipoModalita = 'IS' THEN 'Istanza'||nCampagna
       -- rc 08/07/2021 jira-42
            WHEN pTipoModalita = 'CONT' THEN 'Contraddittori'||nCampagna
       ELSE 'Poligonazioni'||nCampagna END,
       NULL)
      RETURNING ID_LISTA_LAVORAZIONE INTO nIdListaLavorazione;
  END;
  
  BEGIN
    SELECT EL.ID_EVENTO_LAVORAZIONE
    INTO   pIdEventoLavorazione
    FROM   QGIS_T_EVENTO_LAVORAZIONE EL
    WHERE  EL.ID_LISTA_LAVORAZIONE = nIdListaLavorazione
    AND    EL.EXT_ID_AZIENDA       = pIdAzienda
    AND    EL.DATA_LAVORAZIONE     IS NULL
    AND    NOT EXISTS              (SELECT 'X' 
                                    FROM   QGIS_T_SUOLO_LAVORAZIONE SL
                                    WHERE  SL.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE
                                    AND    SL.FLAG_LAVORATO         = 'S')
    AND    NOT EXISTS              (SELECT 'X' 
                                    FROM   QGIS_T_PARTICELLA_LAVORAZIONE PL
                                    WHERE  PL.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE
                                    AND    PL.FLAG_LAVORATO         = 'S');                                    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      INSERT INTO QGIS_T_EVENTO_LAVORAZIONE
      (ID_EVENTO_LAVORAZIONE, ID_LISTA_LAVORAZIONE, DATA_LAVORAZIONE, DATA_INSERIMENTO, EXT_ID_AZIENDA, EXT_ID_UTENTE_INSERIMENTO, 
       EXT_ID_UTENTE_LAVORAZIONE, EXT_ID_UTENTE_INSER_SITICLIENT, EXT_ID_UTENTE_LAVOR_SITICLIENT)
      VALUES
      (SEQ_QGIS_T_EVENTO_LAVORAZIONE.NEXTVAL,nIdListaLavorazione,NULL,SYSDATE,pIdAzienda,pExtIdUtenteAggiornamento,
       NULL,NULL,NULL)
      RETURNING ID_EVENTO_LAVORAZIONE INTO pIdEventoLavorazione;
  END;
  
  IF pTipoModalita IN ('CONT','IS') THEN  -- rc 08/07/2021 jira-42
    SELECT IA.NOTE_RICHIESTA,TER.ID_ELEGGIBILITA_RILEVATA,IA.SHAPE_POLIGONO
    INTO   vNoteRichiesta,nIdEleggibilitaRilevata,sShapePoligono
    FROM   SMRGAA.DB_ISTANZA_APPEZZAMENTO IA,SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA TER
    WHERE  IA.ID_ISTANZA_APPEZZAMENTO = pIdIstanzaAppezzamento
    AND    TER.CODI_RILE_PROD         = IA.CODI_PROD_RILE
    AND    TER.DATA_FINE_VALIDITA     IS NULL;

    FOR rec IN (SELECT DISTINCT SR.ID_SUOLO_RILEVATO,VP.EXT_COD_NAZIONALE,VP.FOGLIO,P.ID_REGIONE
                FROM   SMRGAA.DB_ISTANZA_APPEZZAMENTO IA,QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_SUOLO_RILEVATO SR,
                       SMRGAA.DB_SITICOMU S,SMRGAA.PROVINCIA P,QGIS_T_REGISTRO_SUOLI RS,QGIS_T_REGISTRO_PARTICELLE RP
                WHERE  IA.ID_ISTANZA_APPEZZAMENTO = pIdIstanzaAppezzamento
                AND    VP.ID_VERSIONE_PARTICELLA  = SP.ID_VERSIONE_PARTICELLA
                AND    SR.ID_SUOLO_RILEVATO       = SP.ID_SUOLO_RILEVATO
                AND    SDO_ANYINTERACT(VP.SHAPE,IA.SHAPE_POLIGONO) = 'TRUE'
                AND    SMRGAA.PCK_SMRGAA_UTILITY_QGIS.ISPARTICELLACONDOTTA(VP.EXT_ID_PARTICELLA,pIdAzienda,nCampagna) = 'S' -- rc 06/10/2021 jira-53
                AND    SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(VP.SHAPE,IA.SHAPE_POLIGONO)) > 1
                -- rc 12/07/2021 jira-4884
                AND    VP.EXT_COD_NAZIONALE       = S.COD_NAZIONALE
                AND    S.SIGLA_PROV               = P.SIGLA_PROVINCIA
                -- RC 21/04/2022 JIRA-72
                AND    RS.ID_SUOLO_RILEVATO       = SP.ID_SUOLO_RILEVATO
                AND    RS.DATA_FINE_VALIDITA      IS NULL
                AND    RP.ID_VERSIONE_PARTICELLA  = VP.ID_VERSIONE_PARTICELLA
                AND    RP.DATA_FINE_VALIDITA      IS NULL
                AND    RS.CAMPAGNA                = nCampagna
                AND    RP.CAMPAGNA                = RS.CAMPAGNA) LOOP
      
      bFound := TRUE;
    
      -- rc 12/07/2021 jira-4884
      IF rec.ID_REGIONE != '01' THEN
        CONTINUE;
      END IF;
    
      INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
      (ID_SUOLO_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_SUOLO_RILEVATO, FLAG_SOSPENSIONE, FLAG_CESSATO, NOTE_RICHIESTA, 
       IDENTIFICATIVO_PRATICA_ORIGINE)
      VALUES
      (SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,pIdEventoLavorazione,rec.ID_SUOLO_RILEVATO,'N','N',vNoteRichiesta,
       pExtIdentificativoPratica);

      SELECT COUNT(*)
      INTO   nCont
      FROM   QGIS_T_SUOLO_PROPOSTO
      WHERE  ID_EVENTO_LAVORAZIONE   = pIdEventoLavorazione
      AND    NVL(EXT_ID_ISTA_RIES,0) = NVL(pIdIstanzaAppezzamento,0)
      AND    EXT_COD_NAZIONALE       = rec.EXT_COD_NAZIONALE
      AND    FOGLIO                  = rec.FOGLIO; 
      
      IF nCont = 0 THEN 
        INSERT INTO QGIS_T_SUOLO_PROPOSTO
        (ID_SUOLO_PROPOSTO, ID_EVENTO_LAVORAZIONE, EXT_ID_ELEGGIBILITA_RILEVATA, EXT_ID_ISTA_RIES, SHAPE, 
         EXT_COD_NAZIONALE, FOGLIO,IDENTIFICATIVO_PRATICA_ORIGINE)
        VALUES
        (SEQ_QGIS_T_SUOLO_PROPOSTO.NEXTVAL,pIdEventoLavorazione,nIdEleggibilitaRilevata,pIdIstanzaAppezzamento,sShapePoligono,
         rec.EXT_COD_NAZIONALE,rec.FOGLIO,pExtIdentificativoPratica); 
      END IF;
    END LOOP;
    
    -- RC 24/05/2021 JIRA-29
    IF NOT bFound THEN
      pCodErrore  := '1';
      pDescErrore := 'Attenzione! Non e'' stato possibile inserire l''istanza di riesame nella lista di lavorazione, richiedere '||
                     'l''intervento dell''assistenza';
      RETURN;
    END IF;
  END IF;
  
  IF pTipoModalita = 'PO' THEN
    INSERT INTO QGIS_T_PARTICELLA_LAVORAZIONE
    (ID_PARTICELLA_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_VERSIONE_PARTICELLA, DESCRIZIONE_SOSPENSIONE, FLAG_SOSPENSIONE, FLAG_CESSATO, 
     NOTE_RICHIESTA, EXT_ID_PARTICELLA, EXT_COD_NAZIONALE, FOGLIO, PARTICELLA, SUBALTERNO,
     IDENTIFICATIVO_PRATICA_ORIGINE)
    SELECT SEQ_QGIS_T_PARTICELLA_LAVORAZI.NEXTVAL,pIdEventoLavorazione,NULL,NULL,'N','N',
           pNoteRichiestaParticella,pIdParticella,S.COD_NAZIONALE,SP.FOGLIO,LPAD(SP.PARTICELLA,5,'0'),NVL(SP.SUBALTERNO,' '),
           pExtIdentificativoPratica  -- rc 06/12/2021 jira-63
    FROM   SMRGAA.DB_STORICO_PARTICELLA SP,SMRGAA.DB_SITICOMU S
    WHERE  SP.ID_PARTICELLA      = pIdParticella
    AND    SP.DATA_FINE_VALIDITA IS NULL
    AND    SP.COMUNE             = S.ISTAT_COMUNE
    AND    NVL(SP.SEZIONE,'-')   = NVL(S.ID_SEZC,'-')
    -- rc 08/04/2022
    AND    NOT EXISTS            (SELECT 'X'
                                  FROM   QGIS_T_PARTICELLA_LAVORAZIONE PL
                                  WHERE  PL.EXT_COD_NAZIONALE     = S.COD_NAZIONALE
                                  AND    PL.FOGLIO                = SP.FOGLIO
                                  AND    PL.PARTICELLA            = LPAD(SP.PARTICELLA,5,'0')
                                  AND    PL.SUBALTERNO            = NVL(SP.SUBALTERNO,' ')
                                  AND    PL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione);
  END IF;
  
  -- rc 12/07/2021 jira-4884
  /*DELETE QGIS_T_EVENTO_LAVORAZIONE EL
  WHERE  NOT EXISTS (SELECT 'X'
                     FROM   QGIS_T_SUOLO_PROPOSTO SP
                     WHERE  SP.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE)
  AND    EL.ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione;*/

EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nell''inserimento delle liste di lavorazione: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END InserisciListaLavorazione;

-- rc 14/12/2020 jira-31
PROCEDURE InserisciSuoloNuovo(pExtCodNazionale         VARCHAR2,
                              pFoglio                  NUMBER,
                              pParticella              VARCHAR2,
                              pSubalterno              VARCHAR2,
                              pDataInizioValidita      DATE,
                              pArraySuoli              LIST_SUOLI,
                              pCampagna                NUMBER,  -- RC 21/04/2022 JIRA-72
                              pCodErrore           OUT VARCHAR2,
                              pDescErrore          OUT VARCHAR2) IS

  dDataOperazione   DATE := SYSDATE;
  nIdSuoloRilevato  QGIS_T_SUOLO_RILEVATO.ID_SUOLO_RILEVATO%TYPE;
  nAreaDifference   NUMBER;
  sShape            SDO_GEOMETRY := NULL;
  sDiff             SDO_GEOMETRY := NULL;
  sShapeInters      SDO_GEOMETRY;
  nAreaInters       NUMBER;
  SuoloCessato      ORA_MINING_NUMBER_NT := ORA_MINING_NUMBER_NT();
  SuoloInserito     ORA_MINING_NUMBER_NT := ORA_MINING_NUMBER_NT();
  nAnno             NUMBER;
  nCampagna         NUMBER;
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;

  SELECT VALORE_NUMERICO
  INTO   nAnno
  FROM   QGIS_D_PARAMETRO_PLUGIN
  WHERE  CODICE             = 'ANNO_IMP_SUOLO'
  AND    DATA_FINE_VALIDITA IS NOT NULL;

  IF pCampagna < nAnno THEN
    nCampagna := nAnno;
  ELSE
    nCampagna := pCampagna;
  END IF;

  FOR rec IN (SELECT SHAPE
              FROM TABLE(pArraySuoli)) LOOP

    sShape := SMRGAA.AABGAD_SDO.SDO_UNION(rec.SHAPE,sShape);
  END LOOP;

  FOR recSuolo IN (SELECT SR.*
                   FROM   QGIS_T_SUOLO_RILEVATO SR,QGIS_T_REGISTRO_SUOLI RS
                   WHERE  SR.EXT_COD_NAZIONALE   = pExtCodNazionale
                   AND    SR.FOGLIO              = pFoglio
                   -- RC 21/04/2022 JIRA-72
                   AND    RS.ID_SUOLO_RILEVATO   = SR.ID_SUOLO_RILEVATO
                   AND    RS.CAMPAGNA            = nCampagna
                   AND    RS.DATA_FINE_VALIDITA  IS NULL) LOOP

    sDiff := NULL;

    IF SMRGAA.AABGAD_SDO.SDO_ANYINTERACT(recSuolo.SHAPE,sShape) = 1 then
      IF SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(recSuolo.SHAPE,sShape)) > 0 THEN
        sDiff := SMRGAA.AABGAD_SDO.SDO_DIFFERENCE(recSuolo.SHAPE,sShape);

        UPDATE QGIS_T_SUOLO_RILEVATO
        SET    DATA_FINE_VALIDITA = pDataInizioValidita - INTERVAL '1' SECOND
        WHERE  ID_SUOLO_RILEVATO  = recSuolo.ID_SUOLO_RILEVATO;

        -- RC 21/04/2022 JIRA-72
        SuoloCessato.EXTEND;
        SuoloCessato(SuoloCessato.COUNT) := recSuolo.ID_SUOLO_RILEVATO;
      END IF;
    END IF;

    nAreaDifference := SMRGAA.AABGAD_SDO.SDO_AREA(sDiff);

    IF nAreaDifference > 0 THEN

      INSERT INTO QGIS_T_SUOLO_RILEVATO
      (ID_SUOLO_RILEVATO, AREA, CAMPAGNA, EXT_COD_NAZIONALE, FOGLIO, DATA_INIZIO_VALIDITA,
       DATA_FINE_VALIDITA,DATA_AGGIORNAMENTO,EXT_ID_ELEGGIBILITA_RILEVATA, EXT_ID_UTENTE_AGGIORNAMENTO, ID_TIPO_SORGENTE_SUOLO,
       SHAPE,EXT_ID_UTENTE_LAVOR_SITICLIENT,FLAG_GEOM_CORROTTA, SE_ROW_ID)
      VALUES
      (SEQ_QGIS_T_SUOLO_RILEVATO.NEXTVAL,nAreaDifference,recSuolo.CAMPAGNA,recSuolo.EXT_COD_NAZIONALE,recSuolo.FOGLIO,pDataInizioValidita,
       NULL,dDataOperazione,recSuolo.EXT_ID_ELEGGIBILITA_RILEVATA,recSuolo.EXT_ID_UTENTE_AGGIORNAMENTO,recSuolo.ID_TIPO_SORGENTE_SUOLO,
       sDiff,recSuolo.EXT_ID_UTENTE_LAVOR_SITICLIENT,'N',recSuolo.SE_ROW_ID)
      RETURNING ID_SUOLO_RILEVATO INTO nIdSuoloRilevato;

      -- RC 21/04/2022 JIRA-72
      SuoloInserito.EXTEND;
      SuoloInserito(SuoloInserito.COUNT) := nIdSuoloRilevato;

      FOR rec IN (SELECT SP.ID_VERSIONE_PARTICELLA,VP.SHAPE,
                         (SELECT NVL(MAX(SP1.PROG_POLIGONO),0) + 1
                          FROM   QGIS_T_SUOLO_PARTICELLA SP1
                          WHERE  SP1.ID_VERSIONE_PARTICELLA = SP.ID_VERSIONE_PARTICELLA) MAX_PROG_POLIGONO
                  FROM   QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_REGISTRO_PARTICELLE RP
                  WHERE  SP.ID_SUOLO_RILEVATO      = recSuolo.ID_SUOLO_RILEVATO
                  AND    VP.ID_VERSIONE_PARTICELLA = SP.ID_VERSIONE_PARTICELLA
                  AND    VP.ID_VERSIONE_PARTICELLA = RP.ID_VERSIONE_PARTICELLA
                  AND    RP.DATA_FINE_VALIDITA     IS NULL
                  AND    RP.CAMPAGNA               = nCampagna) LOOP

        sShapeInters := SMRGAA.AABGAD_SDO.SDO_INTERSECTION(sDiff,rec.SHAPE);
        nAreaInters  := SMRGAA.AABGAD_SDO.SDO_AREA(sShapeInters);

        IF nAreaInters > 0 AND sShapeInters IS NOT NULL THEN

          INSERT INTO QGIS_T_SUOLO_PARTICELLA
          (ID_SUOLO_PARTICELLA, ID_SUOLO_RILEVATO, ID_VERSIONE_PARTICELLA,AREA, DATA_AGGIORNAMENTO,PROG_POLIGONO,
           SHAPE,EXT_ID_UTENTE_AGGIORNAMENTO,EXT_ID_UTENTE_LAVOR_SITICLIENT, SE_ROW_ID)
          VALUES
          (SEQ_QGIS_T_SUOLO_PARTICELLA.NEXTVAL,nIdSuoloRilevato,rec.ID_VERSIONE_PARTICELLA,nAreaInters,dDataOperazione,rec.MAX_PROG_POLIGONO,
           sShapeInters,recSuolo.EXT_ID_UTENTE_AGGIORNAMENTO,recSuolo.EXT_ID_UTENTE_LAVOR_SITICLIENT, recSuolo.SE_ROW_ID);
        END IF;
      END LOOP;
    END IF;
  END LOOP;

  FOR rec IN (SELECT *
              FROM TABLE(pArraySuoli)) LOOP

    INSERT INTO QGIS_T_SUOLO_RILEVATO
    (ID_SUOLO_RILEVATO, AREA, CAMPAGNA, EXT_COD_NAZIONALE, FOGLIO, DATA_INIZIO_VALIDITA,
     DATA_FINE_VALIDITA, DATA_AGGIORNAMENTO,
     EXT_ID_ELEGGIBILITA_RILEVATA, EXT_ID_UTENTE_AGGIORNAMENTO, ID_TIPO_SORGENTE_SUOLO, SHAPE,
     EXT_ID_UTENTE_LAVOR_SITICLIENT,FLAG_GEOM_CORROTTA, SE_ROW_ID)
    VALUES
    (SEQ_QGIS_T_SUOLO_RILEVATO.NEXTVAL,SMRGAA.AABGAD_SDO.SDO_AREA(rec.SHAPE),rec.CAMPAGNA,pExtCodNazionale,pFoglio,pDataInizioValidita,
     NULL,dDataOperazione,
     (SELECT TER.ID_ELEGGIBILITA_RILEVATA
      FROM   SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA TER
      WHERE  TER.CODI_RILE_PROD        = LPAD(rec.COD_VARIETA,3,'0')
      AND    TER.FLAG_ASSEGNABILE_QGIS = 'S'),rec.EXT_ID_UTENTE_AGGIORNAMENTO,rec.ID_TIPO_SORGENTE_SUOLO,rec.SHAPE,
     rec.EXT_ID_UTENTE_LAVOR_SITICLIENT,'N',rec.SE_ROW_ID)
    RETURNING ID_SUOLO_RILEVATO INTO nIdSuoloRilevato;

    -- RC 21/04/2022 JIRA-72
    SuoloInserito.EXTEND;
    SuoloInserito(SuoloInserito.COUNT) := nIdSuoloRilevato;

    INSERT INTO QGIS_T_SUOLO_PARTICELLA
    (ID_SUOLO_PARTICELLA, ID_SUOLO_RILEVATO, ID_VERSIONE_PARTICELLA, AREA,
     DATA_AGGIORNAMENTO,
     PROG_POLIGONO, SHAPE,EXT_ID_UTENTE_AGGIORNAMENTO,
     EXT_ID_UTENTE_LAVOR_SITICLIENT, SE_ROW_ID)
    SELECT SEQ_QGIS_T_SUOLO_PARTICELLA.NEXTVAL,nIdSuoloRilevato,VP.ID_VERSIONE_PARTICELLA,SMRGAA.AABGAD_SDO.SDO_AREA(rec.SHAPE),
           dDataOperazione,
           nvl((SELECT MAX(SP1.PROG_POLIGONO) + 1
            FROM   QGIS_T_SUOLO_PARTICELLA SP1
            WHERE  SP1.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA),1),rec.SHAPE,rec.EXT_ID_UTENTE_AGGIORNAMENTO,
           rec.EXT_ID_UTENTE_LAVOR_SITICLIENT,rec.SE_ROW_ID
    FROM   QGIS_T_VERSIONE_PARTICELLA VP
    WHERE  VP.EXT_COD_NAZIONALE  = pExtCodNazionale
    AND    VP.FOGLIO             = pFoglio
    AND    VP.PARTICELLA         = pParticella
    AND    VP.SUBALTERNO         = pSubalterno
    AND    VP.DATA_FINE_VALIDITA IS NULL;
  END LOOP;

  -- RC 21/04/2022 JIRA-72
  AggiornaRegistroSuoli(nCampagna,pExtCodNazionale,pFoglio,SuoloCessato,SuoloInserito,pCodErrore,pDescErrore);
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nell''inserimento delle liste di lavorazione: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;
END InserisciSuoloNuovo;

-- rc 25/03/2021 jira-4744
PROCEDURE SalvaIstanza(pIdEventoLavorazione      QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE,
                       pCodErrore            OUT VARCHAR2,
                       pDescErrore           OUT VARCHAR2) IS

  nIdStatoIstanza           NUMBER;
  istanzaLavorata           SMRGAA.ISTANZA_LAVORATA_COL := SMRGAA.ISTANZA_LAVORATA_COL();
  vCodice                   QGIS_T_LISTA_LAVORAZIONE.CODICE%TYPE;
  nIdFaseIstanza            NUMBER;
  nIdTipoMotivoSospensione  QGIS_T_SUOLO_LAVORAZIONE.ID_TIPO_MOTIVO_SOSPENSIONE%TYPE;
  vDescrizioneSospensione   QGIS_T_SUOLO_LAVORAZIONE.DESCRIZIONE_SOSPENSIONE%TYPE;
  nCont                     SIMPLE_INTEGER := 0;
  nExtIdAzienda             QGIS_T_EVENTO_LAVORAZIONE.EXT_ID_AZIENDA%TYPE;
  nCampagna                 QGIS_T_LISTA_LAVORAZIONE.CAMPAGNA%TYPE;
  nIdEventoLavorazione      QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE;
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  -- rc 19/11/2021 jira-60
  SELECT LL.CODICE,EL.EXT_ID_AZIENDA,LL.CAMPAGNA,CASE WHEN LL.CODICE LIKE 'IS%' THEN 1 
                                                      WHEN LL.CODICE LIKE 'CONT%' OR LL.CODICE LIKE 'SOPR%' THEN 2 
                                                      ELSE NULL END
  INTO   vCodice,nExtIdAzienda,nCampagna,nIdFaseIstanza
  FROM   QGIS_T_LISTA_LAVORAZIONE LL,QGIS_T_EVENTO_LAVORAZIONE EL
  WHERE  EL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione
  AND    LL.ID_LISTA_LAVORAZIONE  = EL.ID_LISTA_LAVORAZIONE;
  
  IF vCodice LIKE 'CONT%' THEN
    BEGIN
      SELECT EL.ID_EVENTO_LAVORAZIONE
      INTO   nIdEventoLavorazione
      FROM   QGIS_T_EVENTO_LAVORAZIONE EL,QGIS_T_LISTA_LAVORAZIONE LL
      WHERE  EL.EXT_ID_AZIENDA       = nExtIdAzienda
      AND    EL.DATA_LAVORAZIONE     IS NULL
      AND    LL.ID_LISTA_LAVORAZIONE = EL.ID_LISTA_LAVORAZIONE
      AND    LL.CODICE               LIKE 'SOPR%'
      AND    LL.CAMPAGNA             = nCampagna;
    
      -- rc 03/01/2022 jira-65
      INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
      (ID_SUOLO_LAVORAZIONE,ID_EVENTO_LAVORAZIONE,ID_SUOLO_RILEVATO,DESCRIZIONE_SOSPENSIONE,FLAG_SOSPENSIONE,FLAG_CESSATO,NOTE_RICHIESTA, 
       NOTE_LAVORAZIONE, ID_TIPO_MOTIVO_SOSPENSIONE, FLAG_LAVORATO, TIPO_SUOLO_ORIGINE, IDENTIFICATIVO_PRATICA_ORIGINE, 
       EXT_ID_UTENTE_LAVORAZIONE,DATA_LAVORAZIONE)
      SELECT SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,nIdEventoLavorazione,ID_SUOLO_RILEVATO,NULL,'N','N',NOTE_RICHIESTA,
             NULL,NULL,'N',NULL,IDENTIFICATIVO_PRATICA_ORIGINE,
             NULL,NULL
      FROM   QGIS_T_SUOLO_LAVORAZIONE SL
      WHERE  SL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione
      AND    SL.FLAG_CESSATO          = 'N'
      AND    NOT EXISTS               (SELECT 'X'
                                       FROM   QGIS_T_SUOLO_LAVORAZIONE SL1
                                       WHERE  SL1.ID_SUOLO_RILEVATO     = SL.ID_SUOLO_RILEVATO
                                       AND    SL1.ID_EVENTO_LAVORAZIONE = SL.ID_EVENTO_LAVORAZIONE);
    
      RETURN;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        NULL;
    END;
  END IF;
  
  FOR rec IN (SELECT SP.EXT_ID_ISTA_RIES,SP.SHAPE,EL.DATA_LAVORAZIONE,SP.ID_EVENTO_LAVORAZIONE
              FROM   QGIS_T_SUOLO_PROPOSTO SP,QGIS_T_EVENTO_LAVORAZIONE EL
              WHERE  SP.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione
              AND    EL.ID_EVENTO_LAVORAZIONE = SP.ID_EVENTO_LAVORAZIONE) LOOP
            
    -- RC 11/10/2021 jira-anag-4937
    BEGIN
      SELECT ID_TIPO_MOTIVO_SOSPENSIONE,DESCRIZIONE_SOSPENSIONE,6
      INTO   nIdTipoMotivoSospensione,vDescrizioneSospensione,nIdStatoIstanza
      FROM   (SELECT SL.ID_TIPO_MOTIVO_SOSPENSIONE,SL.DESCRIZIONE_SOSPENSIONE
              FROM   QGIS_T_SUOLO_RILEVATO SR,QGIS_T_SUOLO_LAVORAZIONE SL,QGIS_T_REGISTRO_SUOLI RS
              WHERE  SR.ID_SUOLO_RILEVATO     = SL.ID_SUOLO_RILEVATO
              AND    SL.ID_EVENTO_LAVORAZIONE = rec.ID_EVENTO_LAVORAZIONE
              AND    SL.FLAG_SOSPENSIONE      = 'S'
              AND    SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(SR.SHAPE,rec.SHAPE)) > 1
              -- RC 21/04/2022 JIRA-72
              AND    RS.ID_SUOLO_RILEVATO     = SR.ID_SUOLO_RILEVATO
              AND    RS.DATA_FINE_VALIDITA    IS NULL
              AND    RS.CAMPAGNA              = nCampagna)
      WHERE  (DESCRIZIONE_SOSPENSIONE IS NOT NULL OR ID_TIPO_MOTIVO_SOSPENSIONE IS NOT NULL)
      AND    ROWNUM           <= 1;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        nIdTipoMotivoSospensione := NULL;
        vDescrizioneSospensione  := NULL;
        nIdStatoIstanza          := 3;
    END;
    
    istanzaLavorata.EXTEND;
    istanzaLavorata(istanzaLavorata.COUNT) := SMRGAA.ISTANZA_LAVORATA_REC(rec.EXT_ID_ISTA_RIES,nIdStatoIstanza,rec.DATA_LAVORAZIONE,
                                                                          nIdTipoMotivoSospensione,vDescrizioneSospensione);
  END LOOP;
  
  IF istanzaLavorata.COUNT > 0 AND nIdFaseIstanza IS NOT NULL THEN
    SMRGAA.PCK_SMRGAA_UTILITY_QGIS.AggiornaStatoIstanza(istanzaLavorata,nIdFaseIstanza,pCodErrore,pDescErrore);
  END IF;
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nel salvataggio dell''istanza di riesame: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END SalvaIstanza;

-- RC 15/04/2021 JIRA-36
PROCEDURE RinunciaIstanzaRiesame(pIdAzienda                     NUMBER,
                                 pIdIstanzaAppezzamento         NUMBER,
                                 pExtIdentificativoPratica      VARCHAR2,
                                 pCodErrore                 OUT VARCHAR2,
                                 pDescErrore                OUT VARCHAR2) IS

  nCampagna             NUMBER;
  nIdListaLavorazione   QGIS_T_LISTA_LAVORAZIONE.ID_LISTA_LAVORAZIONE%TYPE;
  nIdEventoLavorazione  QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE;
  nCont                 SIMPLE_INTEGER := 0;
  sShapePoligono        SMRGAA.DB_ISTANZA_APPEZZAMENTO.SHAPE_POLIGONO%TYPE;
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  SELECT SHAPE_POLIGONO
  INTO   sShapePoligono
  FROM   SMRGAA.DB_ISTANZA_APPEZZAMENTO
  WHERE  ID_ISTANZA_APPEZZAMENTO = pIdIstanzaAppezzamento;
  
  SELECT COUNT(*)
  INTO   nCont
  FROM   QGIS_T_VERSIONE_PARTICELLA VP,SMRGAA.DB_SITICOMU S
  WHERE  VP.DATA_FINE_VALIDITA                    IS NULL
  AND    SDO_ANYINTERACT(VP.SHAPE,sShapePoligono) = 'TRUE'
  AND    VP.EXT_COD_NAZIONALE                     = S.COD_NAZIONALE
  AND    S.ISTATR                                 = '01'
  AND    SMRGAA.PCK_SMRGAA_UTILITY_QGIS.ISPARTICELLACONDOTTA(VP.EXT_ID_PARTICELLA,pIdAzienda,EXTRACT (YEAR FROM SYSDATE)) = 'S'
  AND    SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(VP.SHAPE,sShapePoligono)) > 0;
  
  IF nCont = 0 THEN
    RETURN;
  END IF;
  
  -- rc 01/03/2022 jira-63
  BEGIN
    SELECT DISTINCT LL.CAMPAGNA
    INTO   nCampagna
    FROM   QGIS_T_LISTA_LAVORAZIONE LL,QGIS_T_EVENTO_LAVORAZIONE EL,QGIS_T_SUOLO_PROPOSTO SP
    WHERE  LL.ID_LISTA_LAVORAZIONE  = EL.ID_LISTA_LAVORAZIONE
    AND    SP.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE
    AND    SP.EXT_ID_ISTA_RIES      = pIdIstanzaAppezzamento;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      pCodErrore  := '1';
      pDescErrore := 'Non esiste l''istanza appezzamento a cui si vuole rinunciare';
      RETURN;
  END;
  
  BEGIN
    SELECT LL.ID_LISTA_LAVORAZIONE
    INTO   nIdListaLavorazione
    FROM   QGIS_T_LISTA_LAVORAZIONE LL
    WHERE  LL.CODICE   LIKE 'IS%'
    AND    LL.CAMPAGNA = nCampagna;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      pCodErrore  := '1';
      pDescErrore := 'Non esiste la lista di lavorazione dell''istanza di riesame per l''anno '||nCampagna;
      RETURN;
  END;
  
  BEGIN
    SELECT EL.ID_EVENTO_LAVORAZIONE
    INTO   nIdEventoLavorazione
    FROM   QGIS_T_EVENTO_LAVORAZIONE EL
    WHERE  EL.ID_LISTA_LAVORAZIONE = nIdListaLavorazione
    AND    EL.EXT_ID_AZIENDA       = pIdAzienda
    AND    EL.DATA_LAVORAZIONE     IS NULL;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      BEGIN
        SELECT EL.ID_EVENTO_LAVORAZIONE
        INTO   nIdEventoLavorazione
        FROM   QGIS_T_EVENTO_LAVORAZIONE EL
        WHERE  EL.ID_LISTA_LAVORAZIONE = nIdListaLavorazione
        AND    EL.EXT_ID_AZIENDA       = pIdAzienda
        AND    EL.DATA_LAVORAZIONE     IS NOT NULL;
        
        pCodErrore  := '1';
        pDescErrore := 'L''evento di lavorazione e'' in corso di lavorazione, impossibile procedere';
        RETURN;
      EXCEPTION
        WHEN NO_DATA_FOUND THEN
          pCodErrore  := '1';
          pDescErrore := 'Non esiste l''evento di lavorazione da cui eliminare gli appezzamenti';
          RETURN;
      END;
  END;
  
  SELECT COUNT(*)
  INTO   nCont
  FROM   QGIS_T_EVENTO_BLOCCATO
  WHERE  ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione
  AND    DATA_FINE_VALIDITA    IS NULL;
  
  IF nCont != 0 THEN
    pCodErrore  := '1';
    pDescErrore := 'L''evento di lavorazione e'' in corso di lavorazione, impossibile procedere';
    RETURN;
  END IF;
  
  DELETE QGIS_T_SUOLO_PROPOSTO
  WHERE  ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione
  AND    EXT_ID_ISTA_RIES      = pIdIstanzaAppezzamento;
  
  DELETE QGIS_T_SUOLO_LAVORAZIONE SL
  WHERE  SL.ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione
  AND    NOT EXISTS               (SELECT 'X'
                                   FROM   QGIS_T_SUOLO_RILEVATO SR,QGIS_T_SUOLO_PROPOSTO SP
                                   WHERE  SR.ID_SUOLO_RILEVATO               = SL.ID_SUOLO_RILEVATO
                                   AND    SP.ID_EVENTO_LAVORAZIONE           = SL.ID_EVENTO_LAVORAZIONE
                                   AND    SDO_ANYINTERACT(SR.SHAPE,SP.SHAPE) = 'TRUE'
                                   AND    SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(SR.SHAPE,SP.SHAPE)) > 0);
                                   
  SELECT COUNT(*)
  INTO   nCont
  FROM   QGIS_T_SUOLO_LAVORAZIONE
  WHERE  ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione;
  
  IF nCont = 0 THEN
    -- rc 02/07/2021 jira-41
    DELETE QGIS_T_EVENTO_BLOCCATO
    WHERE  ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione;
    
    DELETE QGIS_T_EVENTO_LAVORAZIONE
    WHERE  ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nella rinuncia dell''istanza di riesame: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END RinunciaIstanzaRiesame;

-- rc 05/10/2021 jira-52
PROCEDURE InserisciSopralluogo(pIdEventoLavorazione           QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE,
                               pExtCodNazionale               VARCHAR2,
                               pFoglio                        NUMBER,
                               pIdAzienda                     NUMBER,
                               pExtIdUtenteAggiornamento      NUMBER,
                               pCodErrore                 OUT VARCHAR2,
                               pDescErrore                OUT VARCHAR2) IS

  nCampagna             QGIS_T_LISTA_LAVORAZIONE.CAMPAGNA%TYPE;
  nIdListaLavorazione   QGIS_T_LISTA_LAVORAZIONE.ID_LISTA_LAVORAZIONE%TYPE;
  nIdEventoLavorazione  QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE;
  vCodLavorazione       VARCHAR2(20);
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  SELECT LL.CAMPAGNA,CASE WHEN LL.ID_TIPO_SORGENTE_SUOLO = 4 THEN 'COSOPR' ELSE 'SOPR' END
  INTO   nCampagna,vCodLavorazione
  FROM   QGIS_T_LISTA_LAVORAZIONE LL,QGIS_T_EVENTO_LAVORAZIONE EL
  WHERE  EL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione
  AND    LL.ID_LISTA_LAVORAZIONE  = EL.ID_LISTA_LAVORAZIONE;
  
  BEGIN
    SELECT LL.ID_LISTA_LAVORAZIONE
    INTO   nIdListaLavorazione
    FROM   QGIS_T_LISTA_LAVORAZIONE LL
    WHERE  LL.CODICE   LIKE vCodLavorazione||'%'
    AND    LL.CAMPAGNA = nCampagna;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      INSERT INTO QGIS_T_LISTA_LAVORAZIONE
      (ID_LISTA_LAVORAZIONE, ID_TIPO_LISTA, CAMPAGNA, CODICE,
       DESCRIZIONE_LISTA,
       ID_TIPO_SORGENTE_SUOLO)
      VALUES
      (SEQ_QGIS_T_LISTA_LAVORAZIONE.NEXTVAL,2,nCampagna,vCodLavorazione,
       CASE WHEN vCodLavorazione = 'SOPR' THEN 'Sopralluoghi' ELSE 'Sopralluoghi CO' END||nCampagna,
       CASE WHEN vCodLavorazione = 'SOPR' THEN NULL ELSE 5 END)
      RETURNING ID_LISTA_LAVORAZIONE INTO nIdListaLavorazione;
  END;
  
  BEGIN
    SELECT EL.ID_EVENTO_LAVORAZIONE
    INTO   nIdEventoLavorazione
    FROM   QGIS_T_EVENTO_LAVORAZIONE EL
    WHERE  EL.ID_LISTA_LAVORAZIONE = nIdListaLavorazione
    AND    EL.EXT_ID_AZIENDA       = pIdAzienda
    AND    EL.DATA_LAVORAZIONE     IS NULL
    AND    NOT EXISTS              (SELECT 'X' 
                                    FROM   QGIS_T_SUOLO_LAVORAZIONE SL 
                                    WHERE  SL.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE
                                    AND    SL.FLAG_LAVORATO         = 'S')
    AND    NOT EXISTS              (SELECT 'X' 
                                    FROM   QGIS_T_PARTICELLA_LAVORAZIONE PL 
                                    WHERE  PL.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE
                                    AND    PL.FLAG_LAVORATO         = 'S');
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      INSERT INTO QGIS_T_EVENTO_LAVORAZIONE
      (ID_EVENTO_LAVORAZIONE, ID_LISTA_LAVORAZIONE, DATA_LAVORAZIONE, DATA_INSERIMENTO, EXT_ID_AZIENDA, EXT_ID_UTENTE_INSERIMENTO, 
       EXT_ID_UTENTE_LAVORAZIONE, EXT_ID_UTENTE_INSER_SITICLIENT, EXT_ID_UTENTE_LAVOR_SITICLIENT)
      VALUES
      (SEQ_QGIS_T_EVENTO_LAVORAZIONE.NEXTVAL,nIdListaLavorazione,NULL,SYSDATE,pIdAzienda,pExtIdUtenteAggiornamento,
       NULL,NULL,NULL)
      RETURNING ID_EVENTO_LAVORAZIONE INTO nIdEventoLavorazione;
  END;
  
  INSERT INTO QGIS_T_SUOLO_PROPOSTO 
  (ID_SUOLO_PROPOSTO, ID_EVENTO_LAVORAZIONE, EXT_ID_ELEGGIBILITA_RILEVATA, EXT_ID_ISTA_RIES, SHAPE, EXT_COD_NAZIONALE, 
   FOGLIO,IDENTIFICATIVO_PRATICA_ORIGINE,EXT_ID_PROCEDIMENTO, CLASSIFICAZIONE_ARCHIVIO_SIAP, IDENTIFICATIVO_PRATICA, 
   EXT_ID_AMM_COMPETENZA,DESCRIZIONE_BANDO, NUMERO_BANDO_DOC, GRUPPO_IDENTIFICATIVO)
  SELECT SEQ_QGIS_T_SUOLO_PROPOSTO.NEXTVAL,nIdEventoLavorazione, EXT_ID_ELEGGIBILITA_RILEVATA, EXT_ID_ISTA_RIES, SHAPE, EXT_COD_NAZIONALE, 
         FOGLIO,IDENTIFICATIVO_PRATICA_ORIGINE,EXT_ID_PROCEDIMENTO, CLASSIFICAZIONE_ARCHIVIO_SIAP, IDENTIFICATIVO_PRATICA, 
         EXT_ID_AMM_COMPETENZA,DESCRIZIONE_BANDO, NUMERO_BANDO_DOC, GRUPPO_IDENTIFICATIVO
  FROM   QGIS_T_SUOLO_PROPOSTO
  WHERE  ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione
  AND    EXT_COD_NAZIONALE     = pExtCodNazionale
  AND    FOGLIO                = pFoglio;
  
  -- rc 22/03/2022 jira-69
  INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
  (ID_SUOLO_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_SUOLO_RILEVATO, DESCRIZIONE_SOSPENSIONE, FLAG_SOSPENSIONE, 
   FLAG_CESSATO, NOTE_RICHIESTA,NOTE_LAVORAZIONE, ID_TIPO_MOTIVO_SOSPENSIONE, FLAG_LAVORATO, TIPO_SUOLO_ORIGINE, 
   IDENTIFICATIVO_PRATICA_ORIGINE,EXT_ID_UTENTE_LAVORAZIONE, DATA_LAVORAZIONE)
  SELECT SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,nIdEventoLavorazione, SL.ID_SUOLO_RILEVATO, SL.DESCRIZIONE_SOSPENSIONE, SL.FLAG_SOSPENSIONE, 
         SL.FLAG_CESSATO, SL.NOTE_RICHIESTA,SL.NOTE_LAVORAZIONE, SL.ID_TIPO_MOTIVO_SOSPENSIONE, SL.FLAG_LAVORATO, SL.TIPO_SUOLO_ORIGINE, 
         SL.IDENTIFICATIVO_PRATICA_ORIGINE,SL.EXT_ID_UTENTE_LAVORAZIONE, SL.DATA_LAVORAZIONE
  FROM   QGIS_T_SUOLO_LAVORAZIONE SL,QGIS_T_SUOLO_RILEVATO SR
  WHERE  SL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione
  AND    SR.ID_SUOLO_RILEVATO     = SL.ID_SUOLO_RILEVATO
  AND    SR.EXT_COD_NAZIONALE     = pExtCodNazionale
  AND    SR.FOGLIO                = pFoglio;
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nell''inserimento del sopralluogo: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END InserisciSopralluogo;

-- rc 03/12/2021 jira-63
PROCEDURE InserisciListaDaGeometria(pIdLista                       NUMBER, 
                                    pIdParticella                  NUMBER,
                                    pIdAppe                        NUMBER,
                                    pIdAppeLav                     NUMBER,
                                    pIdAzienda                     NUMBER,
                                    pDataParticella                DATE,        
                                    pExtIdUtenteAggiornamento      NUMBER,
                                    pCodErrore                 OUT VARCHAR2,
                                    pDescErrore                OUT VARCHAR2) IS

  listIdSuoloRilevato   ORA_MINING_NUMBER_NT := ORA_MINING_NUMBER_NT();
  nIdEventoLavorazione  QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE;
  nCont                 SIMPLE_INTEGER := 0;
  partGeo               LIST_PARTICELLA_GEOMETRIA := LIST_PARTICELLA_GEOMETRIA();
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  IF pIdParticella IS NOT NULL AND pIdAppe IS NOT NULL AND pIdAppeLav IS NOT NULL THEN
    pCodErrore  := '1';
    pDescErrore := 'I parametri per determinare la geometria sono stati valorizzati erroneamente';
    RETURN;
  END IF;
  
  IF pIdParticella IS NOT NULL THEN
    BEGIN
      SELECT OBJ_PARTICELLA_GEOMETRIA(pIdParticella,VP.SHAPE)  -- rc 07/02/2022
      BULK COLLECT INTO partGeo
      FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_REGISTRO_PARTICELLE RP,QGIS_T_LISTA_LAVORAZIONE LL
      WHERE  VP.EXT_ID_PARTICELLA      = pIdParticella
      -- RC 21/04/2022 JIRA-72
      AND    RP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA
      AND    RP.DATA_FINE_VALIDITA     IS NULL
      AND    LL.ID_LISTA_LAVORAZIONE   = pIdLista
      AND    RP.CAMPAGNA               = LL.CAMPAGNA;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        pCodErrore  := '1';
        pDescErrore := 'Non sono stati trovati suoli da inserire in lavorazione, si prega di contattare l''assistenza segnalando il problema';
        RETURN;
    END;
  END IF;
  
  IF pIdAppe IS NOT NULL THEN
    BEGIN
      SELECT OBJ_PARTICELLA_GEOMETRIA(PVT.ID_PART,VT.SHAPE_APPE)  -- rc 07/02/2022
      BULK COLLECT INTO partGeo
      FROM   SMRGAA.AABGAPPE_VERS_TAB VT,SMRGAA.AABGPART_VERS_TAB PVT
      WHERE  VT.ID_APPE     = pIdAppe
      AND    VT.ID_PCG_VERS = PVT.ID_PCG_VERS;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        pCodErrore  := '1';
        pDescErrore := 'Non sono stati trovati suoli da inserire in lavorazione, si prega di contattare l''assistenza segnalando il problema';
        RETURN;
    END;
  END IF;
  
  IF pIdAppeLav IS NOT NULL THEN
    BEGIN
      SELECT OBJ_PARTICELLA_GEOMETRIA(PT.ID_PART,DGT.SHAPE_SUOL_DICH)  -- rc 07/02/2022
      BULK COLLECT INTO partGeo
      FROM   SMRGAA.AABGSUOL_DICH_GRAF_TAB DGT,SMRGAA.AABGPCAT_TAB PT,SMRGAA.AABGISOL_PART_TAB IPT,SMRGAA.AABGSUOL_DICH_TAB DT
      WHERE  DGT.ID_SUOL_DICH = pIdAppeLav
      AND    PT.ID_PCAT       = IPT.ID_PCAT
      AND    IPT.ID_ISOL      = DT.ID_ISOL
      AND    DGT.ID_SUOL_DICH = DT.ID_SUOL_DICH;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        pCodErrore  := '1';
        pDescErrore := 'Non sono stati trovati suoli da inserire in lavorazione, si prega di contattare l''assistenza segnalando il problema';
        RETURN;
    END;
  END IF;
  
  -- rc 07/02/2022
  FOR rec IN (SELECT SR.ID_SUOLO_RILEVATO,SR.SHAPE SHAPE_SUOLI,PG.SHAPE
              FROM   QGIS_T_SUOLO_RILEVATO SR,TABLE(partGeo) PG,QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_VERSIONE_PARTICELLA VP,
                     QGIS_T_REGISTRO_SUOLI RS,QGIS_T_REGISTRO_PARTICELLE RP,QGIS_T_LISTA_LAVORAZIONE LL
              WHERE  SP.ID_SUOLO_RILEVATO      = SR.ID_SUOLO_RILEVATO
              AND    SP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA
              AND    VP.EXT_ID_PARTICELLA      = PG.ID_PARTICELLA
              -- RC 21/04/2022 JIRA-72
              AND    RS.ID_SUOLO_RILEVATO      = SP.ID_SUOLO_RILEVATO
              AND    RS.DATA_FINE_VALIDITA     IS NULL
              AND    RP.ID_VERSIONE_PARTICELLA = VP.ID_VERSIONE_PARTICELLA
              AND    RP.DATA_FINE_VALIDITA     IS NULL
              AND    LL.ID_LISTA_LAVORAZIONE   = pIdLista
              AND    RS.CAMPAGNA               = LL.CAMPAGNA
              AND    RP.CAMPAGNA               = LL.CAMPAGNA) LOOP
  
    IF SMRGAA.AABGAD_SDO.SDO_ANYINTERACT(rec.SHAPE_SUOLI,rec.SHAPE) = 1 THEN
      IF SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(rec.SHAPE_SUOLI,rec.SHAPE)) > 0 THEN
        listIdSuoloRilevato.EXTEND;
        listIdSuoloRilevato(listIdSuoloRilevato.COUNT) := rec.ID_SUOLO_RILEVATO;
      END IF;
    END IF;
  END LOOP;
  
  IF listIdSuoloRilevato.COUNT = 0 THEN
    pCodErrore  := '1';
    pDescErrore := 'Non sono stati trovati suoli da inserire in lavorazione, si prega di contattare l''assistenza segnalando il problema';
    RETURN;
  END IF;
  
  BEGIN
    SELECT EL.ID_EVENTO_LAVORAZIONE
    INTO   nIdEventoLavorazione
    FROM   QGIS_T_EVENTO_LAVORAZIONE EL
    WHERE  EL.ID_LISTA_LAVORAZIONE = pIdLista
    AND    EL.EXT_ID_AZIENDA       = pIdAzienda
    AND    EL.DATA_LAVORAZIONE     IS NULL;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      INSERT INTO QGIS_T_EVENTO_LAVORAZIONE
      (ID_EVENTO_LAVORAZIONE, ID_LISTA_LAVORAZIONE, DATA_LAVORAZIONE, DATA_INSERIMENTO, EXT_ID_AZIENDA, EXT_ID_UTENTE_INSERIMENTO, 
       EXT_ID_UTENTE_LAVORAZIONE, EXT_ID_UTENTE_INSER_SITICLIENT, EXT_ID_UTENTE_LAVOR_SITICLIENT,ID_ESITO)
      VALUES
      (SEQ_QGIS_T_EVENTO_LAVORAZIONE.NEXTVAL,pIdLista,NULL,SYSDATE,pIdAzienda,pExtIdUtenteAggiornamento,
       NULL,NULL,NULL,NULL)
      RETURNING ID_EVENTO_LAVORAZIONE INTO nIdEventoLavorazione;
  END;
  
  FOR rec IN (SELECT COLUMN_VALUE ID_SUOLO_RILEVATO
              FROM TABLE(listIdSuoloRilevato)) LOOP
              
    SELECT COUNT(*)
    INTO   nCont
    FROM   QGIS_T_SUOLO_LAVORAZIONE
    WHERE  ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione
    AND    ID_SUOLO_RILEVATO     = rec.ID_SUOLO_RILEVATO
    AND    FLAG_LAVORATO         = 'N';
    
    IF nCont = 0 THEN
      INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
      (ID_SUOLO_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_SUOLO_RILEVATO, DESCRIZIONE_SOSPENSIONE, FLAG_SOSPENSIONE, FLAG_CESSATO, 
       NOTE_RICHIESTA, NOTE_LAVORAZIONE, ID_TIPO_MOTIVO_SOSPENSIONE, FLAG_LAVORATO, TIPO_SUOLO_ORIGINE, IDENTIFICATIVO_PRATICA_ORIGINE, 
       EXT_ID_UTENTE_LAVORAZIONE, DATA_LAVORAZIONE)
      VALUES
      (SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,nIdEventoLavorazione,rec.ID_SUOLO_RILEVATO,NULL,'N','N',
       NULL,NULL,NULL,'N',NULL,NULL,
       NULL,NULL);
    END IF;
  END LOOP;
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nell''inserimento della lista da geometria: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END InserisciListaDaGeometria;

-- rc 14/02/2022 jira-67
PROCEDURE ValorizzaIdParticella(pIdParticella      NUMBER,
                                pCodErrore     OUT VARCHAR2,
                                pDescErrore    OUT VARCHAR2) IS

  vCodNazionale  QGIS_T_VERSIONE_PARTICELLA.EXT_COD_NAZIONALE%TYPE;
  nFoglio        QGIS_T_VERSIONE_PARTICELLA.FOGLIO%TYPE;
  vParticella    QGIS_T_VERSIONE_PARTICELLA.PARTICELLA%TYPE;
  vSubalterno    QGIS_T_VERSIONE_PARTICELLA.SUBALTERNO%TYPE;
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  SELECT S.COD_NAZIONALE,PC.FOGLIO,LPAD(PC.PARTICELLA,5,'0'),NVL(PC.SUBALTERNO,' ')
  INTO   vCodNazionale,nFoglio,vParticella,vSubalterno
  FROM   SMRGAA.DB_PARTICELLA_CERTIFICATA PC,SMRGAA.DB_SITICOMU S
  WHERE  PC.ID_PARTICELLA      = pIdParticella
  AND    PC.DATA_FINE_VALIDITA IS NULL
  AND    PC.COMUNE             = S.ISTAT_COMUNE
  AND    NVL(PC.SEZIONE,'-')   = NVL(S.ID_SEZC,'-');
  
  UPDATE QGIS_T_VERSIONE_PARTICELLA
  SET    EXT_ID_PARTICELLA = pIdParticella
  WHERE  EXT_COD_NAZIONALE = vCodNazionale
  AND    FOGLIO            = nFoglio
  AND    PARTICELLA        = vParticella
  AND    SUBALTERNO        = vSubalterno
  AND    EXT_ID_PARTICELLA IS NULL;
  
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nella valorizzazione dell''id particella: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END ValorizzaIdParticella;

-- rc 21/04/2022 jira-72
PROCEDURE AggiornaRegistroSuoli(pCampagna             NUMBER,
                                pExtCodNazionale      VARCHAR2,
                                pFoglio               NUMBER,
                                pArrayCessato         ORA_MINING_NUMBER_NT,
                                pArrayInserito        ORA_MINING_NUMBER_NT,
                                pCodErrore        OUT VARCHAR2,
                                pDescErrore       OUT VARCHAR2) IS

  nCont         SIMPLE_INTEGER := 0;
  dData         DATE := SYSDATE;
  listCampagna  ORA_MINING_NUMBER_NT := ORA_MINING_NUMBER_NT();
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  FOR rec IN (SELECT COLUMN_VALUE ID_SUOLO_RILEVATO FROM TABLE(pArrayCessato)) LOOP
    SELECT COUNT(*)
    INTO   nCont
    FROM   QGIS_T_REGISTRO_SUOLI
    WHERE  ID_SUOLO_RILEVATO  = rec.ID_SUOLO_RILEVATO
    AND    DATA_FINE_VALIDITA IS NULL;
    
    IF nCont = 0 THEN
      pCodErrore  := '1';
      pDescErrore := 'Uno o piu'' suoli cessati non sono presenti nel registro dei suoli per la campagna '||pCampagna;
      RETURN;
    END IF;
  END LOOP;
  
  FOR rec IN (SELECT ROWID ROW_ID,CAMPAGNA
              FROM   QGIS_T_REGISTRO_SUOLI
              WHERE  ID_SUOLO_RILEVATO   IN (SELECT COLUMN_VALUE FROM TABLE(pArrayCessato))
              AND    DATA_FINE_VALIDITA  IS NULL
              AND    CAMPAGNA           >= pCampagna) LOOP
  
    UPDATE QGIS_T_REGISTRO_SUOLI
    SET    DATA_FINE_VALIDITA = dData
    WHERE  ROWID              = rec.ROW_ID;
    
    listCampagna.EXTEND;
    listCampagna(listCampagna.COUNT) := rec.CAMPAGNA;
  END LOOP;
  
  FOR recCampagna IN (SELECT DISTINCT COLUMN_VALUE CAMPAGNA FROM TABLE(listCampagna)) LOOP
    FOR rec IN (SELECT COLUMN_VALUE ID_SUOLO_RILEVATO FROM TABLE(pArrayInserito)) LOOP
      
      SELECT COUNT(*)
      INTO   nCont
      FROM   QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_SUOLO_PARTICELLA SP1,QGIS_T_REGISTRO_SUOLI RS,QGIS_T_SUOLO_RILEVATO SR
      WHERE  SP.ID_SUOLO_RILEVATO      = rec.ID_SUOLO_RILEVATO
      AND    SP.ID_VERSIONE_PARTICELLA = SP1.ID_VERSIONE_PARTICELLA
      AND    SP1.ID_SUOLO_RILEVATO     = RS.ID_SUOLO_RILEVATO
      AND    RS.CAMPAGNA               = recCampagna.CAMPAGNA
      AND    RS.DATA_FINE_VALIDITA     IS NULL
      AND    RS.ID_SUOLO_RILEVATO      = SR.ID_SUOLO_RILEVATO
      AND    SR.CAMPAGNA               > pCampagna;
      
      IF nCont = 0 THEN
        INSERT INTO QGIS_T_REGISTRO_SUOLI
        (ID_REGISTRO_SUOLI, EXT_COD_NAZIONALE, FOGLIO, CAMPAGNA, ID_SUOLO_RILEVATO, DATA_INIZIO_VALIDITA, DATA_FINE_VALIDITA)
        VALUES
        (SEQ_QGIS_T_REGISTRO_SUOLI.NEXTVAL,pExtCodNazionale,pFoglio,recCampagna.CAMPAGNA,rec.ID_SUOLO_RILEVATO,dData,NULL);
      END IF;
    END LOOP;
  END LOOP;
  
  IF pArrayCessato.COUNT = 0 OR pArrayCessato IS NULL THEN
    FOR rec IN (SELECT COLUMN_VALUE ID_SUOLO_RILEVATO FROM TABLE(pArrayInserito)) LOOP
      INSERT INTO QGIS_T_REGISTRO_SUOLI
      (ID_REGISTRO_SUOLI, EXT_COD_NAZIONALE, FOGLIO, CAMPAGNA, ID_SUOLO_RILEVATO, DATA_INIZIO_VALIDITA, DATA_FINE_VALIDITA)
      VALUES
      (SEQ_QGIS_T_REGISTRO_SUOLI.NEXTVAL,pExtCodNazionale,pFoglio,pCampagna,rec.ID_SUOLO_RILEVATO,dData,NULL);
    END LOOP;
  END IF;
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nell''aggiornamento del registro suoli: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END AggiornaRegistroSuoli;

-- rc 21/04/2022 jira-72
PROCEDURE AggiornaRegistroParticelle(pCampagna             NUMBER,
                                     pExtCodNazionale      VARCHAR2,
                                     pFoglio               NUMBER,
                                     pArrayCessato         ORA_MINING_NUMBER_NT,
                                     pArrayInserito        ORA_MINING_NUMBER_NT,
                                     pCodErrore        OUT VARCHAR2,
                                     pDescErrore       OUT VARCHAR2) IS

  nCont         SIMPLE_INTEGER := 0;
  dData         DATE := SYSDATE;
  listCampagna  ORA_MINING_NUMBER_NT := ORA_MINING_NUMBER_NT();
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  FOR rec IN (SELECT COLUMN_VALUE ID_VERSIONE_PARTICELLA FROM TABLE(pArrayCessato)) LOOP
    SELECT COUNT(*)
    INTO   nCont
    FROM   QGIS_T_REGISTRO_PARTICELLE
    WHERE  ID_VERSIONE_PARTICELLA = rec.ID_VERSIONE_PARTICELLA
    AND    DATA_FINE_VALIDITA     IS NULL;
    
    IF nCont = 0 THEN
      pCodErrore  := '1';
      pDescErrore := 'Una o piu'' particelle cessate non sono presenti nel registro delle particelle per la campagna '||pCampagna;
      RETURN;
    END IF;
  END LOOP;
  
  FOR rec IN (SELECT ROWID ROW_ID,CAMPAGNA
              FROM   QGIS_T_REGISTRO_PARTICELLE
              WHERE  ID_VERSIONE_PARTICELLA IN (SELECT COLUMN_VALUE FROM TABLE(pArrayCessato))
              AND    DATA_FINE_VALIDITA     IS NULL
              AND    CAMPAGNA              >= pCampagna) LOOP
  
    UPDATE QGIS_T_REGISTRO_PARTICELLE
    SET    DATA_FINE_VALIDITA = dData
    WHERE  ROWID              = rec.ROW_ID;
    
    listCampagna.EXTEND;
    listCampagna(listCampagna.COUNT) := rec.CAMPAGNA;
  END LOOP;
  
  FOR recCampagna IN (SELECT DISTINCT COLUMN_VALUE CAMPAGNA FROM TABLE(listCampagna)) LOOP
    FOR rec IN (SELECT COLUMN_VALUE ID_VERSIONE_PARTICELLA FROM TABLE(pArrayInserito)) LOOP
      INSERT INTO QGIS_T_REGISTRO_PARTICELLE
      (ID_REGISTRO_PARTICELLE, EXT_COD_NAZIONALE, FOGLIO, CAMPAGNA, ID_VERSIONE_PARTICELLA, DATA_INIZIO_VALIDITA, DATA_FINE_VALIDITA)
      VALUES
      (SEQ_QGIS_T_REGISTRO_PARTICELLE.NEXTVAL,pExtCodNazionale,pFoglio,recCampagna.CAMPAGNA,rec.ID_VERSIONE_PARTICELLA,dData,NULL);
    END LOOP;
  END LOOP;
  
  IF pArrayCessato.COUNT = 0 OR pArrayCessato IS NULL THEN
    FOR rec IN (SELECT COLUMN_VALUE ID_VERSIONE_PARTICELLA FROM TABLE(pArrayInserito)) LOOP
      INSERT INTO QGIS_T_REGISTRO_PARTICELLE
      (ID_REGISTRO_PARTICELLE, EXT_COD_NAZIONALE, FOGLIO, CAMPAGNA, ID_VERSIONE_PARTICELLA, DATA_INIZIO_VALIDITA, DATA_FINE_VALIDITA)
      VALUES
      (SEQ_QGIS_T_REGISTRO_PARTICELLE.NEXTVAL,pExtCodNazionale,pFoglio,pCampagna,rec.ID_VERSIONE_PARTICELLA,dData,NULL);
    END LOOP;
  END IF;
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nell''aggiornamento del registro particelle: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END AggiornaRegistroParticelle;

-- rc 28/04/2022 jira-73
PROCEDURE InserisciListaLavorazioneCO(pIdAzienda                     NUMBER,
                                      pCampagna                      NUMBER,
                                      pIdCatalogoMatrice             NUMBER,
                                      pGeometria                     SDO_GEOMETRY,
                                      pExtIdUtenteAggiornamento      NUMBER,
                                      pArrayParticelle               ORA_MINING_NUMBER_NT,
                                      -- rc 18/07/2022 jira-82
                                      pIdentificativoPraticaOrigine  VARCHAR2,
                                      pExtIdProcedimento             NUMBER,
                                      pClassificazioneArchivioSiap   VARCHAR2,
                                      pIdentificativoPratica         VARCHAR2,
                                      pExtIdAmmCompetenza            NUMBER,
                                      pDescrizioneBando              VARCHAR2,
                                      pNumeroBandoDoc                VARCHAR2,
                                      pGruppoIdentificativo          VARCHAR2,
                                      pCodErrore                 OUT VARCHAR2,
                                      pDescErrore                OUT VARCHAR2) IS

  nIdListaLavorazione      QGIS_T_LISTA_LAVORAZIONE.ID_LISTA_LAVORAZIONE%TYPE;
  nIdEventoLavorazione     QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE;
  vCodiRile                VARCHAR2(3);
  nCodiProdRile            NUMBER(3);
  nIdEleggibilitaRilevata  QGIS_T_SUOLO_PROPOSTO.EXT_ID_ELEGGIBILITA_RILEVATA%TYPE;
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  SMRGAA.AABGAD_IN.getRileAppezzamento(pIdCatalogoMatrice,vCodiRile,nCodiProdRile,pCodErrore,pDescErrore);
  
  IF pCodErrore != '0' THEN
    RETURN;
  END IF;
  
  SELECT ID_ELEGGIBILITA_RILEVATA
  INTO   nIdEleggibilitaRilevata
  FROM   SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA
  WHERE  CODI_RILE_PROD     = vCodiRile
  AND    DATA_FINE_VALIDITA IS NULL;
  
  BEGIN
    SELECT ID_LISTA_LAVORAZIONE
    INTO   nIdListaLavorazione
    FROM   QGIS_T_LISTA_LAVORAZIONE
    WHERE  ID_TIPO_SORGENTE_SUOLO = 4
    AND    CAMPAGNA               = pCampagna;
  EXCEPTION
    WHEN TOO_MANY_ROWS THEN
      pCodErrore  := '1';
      pDescErrore := 'Errore nella configurazione della lista dei controlli oggettivi per la campagna '||pCampagna;
      RETURN;
    WHEN NO_DATA_FOUND THEN
      INSERT INTO QGIS_T_LISTA_LAVORAZIONE
      (ID_LISTA_LAVORAZIONE, ID_TIPO_LISTA, CAMPAGNA, CODICE, DESCRIZIONE_LISTA, ID_TIPO_SORGENTE_SUOLO)
      VALUES
      (SEQ_QGIS_T_LISTA_LAVORAZIONE.NEXTVAL,1,pCampagna,'C.O.','Lista dei controlli oggettivi per la campagna '||pCampagna,4)
      RETURNING ID_LISTA_LAVORAZIONE INTO nIdListaLavorazione;
  END;
  
  BEGIN
    SELECT EL.ID_EVENTO_LAVORAZIONE
    INTO   nIdEventoLavorazione
    FROM   QGIS_T_EVENTO_LAVORAZIONE EL
    WHERE  EL.ID_LISTA_LAVORAZIONE = nIdListaLavorazione
    AND    EL.EXT_ID_AZIENDA       = pIdAzienda
    AND    EL.DATA_LAVORAZIONE     IS NULL
    AND    NOT EXISTS              (SELECT 'X'
                                    FROM   QGIS_T_SUOLO_LAVORAZIONE SL
                                    WHERE  SL.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE
                                    AND    SL.FLAG_LAVORATO         = 'S')
    AND    NOT EXISTS              (SELECT 'X'
                                    FROM   QGIS_T_PARTICELLA_LAVORAZIONE PL
                                    WHERE  PL.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE
                                    AND    PL.FLAG_LAVORATO         = 'S');
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      INSERT INTO QGIS_T_EVENTO_LAVORAZIONE
      (ID_EVENTO_LAVORAZIONE, ID_LISTA_LAVORAZIONE, DATA_LAVORAZIONE, DATA_INSERIMENTO, EXT_ID_AZIENDA, EXT_ID_UTENTE_INSERIMENTO, 
       EXT_ID_UTENTE_LAVORAZIONE, EXT_ID_UTENTE_INSER_SITICLIENT, EXT_ID_UTENTE_LAVOR_SITICLIENT, ID_ESITO)
      VALUES
      (SEQ_QGIS_T_EVENTO_LAVORAZIONE.NEXTVAL,nIdListaLavorazione,NULL,SYSDATE,pIdAzienda,pExtIdUtenteAggiornamento,
       NULL,NULL,NULL,NULL)
      RETURNING ID_EVENTO_LAVORAZIONE INTO nIdEventoLavorazione;
  END;
  
  FOR rec IN (SELECT DISTINCT SP.ID_SUOLO_RILEVATO,VP.EXT_COD_NAZIONALE,VP.FOGLIO
              FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_REGISTRO_CO RC,QGIS_T_SUOLO_PARTICELLA SP
              WHERE  RC.CAMPAGNA                          = pCampagna
              AND    RC.DATA_FINE_VALIDITA                IS NULL
              AND    SP.ID_VERSIONE_PARTICELLA            = VP.ID_VERSIONE_PARTICELLA
              AND    SP.ID_SUOLO_RILEVATO                 = RC.ID_SUOLO_RILEVATO
              AND    SDO_ANYINTERACT(VP.SHAPE,pGeometria) = 'TRUE'
              AND    VP.EXT_ID_PARTICELLA                 IN (SELECT COLUMN_VALUE
                                                              FROM TABLE(pArrayParticelle))
              AND    SMRGAA.AABGAD_SDO.SDO_AREA(SMRGAA.AABGAD_SDO.SDO_INTERSECTION(VP.SHAPE,pGeometria)) > 0
              AND    NOT EXISTS                           (SELECT 'X'
                                                           FROM   QGIS_T_SUOLO_LAVORAZIONE SL
                                                           WHERE  SL.ID_EVENTO_LAVORAZIONE = nIdEventoLavorazione
                                                           AND    SL.ID_SUOLO_RILEVATO     = SP.ID_SUOLO_RILEVATO
                                                           AND    SL.FLAG_LAVORATO         = 'N')) LOOP
              
    INSERT INTO QGIS_T_SUOLO_LAVORAZIONE
    (ID_SUOLO_LAVORAZIONE, ID_EVENTO_LAVORAZIONE, ID_SUOLO_RILEVATO, DESCRIZIONE_SOSPENSIONE, FLAG_SOSPENSIONE, FLAG_CESSATO, 
     NOTE_RICHIESTA,NOTE_LAVORAZIONE, ID_TIPO_MOTIVO_SOSPENSIONE, FLAG_LAVORATO, TIPO_SUOLO_ORIGINE, IDENTIFICATIVO_PRATICA_ORIGINE, 
     EXT_ID_UTENTE_LAVORAZIONE, DATA_LAVORAZIONE)
    VALUES
    (SEQ_QGIS_T_SUOLO_LAVORAZIONE.NEXTVAL,nIdEventoLavorazione,rec.ID_SUOLO_RILEVATO,NULL,'N','N',
     NULL,NULL,NULL,'N',NULL,NULL,
     NULL,NULL);
     
    INSERT INTO QGIS_T_SUOLO_PROPOSTO
    (ID_SUOLO_PROPOSTO, ID_EVENTO_LAVORAZIONE, EXT_ID_ELEGGIBILITA_RILEVATA, EXT_ID_ISTA_RIES, SHAPE, EXT_COD_NAZIONALE, FOGLIO, 
     IDENTIFICATIVO_PRATICA_ORIGINE,EXT_ID_PROCEDIMENTO, CLASSIFICAZIONE_ARCHIVIO_SIAP, IDENTIFICATIVO_PRATICA, 
     EXT_ID_AMM_COMPETENZA,DESCRIZIONE_BANDO, NUMERO_BANDO_DOC, GRUPPO_IDENTIFICATIVO)
    VALUES
    (SEQ_QGIS_T_SUOLO_PROPOSTO.NEXTVAL,nIdEventoLavorazione,nIdEleggibilitaRilevata,NULL,pGeometria,rec.EXT_COD_NAZIONALE,rec.FOGLIO,
     pIdentificativoPraticaOrigine,pExtIdProcedimento,pClassificazioneArchivioSiap,pIdentificativoPratica,
     pExtIdAmmCompetenza,pDescrizioneBando,pNumeroBandoDoc,pGruppoIdentificativo);
  END LOOP;
  
  -- rc 15/06/2022 jira-78
  SMRGAA.PCK_SMRGAA_UTILITY_QGIS.InserisciEventoCo(pIdAzienda,pCampagna,pExtIdUtenteAggiornamento,pCodErrore,pDescErrore);
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nell''inserimento delle liste di lavorazione dei controlli oggettivi: '||SQLERRM||' - RIGA = '||
                   dbms_utility.FORMAT_ERROR_BACKTRACE;  
END InserisciListaLavorazioneCO;

-- rc 28/04/2022 jira-73
PROCEDURE EsitoLavorazioneCo(pIdAzienda       NUMBER,
                             pCampagna        NUMBER,
                             pEsito       OUT NUMBER,
                             pDescEsito   OUT VARCHAR2,
                             pCodErrore   OUT VARCHAR2,
                             pDescErrore  OUT VARCHAR2) IS

  nIdListaLavorazione  QGIS_T_LISTA_LAVORAZIONE.ID_LISTA_LAVORAZIONE%TYPE;
  nCont                SIMPLE_INTEGER := 0;
  dDataLavorazione     QGIS_T_EVENTO_LAVORAZIONE.DATA_LAVORAZIONE%TYPE;
  dDtUltimaEsecuzione  QGIS_D_NOME_BATCH.DT_ULTIMA_ESECUZIONE%TYPE;
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  BEGIN
    SELECT ID_LISTA_LAVORAZIONE
    INTO   nIdListaLavorazione
    FROM   QGIS_T_LISTA_LAVORAZIONE
    WHERE  ID_TIPO_SORGENTE_SUOLO IN (4,5)
    AND    CAMPAGNA               = pCampagna;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      pCodErrore  := '1';
      pDescErrore := 'Non e'' presente la lista dei C.O. per la campagna '||pCampagna;
      RETURN;
  END;
  
  SELECT COUNT(*)
  INTO   nCont
  FROM   QGIS_T_EVENTO_LAVORAZIONE EL,QGIS_T_SUOLO_LAVORAZIONE SL
  WHERE  EL.ID_LISTA_LAVORAZIONE  = nIdListaLavorazione
  AND    EL.EXT_ID_AZIENDA        = pIdAzienda
  -- rc 09/05/2022 jira-73
  AND    SL.ID_EVENTO_LAVORAZIONE = EL.ID_EVENTO_LAVORAZIONE;
  
  IF nCont = 0 THEN
    pEsito     := 1;
    pDescEsito := 'Non esiste la richiesta di lavorazione';
    RETURN;
  END IF;
  
  SELECT COUNT(*)
  INTO   nCont
  FROM   QGIS_T_EVENTO_LAVORAZIONE EL,QGIS_T_SUOLO_LAVORAZIONE SL
  WHERE  EL.ID_LISTA_LAVORAZIONE   = nIdListaLavorazione
  AND    EL.EXT_ID_AZIENDA         = pIdAzienda
  AND    SL.ID_EVENTO_LAVORAZIONE  = EL.ID_EVENTO_LAVORAZIONE
  AND    EL.ID_ESITO              != 3;  -- rc 24/05/2022 jira-74
  
  IF nCont != 0 THEN
    pEsito     := 2;
    pDescEsito := 'Lista di lavorazione ancora da evadere';
  ELSE
    -- rc 24/05/2022 jira-74
    SELECT EL.DATA_LAVORAZIONE
    INTO   dDataLavorazione
    FROM   QGIS_T_EVENTO_LAVORAZIONE EL
    WHERE  EL.ID_LISTA_LAVORAZIONE = nIdListaLavorazione
    AND    EL.EXT_ID_AZIENDA       = pIdAzienda;
    
    SELECT DT_ULTIMA_ESECUZIONE
    INTO   dDtUltimaEsecuzione
    FROM   QGIS_D_NOME_BATCH
    WHERE  ID_NOME_BATCH = 1;
    
    IF dDataLavorazione < dDtUltimaEsecuzione THEN
      pEsito     := 3;
      pDescEsito := 'Lista di lavorazione evasa';
    ELSE
      pEsito     := 2;
      pDescEsito := 'Lista di lavorazione ancora da evadere';
    END IF;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nella ricerca dell''esito di lavorazione dei controlli oggettivi: '||SQLERRM||' - RIGA = '||
                   dbms_utility.FORMAT_ERROR_BACKTRACE;  
END EsitoLavorazioneCo;

-- rc 25/05/2022 jira-74
PROCEDURE AggiornaRegistroCo(pCampagna             NUMBER,
                             pExtCodNazionale      VARCHAR2,
                             pFoglio               NUMBER,
                             pArrayCessato         ORA_MINING_NUMBER_NT,
                             pArrayInserito        ORA_MINING_NUMBER_NT,
                             pCodErrore        OUT VARCHAR2,
                             pDescErrore       OUT VARCHAR2) IS

  nCont         SIMPLE_INTEGER := 0;
  dData         DATE := SYSDATE;
  listCampagna  ORA_MINING_NUMBER_NT := ORA_MINING_NUMBER_NT();
  ArrayCessato  ORA_MINING_NUMBER_NT := ORA_MINING_NUMBER_NT();
BEGIN
  pCodErrore  := '0';
  pDescErrore := NULL;
  
  FOR rec IN (SELECT COLUMN_VALUE ID_SUOLO_RILEVATO FROM TABLE(pArrayCessato)) LOOP
    SELECT COUNT(*)
    INTO   nCont
    FROM   QGIS_T_REGISTRO_CO
    WHERE  ID_SUOLO_RILEVATO  = rec.ID_SUOLO_RILEVATO
    AND    DATA_FINE_VALIDITA IS NULL;
    
    IF nCont = 0 THEN
      pCodErrore  := '1';
      pDescErrore := 'Uno o piu'' suoli cessati non sono presenti nel registro dei C.O. per la campagna '||pCampagna;
      RETURN;
    END IF;
  END LOOP;
  
  FOR rec IN (SELECT ROWID ROW_ID,CAMPAGNA
              FROM   QGIS_T_REGISTRO_CO
              WHERE  ID_SUOLO_RILEVATO   IN (SELECT COLUMN_VALUE FROM TABLE(pArrayCessato))
              AND    DATA_FINE_VALIDITA  IS NULL
              AND    CAMPAGNA           >= pCampagna) LOOP
  
    UPDATE QGIS_T_REGISTRO_CO
    SET    DATA_FINE_VALIDITA = dData
    WHERE  ROWID              = rec.ROW_ID;
    
    listCampagna.EXTEND;
    listCampagna(listCampagna.COUNT) := rec.CAMPAGNA;
  END LOOP;
  
  FOR recCampagna IN (SELECT DISTINCT COLUMN_VALUE CAMPAGNA FROM TABLE(listCampagna)) LOOP
    FOR rec IN (SELECT COLUMN_VALUE ID_SUOLO_RILEVATO FROM TABLE(pArrayInserito)) LOOP
      INSERT INTO QGIS_T_REGISTRO_CO
      (ID_REGISTRO_CO, EXT_COD_NAZIONALE, FOGLIO, CAMPAGNA, ID_SUOLO_RILEVATO, DATA_INIZIO_VALIDITA, DATA_FINE_VALIDITA)
      VALUES
      (SEQ_QGIS_T_REGISTRO_CO.NEXTVAL,pExtCodNazionale,pFoglio,recCampagna.CAMPAGNA,rec.ID_SUOLO_RILEVATO,dData,NULL);
    END LOOP;
  END LOOP;
  
  IF pArrayCessato.COUNT = 0 OR pArrayCessato IS NULL THEN
    FOR rec IN (SELECT COLUMN_VALUE ID_SUOLO_RILEVATO FROM TABLE(pArrayInserito)) LOOP
      INSERT INTO QGIS_T_REGISTRO_CO
      (ID_REGISTRO_CO, EXT_COD_NAZIONALE, FOGLIO, CAMPAGNA, ID_SUOLO_RILEVATO, DATA_INIZIO_VALIDITA, DATA_FINE_VALIDITA)
      VALUES
      (SEQ_QGIS_T_REGISTRO_CO.NEXTVAL,pExtCodNazionale,pFoglio,pCampagna,rec.ID_SUOLO_RILEVATO,dData,NULL);
    END LOOP;
  END IF;
  
  SELECT DISTINCT SP1.ID_SUOLO_RILEVATO
  BULK COLLECT INTO ArrayCessato
  FROM   QGIS_T_SUOLO_PARTICELLA SP,QGIS_T_SUOLO_PARTICELLA SP1,QGIS_T_REGISTRO_SUOLI RS
  WHERE  SP.ID_SUOLO_RILEVATO      IN (SELECT COLUMN_VALUE FROM TABLE(pArrayInserito))
  AND    SP.ID_VERSIONE_PARTICELLA = SP1.ID_VERSIONE_PARTICELLA
  AND    RS.ID_SUOLO_RILEVATO      = SP1.ID_SUOLO_RILEVATO
  AND    RS.CAMPAGNA               = pCampagna
  AND    RS.DATA_FINE_VALIDITA     IS NULL;
  
  AggiornaRegistroSuoli(pCampagna,pExtCodNazionale,pFoglio,ArrayCessato,pArrayInserito,pCodErrore,pDescErrore);
EXCEPTION
  WHEN OTHERS THEN
    pCodErrore  := '1';
    pDescErrore := 'Errore nell''aggiornamento del registro co: '||SQLERRM||' - RIGA = '||dbms_utility.FORMAT_ERROR_BACKTRACE;  
END AggiornaRegistroCo;

END PCK_QGIS_LIBRERIA;

/