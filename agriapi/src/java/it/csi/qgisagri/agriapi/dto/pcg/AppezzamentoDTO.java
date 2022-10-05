package it.csi.qgisagri.agriapi.dto.pcg;

import java.io.Serializable;
import java.sql.Timestamp;
import java.util.List;

import org.codehaus.jackson.annotate.JsonIgnore;
import org.codehaus.jackson.annotate.JsonIgnoreProperties;

import it.csi.qgisagri.agriapi.util.GraficoUtils;

@JsonIgnoreProperties(ignoreUnknown = true)
public class AppezzamentoDTO implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = 2458506313442919005L;
  private long                idFasc;
  private String              cuaa;
  private String              codiRegi;
  private String              siglaProv;
  private String              descProv;
  private String              codiBelf;
  private String              descComu;
  private String              codinazi;
  private String              seziCens;
  private String              descSezi;
  private long                numeFogl;
  private long                idIsol;
  private String              codiIsol;
  private long                idAppe;
  private Timestamp           dataInizAppe;
  private Timestamp           dataFineAppe;
  private String              codiRile;
  private String              codiProdRile;
  private long                supeAppe;
  private String              codiEpsg;
  private List<ColturaDTO>    colture;
  private List<SchedaUnarDTO> schedeUnar;
  private String              flagIstanzaRiesame;
  private String              descCodiProdRile;
  private int                 tipoIsol;
  private String              flagModificato;  
  private String              codiceStileGrafico;
  private List<DatiParcellaRiferimentoAppezzamento> parcelle;
  private String              codiRileIstanzaRiesame;
  private String              codiProdRileIstanzaRiesame;
  private String              bloccoFusione;
  @JsonIgnore
  private String              geometry;
  private String              srid;

  public String getSrid()
  {
    return srid;
  }

  public void setSrid(String srid)
  {
    this.srid = srid;
  }

  public String getGeometry()
  {
    return geometry;
  }

  public void setGeometry(String geometry)
  {
    this.geometry = geometry;
  }

  public long getIdFasc()
  {
    return idFasc;
  }

  public void setIdFasc(long idFasc)
  {
    this.idFasc = idFasc;
  }

  public String getCuaa()
  {
    return cuaa;
  }

  public void setCuaa(String cuaa)
  {
    this.cuaa = cuaa;
  }

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

  public String getCodinazi()
  {
    return codinazi;
  }

  public void setCodinazi(String codinazi)
  {
    this.codinazi = codinazi;
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

  public long getNumeFogl()
  {
    return numeFogl;
  }

  public void setNumeFogl(long numeFogl)
  {
    this.numeFogl = numeFogl;
  }

  public long getIdIsol()
  {
    return idIsol;
  }

  public void setIdIsol(long idIsol)
  {
    this.idIsol = idIsol;
  }

  public String getCodiIsol()
  {
    return codiIsol;
  }

  public void setCodiIsol(String codiIsol)
  {
    this.codiIsol = codiIsol;
  }

  public long getIdAppe()
  {
    return idAppe;
  }

  public void setIdAppe(long idAppe)
  {
    this.idAppe = idAppe;
  }

  public String getDataInizAppe()
  {
    return GraficoUtils.DATE.formatDate(dataInizAppe);
  }

  public void setDataInizAppe(Timestamp dataInizAppe)
  {
    this.dataInizAppe = dataInizAppe;
  }

  public String getDataFineAppe()
  {
    return GraficoUtils.DATE.formatDate(dataFineAppe);
  }

  public void setDataFineAppe(Timestamp dataFineAppe)
  {
    this.dataFineAppe = dataFineAppe;
  }

  public String getCodiRile()
  {
    return codiRile;
  }

  public void setCodiRile(String codiRile)
  {
    this.codiRile = codiRile;
  }

  public String getCodiProdRile()
  {
    return codiProdRile;
  }

  public void setCodiProdRile(String codiProdRile)
  {
    this.codiProdRile = codiProdRile;
  }

  public long getSupeAppe()
  {
    return supeAppe;
  }

  public void setSupeAppe(long supeAppe)
  {
    this.supeAppe = supeAppe;
  }

  public String getCodiEpsg()
  {
    return codiEpsg;
  }

  public void setCodiEpsg(String codiEpsg)
  {
    this.codiEpsg = codiEpsg;
  }

  public List<ColturaDTO> getColture()
  {
    return colture;
  }

  public void setColture(List<ColturaDTO> colture)
  {
    this.colture = colture;
  }

  public List<SchedaUnarDTO> getSchedeUnar()
  {
    return schedeUnar;
  }

  public void setSchedeUnar(List<SchedaUnarDTO> schedeUnar)
  {
    this.schedeUnar = schedeUnar;
  }

  public String getFlagIstanzaRiesame()
  {
    return flagIstanzaRiesame;
  }

  public void setFlagIstanzaRiesame(String flagIstanzaRiesame)
  {
    this.flagIstanzaRiesame = flagIstanzaRiesame;
  }

  public String getDescCodiProdRile()
  {
    return descCodiProdRile;
  }

  public void setDescCodiProdRile(String descCodiProdRile)
  {
    this.descCodiProdRile = descCodiProdRile;
  }

  public int getTipoIsol()
  {
    return tipoIsol;
  }

  public void setTipoIsol(int tipoIsol)
  {
    this.tipoIsol = tipoIsol;
  }

  public String getCodiceStileGrafico()
  {
    return codiceStileGrafico;
  }

  public void setCodiceStileGrafico(String codiceStileGrafico)
  {
    this.codiceStileGrafico = codiceStileGrafico;
  }  public String getFlagModificato()
  {
    return flagModificato;
  }

  public void setFlagModificato(String flagModificato)
  {
    this.flagModificato = flagModificato;
  }

  public List<DatiParcellaRiferimentoAppezzamento> getParcelle()
  {
    return parcelle;
  }

  //ho utilizzato setParc, per evitare eccezioni durante la lettura dell'oggetto!
  public void setParc(List<DatiParcellaRiferimentoAppezzamento> parcelle)
  {
    this.parcelle = parcelle;
  }

  public String getCodiRileIstanzaRiesame()
  {
    return codiRileIstanzaRiesame;
  }

  public void setCodiRileIstanzaRiesame(String codiRileIstanzaRiesame)
  {
    this.codiRileIstanzaRiesame = codiRileIstanzaRiesame;
  }

  public String getCodiProdRileIstanzaRiesame()
  {
    return codiProdRileIstanzaRiesame;
  }

  public void setCodiProdRileIstanzaRiesame(String codiProdRileIstanzaRiesame)
  {
    this.codiProdRileIstanzaRiesame = codiProdRileIstanzaRiesame;
  }

  public String getBloccoFusione()
  {
    return bloccoFusione;
  }

  public void setBloccoFusione(String bloccoFusione)
  {
    this.bloccoFusione = bloccoFusione;
  }
}
