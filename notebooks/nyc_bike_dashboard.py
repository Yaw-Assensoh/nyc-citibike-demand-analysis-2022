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

# Load data with caching
@st.cache_data
def load_dashboard_data():
    # Try multiple possible file locations
    possible_paths = [
        '../data/processed/top_20_stations.csv',  # Relative to notebooks folder
        './data/processed/top_20_stations.csv',   # Relative to project root
        'top_20_stations.csv',                    # In same directory
        '../top_20_stations.csv'                  # One level up
    ]
    
    top_stations = None
    daily_data = None
    
    # Find and load top_stations
    for path in possible_paths:
        if os.path.exists(path):
            top_stations = pd.read_csv(path)
            st.sidebar.success(f"✓ Loaded stations from: {path}")
            break
    
    # Find and load daily_data
    daily_paths = [
        '../data/processed/daily_aggregated_data.csv',
        './data/processed/daily_aggregated_data.csv', 
        'daily_aggregated_data.csv',
        '../daily_aggregated_data.csv'
    ]
    
    for path in daily_paths:
        if os.path.exists(path):
            daily_data = pd.read_csv(path)
            daily_data['date'] = pd.to_datetime(daily_data['date'])
            st.sidebar.success(f"✓ Loaded daily data from: {path}")
            break
    
    # If files not found, create sample data
    if top_stations is None or daily_data is None:
        st.sidebar.warning("Using sample data - actual data files not found")
        top_stations, daily_data = create_sample_data()
    
    return top_stations, daily_data

def create_sample_data():
    """Create sample data for demonstration"""
    # Sample top stations
    stations = [
        'Pershing Square North', 'E 17 St & Broadway', 'W 21 St & 6 Ave',
        'Broadway & E 22 St', 'E 31 St & 3 Ave', 'W 41 St & 8 Ave',
        '1 Ave & E 15 St', 'W 33 St & 7 Ave', 'E 20 St & 2 Ave', '8 Ave & W 31 St'
    ]
    trip_counts = [12500, 11800, 11200, 10800, 10500, 9800, 9200, 8800, 8500, 8200]
    
    top_stations = pd.DataFrame({
        'start_station_name': stations,
        'trip_count': trip_counts
    })
    
    # Sample daily data
    dates = pd.date_range('2022-01-01', '2022-12-31', freq='D')
    daily_trips = np.random.randint(8000, 25000, len(dates))
    temperature = np.random.uniform(30, 85, len(dates))
    
    daily_data = pd.DataFrame({
        'date': dates,
        'daily_trips': daily_trips,
        'temperature': temperature
    })
    
    return top_stations, daily_data

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
            'colorscale': 'Blues',
            'colorbar': {'title': 'Trips'}
        },
        hovertemplate='<b>%{x}</b><br>Trips: %{y:,}<extra></extra>'
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
    # Try multiple possible map locations
    map_paths = [
        '../maps/nyc_bike_trips_aggregated.html',
        '../maps/nyc_citibike_interactive_map.html',
        './maps/nyc_bike_trips_aggregated.html',
        './maps/nyc_citibike_interactive_map.html',
        'nyc_bike_trips_aggregated.html',
        'nyc_citibike_interactive_map.html'
    ]
    
    html_content = None
    for map_path in map_paths:
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            st.success(f"✓ Loaded map from: {map_path}")
            break
    
    if html_content:
        st.components.v1.html(html_content, height=600)
    else:
        st.warning("""
        ⚠ Kepler.gl map file not found. 
        Please ensure the map HTML file is in one of these locations:
        - ../maps/nyc_bike_trips_aggregated.html
        - ../maps/nyc_citibike_interactive_map.html
        - ./maps/nyc_bike_trips_aggregated.html
        """)
    
except FileNotFoundError:
    st.warning("""
    ⚠ Kepler.gl map file not found. 
    Please ensure the map HTML file is available in the maps folder.
    """)

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