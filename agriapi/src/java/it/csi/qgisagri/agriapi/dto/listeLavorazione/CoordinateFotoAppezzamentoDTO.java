package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

public class CoordinateFotoAppezzamentoDTO implements Serializable
{
  /**
   * 
   */
  private static final long serialVersionUID = 1L;
  private String idFotoAppezzamento;
  private String latitudine;
  private String longitudine;
  private String direzione;
  
  
  public String getIdFotoAppezzamento()
  {
    return idFotoAppezzamento;
  }
  public void setIdFotoAppezzamento(String idFotoAppezzamento)
  {
    this.idFotoAppezzamento = idFotoAppezzamento;
  }
  public String getLatitudine()
  {
    return latitudine;
  }
  public void setLatitudine(String latitudine)
  {
    this.latitudine = latitudine;
  }
  public String getLongitudine()
  {
    return longitudine;
  }
  public void setLongitudine(String longitudine)
  {
    this.longitudine = longitudine;
  }
  public String getDirezione()
  {
    return direzione;
  }
  public void setDirezione(String direzione)
  {
    this.direzione = direzione;
  }
  
}
