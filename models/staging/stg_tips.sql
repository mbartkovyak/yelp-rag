
    select
        v:user_id::string               as user_id,
        v:business_id::string           as business_id,
        v:text::string                  as text,
        v:date::timestamp_ntz           as tip_date,
        v:compliment_count::integer     as compliment_count

from {{ source('yelp', 'tip_raw') }}
