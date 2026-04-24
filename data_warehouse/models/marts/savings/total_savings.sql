WITH savings AS (
    SELECT
        SUM(svg.grid) AS grid,
        SUM(svg.solar) AS solar,
        SUM(svg.battery) AS battery,
        SUM(svg.home) AS home,
        SUM(svg.kw_saved) AS kw_saved,
        SUM(svg.kw_exported) AS kw_exported,
        SUM(svg.saving) AS saving,
        SUM(svg.export_income) AS export_income,
        SUM(svg.total_saving) AS total_saving
    FROM
        {{ ref('int_finance_cost_savings') }} AS svg
)

SELECT
    svg.grid,
    svg.solar,
    svg.battery,
    svg.home,
    svg.kw_saved,
    svg.kw_exported,
    svg.saving,
    svg.export_income,
    svg.total_saving
FROM savings AS svg
