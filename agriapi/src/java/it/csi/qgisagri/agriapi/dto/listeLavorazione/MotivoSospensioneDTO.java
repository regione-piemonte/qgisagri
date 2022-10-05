package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

public class MotivoSospensioneDTO implements Serializable
{

  
  /**
   * 
   */
  private static final long serialVersionUID = -3112695155636816831L;
  private long idTipoMotivoSospensione;
  private String descrizione;
  

  public String getDescrizione()
  {
    return descrizione;
  }
  public void setDescrizione(String descrizione)
  {
    this.descrizione = descrizione;
  }
  public long getIdTipoMotivoSospensione()
  {
    return idTipoMotivoSospensione;
  }
  public void setIdTipoMotivoSospensione(long idTipoMotivoSospensione)
  {
    this.idTipoMotivoSospensione = idTipoMotivoSospensione;
  }
  
  
}
