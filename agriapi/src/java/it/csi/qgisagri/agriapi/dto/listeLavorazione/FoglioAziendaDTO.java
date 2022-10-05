package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

public class FoglioAziendaDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -4974308162990523444L;
  
  private int foglio;
  private String codiceNazionale;
  private String descrizioneComune;
  private String isDocumentoPresente;
  private int sezione;
  private int numeroParticelle;
  private int numeroSuoliLavorazione;
  private int numeroSuoliProposti;
  private int numeroSuoliSospesi;
  private String utenteBlocco;
  private String statoLavorazioneOrig; // 'L' lavorato , 'N' non lavorato, 'S' sospeso
  private Long idUtenteBlocco;
  
  
  
  public String getStatoLavorazioneOrig()
  {
    return statoLavorazioneOrig;
  }
  public void setStatoLavorazioneOrig(String statoLavorazioneOrig)
  {
    this.statoLavorazioneOrig = statoLavorazioneOrig;
  }
  public String getIsDocumentoPresente()
  {
    return isDocumentoPresente;
  }
  public void setIsDocumentoPresente(String isDocumentoPresente)
  {
    this.isDocumentoPresente = isDocumentoPresente;
  }
  public String getCodiceNazionale()
  {
    return codiceNazionale;
  }
  public void setCodiceNazionale(String codiceNazionale)
  {
    this.codiceNazionale = codiceNazionale;
  }
  public String getDescrizioneComune()
  {
    return descrizioneComune;
  }
  public void setDescrizioneComune(String descrizioneComune)
  {
    this.descrizioneComune = descrizioneComune;
  }
  public int getSezione()
  {
    return sezione;
  }
  public void setSezione(int sezione)
  {
    this.sezione = sezione;
  }
  public int getFoglio()
  {
    return foglio;
  }
  public void setFoglio(int foglio)
  {
    this.foglio = foglio;
  }
  public int getNumeroParticelle()
  {
    return numeroParticelle;
  }
  public void setNumeroParticelle(int numeroParticelle)
  {
    this.numeroParticelle = numeroParticelle;
  }
  public int getNumeroSuoliLavorazione()
  {
    return numeroSuoliLavorazione;
  }
  public void setNumeroSuoliLavorazione(int numeroSuoliLavorazione)
  {
    this.numeroSuoliLavorazione = numeroSuoliLavorazione;
  }
  public int getNumeroSuoliProposti()
  {
    return numeroSuoliProposti;
  }
  public void setNumeroSuoliProposti(int numeroSuoliProposti)
  {
    this.numeroSuoliProposti = numeroSuoliProposti;
  }
  public int getNumeroSuoliSospesi()
  {
    return numeroSuoliSospesi;
  }
  public void setNumeroSuoliSospesi(int numeroSuoliSospesi)
  {
    this.numeroSuoliSospesi = numeroSuoliSospesi;
  }
  public String getUtenteBlocco()
  {
    return utenteBlocco;
  }
  public void setUtenteBlocco(String utenteBlocco)
  {
    this.utenteBlocco = utenteBlocco;
  }
  public boolean isIsFoglioBloccato()
  {
    return utenteBlocco!=null ? true : false;
  }
  public Long getIdUtenteBlocco()
  {
    return idUtenteBlocco;
  }
  public void setIdUtenteBlocco(Long idUtenteBlocco)
  {
    this.idUtenteBlocco = idUtenteBlocco;
  }
  
}
