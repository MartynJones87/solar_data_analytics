import streamlit as st
from dashboard.utils.database import get_daily_savings

st.set_page_config(layout="wide")

df = get_daily_savings()
# Debug source dataframe
# st.dataframe(df)

st.subheader("Daily Cost Savings")
day_cost_savings_df = df  # day_cost_savings(df)
st.dataframe(day_cost_savings_df, width="stretch")
