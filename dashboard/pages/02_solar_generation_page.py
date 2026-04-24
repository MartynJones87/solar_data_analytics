import altair as alt
import streamlit as st

from solar_data.generation.hourly_generation_by_day import hourly_solar_generation_by_day
from solar_data.generation.hourly_generation_by_month import hourly_solar_generation_by_month
from solar_data.utils import load_data

df = load_data()

st.subheader("Hourly Solar Generation by Month")
# daily_col, monthly_col = st.columns(2)


monthly_hourly_solar_generation = hourly_solar_generation_by_month(df)
daily_hourly_solar_generation = hourly_solar_generation_by_day(df)
# st.write(hourly_solar_generation)

# Generate an altair chart heatmap with month on the x axis, hour on the y axis, and the color being the solar generation for that month and hour.

with st.container(horizontal=True):
    st.altair_chart(
        alt.Chart(daily_hourly_solar_generation)
        .mark_rect()
        .encode(
            x=alt.X("day:O", title="Day"),
            y=alt.Y("hour:O", title="Hour of Day"),
            color=alt.Color("solar:Q", title="Solar Generation (kWh)", scale=alt.Scale(scheme="viridis")),
        )
        .properties(title="Hourly Solar Generation by Day"),
        width="stretch",
    )

    st.altair_chart(
        alt.Chart(monthly_hourly_solar_generation)
        .mark_rect()
        .encode(
            x=alt.X("month:O", title="Month"),
            y=alt.Y("hour:O", title="Hour of Day"),
            color=alt.Color("solar:Q", title="Solar Generation (kWh)", scale=alt.Scale(scheme="viridis")),
        )
        .properties(title="Hourly Solar Generation by Month"),
        width="stretch",
    )
