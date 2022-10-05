package it.csi.qgisagri.agriapi.dto.pcg;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.List;

import org.codehaus.jackson.annotate.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class SchedaUnarDTO implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = -4132373891818245030L;
  private long              idStoricoUnitaArborea;
  private String            descComune;
  private String            sezione;
  private int               foglio;
  private Long              particella;
  private String            subalterno;
  private Integer           sestoSuFile;
  private Integer           sestoTraFile;
  private Integer           numCeppi;
  
  private long              progressivoUnar;
  private long              area;
  private String            flagTipoUnar;
  private String            dataImpianto;
  private String            formaAllevamento;
  private Long              idFormaAllevamento;
  private String            utilizzo;
  private String            varieta;
  private String            tipologiaVino; // cambiato nome da flagTipoUnar
  private String            provincia;
  private long              idCatalogoMatrice;
  private long              idUnitaArborea;
  private long              idTipologiaVino;
  
  private String              dataPrimaProduzione;
  private String              dataSovrainnesto;
  private BigDecimal        percentualeVitigno;
  private List<AltriVitigniDTO> pAltriVitigni;  
  private BigDecimal        percentualeFallanza;
  private String            flagProduttiva; //FIXME: da DB si vede che in realtà si tratta di flagImproduttiva
  private Integer           idIrrigazioneUnar;
  private Long              idUnitaArboreaDichiarata; //valorizzata solo per le schede unar lette ad una dichiarazione di consistenza
  private String            vignetoStorico; 
  private String            vignetoEroico;  
  private String            vignetoFamiliare;
  private String            flagInfittimento;
  private int               percentualeRimpiazzo;
  
  public long getIdStoricoUnitaArborea()
  {
    return idStoricoUnitaArborea;
  }

  public void setIdStoricoUnitaArborea(long idStoricoUnitaArborea)
  {
    this.idStoricoUnitaArborea = idStoricoUnitaArborea;
  }

  public long getProgressivoUnar()
  {
    return progressivoUnar;
  }

  public void setProgressivoUnar(long progressivoUnar)
  {
    this.progressivoUnar = progressivoUnar;
  }
  
  public long getArea()
  {
    return area;
  }

  public void setArea(long area)
  {
    this.area = area;
  }

  public Integer getSestoSuFile()
  {
    return sestoSuFile;
  }

  public void setSestoSuFile(Integer sestoSuFile)
  {
    this.sestoSuFile = sestoSuFile;
  }

  public Integer getSestoTraFile()
  {
    return sestoTraFile;
  }

  public void setSestoTraFile(Integer sestoTraFile)
  {
    this.sestoTraFile = sestoTraFile;
  }

  public Integer getNumCeppi()
  {
    return numCeppi;
  }

  public void setNumCeppi(Integer numCeppi)
  {
    this.numCeppi = numCeppi;
  }

  public String getDataImpianto()
  {
    return dataImpianto;
  }

  public void setDataImpianto(String dataImpianto)
  {
    this.dataImpianto = dataImpianto;
  }

  public Long getIdFormaAllevamento()
  {
    return idFormaAllevamento;
  }

  public void setIdFormaAllevamento(Long idFormaAllevamento)
  {
    this.idFormaAllevamento = idFormaAllevamento;
  }

  public String getFormaAllevamento()
  {
    return formaAllevamento;
  }

  public void setFormaAllevamento(String formaAllevamento)
  {
    this.formaAllevamento = formaAllevamento;
  }

  public String getUtilizzo()
  {
    return utilizzo;
  }

  public void setUtilizzo(String utilizzo)
  {
    this.utilizzo = utilizzo;
  }

  public String getVarieta()
  {
    return varieta;
  }

  public void setVarieta(String varieta)
  {
    this.varieta = varieta;
  }

  public String getFlagTipoUnar()
  {
    return flagTipoUnar;
  }

  public void setFlagTipoUnar(String flagTipoUnar)
  {
    this.flagTipoUnar = flagTipoUnar;
  }

  public String getDescComune()
  {
    return descComune;
  }

  public void setDescComune(String descComune)
  {
    this.descComune = descComune;
  }

  public String getSezione()
  {
    return sezione;
  }

  public void setSezione(String sezione)
  {
    this.sezione = sezione;
  }

  public int getFoglio()
  {
    return foglio;
  }

  public void setFoglio(int foglio)
  {
    this.foglio = foglio;
  }
  public Long getParticella()
  {
    return particella;
  }

  public void setParticella(Long particella)
  {
    this.particella = particella;
  }
  
  public String getTipologiaVino()
  {
    return tipologiaVino;
  }

  public void setTipologiaVino(String tipologiaVino)
  {
    this.tipologiaVino = tipologiaVino;
  }

  public String getSubalterno()
  {
    return subalterno;
  }

  public void setSubalterno(String subalterno)
  {
    this.subalterno = subalterno;
  }

  public long getIdCatalogoMatrice()
  {
    return idCatalogoMatrice;
  }

  public void setIdCatalogoMatrice(long idCatalogoMatrice)
  {
    this.idCatalogoMatrice = idCatalogoMatrice;
  }

  public String getProvincia()
  {
    return provincia;
  }

  public void setProvincia(String provincia)
  {
    this.provincia = provincia;
  }

  public void setIdUnitaArborea(long idUnitaArborea)
  {
    this.idUnitaArborea = idUnitaArborea;
  }

  public long getIdUnitaArborea()
  {
    return idUnitaArborea;
  }

  public long getIdTipologiaVino()
  {
    return idTipologiaVino;
  }

  public void setIdTipologiaVino(long idTipologiaVino)
  {
    this.idTipologiaVino = idTipologiaVino;
  }

  public String getDataPrimaProduzione()
  {
    return dataPrimaProduzione;
  }

  public void setDataPrimaProduzione(String dataPrimaProduzione)
  {
    this.dataPrimaProduzione = dataPrimaProduzione;
  }

  public String getDataSovrainnesto()
  {
    return dataSovrainnesto;
  }

  public void setDataSovrainnesto(String dataSovrainnesto)
  {
    this.dataSovrainnesto = dataSovrainnesto;
  }

  public BigDecimal getPercentualeVitigno()
  {
    return percentualeVitigno;
  }

  public void setPercentualeVitigno(BigDecimal percentualeVitigno)
  {
    this.percentualeVitigno = percentualeVitigno;
  }

  public List<AltriVitigniDTO> getpAltriVitigni()
  {
    return pAltriVitigni;
  }

  public void setpAltriVitigni(List<AltriVitigniDTO> pAltriVitigni)
  {
    this.pAltriVitigni = pAltriVitigni;
  }

  public BigDecimal getPercentualeFallanza()
  {
    return percentualeFallanza;
  }

  public void setPercentualeFallanza(BigDecimal percentualeFallanza)
  {
    this.percentualeFallanza = percentualeFallanza;
  }

  public String getFlagProduttiva()
  {
    return flagProduttiva;
  }

  public void setFlagProduttiva(String flagProduttiva)
  {
    this.flagProduttiva = flagProduttiva;
  }

  public Integer getIdIrrigazioneUnar()
  {
    return idIrrigazioneUnar;
  }

  public void setIdIrrigazioneUnar(Integer idIrrigazioneUnar)
  {
    this.idIrrigazioneUnar = idIrrigazioneUnar;
  }

  public Long getIdUnitaArboreaDichiarata()
  {
    return idUnitaArboreaDichiarata;
  }

  public void setIdUnitaArboreaDichiarata(Long idUnitaArboreaDichiarata)
  {
    this.idUnitaArboreaDichiarata = idUnitaArboreaDichiarata;
  }

  public String getVignetoStorico()
  {
    return vignetoStorico;
  }

  public void setVignetoStorico(String vignetoStorico)
  {
    this.vignetoStorico = vignetoStorico;
  }

  public String getVignetoEroico()
  {
    return vignetoEroico;
  }

  public void setVignetoEroico(String vignetoEroico)
  {
    this.vignetoEroico = vignetoEroico;
  }

  public String getVignetoFamiliare()
  {
    return vignetoFamiliare;
  }

  public void setVignetoFamiliare(String vignetoFamiliare)
  {
    this.vignetoFamiliare = vignetoFamiliare;
  }

  public String getFlagInfittimento()
  {
    return flagInfittimento;
  }

  public void setFlagInfittimento(String flagInfittimento)
  {
    this.flagInfittimento = flagInfittimento;
  }

  public int getPercentualeRimpiazzo()
  {
    return percentualeRimpiazzo;
  }

  public void setPercentualeRimpiazzo(int percentualeRimpiazzo)
  {
    this.percentualeRimpiazzo = percentualeRimpiazzo;
  }
}
