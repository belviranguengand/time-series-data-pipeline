with source as (

    select *
    from {{ source('raw_ashrae', 'train') }}

),

renamed as (

    select
        building_id,
        meter,
        timestamp,
        meter_reading
    from source

)

select *
from renamed