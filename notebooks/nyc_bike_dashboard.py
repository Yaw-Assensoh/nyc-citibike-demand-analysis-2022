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
st.markdown("Business Intelligence for Bike Share Optimization")

###############################################################
# SIDEBAR - DATA OVERVIEW AND FILTERS
###############################################################

st.sidebar.header("Data Overview")

@st.cache_data
def load_dashboard_data():
    top_stations = pd.read_csv('../data/processed/top_20_stations.csv')
    daily_data = pd.read_csv('../data/processed/daily_aggregated_data.csv')
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    return top_stations, daily_data

top_stations, daily_data = load_dashboard_data()

st.sidebar.metric("Total Stations Analyzed", len(top_stations))
st.sidebar.metric("Date Range", f"{daily_data['date'].min().date()} to {daily_data['date'].max().date()}")

###############################################################
# MAIN DASHBOARD LAYOUT
###############################################################

col1, col2 = st.columns(2)

###############################################################
# BAR CHART - TOP STATIONS
###############################################################

with col1:
    st.subheader("Top Stations by Popularity")
    
    fig_bar = go.Figure(go.Bar(
        x=top_stations['trip_count'],
        y=top_stations['start_station_name'],
        orientation='h',
        marker_color='#1f77b4',
        hovertemplate='<b>%{y}</b><br>Trips: %{x:,}<extra></extra>'
    ))
    
    fig_bar.update_layout(
        xaxis_title='Number of Trips',
        yaxis_title='Stations',
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

###############################################################
# LINE CHART - DAILY TRENDS
###############################################################

with col2:
    st.subheader("Daily Trips vs Temperature")
    
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_line.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['daily_trips'],
            name='Daily Bike Trips',
            line=dict(color='#1f77b4', width=3)
        ),
        secondary_y=False
    )
    
    fig_line.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['temperature'],
            name='Average Temperature (°F)',
            line=dict(color='#ff7f0e', width=2)
        ),
        secondary_y=True
    )
    
    fig_line.update_layout(height=500)
    fig_line.update_yaxes(title_text="Daily Trips", secondary_y=False)
    fig_line.update_yaxes(title_text="Temperature (°F)", secondary_y=True)
    
    st.plotly_chart(fig_line, use_container_width=True)

###############################################################
# KEPLER.GL MAP VISUALIZATION
###############################################################

st.subheader("Geographic Distribution of Bike Trips")

try:
    with open('../maps/nyc_citibike_interactive_map.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=600)
except FileNotFoundError:
    st.warning("Kepler.gl map file not found")

###############################################################
# KEY PERFORMANCE INDICATORS
###############################################################

st.subheader("Performance Metrics")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    total_trips = top_stations['trip_count'].sum()
    st.metric("Total Trips", f"{total_trips:,}")

with kpi2:
    avg_daily_trips = daily_data['daily_trips'].mean()
    st.metric("Avg Daily Trips", f"{avg_daily_trips:,.0f}")

with kpi3:
    top_trips = top_stations.iloc[0]['trip_count']
    st.metric("Busiest Station", f"{top_trips:,}")

with kpi4:
    peak_daily = daily_data['daily_trips'].max()
    st.metric("Peak Daily Trips", f"{peak_daily:,}")

###############################################################
# BUSINESS INSIGHTS SECTION
###############################################################

st.subheader("Strategic Insights")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.markdown("""
    **Expansion Opportunities:**
    - Focus on high-demand stations
    - Identify underserved areas
    - Seasonal capacity adjustments
    """)

with insight_col2:
    st.markdown("""
    **Operational Recommendations:**
    - Optimize bike redistribution
    - Enhanced maintenance schedules
    - Dynamic pricing during peaks
    """)