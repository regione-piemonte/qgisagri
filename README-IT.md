# Project Title
Fotointerpretazioni GIS delle aree agricole del Piemonte

# Project Description
Il sistema permette la fotointerpretazione delle ortofoto del territorio.

# Getting Started
Il prodotto QGISAGRI è composto dalle seguenti componenti:
- [QGISAGRIPLG](https://github.com/regione-piemonte/qgisagri/qgisagriplg) (plugin per QGIS)
- [AGRIAPI](https://github.com/regione-piemonte/qgisagri/agriapi) (API per interrogazione servizi di profilazione e accesso al db)
- [OGCPROXYAGRI](https://github.com/regione-piemonte/qgisagri/ogcproxyagri) (componente di bridge per esposizione autenticata del map service di sfondo)
- [SITIPIOPRDB](https://github.com/regione-piemonte/qgisagri/sitipioprdb) (script per la gestione della struttura della base dati)
- [SITIPIOPRPLSQL](https://github.com/regione-piemonte/qgisagri/sitipioprplsql) (script per la gestione delle procedure PL/SQL)

# Prerequisites
I prerequisiti per l'installazione delle componenti sono i seguenti:
## Software
- [JDK 8](https://www.apache.org)
- [Apache 2.4](https://www.apache.org)
- [RedHat JBoss 6.4 GA](https://developers.redhat.com)  
- [Oracle Database ](https://www.oracle.com)  

- Tutte le librerie elencate nei file BOM.csv devono essere accessibili per compilare le componenti.
- Le librerie della componente AGRIAPI sono pubblicate nel Repository degli Artefatti del CSI, ma per semplicità sono state incluse nella directory /lib della medesuna componente, ad esclusione della libreria ojdbc6.jar, che è utilizzata dalle componenti AGRCFO e AGRCBO per invocare servizi esterni con protocollo t3 e che deve essere scaricata autonomamente dal sito di Oracle.

# Versioning
Per la gestione del codice sorgente viene utilizzato Git. Per la gestione del versioning si fa riferimento alla metodologia [Semantic Versioning](https://semver.org) 

# Copyrights
(C) Copyright 2021 Regione Piemonte

# License
Il sistema nel suo insieme è distribuito con licenza GPLv2.
Consultare il file gpl-2.0-LICENSE.txt per maggiori dettagli.