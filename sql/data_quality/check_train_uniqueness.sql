-- Data Quality Check
-- Vérifie l'unicité de la clé métier de la table train.
-- Clé métier : building_id + meter + timestamp
-- Résultat attendu : 0 ligne.

SELECT
    building_id,
    meter,
    timestamp,
    COUNT(*) AS occurrences
FROM `time-series-data-pipeline.raw_ashrae.train`
GROUP BY building_id, meter, timestamp
HAVING COUNT(*) > 1;