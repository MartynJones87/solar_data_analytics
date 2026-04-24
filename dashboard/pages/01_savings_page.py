import streamlit as st
from dashboard.utils.database import (
    get_daily_savings,
    get_data_date,
    get_monthly_savings,
    get_payback_forecast,
    get_payback_forecast_development,
    get_total_savings,
)

day_cost_savings_df = get_daily_savings()
total_cost_savings_df = get_total_savings()
payback_forecast_df = get_payback_forecast()

data_date = get_data_date()

st.subheader("Total Savings")
st.metric(
    "Data Date",
    f"{data_date.strftime('%Y-%m-%d')}",
)
col1, col2, col3 = st.columns(3)
col1.metric("Saving", f"£{total_cost_savings_df['saving'][0]:.2f}", None)
col2.metric("Export Income", f"£{total_cost_savings_df['export_income'][0]:.2f}", None)
col3.metric("Total Saving", f"£{total_cost_savings_df['total_saving'][0]:.2f}", None)

st.subheader("Payback Forecast")

pb_col1, pb_col2, pb_col3 = st.columns(3)
pb_col1.metric("% Payback Achieved", f"{(payback_forecast_df['payback_percentage'][0]):.2f}%", None)
pb_col2.metric("Target Payback Date", payback_forecast_df["forecast_payback_date"][0].strftime("%Y-%m-%d"), None)
pb_col3.metric("Estimated Daily Savings", f"£{payback_forecast_df['average_daily_saving'][0]:.2f}", None)

st.subheader("Daily Cost Savings")

st.bar_chart(
    day_cost_savings_df,
    y=[
        "saving",
        "export_income",
    ],
    stack=True,
    x="reading_date",
    y_label="Cost Savings (£)",
    x_label="Date",
)

st.subheader("Monthly Cost Savings")
monthly_savings = get_monthly_savings()
st.dataframe(
    monthly_savings,
    column_config={
        "reading_month": st.column_config.DateColumn(
            "Month",
            format="MMMM YYYY",
        ),
        "saving": st.column_config.NumberColumn(
            "Solar Saving (in GBP)",
            help="The saving made by using solar power in GBP",
            format="£ %.2f",
        ),
        "export_income": st.column_config.NumberColumn(
            "Export Income (in GBP)",
            help="The income made from exporting excess solar power in GBP",
            format="£ %.2f",
        ),
        "total_saving": st.column_config.NumberColumn(
            "Total Saving (in GBP)",
            help="The total saving made by using the battery and solar power in GBP",
            format="£ %.2f",
        ),
    },
)

st.subheader("Daily Cost Savings")
daily_savings = get_daily_savings()
st.dataframe(
    daily_savings,
    column_config={
        "reading_date": st.column_config.DateColumn(
            "Date",
            format="YYYY-MM-DD",
        ),
        "saving": st.column_config.NumberColumn(
            "Solar Saving (in GBP)",
            help="The saving made by using solar power in GBP",
            format="£ %.2f",
        ),
        "export_income": st.column_config.NumberColumn(
            "Export Income (in GBP)",
            help="The income made from exporting excess solar power in GBP",
            format="£ %.2f",
        ),
        "total_saving": st.column_config.NumberColumn(
            "Total Saving (in GBP)",
            help="The total saving made by using the battery and solar power in GBP",
            format="£ %.2f",
        ),
    },
)

payback_development_df = get_payback_forecast_development()
st.subheader("Payback Forecast Development")
st.line_chart(
    payback_development_df,
    x="reading_date",
    y="forecast_payback_date",
    y_label="Forecast Payback Date",
    x_label="Date",
)
