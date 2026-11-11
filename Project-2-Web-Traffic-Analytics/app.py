import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Web Traffic Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------- LOAD DATASET ----------------

@st.cache_data
def load_data():
    df = pd.read_csv("web_traffic_analytics_v2.csv")
    df["Date"] = pd.to_datetime(df["Date"])

    for col in ["StartedRegistration", "Registered", "Bounced"]:
        df[col] = df[col].astype(str).str.strip().str.title()

    return df

df = load_data()

# ---------------- DASHBOARD HEADER ----------------

st.title("📊 Web Traffic Analytics Dashboard")

st.markdown(
    "Analyze website traffic, visitor behaviour, "
    "registration performance and conversion trends."
)

st.divider()

# ---------------- SIDEBAR FILTERS ----------------

st.sidebar.header("🔍 Dashboard Filters")

sources = st.sidebar.multiselect(
    "Select Traffic Source",
    options=sorted(df["Source"].dropna().unique()),
    default=sorted(df["Source"].dropna().unique())
)

devices = st.sidebar.multiselect(
    "Select Device",
    options=sorted(df["DeviceCategory"].dropna().unique()),
    default=sorted(df["DeviceCategory"].dropna().unique())
)

filtered_df = df[
    (df["Source"].isin(sources)) &
    (df["DeviceCategory"].isin(devices))
].copy()

# ---------------- KPI CALCULATIONS ----------------

total_sessions = len(filtered_df)

total_registrations = (
    filtered_df["Registered"] == "Yes"
).sum()

total_bounces = (
    filtered_df["Bounced"] == "Yes"
).sum()

registration_rate = (
    total_registrations / total_sessions * 100
    if total_sessions > 0 else 0
)

bounce_rate = (
    total_bounces / total_sessions * 100
    if total_sessions > 0 else 0
)

avg_duration = (
    filtered_df["SessionDurationSec"].mean()
    if total_sessions > 0 else 0
)

# ---------------- KPI CARDS ----------------

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sessions", f"{total_sessions:,}")

col2.metric(
    "Total Registrations",
    f"{total_registrations:,}"
)

col3.metric(
    "Bounce Rate",
    f"{bounce_rate:.2f}%"
)

col4.metric(
    "Registration Rate",
    f"{registration_rate:.2f}%"
)

st.metric(
    "Average Session Duration",
    f"{avg_duration:.2f} seconds"
)

st.divider()

# ---------------- TRAFFIC SOURCE ANALYSIS ----------------

st.subheader("🌐 Traffic Source Analysis")

if total_sessions > 0:

    source_data = (
        filtered_df.groupby("Source")
        .size()
        .reset_index(name="Sessions")
        .sort_values("Sessions", ascending=False)
    )

    fig1 = px.bar(
        source_data,
        x="Source",
        y="Sessions",
        color="Source",
        title="Sessions by Traffic Source",
        text="Sessions"
    )

    st.plotly_chart(fig1, use_container_width=True)

else:
    st.info("No data available for selected filters.")

# ---------------- DEVICE ANALYSIS ----------------

st.subheader("📱 Device Category Analysis")

if total_sessions > 0:

    device_data = (
        filtered_df.groupby("DeviceCategory")
        .size()
        .reset_index(name="Sessions")
    )

    fig2 = px.pie(
        device_data,
        names="DeviceCategory",
        values="Sessions",
        title="Visitors by Device",
        hole=0.4
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------- MONTHLY TRAFFIC ----------------

st.subheader("📅 Monthly Traffic Trends")

if total_sessions > 0:

    filtered_df["Month"] = (
        filtered_df["Date"].dt.to_period("M").astype(str)
    )

    monthly_data = (
        filtered_df.groupby("Month")
        .size()
        .reset_index(name="Sessions")
    )

    fig3 = px.line(
        monthly_data,
        x="Month",
        y="Sessions",
        markers=True,
        title="Monthly Website Sessions"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------- REGISTRATION FUNNEL ----------------

st.subheader("🎯 Registration Conversion Funnel")

if total_sessions > 0:

    started = (
        filtered_df["StartedRegistration"] == "Yes"
    ).sum()

    completed = (
        filtered_df["Registered"] == "Yes"
    ).sum()

    funnel_data = pd.DataFrame({
        "Stage": [
            "Total Sessions",
            "Registration Started",
            "Registration Completed"
        ],
        "Users": [
            total_sessions,
            started,
            completed
        ]
    })

    fig4 = px.funnel(
        funnel_data,
        x="Users",
        y="Stage",
        title="Website Registration Funnel"
    )

    st.plotly_chart(fig4, use_container_width=True)

# ---------------- LANDING PAGE ANALYSIS ----------------

st.subheader("📄 Landing Page Performance")

if total_sessions > 0:

    landing_data = (
        filtered_df.groupby("LandingPage")
        .agg(
            Total_Sessions=("SessionID", "count"),
            Registrations=("Registered",
                           lambda x: (x == "Yes").sum())
        )
        .reset_index()
    )

    landing_data["Conversion_Rate"] = (
        landing_data["Registrations"] /
        landing_data["Total_Sessions"] * 100
    ).round(2)

    st.dataframe(
        landing_data.sort_values(
            "Total_Sessions",
            ascending=False
        ),
        use_container_width=True
    )

# ---------------- RAW DATA ----------------

with st.expander("📂 View Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    "### Web Traffic Analytics Project"
)

st.caption(
    "Developed using Python, Pandas, Streamlit and Plotly."
)