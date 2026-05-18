
    select
        v:review_id::string             as review_id,
        v:user_id::string               as user_id,
        v:business_id::string           as business_id,
        v:stars::integer                as stars,
        v:useful::integer               as useful_count,
        v:funny::integer                as funny_count,
        v:cool::integer                 as cool_count,
        v:text::string                  as text,
        v:date::timestamp_ntz           as review_date

from {{ source('yelp', 'review_raw') }}
