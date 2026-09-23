select
    building_id,
    meter,
    timestamp,
    count(*) as occurrences
from {{ ref('stg_train') }}
group by
    building_id,
    meter,
    timestamp
having count(*) > 1