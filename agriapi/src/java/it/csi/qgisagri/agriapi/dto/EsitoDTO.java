package it.csi.qgisagri.agriapi.dto;

import it.csi.qgisagri.agriapi.util.AgriApiConstants;

public class EsitoDTO
{
  private String messaggio;
  private int esito;
  
  public EsitoDTO() {
    this.setEsito(AgriApiConstants.ESITO.POSITIVO);
    this.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.MESSAGGIO_POSITIVO);
  }
  public String getMessaggio()
  {
    return messaggio;
  }
  public void setMessaggio(String messaggio)
  {
    this.messaggio = messaggio;
  }
  public int getEsito()
  {
    return esito;
  }
  public void setEsito(int esito)
  {
    this.esito = esito;
  }
  public void setError()
  {
    this.setEsito(AgriApiConstants.ESITO.ERRORE);
    this.setMessaggio(AgriApiConstants.ESITO.MESSAGGIO.MESSAGGIO_ERRORE);
  }
  public void setEmptyMessage(String messaggio)
  {
    this.setEsito(AgriApiConstants.ESITO.ERRORE);
    this.setMessaggio(messaggio);
  }
   
}
