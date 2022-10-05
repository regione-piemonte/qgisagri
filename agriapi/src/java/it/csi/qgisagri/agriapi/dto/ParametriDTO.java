package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;
import java.util.Date;

import it.csi.qgisagri.agriapi.util.GraficoUtils;

public class ParametriDTO implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = 6807059520017592165L;
  private long              idAzienda;
  private long              idUtente;
  private String            dataRiferimento;

  public long getIdAzienda()
  {
    return idAzienda;
  }

  public void setIdAzienda(long idAzienda)
  {
    this.idAzienda = idAzienda;
  }

  public long getIdUtente()
  {
    return idUtente;
  }

  public void setIdUtente(long idUtente)
  {
    this.idUtente = idUtente;
  }

  public String getDataRiferimento()
  {
    return dataRiferimento;
  }

  public void setDataRiferimento(String dataRiferimento)
  {
    this.dataRiferimento = dataRiferimento;
  }

  public Date getDataRiferimentoDate()
  {
    return GraficoUtils.DATE.parseDate(dataRiferimento);
  }
  
}
