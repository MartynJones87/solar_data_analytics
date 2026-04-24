WITH base_solar AS (
    SELECT
        ingested_at,
        CAST(CONCAT(date, ' ', hour) AS TIMESTAMP) AS reading_datetime,
        CAST(grid AS DOUBLE) AS grid,
        CAST(solar AS DOUBLE) AS solar,
        CAST(battery AS DOUBLE) AS battery,
        CAST(home AS DOUBLE) AS home
    FROM
        {{ ref('stg_scraper_solar') }}
),

exclusions AS (
    SELECT
        start_datetime,
        end_datetime
    FROM
        {{ ref('int_admin_exclusions') }}
),

tariffs AS (
    SELECT
        start_date,
        end_date,
        off_peak_rate,
        off_peak_start_hour,
        off_peak_end_hour,
        peak_rate,
        export_rate
    FROM
        {{ ref('int_admin_tariffs') }}
)

SELECT
    sol.reading_datetime,
    sol.grid,
    sol.solar,
    sol.battery,
    sol.home,
    sol.ingested_at,
    tar.off_peak_rate,
    tar.peak_rate,
    tar.export_rate,
    COALESCE(
        DATE_PART('hour', sol.reading_datetime)
        >= DATE_PART('hour', tar.off_peak_start_hour)
        AND DATE_PART('hour', sol.reading_datetime)
        <= DATE_PART('hour', tar.off_peak_end_hour),
        false
    ) AS is_off_peak
FROM
    base_solar AS sol
ANTI JOIN exclusions AS exc
    ON sol.reading_datetime >= exc.start_datetime
        AND sol.reading_datetime <= exc.end_datetime
INNER JOIN tariffs AS tar
    ON DATE_TRUNC('day', sol.reading_datetime) >= tar.start_date
        AND DATE_TRUNC('day', sol.reading_datetime) <= tar.end_date