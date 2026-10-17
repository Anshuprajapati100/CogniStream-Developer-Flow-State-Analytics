from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.insights import generate_insights


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "reports/flow_cognitive_analysis.csv"

st.set_page_config(
    page_title="CogniStream | Developer Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        return None

    df = pd.read_csv(DATA_FILE)
    df["session_date"] = pd.to_datetime(df["session_date"])

    return df


df = load_data()

st.title("CogniStream")
st.markdown("#### Developer Flow-State & Cognitive Load Analytics")

st.caption(
    "Interactive analytics prototype using synthetic developer activity. "
    "Flow indicators are experimental, not validated psychological measurements."
)

if df is None:
    st.error(
        "Analysis dataset not found. "
        "Run data collection, cleaning, analytics and cognitive load scripts."
    )
    st.stop()


# SIDEBAR

st.sidebar.title("CogniStream")
st.sidebar.header("Filters")

developers = sorted(df["developer_id"].unique().tolist())

selected_developers = st.sidebar.multiselect(
    "Developers",
    developers,
    default=developers,
)

min_date = df["session_date"].min().date()
max_date = df["session_date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

filtered = df[
    df["developer_id"].isin(selected_developers)
].copy()

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered = filtered[
        filtered["session_date"].dt.date.between(
            start_date, end_date
        )
    ]

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


# KPI METRICS

total_sessions = len(filtered)
total_developers = filtered["developer_id"].nunique()
coding_hours = filtered["coding_time_min"].sum() / 60
avg_flow = filtered["flow_indicator_score"].mean()

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Developer Sessions", f"{total_sessions}")
c2.metric("Developers", f"{total_developers}")
c3.metric("Coding Hours", f"{coding_hours:.2f}")
c4.metric("Average Flow Indicator", f"{avg_flow:.2f}/100")

st.divider()


# TABS

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Overview",
        "Developer Analytics",
        "Flow & Cognitive Load",
        "Session Explorer",
        "Smart Insights",
    ]
)


# OVERVIEW

with tab1:

    st.subheader("Daily Developer Activity")

    daily = (
        filtered.groupby("session_date", as_index=False)
        .agg(
            coding_minutes=("coding_time_min", "sum"),
            sessions=("session_id", "count"),
        )
    )

    daily["coding_hours"] = daily["coding_minutes"] / 60

    fig = px.line(
        daily,
        x="session_date",
        y="coding_hours",
        markers=True,
        title="Daily Coding Hours",
    )

    st.plotly_chart(fig, width="stretch")

    left, right = st.columns(2)

    fig_interrupt = px.histogram(
        filtered,
        x="interruptions",
        title="Interruptions per Session",
    )

    left.plotly_chart(fig_interrupt, width="stretch")

    fig_switch = px.histogram(
        filtered,
        x="context_switches",
        title="Context Switches per Session",
    )

    right.plotly_chart(fig_switch, width="stretch")


# DEVELOPER ANALYTICS

with tab2:

    st.subheader("Developer Activity Comparison")

    developer_stats = (
        filtered.groupby("developer_id", as_index=False)
        .agg(
            sessions=("session_id", "count"),
            coding_minutes=("coding_time_min", "sum"),
            avg_flow=("flow_indicator_score", "mean"),
            avg_focus=("focus_rating", "mean"),
            avg_load=("cognitive_load_rating", "mean"),
            interruptions=("interruptions", "sum"),
            context_switches=("context_switches", "sum"),
        )
    )

    developer_stats["coding_hours"] = (
        developer_stats["coding_minutes"] / 60
    )

    st.dataframe(
        developer_stats.round(2),
        width="stretch",
        hide_index=True,
    )

    fig = px.bar(
        developer_stats,
        x="developer_id",
        y="coding_hours",
        color="developer_id",
        title="Total Coding Hours by Developer",
    )

    st.plotly_chart(fig, width="stretch")

    fig2 = px.bar(
        developer_stats,
        x="developer_id",
        y="avg_flow",
        color="developer_id",
        title="Average Flow Indicator by Developer",
    )

    st.plotly_chart(fig2, width="stretch")


# FLOW AND COGNITIVE LOAD

with tab3:

    st.subheader("Flow Indicator Analysis")

    left, right = st.columns(2)

    flow_counts = (
        filtered["flow_indicator_band"]
        .value_counts()
        .reindex(["Low", "Moderate", "High"], fill_value=0)
        .reset_index()
    )

    flow_counts.columns = ["Flow Indicator", "Sessions"]

    fig_flow = px.bar(
        flow_counts,
        x="Flow Indicator",
        y="Sessions",
        color="Flow Indicator",
        title="Flow Indicator Distribution",
    )

    left.plotly_chart(fig_flow, width="stretch")

    load_counts = (
        filtered["cognitive_load_band"]
        .value_counts()
        .reindex(["Low", "Moderate", "High"], fill_value=0)
        .reset_index()
    )

    load_counts.columns = ["Cognitive Load", "Sessions"]

    fig_load = px.pie(
        load_counts,
        names="Cognitive Load",
        values="Sessions",
        hole=0.45,
        title="Simulated Cognitive Load Distribution",
    )

    right.plotly_chart(fig_load, width="stretch")

    st.subheader("Activity and Focus Relationships")

    fig_scatter = px.scatter(
        filtered,
        x="interruptions_per_hour",
        y="flow_indicator_score",
        color="developer_id",
        hover_data=["session_id"],
        title="Interruption Rate vs Flow Indicator",
    )

    st.plotly_chart(fig_scatter, width="stretch")

    st.info(
        "The flow score includes interruption frequency in its formula. "
        "Therefore, this chart shows a partly built-in relationship, "
        "not independent evidence that interruptions cause lower flow."
    )


# SESSION EXPLORER

with tab4:

    st.subheader("Developer Session Explorer")

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Sessions",
        data=csv,
        file_name="cognistream_sessions.csv",
        mime="text/csv",
    )

    st.caption(f"Displaying {len(filtered)} sessions.")



# SMART INSIGHTS

with tab5:
    st.subheader("Smart Developer Activity Insights")

    st.caption(
        "Automatically generated descriptive insights from the "
        "selected synthetic developer sessions."
    )

    insights = generate_insights(filtered)

    for number, insight in enumerate(insights, start=1):
        st.markdown(f"**{number}.** {insight}")

    st.divider()

    st.subheader("Focus vs Cognitive Load")

    fig_focus = px.scatter(
        filtered,
        x="cognitive_load_rating",
        y="focus_rating",
        color="developer_id",
        hover_data=["session_id"],
        title="Simulated Focus and Cognitive Load Ratings",
        labels={
            "focus_rating": "Focus Rating (1–5)",
            "cognitive_load_rating": "Cognitive Load Rating (1–5)"
        },
    )

    st.plotly_chart(fig_focus, width="stretch")

    st.info(
        "These are simulated self-report ratings. "
        "The chart illustrates a relationship in synthetic data "
        "and does not demonstrate a real-world causal effect."
    )


st.divider()

st.caption(
    "CogniStream | Infotact Data Analytics Internship | "
    "Synthetic Dataset | Experimental Flow Indicators"
)
