select business_id,
       name,
       address,
       city,
       state,
       postal_code,
       latitude,
       longitude,
       stars,
       review_count,
       is_open,
       categories,
       checkin_dates_raw,
       split(categories, ',') as categories_list,
       case when categories like '%Restaurants%' then 1 else 0 end as is_restaurant
from {{ ref('stg_businesses') }}
left join {{ ref('stg_checkins') }} using (business_id)