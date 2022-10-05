package it.csi.qgisagri.agriapi.dto;

import java.util.List;

import it.csi.qgisagri.agriapi.dto.listeLavorazione.ListaLavorazioneDTO;

public class ListaDTO
{
  private EsitoDTO esitoDTO;
  private List<ListaLavorazioneDTO> elencoListe;
  
  public EsitoDTO getEsitoDTO()
  {
    return esitoDTO;
  }
  public void setEsitoDTO(EsitoDTO esitoDTO)
  {
    this.esitoDTO = esitoDTO;
  }
  public List<ListaLavorazioneDTO> getElencoListe()
  {
    return elencoListe;
  }
  public void setElencoListe(List<ListaLavorazioneDTO> elencoListe)
  {
    this.elencoListe = elencoListe;
  }
 
}
