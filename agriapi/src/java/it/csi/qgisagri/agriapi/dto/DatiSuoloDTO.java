package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;
import java.math.BigDecimal;

public class DatiSuoloDTO implements Serializable
{
	/** serialVersionUID */
	private static final long serialVersionUID = 6807059520017592165L;
	private int annoCampagna;
	private String codiceVarieta;
	private BigDecimal area;
	private String tipoSuolo;
	private String utenteSuolo;
	private String dataValidita;
	private String dataFineValidita;
	private String listaDiLavorazione;
	private String aziendaLavorazione;
	private String dataLavorazione;
	private String utenteLavorazone;

	
	
	public String getDataFineValidita()
  {
    return dataFineValidita;
  }

  public void setDataFineValidita(String dataFineValidita)
  {
    this.dataFineValidita = dataFineValidita;
  }

  public int getAnnoCampagna()
	{
		return annoCampagna;
	}

	public void setAnnoCampagna(int annoCampagna)
	{
		this.annoCampagna = annoCampagna;
	}

	public String getCodiceVarieta()
	{
		return codiceVarieta;
	}

	public void setCodiceVarieta(String codiceVarieta)
	{
		this.codiceVarieta = codiceVarieta;
	}

	public BigDecimal getArea()
	{
		return area;
	}

	public void setArea(BigDecimal area)
	{
		this.area = area;
	}
	
	public String getTipoSuolo()
	{
		return tipoSuolo;
	}

	public void setTipoSuolo(String tipoSuolo)
	{
		this.tipoSuolo = tipoSuolo;
	}

	public String getUtenteSuolo()
	{
		return utenteSuolo;
	}

	public void setUtenteSuolo(String utenteSuolo)
	{
		this.utenteSuolo = utenteSuolo;
	}

	public String getListaDiLavorazione()
	{
		return listaDiLavorazione;
	}

	public void setListaDiLavorazione(String listaDiLavorazione)
	{
		this.listaDiLavorazione = listaDiLavorazione;
	}

	public String getAziendaLavorazione()
	{
		return aziendaLavorazione;
	}

	public void setAziendaLavorazione(String aziendaLavorazione)
	{
		this.aziendaLavorazione = aziendaLavorazione;
	}

	public String getUtenteLavorazone()
	{
		return utenteLavorazone;
	}

	public void setUtenteLavorazone(String utenteLavorazone)
	{
		this.utenteLavorazone = utenteLavorazone;
	}

	public void setDataLavorazione(String dataLavorazione)
	{
		this.dataLavorazione = dataLavorazione;
	}

	public String getDataLavorazione()
	{
		return dataLavorazione;
	}
	
	public void setDataValidita(String dataValidita)
	{
		this.dataValidita = dataValidita;
	}

	public String getDataValidita()
	{
		return dataValidita;
	}
}
