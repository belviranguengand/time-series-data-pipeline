with source as (

    select *
    from {{ source('raw_ashrae', 'weather_train') }}

),

renamed as (

    select
        site_id,
        timestamp,
        air_temperature,
        cloud_coverage,
        dew_temperature,
        precip_depth_1_hr,
        sea_level_pressure,
        wind_direction,
        wind_speed
    from source

)

select *
from renamed
