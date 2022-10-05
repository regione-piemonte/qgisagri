<%@page import="java.util.Date"%>
<%@page import="java.util.List"%>
<%@page import="java.util.Arrays"%>
<%@page import="it.csi.iride2.policy.entity.Identita"%>
<%@page import="it.csi.papua.papuaserv.dto.gestioneutenti.Ruolo"%>
<%@page import="it.csi.papua.papuaserv.dto.gestioneutenti.ws.UtenteAbilitazioni"%>
<%@page import="it.csi.qgisagri.agriapi.util.AgriApiConstants"%>
<%@page import="it.csi.papua.papuaserv.presentation.rest.profilazione.client.PapuaservProfilazioneServiceFactory"%>
<%@taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<!DOCTYPE html>
<html>
<head> 
<title>Piano Colturale Grafico SIAP</title>
<link rel="stylesheet"
	href="https://cdn.rawgit.com/openlayers/openlayers.github.io/master/en/v5.3.0/css/ol.css">
<link rel="stylesheet"
	href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
<link rel="stylesheet"
	href="http://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
</head>
<body>
	<%!private static final List<String> CODICI_FISCALI = Arrays.asList(new String[]
  { "AAAAAA00B77B000F", "AAAAAA00A11B000J", "AAAAAA00A11C000K",
      "AAAAAA00A11D000L", "AAAAAA00A11E000M",
      "AAAAAA00A11F000N", "AAAAAA00A11G000O", "AAAAAA00A11H000P",
      "AAAAAA00A11I000Q", "AAAAAA00A11J000R",
      "AAAAAA00A11K000S", "AAAAAA00A11L000T",
      "AAAAAA00A11M000U", "AAAAAA00A11N000V", "AAAAAA00A11O000W",
      "AAAAAA00A11R000Z", "AAAAAA00A11S000A",
      "AAAAAA00A11T000B", "AAAAAA00A11U000C",
      "AAAAAA00A11V000D", "AAAAAA00A11P000X" });%>
	<%
	  request.setAttribute("CODICI_FISCALI", CODICI_FISCALI);
		  String codiceFiscale = request.getParameter("codiceFiscale");
		  if (codiceFiscale != null)
		  {
		    Identita identita = new Identita();
		    identita.setCodFiscale(codiceFiscale);
		    int index = CODICI_FISCALI.indexOf(codiceFiscale);
		    index+=20;
		    identita.setCognome("CSI PIEMONTE");
		    identita.setNome("DEMO " + index);
		    identita.setLivelloAutenticazione(31);
		    identita.setTimestamp(new Date().toString());
		    identita.setIdProvider("INFOCERT_3");
		    session.setAttribute("identita", identita);
		    request.setAttribute("done", Boolean.TRUE);	    
        System.out.println("Codice fiscale: " + identita.getCodFiscale());
        System.out.println("Nome: " + identita.getNome() + " " + identita.getCognome());
        System.out.println("Livello autenticazione: " + identita.getLivelloAutenticazione());
		    Ruolo[] ruoli = PapuaservProfilazioneServiceFactory.getRestServiceClient().findRuoliForPersonaInApplicazione(
	      identita.getCodFiscale(), identita.getLivelloAutenticazione(), AgriApiConstants.ID_PROCEDIMENTO);
 
	  if(ruoli!=null && ruoli.length>0) { 
	    UtenteAbilitazioni utenteAbilitazioni = PapuaservProfilazioneServiceFactory.getRestServiceClient().login(
	      identita.getCodFiscale(), identita.getCognome(), identita.getNome(),
	      identita.getLivelloAutenticazione(),
	     AgriApiConstants.ID_PROCEDIMENTO, ruoli[0].getCodice());
	    session.setAttribute("utenteAbilitazioni", utenteAbilitazioni);
	  }
	  else{
	   request.setAttribute("done", Boolean.FALSE);
	  }
		  }
	%>

	<div class="container">
		<br />
		<c:if test="${done}">
			<div class="alert alert-success">Identit&agrave; inserita in
				sessione come richiesto</div>
			<br />
		</c:if>
		<c:if test="${!done}">
      <div class="alert alert-danger">Utente non abilitato</div>
      <br />
    </c:if>
		<div class="row">
			<div class="col-md-8 offset-md-2">
				<div class="card" style="width: 100%">
					<div class="card-header">Selezionare il demo</div>
					<div class="card-body">
						<form action="" method="post">
							<select class="form-control" name="codiceFiscale">
								<c:forEach items="${CODICI_FISCALI}" var="c" varStatus="status">
									<option value="${c}"
										<c:if test="${param.codiceFiscale==c}">selected="selected"</c:if>>CSI.DEMO
										${status.index+20}</option>
								</c:forEach>
							</select> <br />
							<button type="submit" class="btn btn-success">Invia</button>
						</form>
					</div>
				</div>
			</div>
		</div>
	</div>
	<script src="https://code.jquery.com/jquery-3.4.1.js"></script>
	<script
		src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.bundle.min.js"></script>
</body>