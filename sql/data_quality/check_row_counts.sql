-- Data Quality Check
-- Vérifie que les volumes chargés dans BigQuery
-- correspondent aux volumes des fichiers sources ASHRAE.
--
-- Résultats attendus :
-- building_metadata : 1 449
-- weather_train     : 139 773
-- train             : 20 216 100

SELECT
    (SELECT COUNT(*)
     FROM `time-series-data-pipeline.raw_ashrae.building_metadata`)
        AS building_metadata_rows,

    (SELECT COUNT(*)
     FROM `time-series-data-pipeline.raw_ashrae.weather_train`)
        AS weather_train_rows,

    (SELECT COUNT(*)
     FROM `time-series-data-pipeline.raw_ashrae.train`)
        AS train_rows;