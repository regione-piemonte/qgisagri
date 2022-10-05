CREATE OR REPLACE PACKAGE BODY PCK_QGIS_UTILITY_API AS

-- RC 09/01/2020 JIRA-4251
FUNCTION getSuoliInLavorazione(pIdEventoLavorazione  QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE,
                               pCodNazionale         QGIS_T_SUOLO_RILEVATO.EXT_COD_NAZIONALE%TYPE,
                               pFoglio               QGIS_T_SUOLO_RILEVATO.FOGLIO%TYPE) RETURN LIST_SUOLI_IN_LAVORAZIONE IS

  nExtIdAzienda             QGIS_T_EVENTO_LAVORAZIONE.EXT_ID_AZIENDA%TYPE;
  nCampagna                 QGIS_T_LISTA_LAVORAZIONE.CAMPAGNA%TYPE;
  outVal                    LIST_SUOLI_IN_LAVORAZIONE := LIST_SUOLI_IN_LAVORAZIONE();
  vTipoSuolo                VARCHAR2(20);
  nIdParticella             QGIS_T_VERSIONE_PARTICELLA.EXT_ID_PARTICELLA%TYPE;
  vPartCond                 VARCHAR2(20);
  vNoteRichiesta            QGIS_T_SUOLO_LAVORAZIONE.NOTE_RICHIESTA%TYPE;
  nIdSuoloLavorazione       QGIS_T_SUOLO_LAVORAZIONE.ID_SUOLO_LAVORAZIONE%TYPE;
  nSrid                     NUMBER;
  nIdTipoMotivoSospensione  QGIS_T_SUOLO_LAVORAZIONE.ID_TIPO_MOTIVO_SOSPENSIONE%TYPE;
  vFlagSospensione          QGIS_T_SUOLO_LAVORAZIONE.FLAG_SOSPENSIONE%TYPE;
  vDescrizioneSospensione   QGIS_T_SUOLO_LAVORAZIONE.DESCRIZIONE_SOSPENSIONE%TYPE;
  nIdTipoSorgenteSuolo      QGIS_T_LISTA_LAVORAZIONE.ID_TIPO_SORGENTE_SUOLO%TYPE;
BEGIN
  SELECT EL.EXT_ID_AZIENDA,LL.CAMPAGNA,NVL(LL.ID_TIPO_SORGENTE_SUOLO,0)
  INTO   nExtIdAzienda,nCampagna,nIdTipoSorgenteSuolo
  FROM   QGIS_T_EVENTO_LAVORAZIONE EL,QGIS_T_LISTA_LAVORAZIONE LL
  WHERE  EL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione
  AND    EL.ID_LISTA_LAVORAZIONE  = LL.ID_LISTA_LAVORAZIONE;
  
  FOR rec IN (SELECT SR.ID_SUOLO_RILEVATO,SR.ID_TIPO_SORGENTE_SUOLO,
                     SDO_UTIL.TO_WKTGEOMETRY(CASE WHEN SMRGAA.AABGAD_SDO.SDO_FIX(SR.SHAPE) IS NULL THEN SR.SHAPE
                                             ELSE SMRGAA.AABGAD_SDO.SDO_FIX(SR.SHAPE) END) WKT,
                     --SDO_UTIL.TO_WKTGEOMETRY(SMRGAA.AABGAD_SDO.SDO_FIX(SR.SHAPE)) WKT,
                     SR.EXT_COD_NAZIONALE,SR.FOGLIO,SR.EXT_ID_ELEGGIBILITA_RILEVATA,TER.CODI_RILE_PROD,SR.FLAG_GEOM_CORROTTA,SR.SHAPE
              FROM   QGIS_T_SUOLO_RILEVATO SR,SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA TER
              WHERE  SR.EXT_ID_ELEGGIBILITA_RILEVATA = TER.ID_ELEGGIBILITA_RILEVATA
              AND    SR.EXT_COD_NAZIONALE            = pCodNazionale
              AND    SR.FOGLIO                       = pFoglio
              -- rc 26/05/2022 jira-74
              AND    ((nIdTipoSorgenteSuolo IN (4,5) AND SR.ID_SUOLO_RILEVATO IN (SELECT RC.ID_SUOLO_RILEVATO
                                                                                  FROM   QGIS_T_REGISTRO_CO RC
                                                                                  WHERE  RC.CAMPAGNA           = nCampagna
                                                                                  AND    RC.DATA_FINE_VALIDITA IS NULL)) OR
                      (nIdTipoSorgenteSuolo NOT IN (4,5) AND SR.ID_SUOLO_RILEVATO IN (SELECT RS.ID_SUOLO_RILEVATO
                                                                                      FROM   QGIS_T_REGISTRO_SUOLI RS
                                                                                      WHERE  RS.CAMPAGNA           = nCampagna
                                                                                      AND    RS.DATA_FINE_VALIDITA IS NULL)))) LOOP
  
    BEGIN
      SELECT NOTE_RICHIESTA,ID_SUOLO_LAVORAZIONE,TIPO_SUOLO_ORIGINE,ID_TIPO_MOTIVO_SOSPENSIONE,FLAG_SOSPENSIONE,DESCRIZIONE_SOSPENSIONE
      INTO   vNoteRichiesta,nIdSuoloLavorazione,vTipoSuolo,nIdTipoMotivoSospensione,vFlagSospensione,vDescrizioneSospensione
      FROM   QGIS_T_SUOLO_LAVORAZIONE
      WHERE  ID_SUOLO_LAVORAZIONE = (SELECT MAX(SL.ID_SUOLO_LAVORAZIONE)
                                     FROM   QGIS_T_SUOLO_LAVORAZIONE SL
                                     WHERE  SL.ID_SUOLO_RILEVATO     = rec.ID_SUOLO_RILEVATO
                                     AND    SL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione);
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        vNoteRichiesta           := NULL;
        nIdSuoloLavorazione      := NULL;
        vTipoSuolo               := NULL;
        nIdTipoMotivoSospensione := NULL;
        vFlagSospensione         := NULL;
        vDescrizioneSospensione  := NULL;
    END;
    
    /*SELECT MAX(VP.EXT_ID_PARTICELLA)
    INTO   nIdParticella
    FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_SUOLO_PARTICELLA SP
    WHERE  VP.ID_VERSIONE_PARTICELLA = SP.ID_VERSIONE_PARTICELLA
    AND    SP.ID_SUOLO_RILEVATO      = rec.ID_SUOLO_RILEVATO;

    vPartCond := SMRGAA.PCK_SMRGAA_UTILITY_QGIS.IsParticellaCondotta(nIdParticella,nExtIdAzienda,nCampagna);

    IF nIdParticella IS NULL THEN
      vPartCond := 'N';
    END IF;*/
    
    IF vTipoSuolo IS NULL THEN    
      SELECT MAX(VP.EXT_ID_PARTICELLA)
      INTO   nIdParticella
      FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_SUOLO_PARTICELLA SP
      WHERE  VP.ID_VERSIONE_PARTICELLA = SP.ID_VERSIONE_PARTICELLA
      AND    SP.ID_SUOLO_RILEVATO      = rec.ID_SUOLO_RILEVATO;

      IF nIdParticella IS NULL THEN
        vPartCond := 'N';
      ELSE
        vPartCond := SMRGAA.PCK_SMRGAA_UTILITY_QGIS.IsParticellaCondotta(nIdParticella,nExtIdAzienda,nCampagna);
      END IF;
      
      IF nIdSuoloLavorazione IS NOT NULL AND rec.FLAG_GEOM_CORROTTA = 'N' THEN
        vTipoSuolo := 'LAV';
      END IF;
    
      IF nIdSuoloLavorazione IS NULL AND rec.FLAG_GEOM_CORROTTA = 'N' AND vPartCond = 'S' THEN
        vTipoSuolo := 'COND';
      END IF;
    
      IF nIdSuoloLavorazione IS NULL AND rec.FLAG_GEOM_CORROTTA = 'S' AND vPartCond = 'N' THEN
        vTipoSuolo := 'KO';
      END IF;
    
      IF nIdSuoloLavorazione IS NOT NULL AND rec.FLAG_GEOM_CORROTTA = 'S' THEN
        vTipoSuolo := 'LAV_KO';
      END IF;
    
      IF nIdSuoloLavorazione IS NULL AND rec.FLAG_GEOM_CORROTTA = 'S' AND vPartCond = 'S' THEN
        vTipoSuolo := 'COND_KO';
      END IF;
    
      IF nIdSuoloLavorazione IS NULL AND rec.FLAG_GEOM_CORROTTA = 'N' AND vPartCond = 'N' THEN
        vTipoSuolo := 'NO_COND';
      END IF;
    END IF;
    
    nSrid := SMRGAA.PCK_SMRGAA_STRUMENTI_GRAFICI.getCodiEPSG(rec.SHAPE);
    
    outVal.EXTEND;
    outVal(outVal.COUNT) := OBJ_SUOLI_IN_LAVORAZIONE(rec.ID_SUOLO_RILEVATO,rec.WKT,rec.EXT_COD_NAZIONALE,rec.FOGLIO,
                                                     rec.EXT_ID_ELEGGIBILITA_RILEVATA,rec.CODI_RILE_PROD,vNoteRichiesta,vTipoSuolo,nSrid,
                                                     nIdTipoMotivoSospensione,vFlagSospensione,vDescrizioneSospensione,
                                                     rec.ID_TIPO_SORGENTE_SUOLO);  -- rc 25/05/2022 jira-74
  END LOOP;
  
  RETURN outVal;
END getSuoliInLavorazione;

-- rc 05/10/2021
FUNCTION getNumSuoliLavoraz(pIdEventoLavorazione  QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE,
                            pCodNazionale         QGIS_T_SUOLO_RILEVATO.EXT_COD_NAZIONALE%TYPE,
                            pFoglio               QGIS_T_SUOLO_RILEVATO.FOGLIO%TYPE) RETURN ORA_MINING_VARCHAR2_NT IS

  nExtIdAzienda             QGIS_T_EVENTO_LAVORAZIONE.EXT_ID_AZIENDA%TYPE;
  nCampagna                 QGIS_T_LISTA_LAVORAZIONE.CAMPAGNA%TYPE;
  outVal                    ORA_MINING_VARCHAR2_NT := ORA_MINING_VARCHAR2_NT();
  vTipoSuolo                VARCHAR2(20);
  nIdParticella             QGIS_T_VERSIONE_PARTICELLA.EXT_ID_PARTICELLA%TYPE;
  vPartCond                 VARCHAR2(20);
  nIdSuoloLavorazione       QGIS_T_SUOLO_LAVORAZIONE.ID_SUOLO_LAVORAZIONE%TYPE;
  nIdTipoSorgenteSuolo      QGIS_T_LISTA_LAVORAZIONE.ID_TIPO_SORGENTE_SUOLO%TYPE;
BEGIN
  SELECT EL.EXT_ID_AZIENDA,LL.CAMPAGNA,NVL(LL.ID_TIPO_SORGENTE_SUOLO,0)
  INTO   nExtIdAzienda,nCampagna,nIdTipoSorgenteSuolo
  FROM   QGIS_T_EVENTO_LAVORAZIONE EL,QGIS_T_LISTA_LAVORAZIONE LL
  WHERE  EL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione
  AND    EL.ID_LISTA_LAVORAZIONE  = LL.ID_LISTA_LAVORAZIONE;
  
  FOR rec IN (SELECT SR.ID_SUOLO_RILEVATO,FLAG_GEOM_CORROTTA
              FROM   QGIS_T_SUOLO_RILEVATO SR,SMRGAA.DB_TIPO_ELEGGIBILITA_RILEVATA TER
              WHERE  SR.EXT_ID_ELEGGIBILITA_RILEVATA = TER.ID_ELEGGIBILITA_RILEVATA
              AND    SR.EXT_COD_NAZIONALE            = pCodNazionale
              AND    SR.FOGLIO                       = pFoglio
              -- rc 27/05/2022 jira-74
              AND    ((nIdTipoSorgenteSuolo IN (4,5) AND SR.ID_SUOLO_RILEVATO IN (SELECT RC.ID_SUOLO_RILEVATO
                                                                                  FROM   QGIS_T_REGISTRO_CO RC
                                                                                  WHERE  RC.CAMPAGNA           = nCampagna
                                                                                  AND    RC.DATA_FINE_VALIDITA IS NULL)) OR
                      (nIdTipoSorgenteSuolo NOT IN (4,5) AND SR.ID_SUOLO_RILEVATO IN (SELECT RS.ID_SUOLO_RILEVATO
                                                                                      FROM   QGIS_T_REGISTRO_SUOLI RS
                                                                                      WHERE  RS.CAMPAGNA           = nCampagna
                                                                                      AND    RS.DATA_FINE_VALIDITA IS NULL)))) LOOP
  
    BEGIN
      SELECT ID_SUOLO_LAVORAZIONE,TIPO_SUOLO_ORIGINE
      INTO   nIdSuoloLavorazione,vTipoSuolo
      FROM   QGIS_T_SUOLO_LAVORAZIONE
      WHERE  ID_SUOLO_LAVORAZIONE = (SELECT MAX(SL.ID_SUOLO_LAVORAZIONE)
                                     FROM   QGIS_T_SUOLO_LAVORAZIONE SL
                                     WHERE  SL.ID_SUOLO_RILEVATO     = rec.ID_SUOLO_RILEVATO
                                     AND    SL.ID_EVENTO_LAVORAZIONE = pIdEventoLavorazione);
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        nIdSuoloLavorazione := NULL;
        vTipoSuolo          := NULL;
    END;
    
    IF vTipoSuolo IS NULL THEN    
      SELECT MAX(VP.EXT_ID_PARTICELLA)
      INTO   nIdParticella
      FROM   QGIS_T_VERSIONE_PARTICELLA VP,QGIS_T_SUOLO_PARTICELLA SP
      WHERE  VP.ID_VERSIONE_PARTICELLA = SP.ID_VERSIONE_PARTICELLA
      AND    SP.ID_SUOLO_RILEVATO      = rec.ID_SUOLO_RILEVATO;

      IF nIdParticella IS NULL THEN
        vPartCond := 'N';
      ELSE
        IF nIdSuoloLavorazione IS NULL THEN
          vPartCond := SMRGAA.PCK_SMRGAA_UTILITY_QGIS.IsParticellaCondotta(nIdParticella,nExtIdAzienda,nCampagna);
        END IF;
      END IF;
      
      IF nIdSuoloLavorazione IS NOT NULL AND rec.FLAG_GEOM_CORROTTA = 'N' THEN
        vTipoSuolo := 'LAV';
      END IF;
    
      IF nIdSuoloLavorazione IS NULL AND rec.FLAG_GEOM_CORROTTA = 'N' AND vPartCond = 'S' THEN
        vTipoSuolo := 'COND';
      END IF;
    
      IF nIdSuoloLavorazione IS NULL AND rec.FLAG_GEOM_CORROTTA = 'S' AND vPartCond = 'N' THEN
        vTipoSuolo := 'KO';
      END IF;
    
      IF nIdSuoloLavorazione IS NOT NULL AND rec.FLAG_GEOM_CORROTTA = 'S' THEN
        vTipoSuolo := 'LAV_KO';
      END IF;
    
      IF nIdSuoloLavorazione IS NULL AND rec.FLAG_GEOM_CORROTTA = 'S' AND vPartCond = 'S' THEN
        vTipoSuolo := 'COND_KO';
      END IF;
    
      IF nIdSuoloLavorazione IS NULL AND rec.FLAG_GEOM_CORROTTA = 'N' AND vPartCond = 'N' THEN
        vTipoSuolo := 'NO_COND';
      END IF;
    END IF;
    
    outVal.EXTEND;
    outVal(outVal.COUNT) := vTipoSuolo;
  END LOOP;
  
  RETURN outVal;
END getNumSuoliLavoraz;

END PCK_QGIS_UTILITY_API;

/