package it.csi.qgisagri.agriapi.dto.anagrafe;

import java.io.Serializable;

public class AziendaDTO implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = 7793821407511129401L;
  private long              idAzienda;
  private String            cuaa;
  private String            partitaIva;
  private String            denominazione;

  public long getIdAzienda()
  {
    return idAzienda;
  }

  public void setIdAzienda(long idAzienda)
  {
    this.idAzienda = idAzienda;
  }

  public String getCuaa()
  {
    return cuaa;
  }

  public void setCuaa(String cuaa)
  {
    this.cuaa = cuaa;
  }

  public String getPartitaIva()
  {
    return partitaIva;
  }

  public void setPartitaIva(String partitaIva)
  {
    this.partitaIva = partitaIva;
  }

  public String getDenominazione()
  {
    return denominazione;
  }

  public void setDenominazione(String denominazione)
  {
    this.denominazione = denominazione;
  }
  
}
