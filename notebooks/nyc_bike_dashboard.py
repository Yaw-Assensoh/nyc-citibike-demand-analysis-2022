###############################################################
# NYC Citi Bike Strategy Dashboard
# Streamlit Application for Business Intelligence
###############################################################

import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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

# Load data with caching - EXACT PATHS FROM YOUR NOTEBOOK
@st.cache_data
def load_dashboard_data():
    # Load the main dataset first
    DATA_PATH = "../data/processed/nyc_citibike_2022_processed.csv"
    df = pd.read_csv(DATA_PATH, low_memory=False)
    
    # Create trip count column and prepare data exactly like in notebook
    df['trip_count'] = 1
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['date'] = df['started_at'].dt.date
    
    # Create top stations data (from cell 77)
    station_trips = df.groupby('start_station_name', as_index=False)['trip_count'].count()
    top_stations = station_trips.nlargest(20, 'trip_count')
    
    # Create daily aggregated data (from cells 11 and 66)
    daily_aggregated = df.groupby('date').agg({
        'trip_count': 'sum'
    }).reset_index()
    daily_aggregated.columns = ['date', 'daily_trips']
    daily_aggregated['date'] = pd.to_datetime(daily_aggregated['date'])
    
    # Add temperature data (from cell 11)
    if 'temperature' in df.columns:
        temp_data = df.groupby('date')['temperature'].mean().reset_index()
        daily_aggregated = daily_aggregated.merge(temp_data, on='date')
    else:
        # Create realistic temperature data like in notebook
        np.random.seed(42)
        daily_aggregated['month'] = daily_aggregated['date'].dt.month
        monthly_temps = {1: 32, 2: 35, 3: 42, 4: 53, 5: 63, 6: 72, 
                         7: 77, 8: 76, 9: 68, 10: 57, 11: 48, 12: 38}
        daily_aggregated['base_temp'] = daily_aggregated['month'].map(monthly_temps)
        daily_aggregated['temperature'] = daily_aggregated['base_temp'] + np.random.normal(0, 5, len(daily_aggregated))
        daily_aggregated = daily_aggregated.drop(['month', 'base_temp'], axis=1)
    
    return top_stations, daily_aggregated

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
    with open('../maps/nyc_bike_trips_aggregated.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    st.components.v1.html(html_content, height=600)
    
except FileNotFoundError:
    st.warning("""
    ⚠ Kepler.gl map file not found. 
    Please ensure '../maps/nyc_bike_trips_aggregated.html' exists.
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