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
        os.path.join(base_dir, "top_20_stations_full.csv"),
        os.path.join(base_dir, "top_20_stations.csv"),
        os.path.join(base_dir, "../data/processed/top_20_stations_full.csv"),
        os.path.join(base_dir, "../data/processed/top_20_stations.csv"),
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
    
    st.markdown("---")
    st.markdown(" *Use the dropdown menu on the left to navigate through different aspects of the analysis*")

###############################################################
# WEATHER IMPACT ANALYSIS PAGE
###############################################################

if page == "Weather Impact Analysis":
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

if page == "Most Popular Stations":
    st.title(" Most Popular Stations")
    st.markdown("### Top 20 Most Popular Stations Analysis")
    
    if top_stations is not None:
        # Display metrics
        total_rides = top_stations['trip_count'].sum()
        st.metric("Total Rides in Selection", f"{total_rides:,}")
        
        # Create bar chart 
        fig_bar = go.Figure(go.Bar(
            x=top_stations['start_station_name'],
            y=top_stations['trip_count'],
            marker_color=top_stations['trip_count'],
            marker_colorscale='Blues'
        ))
        
        fig_bar.update_layout(
            title="Top 20 Most Popular Bike Stations",
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
# INTERACTIVE MAP PAGE - UPDATED PATHS
###############################################################

elif page == "Interactive Map with Aggregated Bike Trips":
    st.title("Interactive Map with Aggregated Bike Trips")
    st.markdown("Explore spatial patterns and identify high-traffic corridors for expansion planning.")

    # Debug: Show current directory structure
    st.info("**Checking for map files...**")
    
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        st.write(f"Current directory: `{base_dir}`")
        
        # List all files in current and parent directories to debug
        import subprocess
        result = subprocess.run(['find', '.', '-name', '*.html', '-type', 'f'], 
                              capture_output=True, text=True)
        if result.stdout:
            st.write("**Found HTML files:**", result.stdout)
        else:
            st.write("**No HTML files found in repository**")
            
    except Exception as e:
        st.write(f"Debug error: {e}")

    # Try multiple possible locations - UPDATED PATHS
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # All possible paths relative to where the script is running
        map_paths = [
            # If script is in root directory
            "nyc_bike_trips_aggregated.html",
            "maps/nyc_bike_trips_aggregated.html",
            "notebooks/nyc_bike_trips_aggregated.html",
            "data/nyc_bike_trips_aggregated.html",
            # If script is in notebooks directory
            "../nyc_bike_trips_aggregated.html",
            "../maps/nyc_bike_trips_aggregated.html",
            "./nyc_bike_trips_aggregated.html",
            # Absolute paths from root
            os.path.join(base_dir, "nyc_bike_trips_aggregated.html"),
            os.path.join(base_dir, "maps/nyc_bike_trips_aggregated.html"),
            os.path.join(base_dir, "../nyc_bike_trips_aggregated.html"),
            os.path.join(base_dir, "../maps/nyc_bike_trips_aggregated.html"),
        ]
        
        html_content = None
        found_path = None
        
        st.write("**Checking paths:**")
        for map_path in map_paths:
            exists = os.path.exists(map_path)
            status = "✅ EXISTS" if exists else "❌ NOT FOUND"
            st.write(f"- `{map_path}` - {status}")
            
            if exists and html_content is None:
                try:
                    with open(map_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    found_path = map_path
                    st.success(f"**✓ Successfully loaded from: `{map_path}`**")
                    break
                except Exception as e:
                    st.warning(f"Could not read {map_path}: {str(e)}")
        
        if html_content:
            st.components.v1.html(html_content, height=600, scrolling=True)
        else:
            # Create a simple interactive map as fallback
            st.warning("Original map file not found. Creating interactive map...")
            create_interactive_map_fallback()
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        create_interactive_map_fallback()


def create_interactive_map_fallback():
    """Create an interactive map when HTML file is not available"""
    try:
        import folium
        from streamlit_folium import st_folium
        
        # Create NYC map centered on Manhattan
        m = folium.Map(location=[40.7505, -73.9934], zoom_start=12)
        
        # Add popular stations from your data
        if 'top_stations' in globals() and top_stations is not None:
            # Use actual station data if available
            st.info(f"Showing {len(top_stations)} popular stations from your data")
            
            # Sample coordinates for popular stations (you would replace with actual coordinates)
            station_coordinates = {
                'W 21 St & 6 Ave': [40.7410, -73.9897],
                'West St & Chambers St': [40.7155, -74.0152],
                'Broadway & W 58 St': [40.7662, -73.9818],
                '6 Ave & W 33 St': [40.7490, -73.9880],
                '1 Ave & E 68 St': [40.7655, -73.9582],
                'Broadway & E 14 St': [40.7340, -73.9909],
                'Broadway & W 25 St': [40.7441, -73.9907],
                'University Pl & E 14 St': [40.7349, -73.9925],
                'Broadway & E 21 St': [40.7393, -73.9899],
                'W 31 St & 7 Ave': [40.7496, -73.9918],
            }
            
            for _, row in top_stations.head(15).iterrows():
                station_name = row['start_station_name']
                trips = row['trip_count']
                
                # Get coordinates or use default Manhattan location
                coords = station_coordinates.get(station_name, [40.7505, -73.9934])
                
                folium.CircleMarker(
                    location=coords,
                    radius=min(20, max(5, trips / 5000)),  # Scale marker size
                    popup=f"<b>{station_name}</b><br>Trips: {trips:,}",
                    tooltip=station_name,
                    color='blue',
                    fillColor='blue',
                    fillOpacity=0.6
                ).add_to(m)
        
        # Display the map
        st_folium(m, width=700, height=500)
        
        # Show analysis
        st.markdown("""
        ### 🗺️ Spatial Analysis
        
        **High-Density Areas Identified:**
        - **Midtown Manhattan**: Highest concentration of popular stations
        - **Financial District**: Consistent commuter traffic  
        - **Tourist Corridors**: Times Square, Herald Square areas
        - **Residential Hubs**: Upper East Side, Chelsea
        
        **Expansion Recommendations:**
        - Enhance station density in high-traffic corridors
        - Improve bike availability during peak hours at top stations
        - Consider strategic partnerships with nearby businesses
        """)
        
    except ImportError:
        st.error("""
        **Unable to create interactive map.** Required packages not installed.
        
        Please add to your `requirements.txt`:
        ```
        folium
        streamlit-folium
        ```
        """)
        
        # Final fallback - just show the analysis
        show_final_fallback_analysis()


def show_final_fallback_analysis():
    """Show analysis when no map can be displayed"""
    st.markdown("""
    ### 📊 Geographic Distribution Analysis
    
    Based on the station popularity data, here are the key spatial patterns:
    
    **Top 5 High-Traffic Zones:**
    1. **Midtown Core** (Times Square to 34th St)
       - Highest station density
       - Tourist and commuter traffic
       - Peak usage during business hours
       
    2. **Financial District** 
       - Strong commuter patterns
       - Weekday-focused usage
       - Connection to transit hubs
       
    3. **Chelsea/Flatiron**
       - Mixed residential/commercial
       - Evening and weekend usage
       - Restaurant and entertainment traffic
       
    4. **Upper East Side**
       - Residential commuter base
       - Connection to subway lines
       - Consistent daily usage
       
    5. **East Village/Union Square**
       - Student and young professional demographic
       - Weekend recreational usage
    """)
    
    if 'top_stations' in globals() and top_stations is not None:
        st.subheader("Station Usage Data")
        st.dataframe(top_stations.head(10), use_container_width=True)

###############################################################
# RECOMMENDATIONS PAGE
###############################################################

if page == "Recommendations":
    st.title("Recommendations")
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
# FOOTER
###############################################################

st.sidebar.markdown("---")
st.sidebar.markdown("**NYC Citi Bike Analysis**")
st.sidebar.markdown("Data Source: NYC Citi Bike 2021-2022")