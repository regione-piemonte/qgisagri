package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

public class ListaLavorazioneDTO implements Serializable
{
  /**
   * 
   */
  private static final long serialVersionUID = 2480241401004093626L;
  private int     idListaLavorazione;
  private int     idTipoLista;
  private int     campagna;
  private String  codiceLista;
  private String  descrizioneLista;
  private String  descrizioneTipoLista;
  
  public int getIdListaLavorazione()
  {
    return idListaLavorazione;
  }
  public void setIdListaLavorazione(int idListaLavorazione)
  {
    this.idListaLavorazione = idListaLavorazione;
  }
  public int getCampagna()
  {
    return campagna;
  }
  public void setCampagna(int campagna)
  {
    this.campagna = campagna;
  }
  
  public String getCodiceLista()
  {
    return codiceLista;
  }
  public void setCodiceLista(String codiceLista)
  {
    this.codiceLista = codiceLista;
  }
  public String getDescrizioneLista()
  {
    return descrizioneLista;
  }
  public void setDescrizioneLista(String descrizioneLista)
  {
    this.descrizioneLista = descrizioneLista;
  }
  public int getIdTipoLista()
  {
    return idTipoLista;
  }
  public void setIdTipoLista(int idTipoLista)
  {
    this.idTipoLista = idTipoLista;
  }
  public String getDescrizioneTipoLista()
  {
    return descrizioneTipoLista;
  }
  public void setDescrizioneTipoLista(String descrizioneTipoLista)
  {
    this.descrizioneTipoLista = descrizioneTipoLista;
  }

  
  

}
