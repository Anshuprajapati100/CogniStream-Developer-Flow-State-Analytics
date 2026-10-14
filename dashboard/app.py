from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "reports/flow_cognitive_analysis.csv"

st.set_page_config(
    page_title="CogniStream Analytics",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        return None

    df = pd.read_csv(DATA_FILE)
    df["session_date"] = pd.to_datetime(df["session_date"])
    return df


st.title("CogniStream")
st.subheader("Developer Flow-State & Cognitive Load Analytics")

st.caption(
    "Prototype dashboard using synthetic developer activity data. "
    "Flow indicators are experimental estimates, not validated "
    "psychological measurements."
)

df = load_data()

if df is None:
    st.error(
        "Analysis dataset not found. Run the data collection, "
        "cleaning, analytics and cognitive-load scripts first."
    )
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

developers = sorted(df["developer_id"].unique().tolist())

selected_developers = st.sidebar.multiselect(
    "Select Developers",
    options=developers,
    default=developers
)

min_date = df["session_date"].min().date()
max_date = df["session_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df[
    df["developer_id"].isin(selected_developers)
].copy()

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        filtered_df["session_date"].dt.date.between(
            start_date, end_date
        )
    ]

if filtered_df.empty:
    st.warning("No sessions found for the selected filters.")
    st.stop()

# KPI Cards
st.header("Overview")

total_sessions = len(filtered_df)
total_developers = filtered_df["developer_id"].nunique()
total_coding_hours = filtered_df["coding_time_min"].sum() / 60
average_flow = filtered_df["flow_indicator_score"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sessions", total_sessions)
col2.metric("Developers", total_developers)
col3.metric("Coding Hours", f"{total_coding_hours:.2f}")
col4.metric("Avg. Flow Indicator", f"{average_flow:.2f}/100")

# Flow and load charts
st.header("Flow & Cognitive Load Analysis")

left, right = st.columns(2)

flow_order = ["Low", "Moderate", "High"]
load_order = ["Low", "Moderate", "High"]

flow_counts = (
    filtered_df["flow_indicator_band"]
    .value_counts()
    .reindex(flow_order, fill_value=0)
    .reset_index()
)

flow_counts.columns = ["Flow Indicator", "Sessions"]

fig_flow = px.bar(
    flow_counts,
    x="Flow Indicator",
    y="Sessions",
    color="Flow Indicator",
    title="Flow Indicator Distribution"
)

left.plotly_chart(fig_flow, width="stretch")

load_counts = (
    filtered_df["cognitive_load_band"]
    .value_counts()
    .reindex(load_order, fill_value=0)
    .reset_index()
)

load_counts.columns = ["Cognitive Load", "Sessions"]

fig_load = px.pie(
    load_counts,
    names="Cognitive Load",
    values="Sessions",
    title="Simulated Cognitive Load Distribution",
    hole=0.45
)

right.plotly_chart(fig_load, width="stretch")

# Daily activity
st.header("Daily Coding Activity")

daily_activity = (
    filtered_df.groupby("session_date", as_index=False)
    .agg(
        coding_minutes=("coding_time_min", "sum"),
        sessions=("session_id", "count")
    )
)

daily_activity["coding_hours"] = (
    daily_activity["coding_minutes"] / 60
)

fig_daily = px.line(
    daily_activity,
    x="session_date",
    y="coding_hours",
    markers=True,
    title="Daily Coding Hours",
    labels={
        "session_date": "Date",
        "coding_hours": "Coding Hours"
    }
)

st.plotly_chart(fig_daily, width="stretch")

# Developer comparison
st.header("Developer Comparison")

developer_summary = (
    filtered_df.groupby("developer_id", as_index=False)
    .agg(
        total_sessions=("session_id", "count"),
        avg_flow_score=("flow_indicator_score", "mean"),
        avg_load_rating=("cognitive_load_rating", "mean"),
        interruptions=("interruptions", "sum")
    )
)

fig_developers = px.bar(
    developer_summary,
    x="developer_id",
    y="avg_flow_score",
    color="developer_id",
    title="Average Flow Indicator by Developer",
    labels={
        "developer_id": "Developer",
        "avg_flow_score": "Average Flow Indicator"
    }
)

st.plotly_chart(fig_developers, width="stretch")

# Detailed data
st.header("Developer Session Data")

st.dataframe(
    filtered_df,
    width="stretch",
    hide_index=True
)

# Download
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv_data,
    file_name="cognistream_filtered_sessions.csv",
    mime="text/csv"
)

st.divider()

st.caption(
    "CogniStream | Data Analytics Internship Project | "
    "Synthetic demonstration dataset"
)
