package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

public class SuoloRilevatoDTO implements Serializable
{
	private static final long serialVersionUID = -2540324271499739939L;
	private long idSuoloRilevato;
	private BigDecimal area;
	private int campagna;
	private String extCodNazionale;
	private int foglio;
	private Date dataInizioValidita;
	private Date dataFineValidita;
	private Date dataAggiornamento;
	private long extIdEleggibilitaRilevata;
	private Long extIdUtenteAggiornamento;
	private int idTipoSorgenteSuolo;
	private String extIdUtenteLavorSiticlient;
	private String flagGeomCorrotta;

	private String geometry;
	private String srid;
	
	
	
	public String getSrid()
  {
    return srid;
  }
  public void setSrid(String srid)
  {
    this.srid = srid;
  }
  public long getIdSuoloRilevato()
	{
		return idSuoloRilevato;
	}
	public void setIdSuoloRilevato(long idSuoloRilevato)
	{
		this.idSuoloRilevato = idSuoloRilevato;
	}
	public BigDecimal getArea()
	{
		return area;
	}
	public void setArea(BigDecimal area)
	{
		this.area = area;
	}
	public int getCampagna()
	{
		return campagna;
	}
	public void setCampagna(int campagna)
	{
		this.campagna = campagna;
	}
	public String getExtCodNazionale()
	{
		return extCodNazionale;
	}
	public void setExtCodNazionale(String extCodNazionale)
	{
		this.extCodNazionale = extCodNazionale;
	}
	public int getFoglio()
	{
		return foglio;
	}
	public void setFoglio(int foglio)
	{
		this.foglio = foglio;
	}
	public Date getDataInizioValidita()
	{
		return dataInizioValidita;
	}
	public void setDataInizioValidita(Date dataInizioValidita)
	{
		this.dataInizioValidita = dataInizioValidita;
	}
	public Date getDataFineValidita()
	{
		return dataFineValidita;
	}
	public void setDataFineValidita(Date dataFineValidita)
	{
		this.dataFineValidita = dataFineValidita;
	}
	public Date getDataAggiornamento()
	{
		return dataAggiornamento;
	}
	public void setDataAggiornamento(Date dataAggiornamento)
	{
		this.dataAggiornamento = dataAggiornamento;
	}
	public long getExtIdEleggibilitaRilevata()
	{
		return extIdEleggibilitaRilevata;
	}
	public void setExtIdEleggibilitaRilevata(long extIdEleggibilitaRilevata)
	{
		this.extIdEleggibilitaRilevata = extIdEleggibilitaRilevata;
	}
	public Long getExtIdUtenteAggiornamento()
	{
		return extIdUtenteAggiornamento;
	}
	public void setExtIdUtenteAggiornamento(Long extIdUtenteAggiornamento)
	{
		this.extIdUtenteAggiornamento = extIdUtenteAggiornamento;
	}
	public int getIdTipoSorgenteSuolo()
	{
		return idTipoSorgenteSuolo;
	}
	public void setIdTipoSorgenteSuolo(int idTipoSorgenteSuolo)
	{
		this.idTipoSorgenteSuolo = idTipoSorgenteSuolo;
	}
	public String getExtIdUtenteLavorSiticlient()
	{
		return extIdUtenteLavorSiticlient;
	}
	public void setExtIdUtenteLavorSiticlient(String extIdUtenteLavorSiticlient)
	{
		this.extIdUtenteLavorSiticlient = extIdUtenteLavorSiticlient;
	}
	public String getFlagGeomCorrotta()
	{
		return flagGeomCorrotta;
	}
	public void setFlagGeomCorrotta(String flagGeomCorrotta)
	{
		this.flagGeomCorrotta = flagGeomCorrotta;
	}
	public String getGeometry()
	{
		return geometry;
	}
	public void setGeometry(String geometry)
	{
		this.geometry = geometry;
	}
	
	
}