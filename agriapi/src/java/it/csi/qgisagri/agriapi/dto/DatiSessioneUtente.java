package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;
import java.util.List;

import it.csi.qgisagri.agriapi.dto.anagrafe.AziendaDTO;
import it.csi.qgisagri.agriapi.dto.tavola.TavolaDTO;

public class DatiSessioneUtente implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = 5906035413230009514L;
  private AziendaDTO        azienda;
  private List<TavolaDTO>   tavole;
  private ParametriDTO      parametri;

  public AziendaDTO getAzienda()
  {
    return azienda;
  }

  public void setAzienda(AziendaDTO azienda)
  {
    this.azienda = azienda;
  }

  public List<TavolaDTO> getTavole()
  {
    return tavole;
  }

  public void setTavole(List<TavolaDTO> tavole)
  {
    this.tavole = tavole;
  }

  public ParametriDTO getParametri()
  {
    return parametri;
  }

  public void setParametri(ParametriDTO parametri)
  {
    this.parametri = parametri;
  }

}
