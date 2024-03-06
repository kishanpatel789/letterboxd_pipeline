WITH movies_w_count AS (
    SELECT *
    ,COUNT(1) OVER (PARTITION BY id) AS id_count
    FROM {{ source('raw', 'movies') }}
)

SELECT {{ dbt_utils.star(from=source('raw', 'movies'), except=["id_count"]) }}
FROM movies_w_count
WHERE date IS NOT NULL  -- remove movies without release years
    AND id_count = 1    -- remove movies with re-used id values