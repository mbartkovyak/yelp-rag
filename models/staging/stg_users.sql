
    select
        v:user_id::string               as user_id,
        v:name::string                  as name,
        v:review_count::integer         as review_count,
        v:yelping_since::timestamp_ntz  as yelping_since,
        v:useful::integer               as useful_count,
        v:funny::integer                as funny_count,
        v:cool::integer                 as cool_count,
        v:fans::integer                 as fans,
        v:average_stars::float          as average_stars,
        v:elite::string                 as elite_years

from {{ source('yelp', 'user_raw') }}
