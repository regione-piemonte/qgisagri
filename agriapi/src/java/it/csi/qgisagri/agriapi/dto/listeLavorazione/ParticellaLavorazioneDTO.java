package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;
import java.util.Date;

import org.codehaus.jackson.annotate.JsonIgnore;

import it.csi.qgisagri.agriapi.dto.Geometry;

public class ParticellaLavorazioneDTO implements Serializable
{

  private static final long serialVersionUID = 109524330298406944L;

  private long idParticellaLavorazione;
  private long idEventoLavorazione;
  private long idVersioneParticella;
  private long idParticella;
  private String idPraticaOrigine;
  private String codiceNazionale;
  private String foglio;
  private String numeroParticella;
  private String descrizioneSospensione;
  private String flagSospensione;
  private String flagPresenzaAllegati;
  private String flagPresenzaCxf;
  private String noteRichiesta;
  private String noteLavorazione;
  private String flagLavorato;
  private String subalterno;
  public long getIdParticellaLavorazione()
  {
    return idParticellaLavorazione;
  }
  public void setIdParticellaLavorazione(long idParticellaLavorazione)
  {
    this.idParticellaLavorazione = idParticellaLavorazione;
  }
  public long getIdEventoLavorazione()
  {
    return idEventoLavorazione;
  }
  public void setIdEventoLavorazione(long idEventoLavorazione)
  {
    this.idEventoLavorazione = idEventoLavorazione;
  }
  public long getIdVersioneParticella()
  {
    return idVersioneParticella;
  }
  public void setIdVersioneParticella(long idVersioneParticella)
  {
    this.idVersioneParticella = idVersioneParticella;
  }
  public long getIdParticella()
  {
    return idParticella;
  }
  public void setIdParticella(long idParticella)
  {
    this.idParticella = idParticella;
  }
  public String getIdPraticaOrigine()
  {
    return idPraticaOrigine;
  }
  public void setIdPraticaOrigine(String idPraticaOrigine)
  {
    this.idPraticaOrigine = idPraticaOrigine;
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
  public String getNumeroParticella()
  {
    return numeroParticella;
  }
  public void setNumeroParticella(String numeroParticella)
  {
    this.numeroParticella = numeroParticella;
  }
  public String getDescrizioneSospensione()
  {
    return descrizioneSospensione;
  }
  public void setDescrizioneSospensione(String descrizioneSospensione)
  {
    this.descrizioneSospensione = descrizioneSospensione;
  }
  public String getFlagSospensione()
  {
    return flagSospensione;
  }
  public void setFlagSospensione(String flagSospensione)
  {
    this.flagSospensione = flagSospensione;
  }
  public String getFlagPresenzaAllegati()
  {
    return flagPresenzaAllegati;
  }
  public void setFlagPresenzaAllegati(String flagPresenzaAllegati)
  {
    this.flagPresenzaAllegati = flagPresenzaAllegati;
  }
  public String getFlagPresenzaCxf()
  {
    return flagPresenzaCxf;
  }
  public void setFlagPresenzaCxf(String flagPresenzaCxf)
  {
    this.flagPresenzaCxf = flagPresenzaCxf;
  }
  public String getNoteRichiesta()
  {
    return noteRichiesta;
  }
  public void setNoteRichiesta(String noteRichiesta)
  {
    this.noteRichiesta = noteRichiesta;
  }
  public String getNoteLavorazione()
  {
    return noteLavorazione;
  }
  public void setNoteLavorazione(String noteLavorazione)
  {
    this.noteLavorazione = noteLavorazione;
  }
  public String getFlagLavorato()
  {
    return flagLavorato;
  }
  public void setFlagLavorato(String flagLavorato)
  {
    this.flagLavorato = flagLavorato;
  }
  public String getSubalterno()
  {
    return subalterno;
  }
  public void setSubalterno(String subalterno)
  {
    this.subalterno = subalterno;
  }
  
  
  
}
