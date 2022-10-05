package it.csi.qgisagri.agriapi.dto.pcg;

import java.io.Serializable;

public class ColturaDTO implements Serializable
{
  /** serialVersionUID */
  private static final long serialVersionUID = 8873661486715832676L;
  private String            codiRile;;
  private String            codiProdRile;
  private String            codiOccu;
  private String            codiDestUsoo;
  private String            codiUsoo;
  private String            codiQual;
  private String            codiOccuVari;
  private String            supeColt;
  private Long              idCatalogoMatrice;
  private Long              idPraticaMantenimento;
  private Long              idSemina;
  private Long              idTipoPeriodoSemina;
  private Long              idFaseAllevamento;
  private String            dataInizioSemina;
  private String            dataFineSemina;

  private String            descUtilizzo;
  private String            descDestinazione;
  private String            descDettaglioUso;
  private String            descQualitaUso;
  private String            descVarieta;
  private String            descrizionePratica;
  private String            descrizioneSemina;
  private String            descrizionePeriodoSemina;
  private String            descrizioneFaseAllevamento;
  private String            flagSau;
  private Long              idAppeDett;
  private String            permanente;
  private Long              supUtilizzataSecondaria;
  private Long              idTipoPeriodoSeminaSecond;
  private Long              idSeminaSecondaria;
  private Long              idCatalogoMatriceSecondario;
  private String            dataInizioDestinazioneSec;
  private String            dataFineDestinazioneSec;
  private String            dataAggiornamento;
  private String            codUtilizzoSec;
  private String            codDestinazioneSec;
  private String            codDettaglioUsoSec;
  private String            codQualitaUsoSec;
  private String            codVarietaSec;
  private String            codSeminaSec;
  private String            codPeriodoSeminaSec;
  private String            descUtilizzoSec;
  private String            descDestinazioneSec;
  private String            descDettaglioUsoSec;
  private String            descQualitaUsoSec;
  private String            descVarietaSec;
  private String            descSeminaSec;
  private String            descPeriodoSeminaSec;
  private String            flagCatalogoAttivo;
  private String            flagCatalogoAttivoSec;

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

  public String getCodiOccu()
  {
    return codiOccu;
  }

  public void setCodiOccu(String codiOccu)
  {
    this.codiOccu = codiOccu;
  }

  public String getCodiDestUsoo()
  {
    return codiDestUsoo;
  }

  public void setCodiDestUsoo(String codiDestUsoo)
  {
    this.codiDestUsoo = codiDestUsoo;
  }

  public String getCodiUsoo()
  {
    return codiUsoo;
  }

  public void setCodiUsoo(String codiUsoo)
  {
    this.codiUsoo = codiUsoo;
  }

  public String getCodiQual()
  {
    return codiQual;
  }

  public void setCodiQual(String codiQual)
  {
    this.codiQual = codiQual;
  }

  public String getCodiOccuVari()
  {
    return codiOccuVari;
  }

  public void setCodiOccuVari(String codiOccuVari)
  {
    this.codiOccuVari = codiOccuVari;
  }

  public String getSupeColt()
  {
    return supeColt;
  }

  public void setSupeColt(String supeColt)
  {
    this.supeColt = supeColt;
  }

  public Long getIdCatalogoMatrice()
  {
    return idCatalogoMatrice;
  }

  public void setIdCatalogoMatrice(Long idCatalogoMatrice)
  {
    this.idCatalogoMatrice = idCatalogoMatrice;
  }

  public Long getIdPraticaMantenimento()
  {
    return idPraticaMantenimento;
  }

  public void setIdPraticaMantenimento(Long idPraticaMantenimento)
  {
    this.idPraticaMantenimento = idPraticaMantenimento;
  }

  public Long getIdSemina()
  {
    return idSemina;
  }

  public void setIdSemina(Long idSemina)
  {
    this.idSemina = idSemina;
  }

  public Long getIdTipoPeriodoSemina()
  {
    return idTipoPeriodoSemina;
  }

  public void setIdTipoPeriodoSemina(Long idTipoPeriodoSemina)
  {
    this.idTipoPeriodoSemina = idTipoPeriodoSemina;
  }

  public Long getIdFaseAllevamento()
  {
    return idFaseAllevamento;
  }

  public void setIdFaseAllevamento(Long idFaseAllevamento)
  {
    this.idFaseAllevamento = idFaseAllevamento;
  }

  public String getDataInizioSemina()
  {
    return dataInizioSemina;
  }

  public void setDataInizioSemina(String dataInizioSemina)
  {
    this.dataInizioSemina = dataInizioSemina;
  }

  public String getDataFineSemina()
  {
    return dataFineSemina;
  }

  public void setDataFineSemina(String dataFineSemina)
  {
    this.dataFineSemina = dataFineSemina;
  }

  public String getDescUtilizzo()
  {
    return descUtilizzo;
  }

  public void setDescUtilizzo(String descUtilizzo)
  {
    this.descUtilizzo = descUtilizzo;
  }

  public String getDescDestinazione()
  {
    return descDestinazione;
  }

  public void setDescDestinazione(String descDestinazione)
  {
    this.descDestinazione = descDestinazione;
  }

  public String getDescDettaglioUso()
  {
    return descDettaglioUso;
  }

  public void setDescDettaglioUso(String descDettaglioUso)
  {
    this.descDettaglioUso = descDettaglioUso;
  }

  public String getDescQualitaUso()
  {
    return descQualitaUso;
  }

  public void setDescQualitaUso(String descQualitaUso)
  {
    this.descQualitaUso = descQualitaUso;
  }

  public String getDescVarieta()
  {
    return descVarieta;
  }

  public void setDescVarieta(String descVarieta)
  {
    this.descVarieta = descVarieta;
  }

  public String getDescrizionePratica()
  {
    return descrizionePratica;
  }

  public void setDescrizionePratica(String descrizionePratica)
  {
    this.descrizionePratica = descrizionePratica;
  }

  public String getDescrizioneSemina()
  {
    return descrizioneSemina;
  }

  public void setDescrizioneSemina(String descrizioneSemina)
  {
    this.descrizioneSemina = descrizioneSemina;
  }

  public String getDescrizionePeriodoSemina()
  {
    return descrizionePeriodoSemina;
  }

  public void setDescrizionePeriodoSemina(String descrizionePeriodoSemina)
  {
    this.descrizionePeriodoSemina = descrizionePeriodoSemina;
  }

  public String getDescrizioneFaseAllevamento()
  {
    return descrizioneFaseAllevamento;
  }

  public void setDescrizioneFaseAllevamento(String descrizioneFaseAllevamento)
  {
    this.descrizioneFaseAllevamento = descrizioneFaseAllevamento;
  }

  public String getFlagSau()
  {
    return flagSau;
  }

  public void setFlagSau(String flagSau)
  {
    this.flagSau = flagSau;
  }

  public Long getIdAppeDett()
  {
    return idAppeDett;
  }

  public void setIdAppeDett(Long idAppeDett)
  {
    this.idAppeDett = idAppeDett;
  }

  public String getPermanente()
  {
    return permanente;
  }

  public void setPermanente(String permanente)
  {
    this.permanente = permanente;
  }

  public Long getSupUtilizzataSecondaria()
  {
    return supUtilizzataSecondaria;
  }

  public void setSupUtilizzataSecondaria(Long supUtilizzataSecondaria)
  {
    this.supUtilizzataSecondaria = supUtilizzataSecondaria;
  }

  public Long getIdTipoPeriodoSeminaSecond()
  {
    return idTipoPeriodoSeminaSecond;
  }

  public void setIdTipoPeriodoSeminaSecond(Long idTipoPeriodoSeminaSecond)
  {
    this.idTipoPeriodoSeminaSecond = idTipoPeriodoSeminaSecond;
  }

  public Long getIdSeminaSecondaria()
  {
    return idSeminaSecondaria;
  }

  public void setIdSeminaSecondaria(Long idSeminaSecondaria)
  {
    this.idSeminaSecondaria = idSeminaSecondaria;
  }

  public Long getIdCatalogoMatriceSecondario()
  {
    return idCatalogoMatriceSecondario;
  }

  public void setIdCatalogoMatriceSecondario(Long idCatalogoMatriceSecondario)
  {
    this.idCatalogoMatriceSecondario = idCatalogoMatriceSecondario;
  }

  public String getDataInizioDestinazioneSec()
  {
    return dataInizioDestinazioneSec;
  }

  public void setDataInizioDestinazioneSec(String dataInizioDestinazioneSec)
  {
    this.dataInizioDestinazioneSec = dataInizioDestinazioneSec;
  }

  public String getDataFineDestinazioneSec()
  {
    return dataFineDestinazioneSec;
  }

  public void setDataFineDestinazioneSec(String dataFineDestinazioneSec)
  {
    this.dataFineDestinazioneSec = dataFineDestinazioneSec;
  }

  public String getDataAggiornamento()
  {
    return dataAggiornamento;
  }

  public void setDataAggiornamento(String dataAggiornamento)
  {
    this.dataAggiornamento = dataAggiornamento;
  }

  public String getCodUtilizzoSec()
  {
    return codUtilizzoSec;
  }

  public void setCodUtilizzoSec(String codUtilizzoSec)
  {
    this.codUtilizzoSec = codUtilizzoSec;
  }

  public String getCodDestinazioneSec()
  {
    return codDestinazioneSec;
  }

  public void setCodDestinazioneSec(String codDestinazioneSec)
  {
    this.codDestinazioneSec = codDestinazioneSec;
  }

  public String getCodDettaglioUsoSec()
  {
    return codDettaglioUsoSec;
  }

  public void setCodDettaglioUsoSec(String codDettaglioUsoSec)
  {
    this.codDettaglioUsoSec = codDettaglioUsoSec;
  }

  public String getCodQualitaUsoSec()
  {
    return codQualitaUsoSec;
  }

  public void setCodQualitaUsoSec(String codQualitaUsoSec)
  {
    this.codQualitaUsoSec = codQualitaUsoSec;
  }

  public String getCodVarietaSec()
  {
    return codVarietaSec;
  }

  public void setCodVarietaSec(String codVarietaSec)
  {
    this.codVarietaSec = codVarietaSec;
  }

  public String getCodSeminaSec()
  {
    return codSeminaSec;
  }

  public void setCodSeminaSec(String codSeminaSec)
  {
    this.codSeminaSec = codSeminaSec;
  }

  public String getCodPeriodoSeminaSec()
  {
    return codPeriodoSeminaSec;
  }

  public void setCodPeriodoSeminaSec(String codPeriodoSeminaSec)
  {
    this.codPeriodoSeminaSec = codPeriodoSeminaSec;
  }

  public String getDescUtilizzoSec()
  {
    return descUtilizzoSec;
  }

  public void setDescUtilizzoSec(String descUtilizzoSec)
  {
    this.descUtilizzoSec = descUtilizzoSec;
  }

  public String getDescDestinazioneSec()
  {
    return descDestinazioneSec;
  }

  public void setDescDestinazioneSec(String descDestinazioneSec)
  {
    this.descDestinazioneSec = descDestinazioneSec;
  }

  public String getDescDettaglioUsoSec()
  {
    return descDettaglioUsoSec;
  }

  public void setDescDettaglioUsoSec(String descDettaglioUsoSec)
  {
    this.descDettaglioUsoSec = descDettaglioUsoSec;
  }

  public String getDescQualitaUsoSec()
  {
    return descQualitaUsoSec;
  }

  public void setDescQualitaUsoSec(String descQualitaUsoSec)
  {
    this.descQualitaUsoSec = descQualitaUsoSec;
  }

  public String getDescVarietaSec()
  {
    return descVarietaSec;
  }

  public void setDescVarietaSec(String descVarietaSec)
  {
    this.descVarietaSec = descVarietaSec;
  }

  public String getDescSeminaSec()
  {
    return descSeminaSec;
  }

  public void setDescSeminaSec(String descSeminaSec)
  {
    this.descSeminaSec = descSeminaSec;
  }

  public String getDescPeriodoSeminaSec()
  {
    return descPeriodoSeminaSec;
  }

  public void setDescPeriodoSeminaSec(String descPeriodoSeminaSec)
  {
    this.descPeriodoSeminaSec = descPeriodoSeminaSec;
  }

  public String getFlagCatalogoAttivo()
  {
    return flagCatalogoAttivo;
  }

  public void setFlagCatalogoAttivo(String flagCatalogoAttivo)
  {
    this.flagCatalogoAttivo = flagCatalogoAttivo;
  }

  public String getFlagCatalogoAttivoSec()
  {
    return flagCatalogoAttivoSec;
  }

  public void setFlagCatalogoAttivoSec(String flagCatalogoAttivoSec)
  {
    this.flagCatalogoAttivoSec = flagCatalogoAttivoSec;
  }
}
