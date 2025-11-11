###############################################################
# NYC Citi Bike Strategy Dashboard - Part 2
###############################################################

import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os
from PIL import Image

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
# SIDEBAR - PAGE SELECTION
###############################################################

page = st.sidebar.selectbox(
    'Select Analysis Aspect',
    [
        "Introduction",
        "Weather Impact Analysis", 
        "Most Popular Stations",
        "Interactive Map with Aggregated Bike Trips",
        "Recommendations"
    ]
)

###############################################################
# DATA LOADING 
###############################################################

@st.cache_data
def load_dashboard_data():
    # Define base directory relative to script location 
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible locations for data files 
    possible_paths = [
        # For local development
        os.path.join(base_dir, "top_20_stations_full.csv"),
        os.path.join(base_dir, "top_20_stations.csv"),
        os.path.join(base_dir, "../data/processed/top_20_stations.csv"),
        os.path.join(base_dir, "../data/processed/top_20_stations_full.csv"),
        # For deployment
        os.path.join(base_dir, "data/processed/top_20_stations.csv"),
        os.path.join(base_dir, "data/processed/top_20_stations_full.csv"),
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
    # Sample top stations based on actual data - FIXED: Now includes 20 stations
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
# INTRODUCTION PAGE
###############################################################

if page == "Introduction":
    st.title("🚴 NYC Citi Bike Strategy Dashboard")
    st.markdown("### Business Intelligence for Bike Share Optimization")
    
    st.markdown("""
    #### Business Challenge
    This dashboard provides actionable insights to address bike availability challenges 
    and support strategic expansion decisions for NYC Citi Bike.
    
    Customers currently complain about bikes not being available at certain times. 
    This analysis examines the potential reasons behind this issue through comprehensive data exploration.
    """)
    
    st.markdown("""
    #### Dashboard Structure
    The analysis is organized into 4 main sections:
    
    - **Weather Impact Analysis**: Correlation between temperature and bike usage patterns
    - **Most Popular Stations**: Identification of high-demand stations for resource allocation
    - **Interactive Map**: Geographic distribution of bike trips and spatial patterns
    - **Recommendations**: Strategic insights based on comprehensive analysis
    """)
    
    # Display data metrics in sidebar 
    if df is not None:
        st.sidebar.header(" Data Overview")
        st.sidebar.metric("Total Stations", df['start_station_name'].nunique())
        st.sidebar.metric("Date Range", f"{df['started_at'].min().date()} to {df['started_at'].max().date()}")
        total_trips = df['trip_count'].sum() if 'trip_count' in df.columns else len(df)
        st.sidebar.metric("Total Trips", f"{total_trips:,}")
    
    st.markdown("---")
    st.markdown(" *Use the dropdown menu on the left to navigate through different aspects of the analysis*")

###############################################################
# WEATHER IMPACT ANALYSIS PAGE
###############################################################

elif page == "Weather Impact Analysis":
    st.title(" Weather Impact Analysis")
    st.markdown("### Daily Bike Trips vs Temperature Correlation")
    
    if daily_data is not None:
        # Create dual-axis line chart 
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
        
        # Layout 
        fig_line.update_layout(
            title='Daily Bike Trips vs Temperature in NYC',
            height=500,
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig_line.update_yaxes(title_text="Daily Trips", secondary_y=False)
        fig_line.update_yaxes(title_text="Temperature (°F)", secondary_y=True)
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Interpretation section (REQUIRED)
        st.markdown("""
        ###  Interpretation of Findings
        
        **There is an obvious correlation between the rise and drop of temperatures and their relationship with the frequency of bike trips taken daily.** 
        
        As temperatures plunge during winter months, so does bike usage, with a noticeable decline starting in November and reaching the lowest points in January and February. 
        Conversely, as temperatures rise in spring and summer, bike usage increases significantly, peaking during the warmest months.
        
        **This insight indicates that the shortage problem may be prevalent merely in the warmer months, approximately from May to October,** 
        when demand surges due to favorable weather conditions. The seasonal pattern suggests opportunities for strategic operational scaling.
        """)
    else:
        st.error("Unable to load data for weather analysis")

###############################################################
# MOST POPULAR STATIONS PAGE
###############################################################

elif page == "Most Popular Stations":
    st.title(" Most Popular Stations")
    st.markdown("### Top 20 Most Popular Stations Analysis")
    
    if df is not None:
        # Season filter in sidebar
        st.sidebar.subheader("Season Filter")
        season_filter = st.sidebar.multiselect(
            'Select seasons:',
            options=df['season'].unique(),
            default=df['season'].unique()
        )
        
        # Filter data based on selection
        df_filtered = df[df['season'].isin(season_filter)]
        
        # Calculate metrics
        station_trips = df_filtered.groupby('start_station_name', as_index=False)['trip_count'].sum()
        top_20_stations = station_trips.nlargest(20, 'trip_count')
        
        # Display metrics
        total_rides = top_20_stations['trip_count'].sum()
        st.metric("Total Rides in Selection", f"{total_rides:,}")
        
        # Create bar chart 
        fig_bar = go.Figure(go.Bar(
            x=top_20_stations['start_station_name'],
            y=top_20_stations['trip_count'],
            marker_color=top_20_stations['trip_count'],
            marker_colorscale='Blues'
        ))
        
        fig_bar.update_layout(
            title=f"Top 20 Most Popular Bike Stations ({', '.join(season_filter)})",
            xaxis_title='Start Stations',
            yaxis_title='Number of Trips',
            height=500,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Interpretation section (REQUIRED)
        st.markdown("""
        ###  Interpretation of Findings
        
        **From the bar chart it is clear that there are some start stations that are more popular than others** - 
        stations in high-traffic areas consistently attract higher usage.
        
        **There is a significant jump between the highest and lowest bars of the plot** indicating clear user preferences 
        for certain stations over others. This concentration of demand at specific locations likely contributes to 
        the availability challenges experienced by customers.
        
        **This is a finding that we could cross reference with the interactive map** to understand whether these popular 
        start stations also account for the most commonly taken trips throughout the city.
        """)
    else:
        st.error("Unable to load data for station analysis")

###############################################################
# INTERACTIVE MAP PAGE - 
###############################################################

st.subheader("Geographic Distribution of Bike Trips")
st.markdown("Explore spatial patterns and identify high-traffic corridors for expansion planning.")

# Try to load the map with more specific error handling
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # More comprehensive search for the map file
    map_search_paths = [
        "nyc_bike_trips_aggregated.html",
        "./nyc_bike_trips_aggregated.html",
        "maps/nyc_bike_trips_aggregated.html", 
        "./maps/nyc_bike_trips_aggregated.html",
        "../maps/nyc_bike_trips_aggregated.html",
        "../nyc_bike_trips_aggregated.html",
        "data/maps/nyc_bike_trips_aggregated.html",
        "../data/maps/nyc_bike_trips_aggregated.html"
    ]
    
    html_content = None
    map_found_path = None
    
    for map_path in map_search_paths:
        full_path = os.path.join(base_dir, map_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                map_found_path = full_path
                st.sidebar.success(f"Map loaded from: {map_path}")
                break
            except Exception as e:
                st.sidebar.warning(f"Found but couldn't read: {map_path}")
                continue
    
    if html_content:
        st.components.v1.html(html_content, height=600, scrolling=True)
    else:
        # Show more helpful information about finding the map
        st.info("""
        ** Interactive Map Visualization**
        
        To view the interactive map, please ensure the map file `nyc_bike_trips_aggregated.html` is available in one of these locations relative to your dashboard script:
        
        - Same directory: `nyc_bike_trips_aggregated.html`
        - `maps/nyc_bike_trips_aggregated.html` 
        - `../maps/nyc_bike_trips_aggregated.html`
        - `data/maps/nyc_bike_trips_aggregated.html`
        
        The map displays aggregated bike trips across NYC, showing spatial patterns and high-traffic corridors for expansion planning.
        """)
        
        # Show current directory info to help user
        st.sidebar.info(f"Current directory: {base_dir}")
        
        # List files in current directory to help debugging
        try:
            current_files = os.listdir(base_dir)
            map_files = [f for f in current_files if f.endswith('.html')]
            if map_files:
                st.sidebar.write("HTML files in current directory:", map_files)
        except:
            pass
    
except Exception as e:
    st.error(f"Error loading map: {str(e)}")
    st.info("The dashboard charts are still fully functional. Please check the map file location.")
    
    # Interpretation section (REQUIRED)
    st.markdown("""
    ### Interpretation of Findings
    
    **Using the filter on the left hand side of the map** we can check whether the most popular start stations also appear in the most popular trips.
    
    **The most popular start stations** identified in our analysis can be cross-referenced with the geographic distribution shown on the map to understand spatial patterns and route preferences.
    
    **While having the aggregated bike trips filter enabled**, we can see spatial patterns that reveal high-frequency routes connecting key destinations throughout the city, with particular concentration in high-traffic areas including Manhattan's core business districts and popular tourist destinations.
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
    st.metric("Busiest Station", f"{top_trips:,}", help=f"Station: {top_station}")

with kpi4:
    peak_daily = daily_data['daily_trips'].max()
    st.metric("Peak Daily Trips", f"{peak_daily:,}")

###############################################################
# RECOMMENDATIONS PAGE
###############################################################


    st.markdown("### Strategic Insights for NYC Citi Bike Operations")
    
    st.markdown("""
    ## Executive Summary
    
    Our comprehensive analysis of NYC Citi Bike usage patterns, seasonal trends, and geographic distribution 
    reveals key insights for addressing bike availability challenges and supporting strategic growth initiatives.
    """)
    
    st.markdown("""
    ##  Key Recommendations
    
    ### 1. Seasonal Operational Scaling
    **Implement dynamic resource allocation based on demand patterns:**
    - Scale back operations by **40-50% between November and April**
    - Maintain full fleet deployment during peak months (**May through October**)
    - Implement gradual transition periods in spring and fall
    
    ### 2. High-Demand Station Optimization  
    **Focus resources on consistently popular locations:**
    - Enhance maintenance schedules for the top 20 stations identified in our analysis
    - Implement predictive bike redistribution to high-demand areas
    - Deploy additional operational staff during peak usage hours
    
    ### 3. Strategic Geographic Expansion
    **Target high-potential areas for station deployment:**
    - Use geographic heat maps to identify underserved corridors
    - Focus expansion along high-traffic routes identified in spatial analysis
    - Consider areas with growing residential and commercial development
    """)
    
    st.markdown("""
    ##  Addressing Stakeholder Questions
    
    **How much would you recommend scaling bikes back between November and April?**
    > Based on our temperature and usage correlation analysis, we recommend scaling back operations by 40-50% during 
    the November-April period, with the most significant reductions in January and February when demand is lowest.
    
    **How could you determine how many more stations to add along the water?**
    > Using our geographic analysis from the interactive map, we would identify high-demand corridors near waterways, 
    analyze current station coverage gaps, and use spatial clustering to determine optimal locations for new station deployment.
    
    **What are some ideas for ensuring bikes are always stocked at the most popular stations?**
    > Implement predictive redistribution algorithms, dynamic pricing incentives for returning bikes to high-demand areas, 
    enhanced maintenance schedules at top stations, and real-time monitoring systems with automated alerts for low inventory situations.
    """)

###############################################################
# FOOTER (Same as original)
###############################################################

st.sidebar.markdown("---")
st.sidebar.markdown("**NYC Citi Bike Analysis**")
st.sidebar.markdown("Data Source: NYC Citi Bike 2021-2022")