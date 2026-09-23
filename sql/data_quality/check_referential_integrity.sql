-- ============================================================
-- DATA QUALITY CHECK : INTÉGRITÉ RÉFÉRENTIELLE
-- ============================================================
-- Objectif :
-- Vérifier que les références entre les tables RAW sont valides.
--
-- Relations contrôlées :
-- train.building_id
--        -> building_metadata.building_id
--
-- building_metadata.site_id
--        -> weather_train.site_id
--
-- Résultat attendu :
-- 0 référence orpheline pour chaque contrôle.
-- ============================================================


-- 1. TRAIN -> BUILDING_METADATA
-- Vérifie que chaque bâtiment présent dans train
-- existe dans building_metadata.

SELECT
    COUNT(DISTINCT t.building_id) AS orphan_buildings
FROM `time-series-data-pipeline.raw_ashrae.train` AS t

LEFT JOIN `time-series-data-pipeline.raw_ashrae.building_metadata` AS b
    ON t.building_id = b.building_id

WHERE b.building_id IS NULL;


-- 2. BUILDING_METADATA -> WEATHER_TRAIN
-- Vérifie que chaque site contenant des bâtiments
-- possède des données météorologiques.

SELECT
    COUNT(DISTINCT b.site_id) AS orphan_sites
FROM `time-series-data-pipeline.raw_ashrae.building_metadata` AS b

LEFT JOIN `time-series-data-pipeline.raw_ashrae.weather_train` AS w
    ON b.site_id = w.site_id

WHERE w.site_id IS NULL;