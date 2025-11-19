import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Popular Stations", layout="wide")

st.title("📍 Most Popular Stations")
st.markdown("### Top 20 Stations Analysis and Demand Patterns")

# Load station data
@st.cache_data
def load_station_data():
    stations = [
        'W 21 St & 6 Ave', 'West St & Chambers St', 'Broadway & W 58 St',
        '6 Ave & W 33 St', '1 Ave & E 68 St', 'Broadway & E 14 St',
        'Broadway & W 25 St', 'University Pl & E 14 St', 'Broadway & E 21 St',
        'W 31 St & 7 Ave', 'E 33 St & 1 Ave', 'Cleveland Pl & Spring St',
        '12 Ave & W 40 St', '6 Ave & W 34 St', 'West St & Liberty St',
        '11 Ave & W 41 St', 'Lafayette St & E 8 St', 'Central Park S & 6 Ave',
        'E 40 St & Park Ave', '8 Ave & W 33 St'
    ]
    
    trip_counts = [129018, 128456, 127890, 126543, 125678, 124321, 123456, 122890, 121234, 120567,
                   119876, 119123, 118456, 117890, 117123, 116456, 115789, 115123, 114456, 113789]
    
    return pd.DataFrame({
        'start_station_name': stations,
        'trip_count': trip_counts
    })

top_stations = load_station_data()

# KPI Metrics
col1, col2, col3 = st.columns(3)

with col1:
    total_rides = top_stations['trip_count'].sum()
    st.metric("Total Station Rides", f"{total_rides:,}")

with col2:
    avg_station = top_stations['trip_count'].mean()
    st.metric("Average per Station", f"{avg_station:,.0f}")

with col3:
    top_station = top_stations.iloc[0]
    st.metric("Top Station Volume", f"{top_station['trip_count']:,}")

# Main Visualization
st.markdown("---")
st.subheader("Top 20 Stations by Usage")

fig = go.Figure(go.Bar(
    x=top_stations['start_station_name'],
    y=top_stations['trip_count'],
    marker=dict(
        color=top_stations['trip_count'],
        colorscale='Blues',
        colorbar=dict(title="Trip Count")
    ),
    hovertemplate='<b>%{x}</b><br>Trips: %{y:,}<extra></extra>'
))

fig.update_layout(
    title="Top 20 Most Popular Bike Stations in NYC",
    xaxis_title='Start Stations',
    yaxis_title='Number of Trips',
    height=500,
    xaxis_tickangle=-45,
    template='plotly_white'
)

st.plotly_chart(fig, use_container_width=True)

# Insights Section
st.markdown("---")
st.subheader("📊 Station Analysis Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Geographic Concentration:**
    - Midtown Manhattan dominates top stations
    - Tourist destinations show heavy usage
    - Commuter hubs consistently popular
    - Waterfront locations emerging as hotspots
    """)

with col2:
    st.markdown("""
    **Operational Implications:**
    - Resource allocation should prioritize top stations
    - Redistribution efforts needed for demand balancing
    - Maintenance scheduling optimization required
    - Expansion opportunities in underserved areas
    """)