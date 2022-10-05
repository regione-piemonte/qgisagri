package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;

public class AllegatoParticellaDTO implements Serializable
{

  private static final long serialVersionUID = -5161229193264642420L;
  private long idAllegato;
  private String nomeLogico;
  private String nomeFisico;
  private String descrizione;
  
  
  
  public long getIdAllegato()
  {
    return idAllegato;
  }
  public void setIdAllegato(long idAllegato)
  {
    this.idAllegato = idAllegato;
  }
  public String getNomeLogico()
  {
    return nomeLogico;
  }
  public void setNomeLogico(String nomeLogico)
  {
    this.nomeLogico = nomeLogico;
  }
  public String getNomeFisico()
  {
    return nomeFisico;
  }
  public void setNomeFisico(String nomeFisico)
  {
    this.nomeFisico = nomeFisico;
  }
  public String getDescrizione()
  {
    return descrizione;
  }
  public void setDescrizione(String descrizione)
  {
    this.descrizione = descrizione;
  }

}
