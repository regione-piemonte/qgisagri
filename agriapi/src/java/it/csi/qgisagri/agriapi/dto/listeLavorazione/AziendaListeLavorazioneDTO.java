package it.csi.qgisagri.agriapi.dto.listeLavorazione;

import java.io.Serializable;
import java.util.Date;

import org.codehaus.jackson.annotate.JsonIgnore;

public class AziendaListeLavorazioneDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = -8767039184142875737L;
  private long idAzienda;
  private long idEventoLavorazione;
  private String cuaa;
  private String denominazione;
  private long numeroFogli;
  @JsonIgnore
  private long numeroFogliBloccati;
  private long numeroParticelle;
  private long numeroSuoliLavorazione;
  private long numeroSuoliProposti;
  private Boolean isAziendaBloccata;
  private String utenteBlocco; 
  private Long idUtenteBlocco; 
  private String flagIconaLavorata;

  @JsonIgnore
  private Date dataLavorazione;
  @JsonIgnore
  private String isSospesa;
  
  
  
  public Date getDataLavorazione()
  {
    return dataLavorazione;
  }
  public void setDataLavorazione(Date dataLavorazione)
  {
    this.dataLavorazione = dataLavorazione;
  }
  public String getIsSospesa()
  {
    return isSospesa;
  }
  public void setIsSospesa(String isSospesa)
  {
    this.isSospesa = isSospesa;
  }
  public long getNumeroFogli()
  {
    return numeroFogli;
  }
  public void setNumeroFogli(long numeroFogli)
  {
    this.numeroFogli = numeroFogli;
  }
  public Boolean getIsAziendaBloccata()
  {
    return isAziendaBloccata;
  }
  public void setIsAziendaBloccata(Boolean isAziendaBloccata)
  {
    this.isAziendaBloccata = isAziendaBloccata;
  }
  public String getCuaa()
  {
    return cuaa;
  }
  public void setCuaa(String cuaa)
  {
    this.cuaa = cuaa;
  }
  public String getDenominazione()
  {
    return denominazione;
  }
  public void setDenominazione(String denominazione)
  {
    this.denominazione = denominazione;
  }
  public long getNumeroParticelle()
  {
    return numeroParticelle;
  }
  public void setNumeroParticelle(long numeroParticelle)
  {
    this.numeroParticelle = numeroParticelle;
  }
  public long getNumeroSuoliLavorazione()
  {
    return numeroSuoliLavorazione;
  }
  public void setNumeroSuoliLavorazione(long numeroSuoliLavorazione)
  {
    this.numeroSuoliLavorazione = numeroSuoliLavorazione;
  }
  public long getNumeroSuoliProposti()
  {
    return numeroSuoliProposti;
  }
  public void setNumeroSuoliProposti(long numeroSuoliProposti)
  {
    this.numeroSuoliProposti = numeroSuoliProposti;
  }
  public long getIdAzienda()
  {
    return idAzienda;
  }
  public void setIdAzienda(long idAzienda)
  {
    this.idAzienda = idAzienda;
  }
  public long getIdEventoLavorazione()
  {
    return idEventoLavorazione;
  }
  public void setIdEventoLavorazione(long idEventoLavorazione)
  {
    this.idEventoLavorazione = idEventoLavorazione;
  }
  public String getFlagIconaLavorata()
  {
    return flagIconaLavorata;
  }
  public void setFlagIconaLavorata(String flagIconaLavorata)
  {
    this.flagIconaLavorata = flagIconaLavorata;
  }
  public String getUtenteBlocco()
  {
    return utenteBlocco;
  }
  public void setUtenteBlocco(String utenteBlocco)
  {
    this.utenteBlocco = utenteBlocco;
  }
  public long getNumeroFogliBloccati()
  {
    return numeroFogliBloccati;
  }
  public void setNumeroFogliBloccati(long numeroFogliBloccati)
  {
    this.numeroFogliBloccati = numeroFogliBloccati;
  }
  public Long getIdUtenteBlocco()
  {
    return idUtenteBlocco;
  }
  public void setIdUtenteBlocco(Long idUtenteBlocco)
  {
    this.idUtenteBlocco = idUtenteBlocco;
  }
  
}
