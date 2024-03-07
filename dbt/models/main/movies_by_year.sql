SELECT date
    ,count(1) cnt_movies
    ,avg(minute) avg_length_min
FROM {{ ref('stg_movies') }}
GROUP BY 1
ORDER BY 1