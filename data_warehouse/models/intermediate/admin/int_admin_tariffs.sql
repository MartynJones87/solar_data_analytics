WITH base_tariffs AS (
    SELECT
        CAST(start_date AS DATE) AS start_date,
        CAST(end_date AS DATE) AS end_date,
        CAST(off_peak_start_hour AS TIME) AS off_peak_start_hour,
        CAST(off_peak_end_hour AS TIME) AS off_peak_end_hour,
        CAST(off_peak_rate AS DOUBLE) AS off_peak_rate,
        CAST(peak_rate AS DOUBLE) AS peak_rate,
        CAST(export_rate AS DOUBLE) AS export_rate
    FROM
        {{ ref('stg_seeded_tariffs') }}
)

SELECT
    tar.start_date,
    tar.end_date,
    tar.off_peak_start_hour,
    tar.off_peak_end_hour,
    tar.off_peak_rate,
    tar.peak_rate,
    tar.export_rate
FROM base_tariffs AS tar
