-- date, theme, cnt_movies, total_length_min, cnt_movies_w_length

SELECT 
    m.date 
    ,t.theme 
    ,count(1) cnt_movies
    ,sum(m.minute) total_length_min
    ,count(m.minute) cnt_movies_w_length
FROM {{ ref('stg_movies') }} m 
LEFT JOIN {{ ref('stg_theme_singles') }} t 
    ON m.id = t.id
WHERE m.date <= 2024
GROUP BY 
    m.date 
    ,t.theme