package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;
import java.util.Date;

import it.csi.qgisagri.agriapi.util.GraficoUtils;

public class DichiarazioneConsistenzaDTO implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = 5054598634293277710L;
  private long   idDichiarazioneConsistenza;
  private Date   data;
  private int    annoCampagna;
  private String motivo;
  private String pratiche;

  public long getIdDichiarazioneConsistenza()
  {
    return idDichiarazioneConsistenza;
  }

  public void setIdDichiarazioneConsistenza(long idDichiarazioneConsistenza)
  {
    this.idDichiarazioneConsistenza = idDichiarazioneConsistenza;
  }

  public String getData()
  {
    return GraficoUtils.DATE.formatDateTime(data);
  }

  public void setData(Date data)
  {
    this.data = data;
  }

  public int getAnnoCampagna()
  {
    return annoCampagna;
  }

  public void setAnnoCampagna(int annoCampagna)
  {
    this.annoCampagna = annoCampagna;
  }

  public String getMotivo()
  {
    return motivo;
  }

  public void setMotivo(String motivo)
  {
    this.motivo = motivo;
  }

  public String getPratiche()
  {
    return pratiche;
  }

  public void setPratiche(String pratiche)
  {
    this.pratiche = pratiche;
  }
}
