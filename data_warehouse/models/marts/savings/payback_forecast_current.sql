WITH payback_forecast AS (
    SELECT
        ddt.data_date,
        pfd.payback_percentage,
        pfd.day_number,
        pfd.days_to_payback,
        pfd.average_daily_saving,
        ddt.data_date
        + INTERVAL (pfd.days_to_payback) DAY AS forecast_payback_date
    FROM
        {{ ref('payback_forecast_development') }} AS pfd
    INNER JOIN
        {{ ref('data_date') }} AS ddt
        ON pfd.reading_date = ddt.data_date
    ORDER BY
        pfd.reading_date ASC
)

SELECT
    pbf.data_date,
    pbf.payback_percentage,
    pbf.day_number,
    pbf.days_to_payback,
    pbf.average_daily_saving,
    pbf.forecast_payback_date
FROM payback_forecast AS pbf
