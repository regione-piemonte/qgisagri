# Project Title
Fotointerpretazioni GIS delle aree agricole del Piemonte - GIS photo-interpretations of the agricultural areas of Piedmont

# Project Description
The system allows the photo-interpretation of the orthophotos of the territory.

# Getting Started
The QGISAGRI product is composed of the following components:
- [QGISAGRIPLG](https://github.com/regione-piemonte/qgisagri/qgisagriplg) (QGIS plugin)
- [AGRIAPI](https://github.com/regione-piemonte/qgisagri/agriapi) (API for querying profiling services and access to the database)
- [OGCPROXYAGRI](https://github.com/regione-piemonte/qgisagri/ogcproxyagri) (bridge component for authenticated display of the background map service)
- [SITIPIOPRDB](https://github.com/regione-piemonte/qgisagri/sitipioprdb) (script for managing the structure of the database)
- [SITIPIOPRPLSQL](https://github.com/regione-piemonte/qgisagri/sitipioprplsql) (script for the management of PL/SQL procedures)

# Prerequisites
The prerequisites for installing the components are as follows:
## Software
- [JDK 8](https://www.apache.org)
- [Apache 2.4](https://www.apache.org)
- [RedHat JBoss 6.4 GA](https://developers.redhat.com)  
- [Oracle 11g](https://www.oracle.com)  

- All libraries listed in the BOM.csv files must be accessible to build the project.
- The libraries of the component AGRIAPI are published in the CSI's Artifact Repository, but for simplicity they have been included in the directory /lib of the component itself, with the exception of the ojdbc6.jar library, which must be downloaded independently from the Oracle website.

# Versioning
Git is used for managing the source code. For versioning management, reference is made to the [Semantic Versioning](https://semver.org) methodology.

# Copyrights
(C) Copyright 2021 Regione Piemonte

# License
This software is distributed under the GPLv2.
See the files gpl-2.0-LICENSE.txt for more details.