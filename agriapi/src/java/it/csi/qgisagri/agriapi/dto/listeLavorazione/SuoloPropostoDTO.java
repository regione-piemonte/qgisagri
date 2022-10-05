package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;

import org.codehaus.jackson.annotate.JsonIgnore;

import it.csi.qgisagri.agriapi.dto.Geometry;

public class SuoloPropostoDTO implements Serializable
{

  private static final long serialVersionUID = 109524330298406944L;
  private Long idFeature;
  
  private Long idEleggibilitaRilevata;
  private String codiceEleggibilitaRilevata;
  private String descEleggibilitaRilevata;
  private String identificativoPraticaOrigine;
  private Geometry geometry;
  private String foglio;
  private String codiceNazionale;
  private String idIstanzaRiesame;
  
  private String geometriaWkt;
  private String annoCampagna;
  private String descrTipoSorgenteSuolo;
  private String utente;
  private Date dataInizioValidita;
  private Date dataFineValidita;
  private String descrListaLavorazione;
  private String descrAzienda;
  private Date dataLavorazione;
  private String srid;
  
  private List<CoordinateFotoAppezzamentoDTO> coordinateFotoAppezzamento;
  
  
  public List<CoordinateFotoAppezzamentoDTO> getCoordinateFotoAppezzamento()
  {
    return coordinateFotoAppezzamento;
  }
  public void setCoordinateFotoAppezzamento(
      List<CoordinateFotoAppezzamentoDTO> coordinateFotoAppezzamento)
  {
    this.coordinateFotoAppezzamento = coordinateFotoAppezzamento;
  }
  public String getIdIstanzaRiesame()
  {
    return idIstanzaRiesame;
  }
  public void setIdIstanzaRiesame(String idIstanzaRiesame)
  {
    this.idIstanzaRiesame = idIstanzaRiesame;
  }
  public String getSrid()
  {
    return srid;
  }
  public void setSrid(String srid)
  {
    this.srid = srid;
  }
  public Date getDataFineValidita()
  {
    return dataFineValidita;
  }
  public void setDataFineValidita(Date dataFineValidita)
  {
    this.dataFineValidita = dataFineValidita;
  }
  public String getDescrTipoSorgenteSuolo()
  {
    return descrTipoSorgenteSuolo;
  }
  public void setDescrTipoSorgenteSuolo(String descrTipoSorgenteSuolo)
  {
    this.descrTipoSorgenteSuolo = descrTipoSorgenteSuolo;
  }
  public String getUtente()
  {
    return utente;
  }
  public void setUtente(String utente)
  {
    this.utente = utente;
  }
  public Date getDataInizioValidita()
  {
    return dataInizioValidita;
  }
  public void setDataInizioValidita(Date dataInizioValidita)
  {
    this.dataInizioValidita = dataInizioValidita;
  }
  public String getDescrListaLavorazione()
  {
    return descrListaLavorazione;
  }
  public void setDescrListaLavorazione(String descrListaLavorazione)
  {
    this.descrListaLavorazione = descrListaLavorazione;
  }
  public String getDescrAzienda()
  {
    return descrAzienda;
  }
  public void setDescrAzienda(String descrAzienda)
  {
    this.descrAzienda = descrAzienda;
  }
  public Date getDataLavorazione()
  {
    return dataLavorazione;
  }
  public void setDataLavorazione(Date dataLavorazione)
  {
    this.dataLavorazione = dataLavorazione;
  }
  public String getAnnoCampagna()
  {
    return annoCampagna;
  }
  public void setAnnoCampagna(String annoCampagna)
  {
    this.annoCampagna = annoCampagna;
  }
  public String getIdentificativoPraticaOrigine()
  {
    return identificativoPraticaOrigine;
  }
  public void setIdentificativoPraticaOrigine(String identificativoPraticaOrigine)
  {
    this.identificativoPraticaOrigine = identificativoPraticaOrigine;
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
  public String getDescEleggibilitaRilevata()
  {
    return descEleggibilitaRilevata;
  }
  public void setDescEleggibilitaRilevata(String descEleggibilitaRilevata)
  {
    this.descEleggibilitaRilevata = descEleggibilitaRilevata;
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
  public Geometry getGeometry()
  {
    return geometry;
  }
  public void setGeometry(Geometry geometry)
  {
    this.geometry = geometry;
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
  public List<HashMap<String, String>> getCoordinateFotoAppezzamentoMap()
  {
    List<HashMap<String, String>> elenco = new ArrayList<HashMap<String,String>>();
    
    if(coordinateFotoAppezzamento!=null && coordinateFotoAppezzamento.get(0).getIdFotoAppezzamento()!=null)
    {
      for (CoordinateFotoAppezzamentoDTO item : coordinateFotoAppezzamento)
      {
          HashMap<String, String> mappa = new HashMap<String, String>();
          mappa.put("idFotoAppezzamento", item.getIdFotoAppezzamento());
          mappa.put("latitudine", item.getLatitudine());
          mappa.put("longitudine", item.getLongitudine());
          elenco.add(mappa);
      }
    }else
    {
      HashMap<String, String> mappa = new HashMap<String, String>();
      elenco.add(mappa);
    }
    
    return elenco;
  }
  
  public String getCoordinateFotoAppezzamentoStrJson()
  {
    String json = "[";
    int count =0;
    if(coordinateFotoAppezzamento!=null && coordinateFotoAppezzamento.get(0).getIdFotoAppezzamento()!=null)
    {
      for (CoordinateFotoAppezzamentoDTO item : coordinateFotoAppezzamento)
      {
        if(count>0)
          json += ",";
        
          json += "{";
          json += "\"idFotoAppezzamento\":\""+item.getIdFotoAppezzamento()+"\",";
          json += "\"latitudine\":\""+item.getLatitudine()+"\",";
          json += "\"longitudine\":\""+item.getLongitudine()+"\",";
          json += "\"direzione\":\""+item.getDirezione()+"\"";
          json += "}";
          
          count++;
      }
    }
    
    json += "]";
    
    
    return json;
  }
  
  
  

 
  
}
