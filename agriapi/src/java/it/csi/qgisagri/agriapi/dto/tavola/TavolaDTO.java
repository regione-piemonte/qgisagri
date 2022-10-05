package it.csi.qgisagri.agriapi.dto.tavola;

import java.io.Serializable;

public class TavolaDTO implements Serializable
{
    /** serialVersionUID */
  private static final long serialVersionUID = 2661251200990488400L;
    private String codiRegi;
    private String siglaProv;
    private String descProv;
    private String codiBelf;
    private String descComu;
    private String codiNazi;
    private String seziCens;
    private String descSezi;
    private String numeFogl;
  private String codiEpsg;

  public String getCodiRegi()
  {
    return codiRegi;
  }

  public void setCodiRegi(String codiRegi)
  {
    this.codiRegi = codiRegi;
  }

  public String getSiglaProv()
  {
    return siglaProv;
  }

  public void setSiglaProv(String siglaProv)
  {
    this.siglaProv = siglaProv;
  }

  public String getDescProv()
  {
    return descProv;
  }

  public void setDescProv(String descProv)
  {
    this.descProv = descProv;
  }

  public String getCodiBelf()
  {
    return codiBelf;
  }

  public void setCodiBelf(String codiBelf)
  {
    this.codiBelf = codiBelf;
  }

  public String getDescComu()
  {
    return descComu;
  }

  public void setDescComu(String descComu)
  {
    this.descComu = descComu;
  }

  public String getCodiNazi()
  {
    return codiNazi;
  }

  public void setCodiNazi(String codiNazi)
  {
    this.codiNazi = codiNazi;
  }

  public String getSeziCens()
  {
    return seziCens;
  }

  public void setSeziCens(String seziCens)
  {
    this.seziCens = seziCens;
  }

  public String getDescSezi()
  {
    return descSezi;
  }

  public void setDescSezi(String descSezi)
  {
    this.descSezi = descSezi;
  }

  public String getNumeFogl()
  {
    return numeFogl;
  }

  public void setNumeFogl(String numeFogl)
  {
    this.numeFogl = numeFogl;
  }

  public String getCodiEpsg()
  {
    return codiEpsg;
  }

  public void setCodiEpsg(String codiEpsg)
  {
    this.codiEpsg = codiEpsg;
  }
}
