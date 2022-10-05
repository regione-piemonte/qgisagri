CREATE OR REPLACE PACKAGE PCK_QGIS_AGGIORNAMENTO_TABELLE AS

  FUNCTION Main RETURN NUMBER;
  
  FUNCTION getDataGisCampagna(pCodNazionale     VARCHAR2,
                              pFoglio           NUMBER,
                              pParticella       VARCHAR2,
                              pSub              VARCHAR2,
                              pAnnoRiferimento  NUMBER,
                              pDataInizio       DATE) RETURN DATE;
  
END PCK_QGIS_AGGIORNAMENTO_TABELLE;

/