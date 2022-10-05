package it.csi.qgisagri.agriapi.dto;

public class AgriAPIResult<T>
{
  private EsitoDTO esitoDTO;
  private T dati;
 
  public EsitoDTO getEsitoDTO()
  {
    return esitoDTO;
  }
  public void setEsitoDTO(EsitoDTO esitoDTO)
  {
    this.esitoDTO = esitoDTO;
  }
  public T getDati()
  {
    return dati;
  }
  public void setDati(T dati)
  {
    this.dati = dati;
  }
  
}
