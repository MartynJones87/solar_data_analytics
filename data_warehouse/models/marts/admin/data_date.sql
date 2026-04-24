WITH ddt AS (
    SELECT MAX(DATE_TRUNC('day', ddt.reading_datetime)) AS data_date
    FROM
        {{ ref('int_generation_solar_cleaned') }} AS ddt
)

SELECT ddt.data_date
FROM ddt
