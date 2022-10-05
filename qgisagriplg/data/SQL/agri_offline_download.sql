-----------------------------------------------------------------------------------------
-- TABLES
-----------------------------------------------------------------------------------------

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