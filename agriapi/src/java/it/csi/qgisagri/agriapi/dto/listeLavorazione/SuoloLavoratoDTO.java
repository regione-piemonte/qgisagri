package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;
import java.util.ArrayList;

import org.locationtech.jts.geom.Geometry;

public class SuoloLavoratoDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = 6178252280750548680L;

  private Long              idEventoLavorazione;
  private Long              idFeature;
  private String            tipoSuolo;
  private String            layer;
  private Long              ogcFid;
  private Long              ogcLayerID;
  private ArrayList<Long>   idFeaturePadre;
  private Double            area;
  private String            codiceNazionale;
  private String            foglio;
  private Long              flagGeometriaVariata;
  private String            codiceEleggibilitaRilevata;
  private Long              flagSospensione;
  private String            descrizioneSospensione;
  private String            noteLavorazione;
  private Geometry          geometry;
  private Long              idTipoMotivoSospensione;

  
  public Long getOgcLayerID()
  {
    return ogcLayerID;
  }
  public void setOgcLayerID(Long ogcLayerID)
  {
    this.ogcLayerID = ogcLayerID;
  }
  public Long getIdEventoLavorazione()
  {
    return idEventoLavorazione;
  }
  public void setIdEventoLavorazione(Long idEventoLavorazione)
  {
    this.idEventoLavorazione = idEventoLavorazione;
  }
  public Long getIdFeature()
  {
    return idFeature;
  }
  public void setIdFeature(Long idFeature)
  {
    this.idFeature = idFeature;
  }
  public String getTipoSuolo()
  {
    return tipoSuolo;
  }
  public void setTipoSuolo(String tipoSuolo)
  {
    this.tipoSuolo = tipoSuolo;
  }
  public Long getOgcFid()
  {
    return ogcFid;
  }
  public void setOgcFid(Long ogcFid)
  {
    this.ogcFid = ogcFid;
  }
  public ArrayList<Long> getIdFeaturePadre()
  {
    return idFeaturePadre;
  }
  public void setIdFeaturePadre(ArrayList<Long> idFeaturePadre)
  {
    this.idFeaturePadre = idFeaturePadre;
  }
  public Double getArea()
  {
    return area;
  }
  public void setArea(Double area)
  {
    this.area = area;
  }
  public String getCodiceNazionale()
  {
    return codiceNazionale;
  }
  public void setCodiceNazionale(String codiceNazionale)
  {
    this.codiceNazionale = codiceNazionale;
  }
  public String getFoglio()
  {
    return foglio;
  }
  public void setFoglio(String foglio)
  {
    this.foglio = foglio;
  }
 
  public String getCodiceEleggibilitaRilevata()
  {
    return codiceEleggibilitaRilevata;
  }
  public void setCodiceEleggibilitaRilevata(String codiceEleggibilitaRilevata)
  {
    this.codiceEleggibilitaRilevata = codiceEleggibilitaRilevata;
  }

  public Long getFlagGeometriaVariata()
  {
    return flagGeometriaVariata;
  }
  public void setFlagGeometriaVariata(Long flagGeometriaVariata)
  {
    this.flagGeometriaVariata = flagGeometriaVariata;
  }
  public Long getFlagSospensione()
  {
    return flagSospensione;
  }
  public void setFlagSospensione(Long flagSospensione)
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
  public String getNoteLavorazione()
  {
    return noteLavorazione;
  }
  public void setNoteLavorazione(String noteLavorazione)
  {
    this.noteLavorazione = noteLavorazione;
  }
  public Geometry getGeometry()
  {
    return geometry;
  }
  public void setGeometry(Geometry geometry)
  {
    this.geometry = geometry;
  }
  public Long getIdTipoMotivoSospensione()
  {
    return idTipoMotivoSospensione;
  }
  public void setIdTipoMotivoSospensione(Long idTipoMotivoSospensione)
  {
    this.idTipoMotivoSospensione = idTipoMotivoSospensione;
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
