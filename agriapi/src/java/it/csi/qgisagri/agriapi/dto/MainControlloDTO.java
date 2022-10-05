package it.csi.qgisagri.agriapi.dto;

import java.math.BigDecimal;

public class MainControlloDTO 
{

  private String               risultato;
  private String            messaggio;
  private BigDecimal        idProcedimento;
  private ControlloDTO      controlli[];

  

  public String getRisultato()
  {
    return risultato;
  }

  public void setRisultato(String risultato)
  {
    this.risultato = risultato;
  }

  public String getMessaggio()
  {
    return messaggio;
  }

  public void setMessaggio(String messaggio)
  {
    this.messaggio = messaggio;
  }

  public ControlloDTO[] getControlli()
  {
    return controlli;
  }

  public void setControlli(ControlloDTO[] controlli)
  {
    this.controlli = controlli;
  }

  public BigDecimal getIdProcedimento()
  {
    return idProcedimento;
  }

  public void setIdProcedimento(BigDecimal idProcedimento)
  {
    this.idProcedimento = idProcedimento;
  }
}
