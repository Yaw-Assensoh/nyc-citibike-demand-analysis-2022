###############################################################
# NYC Citi Bike Strategy Dashboard
# Streamlit Application for Business Intelligence
###############################################################

import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os

###############################################################
# PAGE CONFIGURATION
###############################################################

st.set_page_config(
    page_title='NYC Citi Bike Strategy Dashboard',
    layout='wide',
    initial_sidebar_state='expanded',
    page_icon='🚴'
)

###############################################################
# DASHBOARD HEADER
###############################################################

st.title("🚴 NYC Citi Bike Strategy Dashboard")
st.markdown("""
### Business Intelligence for Bike Share Optimization
This dashboard provides actionable insights to address bike availability challenges 
and support strategic expansion decisions for NYC Citi Bike.
""")

###############################################################
# SIDEBAR - DATA OVERVIEW AND FILTERS
###############################################################

st.sidebar.header("Data Overview")

# Load data with caching - DEPLOYMENT READY PATHS
@st.cache_data
def load_dashboard_data():
    # Define base directory relative to script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible locations for data files
    possible_paths = [
        # For local development
        os.path.join(base_dir, "top_20_stations_full.csv"),
        os.path.join(base_dir, "top_20_stations.csv"),
        os.path.join(base_dir, "../data/processed/top_20_stations_full.csv"),
        os.path.join(base_dir, "../data/processed/top_20_stations.csv"),
        # For deployment
        os.path.join(base_dir, "data/processed/top_20_stations_full.csv"),
        os.path.join(base_dir, "data/processed/top_20_stations.csv"),
    ]
    
    top_stations = None
    daily_data = None
    
    # Find and load top_stations
    for path in possible_paths:
        if os.path.exists(path):
            top_stations = pd.read_csv(path)
            break
    
    # Try multiple possible locations for daily data
    daily_paths = [
        os.path.join(base_dir, "daily_aggregated_data_full.csv"),
        os.path.join(base_dir, "daily_aggregated_data.csv"),
        os.path.join(base_dir, "../data/processed/daily_aggregated_data_full.csv"),
        os.path.join(base_dir, "../data/processed/daily_aggregated_data.csv"),
        os.path.join(base_dir, "data/processed/daily_aggregated_data_full.csv"),
        os.path.join(base_dir, "data/processed/daily_aggregated_data.csv"),
    ]
    
    # Find and load daily_data
    for path in daily_paths:
        if os.path.exists(path):
            daily_data = pd.read_csv(path)
            daily_data['date'] = pd.to_datetime(daily_data['date'])
            break
    
    # If files not found, create sample data
    if top_stations is None or daily_data is None:
        st.sidebar.warning("Using sample data - CSV files not found in expected locations")
        return create_sample_data()
    
    return top_stations, daily_data

def create_sample_data():
    """Create sample data for demonstration"""
    # Sample top stations based on actual data
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
    
    top_stations = pd.DataFrame({
        'start_station_name': stations,
        'trip_count': trip_counts
    })
    
    # Sample daily data
    dates = pd.date_range('2021-01-30', '2022-12-31', freq='D')
    base_trips = 80000
    seasonal_variation = np.sin(2 * np.pi * (dates.dayofyear / 365)) * 20000
    random_noise = np.random.normal(0, 5000, len(dates))
    daily_trips = (base_trips + seasonal_variation + random_noise).astype(int)
    
    # Create realistic temperature data
    monthly_temps = {1: 32, 2: 35, 3: 42, 4: 53, 5: 63, 6: 72, 
                     7: 77, 8: 76, 9: 68, 10: 57, 11: 48, 12: 38}
    base_temp = [monthly_temps[date.month] for date in dates]
    temperature = base_temp + np.random.normal(0, 5, len(dates))
    
    daily_data = pd.DataFrame({
        'date': dates,
        'daily_trips': daily_trips,
        'temperature': temperature
    })
    
    return top_stations, daily_data

# Load the data
with st.spinner('Loading dashboard data...'):
    top_stations, daily_data = load_dashboard_data()

# Display data metrics in sidebar
st.sidebar.metric("Total Stations Analyzed", len(top_stations))
st.sidebar.metric("Date Range", f"{daily_data['date'].min().date()} to {daily_data['date'].max().date()}")
st.sidebar.metric("Peak Daily Trips", f"{daily_data['daily_trips'].max():,}")

###############################################################
# MAIN DASHBOARD LAYOUT
###############################################################

# Create two columns for charts
col1, col2 = st.columns(2)

###############################################################
# BAR CHART - TOP STATIONS
###############################################################

with col1:
    st.subheader("Top 20 Most Popular Stations")
    st.markdown("Identify high-demand stations for resource allocation and maintenance prioritization.")
    
    fig_bar = go.Figure(go.Bar(
        x=top_stations['start_station_name'],
        y=top_stations['trip_count'],
        marker={
            'color': top_stations['trip_count'], 
            'colorscale': 'Blues'
        }
    ))
    
    fig_bar.update_layout(
        xaxis_title='Start Stations',
        yaxis_title='Number of Trips',
        height=500,
        xaxis_tickangle=-45,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

###############################################################
# LINE CHART - DAILY TRENDS
###############################################################

with col2:
    st.subheader(" Daily Trips vs Temperature")
    st.markdown("Analyze seasonal patterns and weather impact on bike usage.")
    
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Daily trips trace
    fig_line.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['daily_trips'],
            name='Daily Bike Trips',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='<b>Date: %{x}</b><br>Trips: %{y:,}<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Temperature trace
    fig_line.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['temperature'],
            name='Average Temperature (°F)',
            line=dict(color='#ff7f0e', width=2),
            hovertemplate='<b>Date: %{x}</b><br>Temperature: %{y:.1f}°F<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig_line.update_layout(
        height=500,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig_line.update_yaxes(title_text="Daily Trips", secondary_y=False)
    fig_line.update_yaxes(title_text="Temperature (°F)", secondary_y=True)
    
    st.plotly_chart(fig_line, use_container_width=True)

###############################################################
# KEPLER.GL MAP VISUALIZATION
###############################################################

st.subheader("Geographic Distribution of Bike Trips")
st.markdown("Explore spatial patterns and identify high-traffic corridors for expansion planning.")

try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    map_paths = [
        os.path.join(base_dir, "nyc_bike_trips_aggregated.html"),
        os.path.join(base_dir, "../maps/nyc_bike_trips_aggregated.html"),
        os.path.join(base_dir, "maps/nyc_bike_trips_aggregated.html"),
    ]
    
    html_content = None
    for map_path in map_paths:
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            break
    
    if html_content:
        st.components.v1.html(html_content, height=600)
    else:
        st.info("""
        **Map Visualization**
        
        To view the interactive map, ensure the map file is available in one of these locations:
        - `nyc_bike_trips_aggregated.html` (same directory)
        - `maps/nyc_bike_trips_aggregated.html`
        - `../maps/nyc_bike_trips_aggregated.html`
        """)
    
except Exception as e:
    st.info("Map visualization not available. The dashboard will still function with the charts above.")

###############################################################
# KEY PERFORMANCE INDICATORS
###############################################################

st.subheader("Key Performance Indicators")

# Create KPI columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    total_trips = top_stations['trip_count'].sum()
    st.metric("Total Trips Analyzed", f"{total_trips:,}")

with kpi2:
    avg_daily_trips = daily_data['daily_trips'].mean()
    st.metric("Average Daily Trips", f"{avg_daily_trips:,.0f}")

with kpi3:
    top_station = top_stations.iloc[0]['start_station_name']
    top_trips = top_stations.iloc[0]['trip_count']
    st.metric("Busiest Station", f"{top_trips:,}")

with kpi4:
    peak_daily = daily_data['daily_trips'].max()
    st.metric("Peak Daily Trips", f"{peak_daily:,}")

###############################################################
# BUSINESS INSIGHTS SECTION
###############################################################

st.subheader(" Strategic Insights")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown("""
    **Expansion Opportunities:**
    - Focus on stations with consistently high demand
    - Identify underserved areas near popular destinations
    - Consider seasonal capacity adjustments
    """)

with insight_col2:
    st.markdown("""
    **⚡ Operational Recommendations:**
    - Optimize bike redistribution based on usage patterns
    - Enhance maintenance schedules for high-traffic stations
    - Implement dynamic pricing during peak demand
    """)