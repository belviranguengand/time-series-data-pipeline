{{
    config(
        materialized='table',
        partition_by={
            "field": "date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=["site_id", "meter"]
    )
}}

with energy as (

    select *
    from {{ ref('mart_energy_consumption') }}

),

daily_consumption as (

    select
        site_id,
        date(timestamp) as date,
        meter,

        sum(meter_reading) as total_meter_reading,
        avg(meter_reading) as avg_meter_reading,
        count(*) as reading_count,
        count(distinct building_id) as building_count

    from energy

    group by
        site_id,
        date(timestamp),
        meter

)

select *
from daily_consumption