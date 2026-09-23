-- ============================================================
-- DATA QUALITY CHECK : VALIDITÉ MÉTIER - TRAIN
-- ============================================================
-- Objectif :
-- Vérifier que les valeurs de la table train respectent
-- les règles métier attendues.
--
-- Règles :
-- 1. meter doit appartenir à {0, 1, 2, 3}
-- 2. meter_reading ne doit pas être négatif
-- 3. building_id ne doit pas être négatif
--
-- Résultat attendu :
-- 0 anomalie pour chaque règle.
-- ============================================================

SELECT
    COUNTIF(meter NOT IN (0, 1, 2, 3)) AS invalid_meter,
    COUNTIF(meter_reading < 0) AS negative_meter_reading,
    COUNTIF(building_id < 0) AS negative_building_id
FROM `time-series-data-pipeline.raw_ashrae.train`;