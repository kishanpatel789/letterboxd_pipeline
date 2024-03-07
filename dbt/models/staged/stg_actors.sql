SELECT DISTINCT * 
FROM {{ source('raw', 'actors') }}