import streamlit as st

# Setup the shared variables for the analysis.
PEAK_UNIT_RATE = 0.289
OFF_PEAK_UNIT_RATE = 0.079
EXPORT_RATE = 0.151

st.set_page_config(layout="wide")


# Load the dataset and cache it for use across all pages.
# @st.cache_data()
# def get_data() -> pd.DataFrame:
#     db_conn = connect_to_duckdb()
#     df = get_monthly_savings(db_conn)
#     return df


pg = st.navigation(
    [
        st.Page(
            "dashboard/pages/01_savings_page.py",
            title="Savings",
        ),
        st.Page(
            "dashboard/pages/02_solar_generation_page.py",
            title="Generation",
        ),
        st.Page(
            "dashboard/pages/03_debug_page.py",
            title="Debug",
        ),
    ]
)
pg.run()
