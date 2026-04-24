SELECT
    date,
    hour,
    grid,
    solar,
    battery,
    home,
    CURRENT_TIMESTAMP AS ingested_at
FROM
    {{ source('raw_data', 'raw_solar_data') }}
