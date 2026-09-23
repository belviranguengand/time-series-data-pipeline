-- ============================================================
-- DATA QUALITY CHECK : VALEURS NULL
-- ============================================================
-- Objectif :
-- Vérifier la complétude des colonnes des tables RAW ASHRAE.
--
-- Important :
-- Un NULL n'est pas automatiquement une erreur.
-- Cette requête sert à identifier et quantifier les valeurs
-- manquantes avant leur traitement éventuel dans dbt.
-- ============================================================


-- 1. BUILDING_METADATA
SELECT
    COUNT(*) AS total_rows,
    COUNTIF(site_id IS NULL) AS null_site_id,
    COUNTIF(building_id IS NULL) AS null_building_id,
    COUNTIF(primary_use IS NULL) AS null_primary_use,
    COUNTIF(square_feet IS NULL) AS null_square_feet,
    COUNTIF(year_built IS NULL) AS null_year_built,
    COUNTIF(floor_count IS NULL) AS null_floor_count
FROM `time-series-data-pipeline.raw_ashrae.building_metadata`;


-- 2. TRAIN
SELECT
    COUNT(*) AS total_rows,
    COUNTIF(building_id IS NULL) AS null_building_id,
    COUNTIF(meter IS NULL) AS null_meter,
    COUNTIF(timestamp IS NULL) AS null_timestamp,
    COUNTIF(meter_reading IS NULL) AS null_meter_reading
FROM `time-series-data-pipeline.raw_ashrae.train`;


-- 3. WEATHER_TRAIN
SELECT
    COUNT(*) AS total_rows,
    COUNTIF(site_id IS NULL) AS null_site_id,
    COUNTIF(timestamp IS NULL) AS null_timestamp,
    COUNTIF(air_temperature IS NULL) AS null_air_temperature,
    COUNTIF(cloud_coverage IS NULL) AS null_cloud_coverage,
    COUNTIF(dew_temperature IS NULL) AS null_dew_temperature,
    COUNTIF(precip_depth_1_hr IS NULL) AS null_precip_depth_1_hr,
    COUNTIF(sea_level_pressure IS NULL) AS null_sea_level_pressure,
    COUNTIF(wind_direction IS NULL) AS null_wind_direction,
    COUNTIF(wind_speed IS NULL) AS null_wind_speed
FROM `time-series-data-pipeline.raw_ashrae.weather_train`;