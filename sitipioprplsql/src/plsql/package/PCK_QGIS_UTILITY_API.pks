CREATE OR REPLACE PACKAGE PCK_QGIS_UTILITY_API AS

  -- RC 09/01/2020 JIRA-4251
  FUNCTION getSuoliInLavorazione(pIdEventoLavorazione  QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE,
                                 pCodNazionale         QGIS_T_SUOLO_RILEVATO.EXT_COD_NAZIONALE%TYPE,
                                 pFoglio               QGIS_T_SUOLO_RILEVATO.FOGLIO%TYPE) RETURN LIST_SUOLI_IN_LAVORAZIONE;
                                 
  -- rc 05/10/2021
  FUNCTION getNumSuoliLavoraz(pIdEventoLavorazione  QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE,
                              pCodNazionale         QGIS_T_SUOLO_RILEVATO.EXT_COD_NAZIONALE%TYPE,
                              pFoglio               QGIS_T_SUOLO_RILEVATO.FOGLIO%TYPE) RETURN ORA_MINING_VARCHAR2_NT;
END PCK_QGIS_UTILITY_API;

/