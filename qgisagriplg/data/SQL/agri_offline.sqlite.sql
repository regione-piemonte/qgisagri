-----------------------------------------------------------------------------------------
-- TABLES
-----------------------------------------------------------------------------------------

-- create settings table
CREATE TABLE IF NOT EXISTS agri_settings (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
);
INSERT OR REPLACE INTO agri_settings(key,value) values('enable_trigger_suoli_bloccati_update', '1');

/*
-- populate 'confine_foglio' feaureclass by union of all 'particelle' geometries
DELETE FROM confine_foglio;
INSERT INTO confine_foglio(geometry)
SELECT 
  CASE 
    WHEN geometry IS NOT NULL AND ST_NumGeometries( geometry ) > 1 THEN ST_Multi( ST_ConvexHull( geometry ) )
	ELSE geometry
  END AS geometry
FROM (
	SELECT ST_Multi( ST_MakeValid( ST_Union( ST_MakeValid( geometry ) ) ) ) AS geometry
	FROM particelle_catastali
);
*/

/* 05/08/2020 - Layer downloaded from Agri service
-- populate 'confine_foglio' feaureclass by convex hull of all 'particelle' geometries
DELETE FROM confine_foglio;

INSERT INTO confine_foglio(geometry)
SELECT ST_Multi( ST_ConvexHull( ST_Multi( ST_MakeValid( ST_Union( ST_MakeValid( geometry ) ) ) ) ) ) AS geometry
FROM particelle_catastali;

SELECT InvalidateLayerStatistics("confine_foglio");
SELECT UpdateLayerStatistics("confine_foglio");
*/

/* SHIFTED TO PLUGIN SOURCES
-- duplicate id feature field on suoli layer
ALTER TABLE "suoli_lavorazione" ADD COLUMN idFeaturePadre JSON;
UPDATE "suoli_lavorazione" SET idFeaturePadre = json_array(idFeature);

-- add cessato column
ALTER TABLE suoli_lavorazione ADD COLUMN cessato BOOLEAN NOT NULL default false;

-- add modificato column
ALTER TABLE suoli_lavorazione ADD COLUMN modificato BOOLEAN NOT NULL default false;

SELECT InvalidateLayerStatistics("suoli_lavorazione");
SELECT UpdateLayerStatistics("suoli_lavorazione");
*/

/* SHIFTED TO PLUGIN SOURCES
-- duplicate id feature field on suoli layer
ALTER TABLE "particelle_catastali" ADD COLUMN idFeaturePadre JSON;
UPDATE "particelle_catastali" SET idFeaturePadre = json_array(idFeature);

-- add cessato column
ALTER TABLE particelle_catastali ADD COLUMN flagCessato BOOLEAN NOT NULL default false;

SELECT InvalidateLayerStatistics("particelle_catastali");
SELECT UpdateLayerStatistics("particelle_catastali");
*/

--------------------------------------------------------------------------------------------
-- try to repair invalid geometries
UPDATE "suoli_lavorazione"
   SET geometry = COALESCE( ST_MakeValid( geometry ), geometry )
 WHERE ST_IsValid( geometry ) = 0;
 
UPDATE "suoli_noconduzione_corrotti"
   SET geometry = COALESCE( ST_MakeValid( geometry ), geometry )
 WHERE ST_IsValid( geometry ) = 0;

--------------------------------------------------------------------------------------------
-- update idFeaturePadre field
UPDATE "suoli_lavorazione" SET idFeaturePadre = json_array(idFeature);
UPDATE "suoli_noconduzione" SET idFeaturePadre = json_array(idFeature);
UPDATE "suoli_noconduzione_corrotti" SET idFeaturePadre = json_array(idFeature);

-- update _flagInvalido field
UPDATE "suoli_lavorazione" SET _flagInvalido = NOT(ST_IsValid(geometry) AND (COALESCE(ST_NumGeometries(geometry),0) = 1) AND (ST_Area(geometry) >= 2.0));
UPDATE "suoli_noconduzione" SET _flagInvalido = NOT(ST_IsValid(geometry) AND (COALESCE(ST_NumGeometries(geometry),0) = 1) AND (ST_Area(geometry) >= 2.0));
UPDATE "suoli_noconduzione_corrotti" SET _flagInvalido = NOT(ST_IsValid(geometry) AND (COALESCE(ST_NumGeometries(geometry),0) = 1) AND (ST_Area(geometry) >= 2.0));
UPDATE "particelle_catastali" SET _flagInvalido = NOT(ST_IsValid(geometry) AND (COALESCE(ST_NumGeometries(geometry),0) = 1) AND (ST_Area(geometry) >= 2.0));

-- update foto_appezzamenti
UPDATE "foto_appezzamenti" SET geometry=MakePoint(longitudine, latitudine, 4326);
--SELECT InvalidateLayerStatistics("foto_appezzamenti");
--SELECT UpdateLayerStatistics("foto_appezzamenti");

/*
-- create index on table ClassiEleggibilita
CREATE INDEX IF NOT EXISTS ClassiEleggibilita_idx
  ON ClassiEleggibilita (codiceEleggibilitaRilevata)
  WHERE codiceEleggibilitaRilevata IS NOT NULL;
  
-- create index on table MotivoSospensione
CREATE INDEX IF NOT EXISTS MotivoSospensione_idx
  ON MotivoSospensione (idTipoMotivoSospensione)
  WHERE idTipoMotivoSospensione IS NOT NULL;
*/

--------------------------------------------------------------------------------------------
--- Dump multipolygons to multipolygons single part
WITH RECURSIVE
  dump(geom, fid, geom_ref, n) AS (
     SELECT NULL, OGC_FID AS fid, geometry AS geom_ref, 0 AS n 
       FROM suoli_lavorazione
      WHERE ST_NumGeometries(geometry) > 1
		UNION ALL
     SELECT ST_Multi(GeometryN(geom_ref,n+1)), fid, geom_ref, n+1 from dump
	 WHERE n+1 <=  ST_NumGeometries(geom_ref)
  )
INSERT INTO suoli_lavorazione (id, note, idEleggibilitaRilevata, codiceEleggibilitaRilevata, 
                              idFeature, codiceNazionale, foglio, idFeaturePadre, cessato, 
							  flagLavorato, flagSospensione, descrizioneSospensione, noteLavorazione,
							  modificato, tipoSuolo, idTipoMotivoSospensione, flagSospensioneOrig, 
							  flagControlloCampo, geometry)
SELECT 

		t2.id, 
		t2.note, 
		t2.idEleggibilitaRilevata, 
		t2.codiceEleggibilitaRilevata, 
		NULL as idFeature, --t2.idFeature 
		t2.codiceNazionale, 
		t2.foglio, 
		t2.idFeaturePadre, 
		0 AS cessato, --t2.cessato, 
		t2.flagLavorato, 
		t2.flagSospensione, 
		t2.descrizioneSospensione, 
		t2.noteLavorazione, 
		CASE
		  WHEN t2.tipoSuolo = 'LAV' OR t2.tipoSuolo = 'LAV_KO' THEN t2.modificato
		  ELSE 1
		END as modificato, --t2.modificato,
		t2.tipoSuolo, 
		t2.idTipoMotivoSospensione,
		t2.flagSospensioneOrig,
		t2.flagControlloCampo,
		t1.geom as geometry 

  FROM dump as t1
  JOIN suoli_lavorazione as t2 ON t2.OGC_FID = t1.fid
WHERE t1.geom is not null;


--- Remove multipolygons with multiple parts  (follow previous query)
UPDATE suoli_lavorazione
   SET cessato = 1
WHERE ST_NumGeometries(geometry) > 1;


--------------------------------------------------------------------------------------------
--- Dump multipolygons to multipolygons single part
WITH RECURSIVE
  dump(geom, fid, geom_ref, n) AS (
     SELECT NULL, OGC_FID AS fid, geometry AS geom_ref, 0 AS n 
       FROM "suoli_noconduzione_corrotti"
      WHERE ST_NumGeometries(geometry) > 1
		UNION ALL
     SELECT ST_Multi(GeometryN(geom_ref,n+1)), fid, geom_ref, n+1 from dump
	 WHERE n+1 <=  ST_NumGeometries(geom_ref)
  )
INSERT INTO "suoli_noconduzione_corrotti" (id, note, idEleggibilitaRilevata, codiceEleggibilitaRilevata, 
                              idFeature, codiceNazionale, foglio, idFeaturePadre, cessato, 
							  flagLavorato, flagSospensione, descrizioneSospensione, noteLavorazione,
							  modificato, tipoSuolo, flagSospensioneOrig, flagControlloCampo, geometry)
SELECT 

		t2.id, 
		t2.note, 
		t2.idEleggibilitaRilevata, 
		t2.codiceEleggibilitaRilevata, 
		NULL as idFeature, --t2.idFeature 
		t2.codiceNazionale, 
		t2.foglio, 
		t2.idFeaturePadre, 
		0 AS cessato, --t2.cessato, 
		t2.flagLavorato, 
		t2.flagSospensione, 
		t2.descrizioneSospensione, 
		t2.noteLavorazione, 
		t2.modificato, 
		t2.tipoSuolo,
		t2.flagSospensioneOrig,
		t2.flagControlloCampo,
		t1.geom as geometry 

  FROM dump as t1
  JOIN "suoli_noconduzione_corrotti" as t2 ON t2.OGC_FID = t1.fid
WHERE t1.geom is not null;


--- Remove multipolygons with multiple parts (follow previous query)
UPDATE "suoli_noconduzione_corrotti"
   SET cessato = 1
WHERE ST_NumGeometries(geometry) > 1;


--------------------------------------------------------------------------------------------
--- Update flagSospensione field
UPDATE suoli_rilevati 
   SET flagSospensione = 1 
 WHERE flagSospensioneOrig = 'S';
 
UPDATE suoli_lavorazione 
   SET flagSospensione = 1 
 WHERE flagSospensioneOrig = 'S';
 
UPDATE suoli_noconduzione_corrotti 
   SET flagSospensione = 1 
 WHERE flagSospensioneOrig = 'S';
 
UPDATE particelle_catastali 
   SET flagSospensione = 1 
 WHERE flagSospensioneOrig = 'S';
 
UPDATE particelle_catastali_originali 
   SET flagSospensione = 1 
 WHERE flagSospensioneOrig = 'S';

-----------------------------------------------------------------------------------------
-- VIEWS
-----------------------------------------------------------------------------------------

-- create view ElencoFogliAzienda_v with working state
CREATE VIEW IF NOT EXISTS ElencoFogliAzienda_v AS 
SELECT
    t1.*
  , CASE 
      WHEN NOT t1._selected THEN t1._statoLavorazione
	  WHEN t2._statoLavorazioneEdit IS NULL 
	   AND t3.part_totale > 0 THEN 100        /*LAVORATO*/
      ELSE ifnull(t2._statoLavorazioneEdit, 0)
    END AS _statoLavorazioneEdit
  , CASE 
      WHEN NOT t1._selected THEN t1._statoLavorazione
	  WHEN t3.part_totale > 0 
	    AND t3.part_undone > 0 THEN 0        /*NON LAVORATO*/
      ELSE 100                               /*LAVORATO    */
    END AS _statoLavorazionePartEdit
	
  
FROM ElencoFogliAzienda t1
LEFT JOIN (

   -- calculate _statoLavorazione field
   SELECT 
	    codiceNazionale
	  , foglio
	  , CASE
		  WHEN lavorati = 0 THEN 0        /* NON LAVORATO   */
		  WHEN lavorati = 0 AND noFeaturePadre > 0 THEN 50 /* IN LAVORAZIONE: THERE'RE SUOLI WITHOUT PARENT   */
		  WHEN lavorati < totale THEN 50  /* IN LAVORAZIONE */
		  ELSE 100                        /* LAVORATO       */
	    END AS _statoLavorazioneEdit
	   
	FROM (
	
		    -- group on flagLavorato,  flagSospensione, cessato
			SELECT 
			    codiceNazionale
			  , foglio
			  , SUM(
			      CASE 
			        WHEN COALESCE(flagLavorato,0) = 1 OR 
			             COALESCE(flagSospensione,0) = 1 OR 
			             COALESCE(cessato,0) = 1 
			          THEN 1 
				    ELSE 0 
				  END) AS lavorati
				  
			  , SUM(
			      CASE 
			        WHEN COALESCE(numFeaturePadre,0) = 0 AND 
			             COALESCE(cessato,0) != 1
			          THEN 1 
			        ELSE 0 
			      END) AS noFeaturePadre
			  
			  , COUNT(*) AS totale
			  
			FROM (
				    -- query suoli lavorati
				    SELECT 
				          codiceNazionale
				        , foglio
				        , flagLavorato
				        , flagSospensione
				        , cessato
				        , json_array_length(idFeaturePadre) AS numFeaturePadre
		              FROM suoli_lavorazione 
		            WHERE tipoSuolo in ('LAV','LAV_KO','COND_KO') /*('LAV','LAV_KO','COND','COND_KO')*/
		
		            UNION ALL
					
					-- query suoli noconduzione corrotti
		            SELECT 
		                 codiceNazionale
		               , foglio
		               , flagLavorato
		               , flagSospensione
		               , cessato
		               , json_array_length(idFeaturePadre) AS numFeaturePadre
		               
		              FROM suoli_noconduzione_corrotti 
			) t
			GROUP BY codiceNazionale, foglio
		
     ) t
     
) t2 ON t1.codiceNazionale=t2.codiceNazionale AND t1.foglio=t2.foglio
LEFT JOIN (
 
   SELECT
    codiceNazionale
  , foglio
  , count() AS part_totale
  , count(case when _statoLavorazionePart = 0 then 1 else null end) AS part_undone
  FROM ParticelleLavorazioni_v

) t3 ON t1.codiceNazionale=t3.codiceNazionale AND t1.foglio=t3.foglio;


-- create view suoli_rilevati_v with working state
CREATE VIEW IF NOT EXISTS suoli_rilevati_v AS
SELECT
    t1.idFeature,
	--t2.idFeaturePadre,
	t1.tipoSuolo,
	t1.codiceEleggibilitaRilevata, 
	t3.descEleggibilitaRilevata,
	t1.foglio, 
	t1.codiceNazionale,
	CASE
	   WHEN COALESCE(t2.flagSospensione, false) THEN 2    /* SOSPESO     */
	   WHEN COALESCE(t2.flagLavorato, false)  THEN 1   /* LAVORATO    */
	   WHEN COALESCE(t2.cessato, false)  THEN 1   /* LAVORATO    */
	   ELSE 0                                     /* DA LAVORARE */
	END AS _statoLavorazioneSuolo
	
FROM suoli_rilevati t1

LEFT JOIN (

SELECT 
   idFeature, tipoSuolo, flagLavorato, flagSospensione, cessato
FROM suoli_lavorazione
/*WHERE tipoSuolo in ('LAV','LAV_KO','COND','COND_KO')*/  /* WITH SUOLI COND */
WHERE tipoSuolo in ('LAV','LAV_KO','COND_KO')      /* WITHOUT SUOLI COND */ /*23-04-20 By Rita*/

UNION ALL 

SELECT 
   idFeature, tipoSuolo, flagLavorato, flagSospensione, cessato
FROM suoli_noconduzione_corrotti

) t2 ON t1.idFeature = t2.idFeature

LEFT JOIN ClassiEleggibilita t3 ON t1.codiceEleggibilitaRilevata = t3.codiceEleggibilitaRilevata

/*WHERE  t1.tipoSuolo in ('LAV', 'LAV_KO', 'COND_KO', 'KO', 'COND')*/                                                  /* WITH ALL SUOLI COND */
/*WHERE  t1.tipoSuolo in ('LAV','LAV_KO','COND_KO','KO') OR (t1.tipoSuolo = 'COND' AND _statoLavorazioneSuolo != 0)*/  /* WITH ONLY SUOLI COND NOT MODIFIED */ 
WHERE  t1.tipoSuolo in ('LAV','LAV_KO','COND_KO','KO')                                                                 /* WITHOUT SUOLI COND */ /*23-04-20 By Rita*/

/*ORDER BY (t1.tipoSuolo = 'COND' AND _statoLavorazioneSuolo = 0), t1.tipoSuolo;*/ /* WITH ALL SUOLI COND */
ORDER BY t1.tipoSuolo;
       
-- create view ParticelleLavorazioni_v with working state
CREATE VIEW IF NOT EXISTS ParticelleLavorazioni_v AS
SELECT
    t1.*
    
  , CASE
      WHEN t2._statoLavorazionePart IS NULL AND 
	       t1.flagSospensione = 'S' THEN 33         /* SOSPESA LAVORAZIONE (NO FEATURE) */
	  ELSE coalesce(t2._statoLavorazionePart, 0)
    END AS _statoLavorazionePart
    
  , CASE
      WHEN t2._statoLavorazionePart IS NULL THEN t1.flagSospensione
      WHEN t2.flagSospensione = 1 THEN 'S'
      ELSE 'N'
    END AS _flagSospensioneEdit
    
  , CASE
      WHEN t2._statoLavorazionePart IS NULL THEN t1.descrizioneSospensione
      ELSE t2.descrizioneSospensione
    END AS _descrizioneSospensioneEdit
    
  , CASE
      WHEN t2._statoLavorazionePart IS NULL THEN false
      ELSE true
    END AS _has_geometry
    
  , coalesce(t2._count, 1) > 1 AS _duplicated
  
FROM ParticelleLavorazioni t1
LEFT JOIN (
	SELECT *, COUNT(*) OVER (PARTITION BY numeroParticella, subalterno) _count
	FROM (
		SELECT *, rank() OVER win AS _rank, row_number() OVER win AS _row
		FROM (   
		   SELECT
				ltrim(numeroParticella, '0') AS numeroParticella
			  , trim(coalesce(subalterno, '')) subalterno
			  , flagSospensione
			  , descrizioneSospensione
			  , CASE
			      WHEN COALESCE(flagCessato, false) AND 
				       TRIM(COALESCE(idFeature,'')) = '' THEN NULL /* CESSATA, MA SENZA ID(NON PROVENIENTE DA DB REMOTO) */
				  WHEN COALESCE(flagCessato, false)  THEN 1     /* CESSATA     */
				  WHEN COALESCE(flagSospensione, false) THEN 3  /* SOSPESA     */
				  WHEN COALESCE(flagLavorato, false)  THEN 2    /* LAVORATA    */
				  ELSE 0                                        /* DA LAVORARE */
				END AS _statoLavorazionePart
			  , CASE
				  WHEN COALESCE(flagCessato, false)  THEN 1     /* FITTIZIA     */
				  ELSE 0                                        /* NON FITTIZIA */
				END AS _statoFictPart
			  FROM particelle_catastali
			  WHERE flagLavorato = 1 OR flagCessato = 1 OR flagSospensione = 1 
		)
		WINDOW win AS (PARTITION BY numeroParticella, subalterno  ORDER BY numeroParticella, subalterno, _statoFictPart)
	)
	WHERE (_statoFictPart = 1 AND _row = 1) OR (_statoFictPart = 0 AND _rank = 1)
) t2 
ON t2.numeroParticella = ltrim(t1.numeroParticella, '0') AND t2.subalterno = trim(coalesce(t1.subalterno, ''))
ORDER BY numeroParticella, subalterno, _statoLavorazionePart DESC;

-----------------------------------------------------------------------------------------
-- TRIGGERS
-----------------------------------------------------------------------------------------

/*
CREATE TRIGGER IF NOT EXISTS insert_ElencoFogliAzienda_v
    INSTEAD OF INSERT ON ElencoFogliAzienda_v
BEGIN
    -- insert the new record
	INSERT INTO ElencoFogliAzienda(foglio,codiceNazionale,descrizioneComune,sezione,
                                                         numeroParticelle,numeroSuoliLavorazione,numeroSuoliProposti,
                                                         numeroSuoliSospesi,utenteBlocco,isFoglioBloccato,idEventoLavorazione,selected)
    VALUES(NEW.foglio,
	              NEW.codiceNazionale,
				  NEW.descrizioneComune,
				  NEW.sezione,
				  NEW.numeroParticelle,
				  NEW.numeroSuoliLavorazione,
				  NEW.numeroSuoliProposti,
				  NEW.numeroSuoliSospesi,
				  NEW.utenteBlocco,
				  NEW.isFoglioBloccato,
				  NEW.idEventoLavorazione,
				  COALESCE(NEW.selected,0))
				  
				  
   ON CONFLICT(codiceNazionale,sezione,foglio) DO UPDATE SET 
              numeroSuoliLavorazione = NEW.numeroSuoliLavorazione,
              numeroSuoliProposti = NEW.numeroSuoliProposti,
              numeroSuoliSospesi = NEW.numeroSuoliSospesi,
              utenteBlocco = NEW.utenteBlocco,
              isFoglioBloccato = NEW.isFoglioBloccato,
			  selected = COALESCE(NEW.selected,0);
  
END;
*/

--DROP TRIGGER IF EXISTS suoli_proposti_insert;
CREATE TRIGGER IF NOT EXISTS suoli_proposti_insert
    BEFORE INSERT ON suoli_proposti
BEGIN
    SELECT RAISE(ABORT, 'La geometria dei suoli proposti non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS suoli_proposti_update;
CREATE TRIGGER IF NOT EXISTS suoli_proposti_update
    BEFORE UPDATE ON suoli_proposti
BEGIN
    SELECT RAISE(ABORT, 'La geometria dei suoli proposti non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS suoli_proposti_delete;
CREATE TRIGGER IF NOT EXISTS suoli_proposti_delete
    BEFORE DELETE ON suoli_proposti
BEGIN
    SELECT RAISE(ABORT, 'La geometria dei suoli proposti non può essere modificata.');
END;

-----------------------------------------------------------------------------------------

--DROP TRIGGER IF EXISTS suoli_rilevati_insert;
CREATE TRIGGER IF NOT EXISTS suoli_rilevati_insert
    BEFORE INSERT ON suoli_rilevati
BEGIN
    SELECT RAISE(ABORT, 'La geometria dei suoli rilevati non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS suoli_rilevati_update;
CREATE TRIGGER IF NOT EXISTS suoli_rilevati_update
    BEFORE UPDATE ON suoli_rilevati
BEGIN
    SELECT RAISE(ABORT, 'La geometria dei suoli rilevati non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS suoli_rilevati_delete;
CREATE TRIGGER IF NOT EXISTS suoli_rilevati_delete
    BEFORE DELETE ON suoli_rilevati
BEGIN
    SELECT RAISE(ABORT, 'La geometria dei suoli rilevati non può essere modificata.');
END;

-----------------------------------------------------------------------------------------

--DROP TRIGGER IF EXISTS particelle_catastali_insert;
CREATE TRIGGER IF NOT EXISTS particelle_catastali_insert
    BEFORE INSERT ON particelle_catastali
BEGIN
    SELECT
    CASE
	    WHEN (1 != (SELECT idTipoLista FROM ListaLavorazione) )
		THEN RAISE(ABORT, 'La geometria delle particelle catastali non può essere modificata.')
    END;
END;

--DROP TRIGGER IF EXISTS particelle_catastali_update;
CREATE TRIGGER IF NOT EXISTS particelle_catastali_update
    BEFORE UPDATE ON particelle_catastali
BEGIN
    SELECT
    CASE
	    WHEN (1 != (SELECT idTipoLista FROM ListaLavorazione) )
		THEN RAISE(ABORT, 'La geometria delle particelle catastali non può essere modificata.')
    END;
END;

--DROP TRIGGER IF EXISTS particelle_catastali_delete;
CREATE TRIGGER IF NOT EXISTS particelle_catastali_delete
    BEFORE DELETE ON particelle_catastali
BEGIN
    SELECT
    CASE
	    WHEN (1 != (SELECT idTipoLista FROM ListaLavorazione) ) 
	      THEN RAISE(ABORT, 'La geometria delle particelle catastali non può essere modificata.')
		WHEN OLD.flagCessato = 1 
		  THEN RAISE(ABORT, 'La geometria delle particelle catastali non può essere modificata.') 
    END;
	--- update cessato field and terminate delete command silently
	UPDATE "particelle_catastali" SET flagCessato=1 WHERE OGC_FID=old.OGC_FID;
	SELECT RAISE(IGNORE);
END;

-----------------------------------------------------------------------------------------

--DROP TRIGGER IF EXISTS particelle_catastali_originali_insert;
CREATE TRIGGER IF NOT EXISTS particelle_catastali_originali_insert
    BEFORE INSERT ON particelle_catastali_originali
BEGIN
    SELECT RAISE(ABORT, 'La geometria delle particelle catastali non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS particelle_catastali_originali_update;
CREATE TRIGGER IF NOT EXISTS particelle_catastali_originali_update
    BEFORE UPDATE ON particelle_catastali_originali
BEGIN
    SELECT RAISE(ABORT, 'La geometria delle particelle catastali non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS particelle_catastali_originali_delete;
CREATE TRIGGER IF NOT EXISTS particelle_catastali_originali_delete
    BEFORE DELETE ON particelle_catastali_originali
BEGIN
    SELECT RAISE(ABORT, 'La geometria delle particelle catastali non può essere modificata.');
END;

-----------------------------------------------------------------------------------------

--DROP TRIGGER IF EXISTS suoli_noconduzione_insert;
CREATE TRIGGER IF NOT EXISTS suoli_noconduzione_insert
    BEFORE INSERT ON suoli_noconduzione
BEGIN
    SELECT RAISE(ABORT, 'La geometria dei "suoli non in conduzione" non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS suoli_noconduzione_update;
CREATE TRIGGER IF NOT EXISTS suoli_noconduzione_update
    BEFORE UPDATE ON suoli_noconduzione
BEGIN
    SELECT
    CASE
	    WHEN (1 != (SELECT idTipoLista FROM ListaLavorazione) )
			THEN RAISE(ABORT, 'La geometria dei "suoli non in conduzione" non può essere modificata.')
		WHEN (
	     SELECT 
			NEW.OGC_FID != OLD.OGC_FID OR 
			NEW.id != OLD.id OR
			NEW.note != OLD.note OR
			NEW.idEleggibilitaRilevata != OLD.idEleggibilitaRilevata OR
			NEW.codiceEleggibilitaRilevata != OLD.codiceEleggibilitaRilevata OR
			NEW.idFeature != OLD.idFeature OR
			NEW.codiceNazionale != OLD.codiceNazionale OR
			NEW.foglio != OLD.foglio OR
			--NEW.idFeaturePadre != OLD.idFeaturePadre OR
			--NEW.cessato = 0) OR
			NEW.flagLavorato != OLD.flagLavorato OR
			--NEW._flagInvalido != OLD._flagInvalido OR
			NEW.flagSospensione != OLD.flagSospensione OR
			NEW.descrizioneSospensione != OLD.descrizioneSospensione OR
			NEW.noteLavorazione != OLD.noteLavorazione OR
			NEW.modificato != OLD.modificato OR
			NEW.tipoSuolo != OLD.tipoSuolo OR
			NEW.flagControlloCampo != OLD.flagControlloCampo OR
			NEW.geometry != OLD.geometry
	   ) THEN RAISE(ABORT, 'Gli attributi dei "suoli non in conduzione" non possono essere modificati.') 
    END;
END;

--DROP TRIGGER IF EXISTS suoli_noconduzione_delete;
CREATE TRIGGER IF NOT EXISTS suoli_noconduzione_delete
    BEFORE DELETE ON suoli_noconduzione
BEGIN
    SELECT
    CASE
	    WHEN (1 != (SELECT idTipoLista FROM ListaLavorazione) ) 
	      THEN RAISE(ABORT, 'La geometria dei "suoli non in conduzione" non può essere modificata.')
		WHEN OLD.cessato = 1 
		  THEN RAISE(ABORT, 'La geometria dei "suoli non in conduzione" non può essere modificata.') 
    END;
	--- update cessato field and terminate delete command silently
	UPDATE "suoli_noconduzione" SET cessato=1 WHERE OGC_FID=old.OGC_FID;
	SELECT RAISE(IGNORE);
END;

-----------------------------------------------------------------------------------------

/*
--DROP TRIGGER IF EXISTS suoli_noconduzione_corrotti_insert;
CREATE TRIGGER IF NOT EXISTS suoli_noconduzione_corrotti_insert
    BEFORE INSERT ON suoli_noconduzione_corrotti
BEGIN
    SELECT RAISE(ABORT, 'La geometria dei "suoli non in conduzione" non può essere creata.');
END;
*/

--DROP TRIGGER IF EXISTS suoli_noconduzione_corrotti_delete;
CREATE TRIGGER IF NOT EXISTS suoli_noconduzione_corrotti_delete
    BEFORE DELETE ON suoli_noconduzione_corrotti
BEGIN
    SELECT
	CASE
	  WHEN OLD.cessato = 1 THEN RAISE(ABORT, 'La geometria dei suoli cessati non può essere modificata.') 
	  --WHEN OLD.idFeature IS NULL THEN RAISE(ABORT, 'Il campo idFeature deve essere valorizzato per i suoli da rimuovere')
	  --ELSE RAISE(IGNORE)
	END;
	--- update cessato field and terminate delete command silently
	UPDATE "suoli_noconduzione_corrotti" SET cessato=1 WHERE OGC_FID=old.OGC_FID;
	SELECT RAISE(IGNORE);
END;

--DROP TRIGGER IF EXISTS suoli_noconduzione_corrotti_update;
CREATE TRIGGER IF NOT EXISTS suoli_noconduzione_corrotti_update 
 BEFORE UPDATE ON suoli_noconduzione_corrotti
 FOR EACH ROW
BEGIN
    SELECT
    CASE
	  -- can update only geometry field
      WHEN (
	     SELECT 
	        (OLD.idFeature IS NOT NULL) AND
	        (NEW.OGC_FID == OLD.OGC_FID) AND (
			    ---(NEW.OGC_FID != OLD.OGC_FID) OR
				(NEW.id != OLD.id) OR
				(NEW.note != OLD.note) OR
				(NEW.idEleggibilitaRilevata != OLD.idEleggibilitaRilevata) OR
				(NEW.codiceEleggibilitaRilevata != OLD.codiceEleggibilitaRilevata) OR
				(NEW.idFeature != OLD.idFeature) OR
				(NEW.codiceNazionale != OLD.codiceNazionale) OR
				(NEW.foglio != OLD.foglio) OR
				--(NEW.idFeaturePadre != OLD.idFeaturePadre) OR
				--(NEW.cessato = 0) OR
				--(NEW.cessato != OLD.cessato) OR
				--(NEW.flagLavorato != OLD.flagLavorato) OR
				--(NEW._flagInvalido != OLD._flagInvalido) OR
				(NEW.flagSospensione != OLD.flagSospensione) OR
				(NEW.descrizioneSospensione != OLD.descrizioneSospensione) OR
				(NEW.noteLavorazione != OLD.noteLavorazione) OR
				--(NEW.modificato != OLD.modificato) OR
				(NEW.tipoSuolo != OLD.tipoSuolo) OR
				(NEW.flagControlloCampo != OLD.flagControlloCampo)
			)
	   ) THEN RAISE(ABORT, 'Gli attributi dei "suoli non in conduzione" non possono essere modificati.') 
    END;
END;

-----------------------------------------------------------------------------------------

--DROP TRIGGER IF EXISTS suoli_lavorazione_delete;
CREATE TRIGGER IF NOT EXISTS suoli_lavorazione_delete
    BEFORE DELETE ON suoli_lavorazione
BEGIN
	SELECT
	CASE
	  WHEN OLD.cessato = 1 THEN RAISE(ABORT, 'La geometria dei suoli cessati non può essere modificata.') 
	  --WHEN OLD.idFeature IS NULL THEN RAISE(ABORT, 'Il campo idFeature deve essere valorizzato per i suoli da rimuovere')
	  --ELSE RAISE(IGNORE)
	END;
	--- update cessato field and terminate delete command silently
	UPDATE "suoli_lavorazione" SET cessato=1 WHERE OGC_FID=old.OGC_FID;
	SELECT RAISE(IGNORE);
END;

/*
--DROP TRIGGER IF EXISTS suoli_lavorazione_update;
CREATE TRIGGER IF NOT EXISTS suoli_lavorazione_update 
 BEFORE UPDATE ON suoli_lavorazione
 FOR EACH ROW
BEGIN
    SELECT
    CASE
      --WHEN OLD.cessato = 1 THEN RAISE(ABORT, 'La geometria dei suoli cessati non può essere modificata.') 
	  WHEN (0 = (SELECT value FROM agri_settings WHERE key = 'enable_trigger_suoli_bloccati_update') ) THEN 1
      WHEN (SELECT NEW.flagLavBloc = 'B') THEN RAISE(ABORT, 'La geometria dei suoli bloccati non può essere modificata.') 
    END;
END;

--DROP TRIGGER IF EXISTS suoli_bloccati_after_update;
CREATE TRIGGER IF NOT EXISTS suoli_bloccati_after_update
  AFTER UPDATE ON suoli_lavorazione
BEGIN
    UPDATE agri_settings SET value='1' WHERE key = 'enable_trigger_suoli_bloccati_update';
END;
*/

-----------------------------------------------------------------------------------------

--DROP TRIGGER IF EXISTS confine_foglio_insert;
CREATE TRIGGER IF NOT EXISTS confine_foglio_insert
    BEFORE INSERT ON confine_foglio
BEGIN
    SELECT RAISE(ABORT, 'La geometria del confine foglio non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS confine_foglio_update;
CREATE TRIGGER IF NOT EXISTS confine_foglio_update
    BEFORE UPDATE ON confine_foglio
BEGIN
    SELECT RAISE(ABORT, 'La geometria del confine foglio non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS confine_foglio_delete;
CREATE TRIGGER IF NOT EXISTS confine_foglio_delete
    BEFORE DELETE ON confine_foglio
BEGIN
    SELECT RAISE(ABORT, 'La geometria del confine foglio non può essere modificata.');
END;

-----------------------------------------------------------------------------------------

--DROP TRIGGER IF EXISTS foto_appezzamenti_insert;
CREATE TRIGGER IF NOT EXISTS foto_appezzamenti_insert
    BEFORE INSERT ON foto_appezzamenti
BEGIN
    SELECT RAISE(ABORT, 'La geometria non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS foto_appezzamenti_update;
CREATE TRIGGER IF NOT EXISTS foto_appezzamenti_update
    BEFORE UPDATE ON foto_appezzamenti
BEGIN
    SELECT RAISE(ABORT, 'La geometria non può essere modificata.');
END;

--DROP TRIGGER IF EXISTS foto_appezzamenti_delete;
CREATE TRIGGER IF NOT EXISTS foto_appezzamenti_delete
    BEFORE DELETE ON foto_appezzamenti
BEGIN
    SELECT RAISE(ABORT, 'La geometria non può essere modificata.');
END;

-----------------------------------------------------------------------------------------
-- TERMINATE
-----------------------------------------------------------------------------------------

-- clear db
VACUUM;
