-- ===============================================
-- TRANSFORMACIÓN SILVER → GOLD (CORREGIDO)
-- Script optimizado para ejecutar en una sola conexión
-- ===============================================

-- 1. GOLD_USER_ANALYTICS: Métricas completas por usuario
IF OBJECT_ID('gold_user_analytics', 'U') IS NOT NULL
    DROP TABLE gold_user_analytics;

SELECT 
    u.user_id,
    u.age,
    u.country,
    u.signup_date,
    u.total_watch_time_hours,
    COUNT(vs.session_id) as total_sessions,
    AVG(vs.duration_minutes) as avg_session_duration,
    SUM(vs.duration_minutes) as total_minutes_watched,
    COUNT(DISTINCT vs.content_id) as unique_content_watched,
    CASE 
        WHEN u.total_watch_time_hours >= 500 THEN 'Power User'
        WHEN u.total_watch_time_hours >= 300 THEN 'Heavy User'
        WHEN u.total_watch_time_hours >= 150 THEN 'Regular User'
        ELSE 'Light User'
    END as user_segment,
    DATEDIFF(DAY, u.signup_date, GETDATE()) as days_since_signup
INTO gold_user_analytics
FROM silver_users u
LEFT JOIN silver_viewing_sessions vs ON u.user_id = vs.user_id
GROUP BY u.user_id, u.age, u.country, u.signup_date, u.total_watch_time_hours;

-- 2. GOLD_CONTENT_PERFORMANCE: Análisis de rendimiento de contenido
IF OBJECT_ID('gold_content_performance', 'U') IS NOT NULL
    DROP TABLE gold_content_performance;

SELECT 
    c.content_id,
    c.title,
    c.genre,
    c.content_type,
    c.duration_minutes,
    COALESCE(c.release_year, 2020) AS release_year,
    c.rating,
    c.production_budget,
    COUNT(vs.session_id) as total_views,
    COUNT(DISTINCT vs.user_id) as unique_viewers,
    ISNULL(AVG(vs.duration_minutes), 0) as avg_watch_time,
    CASE 
        WHEN c.duration_minutes > 0 THEN 
            ROUND(ISNULL(AVG(vs.duration_minutes), 0) * 100.0 / c.duration_minutes, 2)
        ELSE 0 
    END as avg_completion_rate,
    CASE 
        WHEN c.production_budget > 0 THEN 
            ROUND(COUNT(vs.session_id) * 1.0 / (c.production_budget / 1000000.0), 2)
        ELSE 0 
    END as views_per_million_budget,
    CASE 
        WHEN c.rating >= 4.5 THEN 'Excellent'
        WHEN c.rating >= 4.0 THEN 'Very Good'
        WHEN c.rating >= 3.5 THEN 'Good'
        WHEN c.rating >= 3.0 THEN 'Average'
        ELSE 'Below Average'
    END as rating_category
INTO gold_content_performance
FROM bronze.content c
LEFT JOIN silver_viewing_sessions vs ON c.content_id = vs.content_id
GROUP BY c.content_id, c.title, c.genre, c.content_type, c.duration_minutes, 
         c.release_year, c.rating, c.production_budget;

-- 3. GOLD_COUNTRY_INSIGHTS: Análisis por país
IF OBJECT_ID('gold_country_insights', 'U') IS NOT NULL
    DROP TABLE gold_country_insights;

SELECT 
    u.country,
    COUNT(DISTINCT u.user_id) as total_users,
    AVG(u.total_watch_time_hours) as avg_watch_hours_per_user,
    AVG(CAST(u.age AS FLOAT)) as avg_user_age,
    COUNT(vs.session_id) as total_sessions,
    ISNULL(AVG(vs.duration_minutes), 0) as avg_session_duration,
    COUNT(DISTINCT vs.content_id) as unique_content_consumed
INTO gold_country_insights
FROM silver_users u
LEFT JOIN silver_viewing_sessions vs ON u.user_id = vs.user_id
GROUP BY u.country;

-- 4. GOLD_GENRE_ANALYTICS: Rendimiento por género
IF OBJECT_ID('gold_genre_analytics', 'U') IS NOT NULL
    DROP TABLE gold_genre_analytics;

SELECT 
    c.genre,
    COUNT(DISTINCT c.content_id) as total_content_items,
    COUNT(vs.session_id) as total_views,
    COUNT(DISTINCT vs.user_id) as unique_viewers,
    AVG(CAST(c.production_budget AS BIGINT)) as avg_production_budget,
    SUM(CAST(c.production_budget AS BIGINT)) as total_investment,
    AVG(c.rating) as avg_genre_rating,
    AVG(c.duration_minutes) as avg_content_duration,
    ISNULL(AVG(vs.duration_minutes), 0) as avg_watch_time
INTO gold_genre_analytics
FROM bronze.content c
LEFT JOIN silver_viewing_sessions vs ON c.content_id = vs.content_id
GROUP BY c.genre;

-- 5. GOLD_EXECUTIVE_SUMMARY: KPIs ejecutivos
IF OBJECT_ID('gold_executive_summary', 'U') IS NOT NULL
    DROP TABLE gold_executive_summary;

SELECT 
    'Platform Overview' as metric_category,
    (SELECT COUNT(*) FROM silver_users) as active_users_100h_plus,
    (SELECT COUNT(*) FROM bronze.content) as total_content_catalog,
    (SELECT COUNT(*) FROM silver_viewing_sessions) as total_viewing_sessions,
    (SELECT ROUND(AVG(total_watch_time_hours), 2) FROM silver_users) as avg_user_engagement_hours,
    (SELECT COUNT(DISTINCT content_id) FROM silver_viewing_sessions) as content_with_views
INTO gold_executive_summary;

-- 6. GOLD_USER_SEGMENTATION: Segmentación de usuarios  
IF OBJECT_ID('gold_user_segmentation', 'U') IS NOT NULL
    DROP TABLE gold_user_segmentation;

SELECT 
    user_segment,
    COUNT(*) as users_in_segment,
    AVG(total_watch_time_hours) as avg_watch_hours,
    AVG(total_sessions) as avg_sessions_per_user,
    AVG(unique_content_watched) as avg_unique_content,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM gold_user_analytics), 2) as segment_percentage
INTO gold_user_segmentation
FROM gold_user_analytics
GROUP BY user_segment;