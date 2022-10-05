package it.csi.qgisagri.agriapi.dto.pcg;

import java.io.Serializable;
import java.math.BigDecimal;

import org.codehaus.jackson.annotate.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class AltriVitigniDTO implements Serializable
{
  private static final long serialVersionUID = 4986884770374896858L;
  private BigDecimal percentualeAltroVitigno;
  private Long idCatalogoMatriceAltro; //nullabile per evitare che diventi uno zero in scrittura
  
  public BigDecimal getPercentualeAltroVitigno()
  {
    return percentualeAltroVitigno;
  }
  public void setPercentualeAltroVitigno(BigDecimal percentualeAltroVitigno)
  {
    this.percentualeAltroVitigno = percentualeAltroVitigno;
  }
  public Long getIdCatalogoMatriceAltro()
  {
    return idCatalogoMatriceAltro;
  }
  public void setIdCatalogoMatriceAltro(Long idCatalogoMatriceAltro)
  {
    this.idCatalogoMatriceAltro = idCatalogoMatriceAltro;
  }
  
  
}
