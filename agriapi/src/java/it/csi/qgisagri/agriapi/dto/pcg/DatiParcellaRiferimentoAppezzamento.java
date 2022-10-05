package it.csi.qgisagri.agriapi.dto.pcg;

import java.io.Serializable;

public class DatiParcellaRiferimentoAppezzamento implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = -5265519724930975894L;

  private String codiceParcella;
  private String codiceMacroUsoParcella;
  private String descMacroUsoParcella;
  
  public DatiParcellaRiferimentoAppezzamento()
  {
  }
  
  public DatiParcellaRiferimentoAppezzamento(String codiceParcella, String codiceMacroUsoParcella, String descMacroUsoParcella)
  {
    super();
    this.codiceParcella = codiceParcella;
    this.codiceMacroUsoParcella = codiceMacroUsoParcella;
    this.descMacroUsoParcella = descMacroUsoParcella;
  }

  public String getCodiceParcella()
  {
    return codiceParcella;
  }

  public void setCodiceParcella(String codiceParcella)
  {
    this.codiceParcella = codiceParcella;
  }

  public String getCodiceMacroUsoParcella()
  {
    return codiceMacroUsoParcella;
  }

  public void setCodiceMacroUsoParcella(String codiceMacroUsoParcella)
  {
    this.codiceMacroUsoParcella = codiceMacroUsoParcella;
  }

  public String getDescMacroUsoParcella()
  {
    return descMacroUsoParcella;
  }

  public void setDescMacroUsoParcella(String descMacroUsoParcella)
  {
    this.descMacroUsoParcella = descMacroUsoParcella;
  }
}
