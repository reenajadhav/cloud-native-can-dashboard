import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path

# -----------------------------------------------------
# Page Configuration
# -----------------------------------------------------

st.set_page_config(
    page_title="CAN Analytics Dashboard",
    page_icon="🚗",
    layout="wide"
)

# -----------------------------------------------------
# Database
# -----------------------------------------------------

DECODED_DB = Path("/shared/decoded.db")

if not DECODED_DB.exists():
    st.error(
        f"Waiting for parser output...\n{DECODED_DB} not found"
    )
    st.stop()


# -----------------------------------------------------
# Read Database
# -----------------------------------------------------

@st.cache_data(ttl=2)
def load_data():

    conn = sqlite3.connect(DECODED_DB)

    query = """
    SELECT
        timestamp,
        can_id,
        signal_name,
        signal_value
    FROM decoded_signals
    ORDER BY id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


df = load_data()

if df.empty:
    st.warning("No decoded signals available yet.")
    st.stop()

# -----------------------------------------------------
# Title
# -----------------------------------------------------

st.title("🚗 CAN Analytics Dashboard")

st.markdown("---")

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------

st.sidebar.header("CAN Analysis")

signals = sorted(
    df["signal_name"].unique()
)

selected_signal = st.sidebar.selectbox(
    "Select Signal",
    signals
)

# -----------------------------------------------------
# Filter Data
# -----------------------------------------------------

filtered = df[
    df["signal_name"] == selected_signal
]

# Show latest 300 samples only
filtered = filtered.tail(300)

# Sort timestamps
filtered = filtered.sort_values(
    by="timestamp"
)
# Remove duplicate timestamps if parser inserts duplicates
filtered = filtered.drop_duplicates(
    subset=["timestamp"],
    keep="last"
)
# -----------------------------------------------------
# Statistics
# -----------------------------------------------------

latest_value = filtered["signal_value"].iloc[-1]

minimum_value = filtered["signal_value"].min()

maximum_value = filtered["signal_value"].max()

average_value = filtered["signal_value"].mean()

can_id = filtered["can_id"].iloc[0]

# -----------------------------------------------------
# Metrics
# -----------------------------------------------------

st.subheader(
    f"CAN ID : {can_id} | Signal : {selected_signal}"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Current Value",
        f"{latest_value:.2f}"
    )

with col2:
    st.metric(
        "Minimum",
        f"{minimum_value:.2f}"
    )

with col3:
    st.metric(
        "Maximum",
        f"{maximum_value:.2f}"
    )

with col4:
    st.metric(
        "Average",
        f"{average_value:.2f}"
    )

st.markdown("---")

# -----------------------------------------------------
# Trend Chart
# -----------------------------------------------------

st.subheader("Live Signal Trend")

fig = px.line(
    filtered,
    x="timestamp",
    y="signal_value",
    markers=True,
    title=f"{selected_signal} vs Time"
)

fig.update_layout(
    xaxis_title="Timestamp",
    yaxis_title=selected_signal,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------------------------
# Histogram
# -----------------------------------------------------

st.subheader("Signal Distribution")

hist = px.histogram(
    filtered,
    x="signal_value",
    nbins=20,
    title=f"{selected_signal} Distribution"
)

st.plotly_chart(
    hist,
    use_container_width=True
)

# -----------------------------------------------------
# Statistics Summary
# -----------------------------------------------------

st.subheader("Statistics Summary")

stats_df = pd.DataFrame(
    {
        "Metric": [
            "Samples",
            "Minimum",
            "Maximum",
            "Average",
            "Current"
        ],
        "Value": [
            len(filtered),
            round(minimum_value, 2),
            round(maximum_value, 2),
            round(average_value, 2),
            round(latest_value, 2)
        ]
    }
)

st.dataframe(
    stats_df,
    use_container_width=True
)

# -----------------------------------------------------
# Decoded Signals
# -----------------------------------------------------

st.subheader("Decoded Signals")

st.dataframe(
    filtered.sort_values(
        by="timestamp",
        ascending=False
    ),
    use_container_width=True,
    height=300
)

# -----------------------------------------------------
# Download
# -----------------------------------------------------

st.download_button(
    label="Download Signal Data",
    data=filtered.to_csv(index=False),
    file_name=f"{selected_signal}.csv",
    mime="text/csv"
)

# -----------------------------------------------------
# Auto Refresh
# -----------------------------------------------------

st.caption("Refreshing every 2 seconds...")
st.rerun()