package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;
import java.util.Date;

import org.codehaus.jackson.annotate.JsonIgnore;

import it.csi.qgisagri.agriapi.dto.Geometry;

public class SuoloLavorazioneDTO implements Serializable
{

  private static final long serialVersionUID = 109524330298406944L;
  private Long idFeature;
  private String geometriaWkt;
  private String srid;
  
  private String idTipoMotivoSospensione;
  private String idTipoSorgenteSuolo;
  private String flagSospensione;
  private String descrizioneSospensione;
  
  private String foglio;
  private String codiceNazionale;
  private Long idEleggibilitaRilevata;
  private String codiceEleggibilitaRilevata;
  private Geometry geometry;
  private Date dataFineValidita;
  private Long extIdAzienda;
  private String note;
  private String noteLavorazione;
  private String flagPresenzaUnar;
  private String errore;
  private String tipoSuolo;

  
  
  public String getIdTipoSorgenteSuolo()
  {
    return idTipoSorgenteSuolo;
  }
  public void setIdTipoSorgenteSuolo(String idTipoSorgenteSuolo)
  {
    this.idTipoSorgenteSuolo = idTipoSorgenteSuolo;
  }
  public String getIdTipoMotivoSospensione()
  {
    return idTipoMotivoSospensione;
  }
  public void setIdTipoMotivoSospensione(String idTipoMotivoSospensione)
  {
    this.idTipoMotivoSospensione = idTipoMotivoSospensione;
  }
  public String getFlagSospensione()
  {
    return flagSospensione;
  }
  public void setFlagSospensione(String flagSospensione)
  {
    this.flagSospensione = flagSospensione;
  }
  public String getDescrizioneSospensione()
  {
    return descrizioneSospensione;
  }
  public void setDescrizioneSospensione(String descrizioneSospensione)
  {
    this.descrizioneSospensione = descrizioneSospensione;
  }
  public String getSrid()
  {
    return srid;
  }
  public void setSrid(String srid)
  {
    this.srid = srid;
  }
  public String getFlagPresenzaUnar()
  {
    return flagPresenzaUnar;
  }
  public void setFlagPresenzaUnar(String flagPresenzaUnar)
  {
    this.flagPresenzaUnar = flagPresenzaUnar;
  }
  public String getFoglio()
  {
    return foglio;
  }
  public void setFoglio(String foglio)
  {
    this.foglio = foglio;
  }
  public String getCodiceNazionale()
  {
    return codiceNazionale;
  }
  public void setCodiceNazionale(String codiceNazionale)
  {
    this.codiceNazionale = codiceNazionale;
  }
  public Long getIdFeature()
  {
    return idFeature;
  }
  public void setIdFeature(Long idFeature)
  {
    this.idFeature = idFeature;
  }
  @JsonIgnore
  public String getGeometriaWkt()
  {
    return geometriaWkt;
  }
  public void setGeometriaWkt(String geometriaWkt)
  {
    this.geometriaWkt = geometriaWkt;
  }
  public Long getIdEleggibilitaRilevata()
  {
    return idEleggibilitaRilevata;
  }
  public void setIdEleggibilitaRilevata(Long idEleggibilitaRilevata)
  {
    this.idEleggibilitaRilevata = idEleggibilitaRilevata;
  }
  public String getCodiceEleggibilitaRilevata()
  {
    return codiceEleggibilitaRilevata;
  }
  public void setCodiceEleggibilitaRilevata(String codiceEleggibilitaRilevata)
  {
    this.codiceEleggibilitaRilevata = codiceEleggibilitaRilevata;
  }

  @JsonIgnore
  public Date getDataFineValidita()
  {
    return dataFineValidita;
  }
  public void setDataFineValidita(Date dataFineValidita)
  {
    this.dataFineValidita = dataFineValidita;
  }
  
  
  
  
  

  public Geometry getGeometry()
  {
    return geometry;
  }
  public void setGeometry(Geometry geometry)
  {
    this.geometry = geometry;
  }
  @JsonIgnore
  public Long getExtIdAzienda()
  {
    return extIdAzienda;
  }
  public void setExtIdAzienda(Long extIdAzienda)
  {
    this.extIdAzienda = extIdAzienda;
  }
  public String getNote()
  {
    return note;
  }
  public void setNote(String note)
  {
    this.note = note;
  }
  public String getErrore()
  {
    return errore;
  }
  public void setErrore(String errore)
  {
    this.errore = errore;
  }
  public String getTipoSuolo()
  {
    return tipoSuolo;
  }
  public void setTipoSuolo(String tipoSuolo)
  {
    this.tipoSuolo = tipoSuolo;
  }
  public String getNoteLavorazione()
  {
    return noteLavorazione;
  }
  public void setNoteLavorazione(String noteLavorazione)
  {
    this.noteLavorazione = noteLavorazione;
  }
  
}
