-- group themes into fewer categories and pick one random theme group per movie
WITH themes_grouped AS (
    SELECT DISTINCT 
        t.id
        ,COALESCE(tg.theme_group, 'Other') AS theme_group
    FROM {{ ref('stg_themes') }} t
    LEFT JOIN {{ ref('theme_groups') }} tg 
        ON t.theme = tg.theme
),

themegroups_ranked AS (
    SELECT * 
        ,RANDOM() AS rand_num
        ,ROW_NUMBER() OVER (PARTITION BY id ORDER BY rand_num) AS rn
    FROM themes_grouped
)

SELECT id 
    ,theme_group AS theme
FROM themegroups_ranked
WHERE rn = 1