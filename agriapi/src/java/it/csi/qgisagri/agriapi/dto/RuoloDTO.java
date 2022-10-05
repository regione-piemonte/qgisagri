package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;

public class RuoloDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -2260151515102725970L;
  
  private Long idRuolo;
  private String codice;
  private String descrizione;
  private String codiceFiscale;
  
  public RuoloDTO(Long idRuolo, String codice, String descrizione, String codiceFiscale)
  {
    this.idRuolo=idRuolo;
    this.codice=codice;
    this.descrizione=descrizione;
    this.codiceFiscale=codiceFiscale;
  }
  
  public String getCodiceFiscale()
  {
    return codiceFiscale;
  }

  public void setCodiceFiscale(String codiceFiscale)
  {
    this.codiceFiscale = codiceFiscale;
  }

  public String getCodice()
  {
    return codice;
  }
  public void setCodice(String codice)
  {
    this.codice = codice;
  }
  public String getDescrizione()
  {
    return descrizione;
  }
  public void setDescrizione(String descrizione)
  {
    this.descrizione = descrizione;
  }
  public Long getIdRuolo()
  {
    return idRuolo;
  }
  public void setIdRuolo(Long idRuolo)
  {
    this.idRuolo = idRuolo;
  }
   
}
