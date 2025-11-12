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

    # Explanation why we're not using the large HTML file
    st.info("""
    **Note:** For optimal performance, we're generating an interactive map directly in the app 
    instead of loading large pre-rendered HTML files. This provides the same insights with faster loading.
    """)

    try:
        import folium
        from streamlit_folium import st_folium
        import branca.colormap as cm

        # Create the map
        m = folium.Map(location=[40.7505, -73.9934], zoom_start=11)
        
        # Create a color scale for trip counts
        if 'top_stations' in globals() and top_stations is not None:
            max_trips = top_stations['trip_count'].max()
            min_trips = top_stations['trip_count'].min()
            colormap = cm.LinearColormap(
                colors=['green', 'yellow', 'red'],
                vmin=min_trips,
                vmax=max_trips,
                caption='Trip Count'
            )
            
            # Station coordinates (approximate locations for popular stations)
            station_coords = {
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
                'E 33 St & 1 Ave': [40.7453, -73.9710],
                'Cleveland Pl & Spring St': [40.7223, -73.9977],
                '12 Ave & W 40 St': [40.7605, -74.0027],
                '6 Ave & W 34 St': [40.7500, -73.9860],
                'West St & Liberty St': [40.7105, -74.0154],
                '11 Ave & W 41 St': [40.7603, -74.0020],
                'Lafayette St & E 8 St': [40.7302, -73.9911],
                'Central Park S & 6 Ave': [40.7659, -73.9763],
                'E 40 St & Park Ave': [40.7507, -73.9758],
                '8 Ave & W 33 St': [40.7500, -73.9920],
            }
            
            # Add markers for each station
            for _, station in top_stations.iterrows():
                name = station['start_station_name']
                trips = station['trip_count']
                
                if name in station_coords:
                    lat, lon = station_coords[name]
                    
                    # Calculate marker size based on trip count
                    radius = max(5, min(20, (trips - min_trips) / (max_trips - min_trips) * 15 + 5))
                    
                    color = colormap(trips)
                    
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=radius,
                        popup=folium.Popup(
                            f"""
                            <b>{name}</b><br>
                            Total Trips: <b>{trips:,}</b><br>
                            <div style="background-color:{color}; width:20px; height:10px; display:inline-block;"></div>
                            """,
                            max_width=300
                        ),
                        tooltip=f"{name}: {trips:,} trips",
                        color=color,
                        fillColor=color,
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(m)
            
            # Add colormap to the map
            colormap.add_to(m)
            
            # Add high-traffic area overlays
            high_traffic_zones = [
                ([40.7505, -73.9934], 800, "Midtown Core", "#ff0000"),
                ([40.7155, -74.0152], 600, "Financial District", "#ff6600"),
                ([40.7410, -73.9897], 500, "Chelsea/Flatiron", "#ff9900"),
                ([40.7655, -73.9582], 400, "Upper East Side", "#ffcc00"),
            ]
            
            for center, radius, name, color in high_traffic_zones:
                folium.Circle(
                    location=center,
                    radius=radius,
                    popup=f"<b>{name}</b><br>High Traffic Zone",
                    color=color,
                    fillColor=color,
                    fillOpacity=0.1,
                    weight=2
                ).add_to(m)
        
        # Display the map
        st_folium(m, width=700, height=600)
        
        # Analysis section
        st.markdown("---")
        st.subheader("Spatial Analysis Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ###  High-Density Clusters
            - **Midtown Manhattan**: Highest station density and usage
            - **Financial District**: Strong commuter patterns
            - **Tourist Corridors**: Times Square, Herald Square
            - **Residential Hubs**: Upper East Side, Chelsea
            
            ###  Usage Patterns
            - Larger circles indicate higher trip volumes
            - Red markers show most popular stations
            - Green markers show moderate usage stations
            """)
        
        with col2:
            st.markdown("""
            ###  Strategic Opportunities
            - **Resource Allocation**: Focus on red zone stations
            - **Expansion Areas**: Gaps between high-density clusters
            - **Peak Management**: Dynamic pricing in high-demand areas
            - **Maintenance**: Priority scheduling for top stations
            """)
        
        # Show data table
        st.subheader("Top Stations Data")
        st.dataframe(top_stations, use_container_width=True)
        
    except ImportError as e:
        st.error("Map dependencies not available. Please install folium and streamlit-folium.")
        show_analytical_fallback()

def show_analytical_fallback():
    """Show analytical insights when map cannot be displayed"""
    st.markdown("""
    ## 📍 Geographic Distribution Analysis
    
    ### High-Traffic Corridors (Based on Station Data):
    
    **1. Midtown Core Cluster** 🟥
    - W 21 St & 6 Ave (129,018 trips)
    - Broadway & W 58 St (127,890 trips) 
    - 6 Ave & W 33 St (126,543 trips)
    - W 31 St & 7 Ave (120,567 trips)
    
    **2. Downtown Financial District** 🟧
    - West St & Chambers St (128,456 trips)
    - High commuter concentration
    - Business-hour focused usage
    
    **3. Chelsea/Flatiron Zone** 🟨
    - Broadway & W 25 St (123,456 trips)
    - University Pl & E 14 St (122,890 trips)
    - Mixed residential/commercial usage
    
    **4. East Side Residential** 🟩
    - 1 Ave & E 68 St (125,678 trips)
    - E 33 St & 1 Ave (119,876 trips)
    - Consistent daily commuter traffic
    """)
    
    if 'top_stations' in globals() and top_stations is not None:
        st.subheader("Station Performance Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Stations", len(top_stations))
        with col2:
            st.metric("Max Trips", f"{top_stations['trip_count'].max():,}")
        with col3:
            st.metric("Avg Trips", f"{top_stations['trip_count'].mean():,.0f}")
        
        st.dataframe(top_stations, use_container_width=True)

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