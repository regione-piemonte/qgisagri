-----------------------------------------------------------------------------------------
-- TRIGGERS
-----------------------------------------------------------------------------------------

-- suoli_proposti
DROP TRIGGER IF EXISTS suoli_proposti_insert;
DROP TRIGGER IF EXISTS suoli_proposti_update;
DROP TRIGGER IF EXISTS suoli_proposti_delete;

-- suoli_rilevati
DROP TRIGGER IF EXISTS suoli_rilevati_insert;
DROP TRIGGER IF EXISTS suoli_rilevati_update;
DROP TRIGGER IF EXISTS suoli_rilevati_delete;

-- particelle_catastali
DROP TRIGGER IF EXISTS particelle_catastali_insert;
DROP TRIGGER IF EXISTS particelle_catastali_update;
DROP TRIGGER IF EXISTS particelle_catastali_delete;

-- particelle_catastali_originali
DROP TRIGGER IF EXISTS particelle_catastali_originali_insert;
DROP TRIGGER IF EXISTS particelle_catastali_originali_update;
DROP TRIGGER IF EXISTS particelle_catastali_originali_delete;

-- suoli_noconduzione
DROP TRIGGER IF EXISTS suoli_noconduzione_insert;
DROP TRIGGER IF EXISTS suoli_noconduzione_update;
DROP TRIGGER IF EXISTS suoli_noconduzione_delete;

-- suoli_noconduzione_corrotti
--DROP TRIGGER IF NOT EXISTS suoli_noconduzione_corrotti_insert;
DROP TRIGGER IF EXISTS suoli_noconduzione_corrotti_delete;
DROP TRIGGER IF EXISTS suoli_noconduzione_corrotti_update; 

-- suoli_lavorazione
DROP TRIGGER IF EXISTS suoli_lavorazione_delete;
/*
DROP TRIGGER IF EXISTS suoli_lavorazione_update;
DROP TRIGGER IF EXISTS suoli_bloccati_after_update;
*/

-- confine_foglio
DROP TRIGGER IF EXISTS confine_foglio_insert;
DROP TRIGGER IF EXISTS confine_foglio_update;
DROP TRIGGER IF EXISTS confine_foglio_delete;

-- foto_appezzamenti
DROP TRIGGER IF EXISTS foto_appezzamenti_insert;
DROP TRIGGER IF EXISTS foto_appezzamenti_update;
DROP TRIGGER IF EXISTS foto_appezzamenti_delete;

-----------------------------------------------------------------------------------------
-- TABLES
-----------------------------------------------------------------------------------------

-- ElencoFogliAzienda : 
--UPDATE ElencoFogliAzienda SET _statoLavorazione = {_statoLavorazione} WHERE _selected = 1; 
UPDATE ElencoFogliAzienda SET _selected = 0;

-- suoli_proposti
DELETE FROM suoli_proposti;
SELECT InvalidateLayerStatistics("suoli_proposti");
SELECT UpdateLayerStatistics("suoli_proposti");

-- suoli_rilevati
DELETE FROM suoli_rilevati;
SELECT InvalidateLayerStatistics("suoli_rilevati");
SELECT UpdateLayerStatistics("suoli_rilevati");

-- particelle_catastali
DELETE FROM particelle_catastali;
SELECT InvalidateLayerStatistics("particelle_catastali");
SELECT UpdateLayerStatistics("particelle_catastali");

-- particelle_catastali_originali
DELETE FROM particelle_catastali_originali;
SELECT InvalidateLayerStatistics("particelle_catastali_originali");
SELECT UpdateLayerStatistics("particelle_catastali_originali");

-- suoli_noconduzione
DELETE FROM suoli_noconduzione;
SELECT InvalidateLayerStatistics("suoli_noconduzione");
SELECT UpdateLayerStatistics("suoli_noconduzione");


-- suoli_noconduzione_corrotti
DELETE FROM suoli_noconduzione_corrotti;
SELECT InvalidateLayerStatistics("suoli_noconduzione_corrotti");
SELECT UpdateLayerStatistics("suoli_noconduzione_corrotti");

-- suoli_lavorazione
DELETE FROM suoli_lavorazione;
SELECT InvalidateLayerStatistics("suoli_lavorazione");
SELECT UpdateLayerStatistics("suoli_lavorazione");

-- confine_foglio
DELETE FROM confine_foglio;
SELECT InvalidateLayerStatistics("confine_foglio");
SELECT UpdateLayerStatistics("confine_foglio");

-- suoli punti
DELETE FROM suoli_punti;
SELECT InvalidateLayerStatistics("suoli_punti");
SELECT UpdateLayerStatistics("suoli_punti");


-- suoli linee
DELETE FROM suoli_linee;
SELECT InvalidateLayerStatistics("suoli_linee");
SELECT UpdateLayerStatistics("suoli_linee");

-- foto appezzamenti
DELETE FROM foto_appezzamenti;
SELECT InvalidateLayerStatistics("foto_appezzamenti");
SELECT UpdateLayerStatistics("foto_appezzamenti");


-----------------------------------------------------------------------------------------
-- TERMINATE
-----------------------------------------------------------------------------------------

-- clear db
VACUUM;
