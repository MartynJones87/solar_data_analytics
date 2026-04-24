WITH base_exclusions AS (
    SELECT
        exclusion_reason,
        CAST(CONCAT(start_date, ' ', start_time) AS TIMESTAMP)
            AS start_datetime,
        CAST(CONCAT(end_date, ' ', end_time) AS TIMESTAMP) AS end_datetime
    FROM
        {{ ref('stg_seeded_exclusions') }}
)

SELECT
    exc.exclusion_reason,
    exc.start_datetime,
    exc.end_datetime
FROM base_exclusions AS exc
