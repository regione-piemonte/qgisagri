CREATE OR REPLACE PACKAGE PCK_SITI_SVECCHIA AS

  PROCEDURE CreateIndex;
  
  PROCEDURE TabSitiSuolo(pSiglaProv  SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE,
                         pNoPiemonte  VARCHAR2);
                         
  PROCEDURE IndSitisuolo;
  
  PROCEDURE TabSitiPartFuture(pSiglaProv  SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE,
                              pNoPiemonte  VARCHAR2);
  
  PROCEDURE TabSitiPart(pSiglaProv  SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE,
                        pNoPiemonte  VARCHAR2);
  
  PROCEDURE IndSitiPart;
  
  PROCEDURE Rf;
  
  PROCEDURE PopolamentoQgis(pSiglaProv  SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE,
                            pNoPiemonte  VARCHAR2);
                            
  PROCEDURE ListeLav(pAnnoCampagna  NUMBER,
                     pSiglaProv     SMRGAA.DB_SITICOMU.SIGLA_PROV%TYPE);
                     
  PROCEDURE StatListeLav;
  
  PROCEDURE SuoloProposto;
  
  FUNCTION is_numeric(str IN VARCHAR2) RETURN CHAR;
  
  FUNCTION Cdt(pStr  VARCHAR2) RETURN INTEGER;
  
  FUNCTION ReturnAzienda(pAnnoCampagna          NUMBER,
                         pIdVersioneParticella  QGIS_T_VERSIONE_PARTICELLA.ID_VERSIONE_PARTICELLA%TYPE,
                         pProvRif               SITILISTALAV.PROV_RIF%TYPE,
                         pDatains               SITIPLAV.DATAINS%TYPE) RETURN QGIS_T_EVENTO_LAVORAZIONE.EXT_ID_AZIENDA%TYPE;
  
END PCK_SITI_SVECCHIA;

/