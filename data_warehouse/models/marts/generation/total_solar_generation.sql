SELECT
    SUM(solar) AS total_solar_generation,
    SUM(solar) / COUNT(*) AS average_daily_solar_generation
FROM
    {{ ref('int_generation_solar_cleaned') }}
