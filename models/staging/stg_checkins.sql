
    select
        v:business_id::string           as business_id,
        v:date::string                  as checkin_dates_raw

from {{ source('yelp', 'checkin_raw') }}
