select
    building_id,
    meter,
    timestamp,
    count(*) as occurrences
from {{ ref('mart_energy_consumption') }}
group by
    building_id,
    meter,
    timestamp
having count(*) > 1