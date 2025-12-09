import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------
# Page config
# ----------------------
st.set_page_config(
    page_title="FEMA Disaster Relief Dashboard",
    layout="wide"
)

# ----------------------
# Load data
# ----------------------
@st.cache_data
def load_data():
    return pd.read_csv("fema_final.csv")

# Try to load data and show error on screen if it fails
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Make a nicer label for TSA eligibility
df["tsaEligibleLabel"] = df["tsaEligible"].map({1: "Eligible", 0: "Not eligible"})

# ----------------------
# Title / intro
# ----------------------
st.title("FEMA Disaster Relief Dashboard")
st.write("Author: Your Name Here")  # change to your name(s)

st.markdown(
    """
    This dashboard explores FEMA Individual Assistance housing data, focusing on 
    **repair amounts** and **Transitional Shelter Assistance (TSA) eligibility** 
    across several disaster-impacted states.
    """
)

# ----------------------
# Sidebar filters
# ----------------------
st.sidebar.header("Filters")

states = sorted(df["damagedStateAbbreviation"].dropna().unique())
selected_states = st.sidebar.multiselect(
    "Select state(s):",
    options=states,
    default=states  # show all by default
)

res_types = sorted(df["residenceType"].dropna().unique())
selected_res_types = st.sidebar.multiselect(
    "Select residence type(s):",
    options=res_types,
    default=res_types
)

tsa_filter = st.sidebar.multiselect(
    "TSA eligibility:",
    options=["Eligible", "Not eligible"],
    default=["Eligible", "Not eligible"]
)

# Apply filters
filtered_df = df[
    df["damagedStateAbbreviation"].isin(selected_states)
    & df["residenceType"].isin(selected_res_types)
    & df["tsaEligibleLabel"].isin(tsa_filter)
]

st.subheader("Filtered Data Preview")
st.write(filtered_df.head())

st.write(
    f"Current sample size after filters: **{len(filtered_df):,}** applicants."
)

# ----------------------
# Histogram of repairAmount
# ----------------------
st.subheader("Histogram of Repair Amount")

fig_hist = px.histogram(
    filtered_df,
    x="repairAmount",
    nbins=40,
    title="Distribution of Repair Amounts",
    labels={"repairAmount": "Repair Amount (USD)", "count": "Number of Applicants"}
)

st.plotly_chart(fig_hist, use_container_width=True)

st.markdown(
    """
    *Insight:* The histogram shows how repair amounts are distributed for the 
    selected group. In general, most households cluster at lower repair amounts, 
    with a long right tail representing a smaller number of very high-cost cases.
    """
)

# ----------------------
# Boxplot of repairAmount by TSA eligibility
# ----------------------
st.subheader("Repair Amount by TSA Eligibility")

fig_box = px.box(
    filtered_df,
    x="tsaEligibleLabel",
    y="repairAmount",
    title="Repair Amount by TSA Eligibility",
    labels={
        "tsaEligibleLabel": "TSA Eligibility",
        "repairAmount": "Repair Amount (USD)"
    }
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown(
    """
    *Insight:* TSA-eligible households tend to have **higher repair amounts** than 
    non-eligible households, which matches the statistical results from the 
    inferential analysis section. This suggests TSA is being targeted toward 
    households with more severe housing damage.
    """
)

# ----------------------
# Summary stats
# ----------------------
st.subheader("Summary Statistics (Current Filters)")

summary = (
    filtered_df
    .groupby("tsaEligibleLabel")["repairAmount"]
    .agg(["count", "mean", "median"])
    .round(2)
)

st.write(summary)

