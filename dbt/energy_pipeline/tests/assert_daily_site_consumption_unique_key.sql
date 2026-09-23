select
    site_id,
    date,
    meter,
    count(*) as occurrences
from {{ ref('mart_daily_site_consumption') }}
group by
    site_id,
    date,
    meter
having count(*) > 1
