SELECT
    DATE_TRUNC('day', gsc.reading_datetime) AS reading_day,
    DATE_PART('hour', gsc.reading_datetime) AS reading_hour,
    AVG(gsc.solar) AS average_solar_generation,
    MAX(gsc.solar) AS maximum_solar_generation,
    MIN(gsc.solar) AS minimum_solar_generation
FROM
    {{ ref('int_generation_solar_cleaned') }} AS gsc
GROUP BY
    DATE_TRUNC('day', gsc.reading_datetime),
    DATE_PART('hour', gsc.reading_datetime)
