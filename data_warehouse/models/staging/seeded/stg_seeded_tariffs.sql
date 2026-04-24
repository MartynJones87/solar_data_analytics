WITH source AS (

    {#-
    Normally we would select from the table here, but we are using seeds to load
    our data in this project
    #}
    SELECT * FROM {{ ref('raw_tariffs') }}

)

SELECT
    src.start_date,
    src.end_date,
    src.off_peak_start_hour,
    src.off_peak_end_hour,
    src.off_peak_rate,
    src.peak_rate,
    src.export_rate
FROM source AS src
