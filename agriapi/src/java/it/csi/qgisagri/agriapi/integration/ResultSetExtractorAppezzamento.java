package it.csi.qgisagri.agriapi.integration;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.ResultSetExtractor;

import it.csi.qgisagri.agriapi.dto.pcg.AppezzamentoDTO;
import it.csi.qgisagri.agriapi.dto.pcg.ColturaDTO;
import it.csi.qgisagri.agriapi.dto.pcg.DatiParcellaRiferimentoAppezzamento;
import it.csi.qgisagri.agriapi.dto.pcg.SchedaUnarDTO;
import it.csi.qgisagri.agriapi.util.GraficoUtils;
import oracle.sql.ARRAY;
import oracle.sql.Datum;
import oracle.sql.STRUCT;

public class ResultSetExtractorAppezzamento extends ResultSetExtractorBase
    implements ResultSetExtractor<List<AppezzamentoDTO>>
{
  GenericDatabaseObjectReader<AppezzamentoDTO> reader = new GenericDatabaseObjectReader<AppezzamentoDTO>(
      AppezzamentoDTO.class);

  @Override
  public List<AppezzamentoDTO> extractData(ResultSet rs)
      throws SQLException, DataAccessException
  {
    AppezzamentoDTO appezzamentoDTO = null;
    List<AppezzamentoDTO> results = new ArrayList<AppezzamentoDTO>();
    while ((appezzamentoDTO = reader.extractObject(rs)) != null)
    {
      results.add(appezzamentoDTO);
      try
      {
        List<ColturaDTO> colture = leggiColture(rs);
        appezzamentoDTO.setColture(colture);
        appezzamentoDTO.setSchedeUnar(leggiSchedeUnar(rs));
        appezzamentoDTO.setParc(leggiParcelle(rs));
        appezzamentoDTO.setGeometry(rs.getString("SHAPE"));
      }
      catch (Exception e)
      {
        e.printStackTrace();
      }
    }
    return results;
  }

  private List<DatiParcellaRiferimentoAppezzamento> leggiParcelle(ResultSet rs) throws SQLException
  {
    List<DatiParcellaRiferimentoAppezzamento> parcelle = new ArrayList<>();
    Object listaTable = rs.getObject("parcelle");
    listaTable = rs.getObject("parcelle");

    if (listaTable != null)
    {

      ARRAY arResultSet = (ARRAY) listaTable;

      if (arResultSet != null)
      {
        Datum[] attributi = null;
        ResultSet rs2 = arResultSet.getResultSet();
        while (rs2.next())
        {
          attributi = ((STRUCT) rs2.getObject(2))
              .getOracleAttributes();

          DatiParcellaRiferimentoAppezzamento parcella=new DatiParcellaRiferimentoAppezzamento(
              gestisciCampo(attributi[0]),
              gestisciCampo(attributi[1]),
              gestisciCampo(attributi[2]));
          parcelle.add(parcella);
        }
      }
    }
    return parcelle;
  }

  private List<ColturaDTO> leggiColture(ResultSet rs) throws Exception
  {
    List<ColturaDTO> list = new ArrayList<ColturaDTO>();
    Object listaTable = rs.getObject("coltivazioni");

    if (listaTable != null)
    {

      ARRAY arResultSet = (ARRAY) listaTable;

      if (arResultSet != null)
      {
        Datum[] attributi = null;
        ResultSet rs2 = arResultSet.getResultSet();
        while (rs2.next())
        {
          attributi = ((STRUCT) rs2.getObject(2))
              .getOracleAttributes();

          int index = 0;
          ColturaDTO colturaDTO = new ColturaDTO();
          colturaDTO.setCodiRile(rs.getString("codi_rile"));
          colturaDTO.setCodiProdRile(rs.getString("codi_prod_rile"));

          colturaDTO.setCodiOccu(gestisciCampo(attributi[index++]));
          colturaDTO
              .setCodiDestUsoo(gestisciCampo(attributi[index++]));
          colturaDTO.setCodiUsoo(gestisciCampo(attributi[index++]));
          colturaDTO.setCodiQual(gestisciCampo(attributi[index++]));
          colturaDTO
              .setCodiOccuVari(gestisciCampo(attributi[index++]));
          colturaDTO.setSupeColt(gestisciCampo(attributi[index++]));

          colturaDTO.setIdCatalogoMatrice(
              gestisciCampoLong(attributi[index++]));
          colturaDTO.setIdPraticaMantenimento(
              gestisciCampoLong(attributi[index++]));
          colturaDTO
              .setIdSemina(gestisciCampoLong(attributi[index++]));
          colturaDTO.setIdTipoPeriodoSemina(
              gestisciCampoLong(attributi[index++]));
          colturaDTO.setIdFaseAllevamento(
              gestisciCampoLong(attributi[index++]));
          Date dataInizioSemina = gestisciCampoData(attributi[index++]);
          if (dataInizioSemina != null)
          {
            colturaDTO.setDataInizioSemina(GraficoUtils.DATE.formatDate(dataInizioSemina));
          }
          Date dataFineSemina = gestisciCampoData(attributi[index++]);
          if (dataFineSemina != null)
          {
            colturaDTO.setDataFineSemina(GraficoUtils.DATE.formatDate(dataFineSemina));
          }
          colturaDTO.setDescUtilizzo(gestisciCampo(attributi[index++]));
          colturaDTO.setDescDestinazione(gestisciCampo(attributi[index++]));
          colturaDTO.setDescDettaglioUso(gestisciCampo(attributi[index++]));
          colturaDTO.setDescQualitaUso(gestisciCampo(attributi[index++]));
          colturaDTO.setDescVarieta(gestisciCampo(attributi[index++]));
          colturaDTO.setDescrizionePratica(gestisciCampo(attributi[index++]));
          colturaDTO.setDescrizioneSemina(gestisciCampo(attributi[index++]));
          colturaDTO.setDescrizionePeriodoSemina(gestisciCampo(attributi[index++]));
          colturaDTO.setDescrizioneFaseAllevamento(gestisciCampo(attributi[index++]));
          String flagSau = gestisciCampo(attributi[index++]);
          colturaDTO.setFlagSau(flagSau);
          colturaDTO.setIdAppeDett(gestisciCampoLong(attributi[index++]));
          colturaDTO.setPermanente(gestisciCampo(attributi[index++]));
          colturaDTO.setSupUtilizzataSecondaria(gestisciCampoLong(attributi[index++]));
          colturaDTO.setIdTipoPeriodoSeminaSecond(gestisciCampoLong(attributi[index++]));
          colturaDTO.setIdSeminaSecondaria(gestisciCampoLong(attributi[index++]));
          colturaDTO.setIdCatalogoMatriceSecondario(gestisciCampoLong(attributi[index++]));
          colturaDTO.setDataInizioDestinazioneSec(gestisciCampoDataAsString(attributi[index++]));
          colturaDTO.setDataFineDestinazioneSec(gestisciCampoDataAsString(attributi[index++]));
          colturaDTO.setDataAggiornamento(gestisciCampoTimestampAsString(attributi[index++]));
          colturaDTO.setDescUtilizzoSec(gestisciCampo(attributi[index++]));
          colturaDTO.setDescDestinazioneSec(gestisciCampo(attributi[index++]));
          colturaDTO.setDescDettaglioUsoSec(gestisciCampo(attributi[index++]));
          colturaDTO.setDescQualitaUsoSec(gestisciCampo(attributi[index++]));
          colturaDTO.setDescVarietaSec(gestisciCampo(attributi[index++]));
          colturaDTO.setDescSeminaSec(gestisciCampo(attributi[index++]));
          colturaDTO.setCodUtilizzoSec(gestisciCampo(attributi[index++]));
          colturaDTO.setCodDestinazioneSec(gestisciCampo(attributi[index++]));
          colturaDTO.setCodDettaglioUsoSec(gestisciCampo(attributi[index++]));
          colturaDTO.setCodQualitaUsoSec(gestisciCampo(attributi[index++]));
          colturaDTO.setCodVarietaSec(gestisciCampo(attributi[index++]));
          colturaDTO.setCodSeminaSec(gestisciCampo(attributi[index++]));
          colturaDTO.setDescPeriodoSeminaSec(gestisciCampo(attributi[index++]));
          colturaDTO.setCodPeriodoSeminaSec(gestisciCampo(attributi[index++]));
          try
          {
            colturaDTO.setFlagCatalogoAttivo(gestisciCampo(attributi[index++]));
            colturaDTO.setFlagCatalogoAttivoSec(gestisciCampo(attributi[index++]));
          }
          catch (Exception e)
          {
            e.printStackTrace();
          }
          list.add(colturaDTO);
        }
      }
    }
    return list;
  }

  private List<SchedaUnarDTO> leggiSchedeUnar(ResultSet rs)
      throws Exception
  {
    List<SchedaUnarDTO> list = new ArrayList<SchedaUnarDTO>();
    Object listaTable = rs.getObject("DETTAGLIO_SCHEDE_UNAR");

    if (listaTable != null)
    {

      ARRAY arResultSet = (ARRAY) listaTable;

      if (arResultSet != null)
      {
        Datum[] attributi = null;
        ResultSet rs2 = arResultSet.getResultSet();
        while (rs2.next())
        {
          attributi = ((STRUCT) rs2.getObject(2))
              .getOracleAttributes();

          int index = 0;
          SchedaUnarDTO schedaUnarDTO = new SchedaUnarDTO();
          schedaUnarDTO.setIdStoricoUnitaArborea(
              attributi[index++].longValue());
          schedaUnarDTO
              .setProgressivoUnar(attributi[index++].intValue());
          schedaUnarDTO.setArea(gestisciCampoLong(attributi[index++]));
          schedaUnarDTO.setSestoSuFile(
              gestisciCampoInteger(attributi[index++]));
          schedaUnarDTO.setSestoTraFile(
              gestisciCampoInteger(attributi[index++]));
          schedaUnarDTO
              .setNumCeppi(gestisciCampoInteger(attributi[index++]));
          schedaUnarDTO
              .setDataImpianto(gestisciCampoDataAsString(attributi[index++]));
          schedaUnarDTO
              .setFormaAllevamento(gestisciCampo(attributi[index++]));
          schedaUnarDTO
              .setUtilizzo(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setVarieta(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setTipologiaVino(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setFlagTipoUnar(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setDescComune(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setSezione(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setFoglio(gestisciCampoLong(attributi[index++]).intValue());
          schedaUnarDTO.setParticella(gestisciCampoLong(attributi[index++]));
          schedaUnarDTO.setSubalterno(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setVignetoStorico(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setVignetoEroico(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setVignetoFamiliare(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setFlagInfittimento(gestisciCampo(attributi[index++]));
          schedaUnarDTO.setPercentualeRimpiazzo(gestisciCampoInteger(attributi[index++]));
          list.add(schedaUnarDTO);
        }
      }
    }
    return list;
  }
}
