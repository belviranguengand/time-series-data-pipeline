with source as (

    select *
    from {{ source('raw_ashrae', 'building_metadata') }}

),

renamed as (

    select
        site_id,
        building_id,
        primary_use,
        square_feet,
        year_built,
        floor_count
    from source

)

select *
from renamed