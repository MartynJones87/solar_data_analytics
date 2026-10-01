import altair as alt

import streamlit as st
from dashboard.utils.database import (
    get_average_solar_generation_by_day_hour,
    get_average_solar_generation_by_month_hour,
)

st.subheader("Solar Generation")
# daily_col, monthly_col = st.columns(2)


monthly_hourly_solar_generation = get_average_solar_generation_by_month_hour()
daily_hourly_solar_generation = get_average_solar_generation_by_day_hour()
# st.write(hourly_solar_generation)

# Generate an altair chart heatmap with month on the x axis, hour on the y axis, and the color being the solar generation for that month and hour.

# with st.container(horizontal=False):
st.altair_chart(
    alt.Chart(daily_hourly_solar_generation)
    .mark_rect()
    .encode(
        x=alt.X(
            "yearmonthdate(reading_day):O",
            title="Day",
            axis=alt.Axis(format="%Y-%m-%d", labelAngle=-90),
        ),
        y=alt.Y("reading_hour:O", title="Hour of Day"),
        color=alt.Color(
            "average_solar_generation:Q", title="Solar Generation (kWh)", scale=alt.Scale(scheme="viridis")
        ),
    )
    .properties(title="Hourly Solar Generation by Day"),
    width="stretch",
)

st.altair_chart(
    alt.Chart(monthly_hourly_solar_generation)
    .mark_rect()
    .encode(
        x=alt.X(
            "yearmonth(reading_month):O",
            title="Month",
            axis=alt.Axis(format="%Y-%m", labelAngle=-90),
        ),
        y=alt.Y("reading_hour:O", title="Hour of Day"),
        color=alt.Color(
            "average_solar_generation:Q", title="Solar Generation (kWh)", scale=alt.Scale(scheme="viridis")
        ),
    )
    .properties(title="Hourly Solar Generation by Month"),
    width="stretch",
)
