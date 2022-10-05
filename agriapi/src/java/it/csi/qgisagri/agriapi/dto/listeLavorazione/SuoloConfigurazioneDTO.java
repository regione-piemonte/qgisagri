package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

public class SuoloConfigurazioneDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -133917744481678108L;

  private Long              idEventoLavorazione;
  private Long              flagDiffAreaSuoli;
  private Long              flagCessatiSuoli;
  private Long              flagAreaMinSuoli;
  private Long              flagDiffPartSuoli;
  
  private String            anomalia;
  private String            layer;
  
  
  public Long getIdEventoLavorazione()
  {
    return idEventoLavorazione;
  }
  public void setIdEventoLavorazione(Long idEventoLavorazione)
  {
    this.idEventoLavorazione = idEventoLavorazione;
  }
  
  
  
  
  public Long getFlagDiffPartSuoli()
  {
    return flagDiffPartSuoli;
  }
  public void setFlagDiffPartSuoli(Long flagDiffPartSuoli)
  {
    this.flagDiffPartSuoli = flagDiffPartSuoli;
  }
  public Long getFlagAreaMinSuoli()
  {
    return flagAreaMinSuoli;
  }
  public void setFlagAreaMinSuoli(Long flagAreaMinSuoli)
  {
    this.flagAreaMinSuoli = flagAreaMinSuoli;
  }
  public Long getFlagDiffAreaSuoli()
  {
    return flagDiffAreaSuoli;
  }
  public void setFlagDiffAreaSuoli(Long flagDiffAreaSuoli)
  {
    this.flagDiffAreaSuoli = flagDiffAreaSuoli;
  }
  public Long getFlagCessatiSuoli()
  {
    return flagCessatiSuoli;
  }
  public void setFlagCessatiSuoli(Long flagCessatiSuoli)
  {
    this.flagCessatiSuoli = flagCessatiSuoli;
  }
  public String getAnomalia()
  {
    return anomalia;
  }
  public void setAnomalia(String anomalia)
  {
    this.anomalia = anomalia;
  }
  public String getLayer()
  {
    return layer;
  }
  public void setLayer(String layer)
  {
    this.layer = layer;
  }
  
  

}
