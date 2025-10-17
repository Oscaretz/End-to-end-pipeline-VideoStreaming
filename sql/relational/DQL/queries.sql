-- 1. Top 5 most-watched content by country
WITH ranked_content AS (
    SELECT
        u.country,
        v.content_id,
        SUM(v.watch_duration_minutes) AS total_watch_minutes,
        ROW_NUMBER() OVER (PARTITION BY u.country ORDER BY SUM(v.watch_duration_minutes) DESC) AS rn
    FROM viewing_sessions v
    JOIN users u ON v.user_id = u.user_id
    GROUP BY u.country, v.content_id
)
SELECT country, content_id, total_watch_minutes
FROM ranked_content
WHERE rn <= 5
ORDER BY country, total_watch_minutes DESC;

-- 2. User retention analysis by subscription type
-- Retention: users who have more than 1 session
SELECT
    u.subscription_type,
    COUNT(DISTINCT u.user_id) AS total_users,
    COUNT(DISTINCT CASE WHEN v.session_id IS NOT NULL THEN u.user_id END) AS retained_users,
    ROUND(
        COUNT(DISTINCT CASE WHEN v.session_id IS NOT NULL THEN u.user_id END) / COUNT(DISTINCT u.user_id) * 100, 2
    ) AS retention_percentage
FROM users u
LEFT JOIN viewing_sessions v ON u.user_id = v.user_id
GROUP BY u.subscription_type;

-- 3. Revenue analysis by content genre
-- Assuming 'price_per_hour' column exists in viewing_sessions
SELECT
    v.genre,
    ROUND(SUM(v.watch_duration_minutes / 60 * v.price_per_hour), 2) AS total_revenue
FROM viewing_sessions v
GROUP BY v.genre
ORDER BY total_revenue DESC;

-- 4. Seasonal viewing patterns
SELECT
    MONTH(v.watch_date) AS month,
    AVG(v.watch_duration_minutes) AS avg_watch_minutes,
    COUNT(v.session_id) AS total_sessions
FROM viewing_sessions v
GROUP BY MONTH(v.watch_date)
ORDER BY month;

-- 5. Device preference correlation with completion rates
SELECT
    device_type,
    ROUND(AVG(completion_percentage), 2) AS avg_completion_percentage,
    COUNT(session_id) AS total_sessions
FROM viewing_sessions
GROUP BY device_type
ORDER BY avg_completion_percentage DESC;
