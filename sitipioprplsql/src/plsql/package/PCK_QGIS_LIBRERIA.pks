CREATE OR REPLACE PACKAGE PCK_QGIS_LIBRERIA AS
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
                                      pIdEventoLavorazione       OUT QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE);
                                      
  -- rc 14/12/2020 jira-31
  PROCEDURE InserisciSuoloNuovo(pExtCodNazionale         VARCHAR2,
                                pFoglio                  NUMBER,
                                pParticella              VARCHAR2,
                                pSubalterno              VARCHAR2,
                                pDataInizioValidita      DATE,
                                pArraySuoli              LIST_SUOLI,
                                pCampagna                NUMBER,  -- RC 21/04/2022 JIRA-72
                                pCodErrore           OUT VARCHAR2,
                                pDescErrore          OUT VARCHAR2);
                                
  -- rc 25/03/2021 jira-4744
  PROCEDURE SalvaIstanza(pIdEventoLavorazione      QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE,
                         pCodErrore            OUT VARCHAR2,
                         pDescErrore           OUT VARCHAR2);
                         
  -- RC 15/04/2021 JIRA-36
  PROCEDURE RinunciaIstanzaRiesame(pIdAzienda                     NUMBER,
                                   pIdIstanzaAppezzamento         NUMBER,
                                   pExtIdentificativoPratica      VARCHAR2,
                                   pCodErrore                 OUT VARCHAR2,
                                   pDescErrore                OUT VARCHAR2);
                                   
  -- rc 05/10/2021 jira-52
  PROCEDURE InserisciSopralluogo(pIdEventoLavorazione           QGIS_T_EVENTO_LAVORAZIONE.ID_EVENTO_LAVORAZIONE%TYPE,
                                 pExtCodNazionale               VARCHAR2,
                                 pFoglio                        NUMBER,
                                 pIdAzienda                     NUMBER,
                                 pExtIdUtenteAggiornamento      NUMBER,
                                 pCodErrore                 OUT VARCHAR2,
                                 pDescErrore                OUT VARCHAR2);

  -- rc 03/12/2021 jira-63
  PROCEDURE InserisciListaDaGeometria(pIdLista                       NUMBER, 
                                      pIdParticella                  NUMBER,
                                      pIdAppe                        NUMBER,
                                      pIdAppeLav                     NUMBER,
                                      pIdAzienda                     NUMBER,
                                      pDataParticella                DATE,        
                                      pExtIdUtenteAggiornamento      NUMBER,
                                      pCodErrore                 OUT VARCHAR2,
                                      pDescErrore                OUT VARCHAR2);

  -- rc 14/02/2022 jira-67
  PROCEDURE ValorizzaIdParticella(pIdParticella      NUMBER,
                                  pCodErrore     OUT VARCHAR2,
                                  pDescErrore    OUT VARCHAR2);
                                  
  -- rc 21/04/2022 jira-72
  PROCEDURE AggiornaRegistroSuoli(pCampagna             NUMBER,
                                  pExtCodNazionale      VARCHAR2,
                                  pFoglio               NUMBER,
                                  pArrayCessato         ORA_MINING_NUMBER_NT,
                                  pArrayInserito        ORA_MINING_NUMBER_NT,
                                  pCodErrore        OUT VARCHAR2,
                                  pDescErrore       OUT VARCHAR2);
                                  
  -- rc 21/04/2022 jira-72
  PROCEDURE AggiornaRegistroParticelle(pCampagna             NUMBER,
                                       pExtCodNazionale      VARCHAR2,
                                       pFoglio               NUMBER,
                                       pArrayCessato         ORA_MINING_NUMBER_NT,
                                       pArrayInserito        ORA_MINING_NUMBER_NT,
                                       pCodErrore        OUT VARCHAR2,
                                       pDescErrore       OUT VARCHAR2);
                                       
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
                                        pDescErrore                OUT VARCHAR2);
                                        
  -- rc 28/04/2022 jira-73
  PROCEDURE EsitoLavorazioneCo(pIdAzienda       NUMBER,
                               pCampagna        NUMBER,
                               pEsito       OUT NUMBER,
                               pDescEsito   OUT VARCHAR2,
                               pCodErrore   OUT VARCHAR2,
                               pDescErrore  OUT VARCHAR2);
                               
  -- rc 25/05/2022 jira-74
  PROCEDURE AggiornaRegistroCo(pCampagna             NUMBER,
                               pExtCodNazionale      VARCHAR2,
                               pFoglio               NUMBER,
                               pArrayCessato         ORA_MINING_NUMBER_NT,
                               pArrayInserito        ORA_MINING_NUMBER_NT,
                               pCodErrore        OUT VARCHAR2,
                               pDescErrore       OUT VARCHAR2);
                                        
END PCK_QGIS_LIBRERIA;

/