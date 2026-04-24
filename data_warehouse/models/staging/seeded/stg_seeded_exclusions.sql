WITH source AS (

    {#-
    Normally we would select from the table here, but we are using seeds to load
    our data in this project
    #}
    SELECT * FROM {{ ref('raw_exclusions') }}

)

SELECT
    start_date,
    start_time,
    end_date,
    end_time,
    exclusion_reason
FROM source
