package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

public class ClasseEleggibilitaDTO implements Serializable
{

  private static final long serialVersionUID = 2813352067313547822L;
  private String codiceEleggibilitaRilevata;
  private String descEleggibilitaRilevata;
  private String flagAssegnabileQgis;

  
  
  
  public String getFlagAssegnabileQgis()
  {
    return flagAssegnabileQgis;
  }
  public void setFlagAssegnabileQgis(String flagAssegnabileQgis)
  {
    this.flagAssegnabileQgis = flagAssegnabileQgis;
  }
  public String getCodiceEleggibilitaRilevata()
  {
    return codiceEleggibilitaRilevata;
  }
  public void setCodiceEleggibilitaRilevata(String codiceEleggibilitaRilevata)
  {
    this.codiceEleggibilitaRilevata = codiceEleggibilitaRilevata;
  }
  public String getDescEleggibilitaRilevata()
  {
    return descEleggibilitaRilevata;
  }
  public void setDescEleggibilitaRilevata(String descEleggibilitaRilevata)
  {
    this.descEleggibilitaRilevata = descEleggibilitaRilevata;
  }
  
  
  
}
