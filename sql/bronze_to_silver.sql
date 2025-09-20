-- 1. Filtrar usuarios con más de 100 horas de visualización
IF OBJECT_ID('silver_users', 'U') IS NOT NULL
    DROP TABLE silver_users;

SELECT DISTINCT
    user_id,
    age,
    country,
    registration_date AS signup_date,
    CAST(total_watch_time_hours AS FLOAT) AS total_watch_time_hours
INTO silver_users
FROM bronze.users
WHERE TRY_CAST(total_watch_time_hours AS FLOAT) > 100
  AND user_id IS NOT NULL;


-- 2. Filtrar sesiones válidas (solo usuarios activos)
IF OBJECT_ID('silver_viewing_sessions', 'U') IS NOT NULL
    DROP TABLE silver_viewing_sessions;

SELECT DISTINCT
    vs.session_id,
    vs.user_id,
    vs.content_id,
    vs.watch_date AS start_time,
    vs.watch_date AS end_time,  -- Usando la misma fecha para ambos campos
    CAST(vs.watch_duration_minutes AS FLOAT) AS duration_minutes
INTO silver_viewing_sessions
FROM bronze.viewing_sessions vs
JOIN silver_users su ON vs.user_id = su.user_id
WHERE TRY_CAST(vs.watch_duration_minutes AS FLOAT) > 0
  AND vs.session_id IS NOT NULL
  AND vs.content_id IS NOT NULL;


-- 3. Filtrar contenido visto por usuarios activos
IF OBJECT_ID('silver_content', 'U') IS NOT NULL
    DROP TABLE silver_content;

SELECT DISTINCT
    c.content_id,
    c.title,
    c.genre,  
    c.duration_minutes,
    COALESCE(c.release_year, 2020) AS release_year,  -- Default para series sin release_year
    CASE 
        WHEN c.rating < 0 THEN 0
        WHEN c.rating > 5 THEN 5
        ELSE c.rating
    END AS rating,
    c.views_count,
    c.production_budget,
    c.content_type,
    c.seasons,
    c.total_episodes
INTO silver_content
FROM bronze.content c
JOIN (
    SELECT DISTINCT content_id 
    FROM silver_viewing_sessions
) sv ON c.content_id = sv.content_id
WHERE c.duration_minutes > 0;