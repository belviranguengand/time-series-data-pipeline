-- ============================================================
-- DATA QUALITY CHECK : GAPS TEMPORELS - WEATHER_TRAIN
-- ============================================================
-- Objectif :
-- Vérifier la complétude temporelle des données météo
-- pour chacun des 16 sites.
--
-- Période : année 2016
-- 2016 est une année bissextile :
-- 366 jours × 24 heures = 8 784 heures attendues par site.
--
-- Un gap temporel correspond à une heure attendue
-- pour laquelle aucune ligne n'existe.
--
-- Résultat observé :
-- 16 sites analysés
-- 14 sites avec au moins un gap
-- 2 sites complets (0 et 8)
-- 771 heures manquantes au total
-- ============================================================

SELECT
    site_id,
    COUNT(DISTINCT timestamp) AS heures_presentes,
    8784 - COUNT(DISTINCT timestamp) AS heures_manquantes
FROM `time-series-data-pipeline.raw_ashrae.weather_train`
GROUP BY site_id
ORDER BY site_id;