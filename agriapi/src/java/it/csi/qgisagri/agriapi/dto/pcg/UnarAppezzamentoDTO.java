package it.csi.qgisagri.agriapi.dto.pcg;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

import it.csi.qgisagri.agriapi.util.GraficoUtils;

public class UnarAppezzamentoDTO implements Serializable
{
	private static final long serialVersionUID = -9008872795478690920L;
	private String tipo;
	private BigDecimal superficie;
	private String annoImpianto;
	private String varieta;
	private long idUnitaArborea;
	private String dataAggiornamento;
	
	private String comune;
	private String sezione;
	private String foglio;
	private String particella;
	private String subalterno;
	private String varietaFag;
	
	
	
	
	public String getVarietaFag()
  {
    return varietaFag;
  }
  public void setVarietaFag(String varietaFag)
  {
    this.varietaFag = varietaFag;
  }
  public String getComune()
  {
    return comune;
  }
  public void setComune(String comune)
  {
    this.comune = comune;
  }
  public String getSezione()
  {
    return sezione;
  }
  public void setSezione(String sezione)
  {
    this.sezione = sezione;
  }
  public String getFoglio()
  {
    return foglio;
  }
  public void setFoglio(String foglio)
  {
    this.foglio = foglio;
  }
  public String getParticella()
  {
    return particella;
  }
  public void setParticella(String particella)
  {
    this.particella = particella;
  }
  public String getSubalterno()
  {
    return subalterno;
  }
  public void setSubalterno(String subalterno)
  {
    this.subalterno = subalterno;
  }
  public String getTipo()
	{
		return tipo;
	}
	public void setTipo(String tipo)
	{
		this.tipo = tipo;
	}
	public BigDecimal getSuperficie()
	{
		return superficie;
	}
	public void setSuperficie(BigDecimal superficie)
	{
		this.superficie = superficie;
	}
	public String getVarieta()
	{
		return varieta;
	}
	public void setVarieta(String varieta)
	{
		this.varieta = varieta;
	}
	public long getIdUnitaArborea()
	{
		return idUnitaArborea;
	}
	public void setIdUnitaArborea(long idUnitaArborea)
	{
		this.idUnitaArborea = idUnitaArborea;
	}
	public String getAnnoImpianto()
  {
    return annoImpianto;
  }
  public void setAnnoImpianto(String annoImpianto)
  {
    this.annoImpianto = annoImpianto;
  }
  public String getDataAggiornamento()
	{
		return dataAggiornamento;
	}
	public void setDataAggiornamento(String dataAggiornamento)
	{
		this.dataAggiornamento = dataAggiornamento;
	}
}