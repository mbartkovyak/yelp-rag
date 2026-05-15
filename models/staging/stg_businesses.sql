
    select
        v:business_id::string      as business_id,
        v:name::string             as name,
        v:address::string          as address,
        v:city::string             as city,
        v:state::string            as state,
        v:postal_code::string      as postal_code,
        v:latitude::float          as latitude,
        v:longitude::float         as longitude,
        v:stars::float             as stars,
        v:review_count::integer    as review_count,
        v:is_open::integer         as is_open,
        v:categories::string       as categories

from {{ source('yelp', 'business_raw') }}
