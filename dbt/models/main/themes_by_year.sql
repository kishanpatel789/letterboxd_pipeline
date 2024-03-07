SELECT m.date
    ,t.theme 
    ,count(1) num_movies 
FROM staged.stg_movies m 
INNER JOIN staged.stg_themes t
    ON m.id = t.id 
GROUP BY 1, 2
ORDER BY 1, 2