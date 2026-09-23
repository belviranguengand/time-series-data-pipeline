{{
    config(
        materialized='table',
        partition_by={
            "field": "timestamp",
            "data_type": "timestamp",
            "granularity": "day"
        },
        cluster_by=["site_id", "building_id", "meter"]
    )
}}

with energy as (

    select *
    from {{ ref('stg_train') }}

),

buildings as (

    select *
    from {{ ref('stg_building_metadata') }}

),

weather as (

    select *
    from {{ ref('stg_weather') }}

),

energy_with_buildings as (

    select
        e.building_id,
        b.site_id,
        e.meter,
        e.timestamp,
        e.meter_reading,
        b.primary_use,
        b.square_feet,
        b.year_built,
        b.floor_count
    from energy e
    left join buildings b
        on e.building_id = b.building_id

),

final as (

    select
        e.building_id,
        e.site_id,
        e.meter,
        e.timestamp,
        e.meter_reading,
        e.primary_use,
        e.square_feet,
        e.year_built,
        e.floor_count,
        w.air_temperature,
        w.cloud_coverage,
        w.dew_temperature,
        w.precip_depth_1_hr,
        w.sea_level_pressure,
        w.wind_direction,
        w.wind_speed
    from energy_with_buildings e
    left join weather w
        on e.site_id = w.site_id
        and e.timestamp = w.timestamp

)

select *
from final