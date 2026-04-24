-- Calculate target payback date based on current savings rate and total cost
-- of the system, which is £10,200. We can calculate the number of days to 
-- payback as (total cost of system) / (total savings / number of days in 
-- dataset), then add that number of days to the last date in the dataset to
-- get the target payback date.

WITH payback_day AS (
    SELECT
        DATE_TRUNC('day', svg.reading_datetime) AS reading_date,
        SUM(svg.total_saving) AS total_saving
    FROM
        {{ ref('int_finance_cost_savings') }} AS svg
    GROUP BY
        DATE_TRUNC('day', svg.reading_datetime)
    ORDER BY
        DATE_TRUNC('day', svg.reading_datetime) ASC
),

payback_base AS (
    SELECT
        pbd.reading_date,
        pbd.total_saving,
        10200 AS installation_cost,
        SUM(pbd.total_saving)
            OVER (ORDER BY pbd.reading_date)
            AS cumulative_saving,
        ROW_NUMBER() OVER (ORDER BY pbd.reading_date) AS day_number
    FROM
        payback_day AS pbd
    ORDER BY
        pbd.reading_date ASC
),

payback AS (
    SELECT
        pbb.reading_date,
        pbb.total_saving,
        pbb.cumulative_saving,
        pbb.day_number,
        pbb.installation_cost,
        pbb.cumulative_saving / pbb.day_number AS average_daily_saving,
        (pbb.cumulative_saving / pbb.installation_cost)
        * 100 AS payback_percentage,
        CAST(
            (
                pbb.installation_cost / (pbb.cumulative_saving / pbb.day_number)
            ) AS INTEGER
        ) AS days_to_payback
    FROM payback_base AS pbb
)

SELECT
    payback.reading_date,
    payback.total_saving,
    payback.cumulative_saving,
    payback.day_number,
    payback.installation_cost,
    payback.payback_percentage,
    payback.days_to_payback,
    payback.average_daily_saving,
    payback.reading_date
    + INTERVAL (payback.days_to_payback) DAY AS forecast_payback_date
FROM
    payback AS payback
ORDER BY
    payback.reading_date ASC

