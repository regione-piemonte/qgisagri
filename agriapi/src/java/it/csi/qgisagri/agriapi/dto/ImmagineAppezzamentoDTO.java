package it.csi.qgisagri.agriapi.dto;

import java.io.Serializable;

public class ImmagineAppezzamentoDTO implements Serializable
{

  /**
   * 
   */
  private static final long serialVersionUID = 8073142888039138247L;
  
  private byte[] content;
  private String nomeLogicoFile;
  private String nomeFisicoFile;
  public byte[] getContent()
  {
    return content;
  }
  public void setContent(byte[] content)
  {
    this.content = content;
  }
  public String getNomeLogicoFile()
  {
    return nomeLogicoFile;
  }
  public void setNomeLogicoFile(String nomeLogicoFile)
  {
    this.nomeLogicoFile = nomeLogicoFile;
  }
  public String getNomeFisicoFile()
  {
    return nomeFisicoFile;
  }
  public void setNomeFisicoFile(String nomeFisicoFile)
  {
    this.nomeFisicoFile = nomeFisicoFile;
  }
  public String getfileNameDownload()
  {
    if(nomeLogicoFile!=null && nomeLogicoFile.trim().length()>0)
    {
      return nomeLogicoFile+nomeFisicoFile.substring(nomeFisicoFile.lastIndexOf("."));
    }
    
    return nomeFisicoFile;
  }

  
}
