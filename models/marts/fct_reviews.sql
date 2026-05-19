select r.business_id,
        r.review_id,
       r.stars,
       r.text,
       r.review_date,
       r.useful_count,
       r.funny_count,
       r.cool_count,
       b.name,
       city,
       state,
       postal_code,
       review_count, 
       split(categories, ',') as categories_list
from {{ ref('stg_reviews') }} r
left join {{ ref('stg_businesses') }} b using (business_id)