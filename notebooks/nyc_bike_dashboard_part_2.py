###############################################################
# NYC Citi Bike Strategy Dashboard - Part 2
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
    initial_sidebar_state='expanded'
)

###############################################################
# CUSTOM CSS FOR CLEAN STYLING
###############################################################

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

###############################################################
# SIDEBAR - PAGE SELECTION & FILTERS
###############################################################

st.sidebar.title("NYC Citi Bike Analysis")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    'Select Analysis Page',
    [
        "Introduction",
        "Weather Impact Analysis", 
        "Most Popular Stations",
        "Interactive Map Analysis",
        "Recommendations"
    ]
)

# Season filter for relevant pages
if page in ["Most Popular Stations", "Weather Impact Analysis"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Filters")
    
    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    selected_seasons = st.sidebar.multiselect(
        'Select seasons to display:',
        options=seasons,
        default=seasons
    )

###############################################################
# DATA LOADING FUNCTION
###############################################################

@st.cache_data
def load_dashboard_data():
    # Define base directory relative to script location 
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible locations for data files 
    possible_paths = [
        os.path.join(base_dir, "data/processed/top_20_stations_full.csv"),
        os.path.join(base_dir, "data/processed/top_20_stations.csv"),
        os.path.join(base_dir, "../data/processed/top_20_stations_full.csv"),
        os.path.join(base_dir, "../data/processed/top_20_stations.csv"),
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
        os.path.join(base_dir, "data/processed/daily_aggregated_data_full.csv"),
        os.path.join(base_dir, "data/processed/daily_aggregated_data.csv"),
        os.path.join(base_dir, "../data/processed/daily_aggregated_data_full.csv"),
        os.path.join(base_dir, "../data/processed/daily_aggregated_data.csv"),
    ]
    
    # Find and load daily_data
    for path in daily_paths:
        if os.path.exists(path):
            daily_data = pd.read_csv(path)
            daily_data['date'] = pd.to_datetime(daily_data['date'])
            break
    
    # If files not found, show error
    if top_stations is None:
        st.error("Error: Could not find top_stations CSV files in data/processed/")
        return None, None
    
    if daily_data is None:
        st.error("Error: Could not find daily_aggregated_data CSV files in data/processed/")
        return None, None
    
    return top_stations, daily_data

# Load the data
with st.spinner('Loading dashboard data...'):
    top_stations, daily_data = load_dashboard_data()

# Only show metrics if data loaded successfully
if top_stations is not None and daily_data is not None:
    st.sidebar.metric("Total Stations Analyzed", len(top_stations))
    st.sidebar.metric("Date Range", f"{daily_data['date'].min().date()} to {daily_data['date'].max().date()}")
    st.sidebar.metric("Peak Daily Trips", f"{daily_data['daily_trips'].max():,}")


# Apply season filter if selected
if page in ["Most Popular Stations", "Weather Impact Analysis"] and 'selected_seasons' in locals():
    if selected_seasons:
        filtered_daily_data = daily_data[daily_data['season'].isin(selected_seasons)]
    else:
        filtered_daily_data = daily_data
else:
    filtered_daily_data = daily_data

###############################################################
# INTRODUCTION PAGE
###############################################################

if page == "Introduction":
    
    st.markdown('<h1 class="main-header">NYC Citi Bike Strategy Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Data-Driven Insights for Bike Share Optimization")
    
    # Key Metrics Overview
    st.markdown("---")
    st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_trips = daily_data['daily_trips'].sum()
        st.metric("Total Trips Analyzed", f"{total_trips:,.0f}")
    
    with col2:
        avg_daily = daily_data['daily_trips'].mean()
        st.metric("Average Daily Trips", f"{avg_daily:,.0f}")
    
    with col3:
        peak_daily = daily_data['daily_trips'].max()
        st.metric("Peak Daily Trips", f"{peak_daily:,.0f}")
    
    with col4:
        total_stations = len(top_stations)
        st.metric("Stations Analyzed", f"{total_stations}")
    
    st.markdown("---")
    
    # Business Challenge Section
    st.markdown('<div class="section-header">Business Challenge</div>', unsafe_allow_html=True)
    
    st.markdown("""
    NYC Citi Bike is experiencing customer complaints about bike availability issues during peak hours and in high-demand areas. 
    This comprehensive analysis examines usage patterns, seasonal impacts, and geographic distribution to provide data-driven solutions.
    
    **Analysis Objectives:**
    - Identify patterns in bike usage and demand fluctuations
    - Understand seasonal and weather impacts on ridership  
    - Pinpoint high-demand stations and usage corridors
    - Provide strategic recommendations for operational optimization
    """)
    
    # Dashboard Navigation
    st.markdown("---")
    st.markdown('<div class="section-header">Dashboard Navigation</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Use the sidebar to navigate through different analysis sections:
    - **Weather Impact Analysis**: Temperature and seasonal usage patterns
    - **Most Popular Stations**: Top stations and demand concentration  
    - **Interactive Map Analysis**: Geographic distribution and hotspots
    - **Recommendations**: Strategic insights and solutions
    """)

###############################################################
# WEATHER IMPACT ANALYSIS PAGE - DUAL AXIS LINE CHART
###############################################################

elif page == "Weather Impact Analysis":
    
    st.markdown('<h1 class="main-header">Weather Impact Analysis</h1>', unsafe_allow_html=True)
    st.markdown("### Understanding Temperature and Seasonal Effects on Bike Usage")
    
    # Display current filter status
    if 'selected_seasons' in locals() and selected_seasons:
        season_text = f"Showing data for: {', '.join(selected_seasons)}"
        display_data = filtered_daily_data
    else:
        season_text = "Showing data for all seasons"
        display_data = daily_data
    
    st.info(season_text)
    
    # KPI Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_trips = display_data['daily_trips'].mean()
        st.metric("Average Daily Trips", f"{avg_trips:,.0f}")
    
    with col2:
        avg_temp = display_data['temperature'].mean()
        st.metric("Average Temperature", f"{avg_temp:.1f}°F")
    
    with col3:
        correlation = display_data['daily_trips'].corr(display_data['temperature'])
        st.metric("Temperature Correlation", f"{correlation:.3f}")
    
    # Main visualization
    st.markdown("---")
    st.markdown('<div class="section-header">Daily Trips vs Temperature</div>', unsafe_allow_html=True)
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add Daily Trips line (left axis)
    fig.add_trace(
        go.Scatter(
            x=display_data['date'],
            y=display_data['daily_trips'],
            name="Daily Bike Trips",
            line=dict(color="#3366CC", width=3),
            opacity=0.9,
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Trips: %{y:,}<extra></extra>"
        ),
        secondary_y=False,
    )
    
    # Add Temperature line (right axis)
    fig.add_trace(
        go.Scatter(
            x=display_data['date'],
            y=display_data['temperature'],
            name="Temperature (°F)",
            line=dict(color="#FF6633", width=2.5),
            opacity=0.8,
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Temp: %{y:.1f}°F<extra></extra>"
        ),
        secondary_y=True,
    )
    
    # Update layout for better readability
    fig.update_layout(
        height=500,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        title_font_size=16,
        font_size=12,
        margin=dict(t=80, l=80, r=80, b=80)
    )
    
    # Set y-axes titles with better spacing
    fig.update_yaxes(
        title_text="<b>Daily Bike Trips</b>",
        secondary_y=False,
        title_font=dict(size=14),
        gridcolor='lightgray',
        gridwidth=0.5
    )
    
    fig.update_yaxes(
        title_text="<b>Temperature (°F)</b>",
        secondary_y=True,
        title_font=dict(size=14),
        gridcolor='lightgray',
        gridwidth=0.25
    )
    
    fig.update_xaxes(
        title_text="<b>Date</b>",
        title_font=dict(size=14),
        gridcolor='lightgray',
        gridwidth=0.5
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("There is an obvious correlation between the rise and drop of temperatures and their relationship " \
    "with the frequency of bike trips taken daily. As temperatures plunge, so does bike usage. This insight indicates that the " \
    "shortage problem may be prevalent merely in the warmer months, approximately from May to October.")
    
    # Additional insights columns
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        st.markdown("""
        ** Temperature Impact:**
        
        - Strong positive correlation between temperature and bike usage
        - Optimal temperature range: 65°F - 80°F for maximum ridership
        - Significant usage drop below 45°F
        - Summer peaks show 60-70% higher usage than winter lows
        """)
    
    with col_insight2:
        st.markdown("""
        **Seasonal Patterns:**
        
        - High season: May through October
        - Shoulder seasons: April and November
        - Low season: December through March
        - Weekend effect: 20% higher usage on weekends
        """)

###############################################################
# MOST POPULAR STATIONS PAGE 
###############################################################

elif page == "Most Popular Stations":
    
    st.markdown('<h1 class="main-header">Most Popular Stations</h1>', unsafe_allow_html=True)
    st.markdown("### Top 20 Stations Analysis and Demand Patterns")
    
    # Filter note
    if 'selected_seasons' in locals() and len(selected_seasons) < 4:
        filter_note = f"Showing annual data for reference - {len(selected_seasons)} season(s) selected in filter"
    else:
        filter_note = "Showing annual station performance data"
    
    st.info(filter_note)
    
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
    
    # Main Visualization - IMPROVED BAR CHART ONLY
    st.markdown("---")
    st.markdown('<div class="section-header">Top 20 Stations by Usage</div>', unsafe_allow_html=True)
    
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
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights Section
    st.markdown("---")
    st.markdown('<div class="section-header">Station Analysis Insights</div>', unsafe_allow_html=True)
    
st.markdown("""
**Geographic Concentration:**
- Midtown Manhattan dominates top stations
- Tourist destinations show heavy usage
- Commuter hubs consistently popular
- Waterfront locations emerging as hotspots

**Operational Implications:**
- Resource allocation should prioritize top stations
- Redistribution efforts needed for demand balancing
- Maintenance scheduling optimization required
- Expansion opportunities in underserved areas
""")

###############################################################
# FOOTER
###############################################################

st.sidebar.markdown("---")
st.sidebar.markdown("Dashboard Information")
st.sidebar.markdown("Data Source: NYC Citi Bike 2021-2022")
st.sidebar.markdown("Version: 2.0")