SELECT date, count(1) cnt_movies
FROM {{ ref('stg_movies') }}
GROUP BY 1
ORDER BY 1