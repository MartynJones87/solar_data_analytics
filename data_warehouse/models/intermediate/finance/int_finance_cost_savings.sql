-- Selects raw data from the cleaned solar table
WITH solar_base AS (
    SELECT
        reading_datetime,
        grid,
        solar,
        battery,
        home,
        off_peak_rate,
        peak_rate,
        export_rate,
        is_off_peak
    FROM
        {{ ref('int_generation_solar_cleaned') }}
),

-- Calculates energy savings (kW) from solar/battery usage and grid exports
kw_savings AS (
    SELECT
        sol.reading_datetime,
        sol.grid,
        sol.solar,
        sol.battery,
        sol.home,
        sol.off_peak_rate,
        sol.peak_rate,
        sol.export_rate,
        sol.is_off_peak,

        -- kw_saved: Energy offset from grid during peak hours
        -- If grid > 0 (importing), calculate home usage minus grid import
        -- If grid <= 0 (not importing), all home usage is from solar/battery
        CASE
            WHEN sol.is_off_peak = false
                THEN CASE
                        WHEN sol.grid > 0
                            THEN sol.home - sol.grid
                        ELSE sol.home
                    END
            ELSE 0
        END AS kw_saved,

        -- kw_exported: Excess energy sent back to grid
        -- When grid < 0, convert negative value to positive export amount
        CASE
            WHEN sol.grid < 0
                THEN -sol.grid
            ELSE 0
        END AS kw_exported
    FROM solar_base AS sol
),

-- Purpose: Calculates financial values ($) from energy savings and exports
savings AS (
    SELECT
        kws.reading_datetime,
        kws.grid,
        kws.solar,
        kws.battery,
        kws.home,
        kws.off_peak_rate,
        kws.peak_rate,
        kws.export_rate,
        kws.is_off_peak,
        kws.kw_saved,
        kws.kw_exported,

        -- saving: Money saved by using solar/battery instead
        -- of grid during peak hours
        kws.kw_saved * kws.peak_rate AS saving,

        -- export_income: Revenue earned from exporting excess solar to grid
        kws.kw_exported * kws.export_rate AS export_income,

        -- battery_charge_cost: Cost to charge battery during off-peak hours
        -- Only applies when charging (battery > 0) during off-peak
        CASE
            WHEN kws.is_off_peak = true AND kws.battery > 0
                THEN (-1 * kws.battery) * kws.off_peak_rate
            ELSE 0
        END AS battery_charge_cost
    FROM
        kw_savings AS kws
)

-- Final SELECT
-- Combines all savings calculations into final output
SELECT
    svg.reading_datetime,
    svg.grid,
    svg.solar,
    svg.battery,
    svg.home,
    svg.off_peak_rate,
    svg.peak_rate,
    svg.export_rate,
    svg.is_off_peak,
    svg.kw_saved,
    svg.kw_exported,

    -- saving: Net savings (solar savings minus battery charging cost)
    svg.export_income,

    -- export_income: Revenue from grid exports
    svg.saving + svg.battery_charge_cost AS saving,

    -- Total benefit = savings + export income - battery charging cost
    (svg.saving + svg.export_income + svg.battery_charge_cost) AS total_saving
FROM
    savings AS svg
