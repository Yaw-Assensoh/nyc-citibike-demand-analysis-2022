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
    
    # Use exact paths from your file structure
    data_dir = os.path.join(base_dir, "data/processed")
    
    top_stations = None
    daily_data = None
    
    # Load top stations data
    top_stations_path = os.path.join(data_dir, "top_20_stations.csv")
    if os.path.exists(top_stations_path):
        top_stations = pd.read_csv(top_stations_path)
    
    # Load daily data
    daily_data_path = os.path.join(data_dir, "daily_aggregated_data.csv")
    if os.path.exists(daily_data_path):
        daily_data = pd.read_csv(daily_data_path)
        daily_data['date'] = pd.to_datetime(daily_data['date'])
    
    return top_stations, daily_data

# Load the data
with st.spinner('Loading dashboard data...'):
    top_stations, daily_data = load_dashboard_data()

# Display data metrics in sidebar
if top_stations is not None and daily_data is not None:
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
    
    if top_stations is not None:
        # SEASON FILTER ON THE LEFT SIDEBAR
        st.sidebar.header("Season Filter")
        selected_seasons = st.sidebar.multiselect(
            "Select seasons to display:",
            ["Winter", "Spring", "Summer", "Fall"],
            default=["Winter", "Spring", "Summer", "Fall"]
        )
        
        # Display metrics
        total_rides = top_stations['trip_count'].sum()
        st.metric("Total Rides", f"{total_rides:,}")
        st.write(f"Showing data for: {', '.join(selected_seasons)}")
        
        # Create bar chart 
        fig_bar = go.Figure(go.Bar(
            x=top_stations['start_station_name'],
            y=top_stations['trip_count'],
            marker_color=top_stations['trip_count'],
            marker_colorscale='Blues',
            hovertemplate='<b>%{x}</b><br>Trips: %{y:,}<extra></extra>'
        ))
        
        fig_bar.update_layout(
            title=f"Top 20 Most Popular Bike Stations",
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
# INTERACTIVE MAP PAGE
###############################################################

elif page == "Interactive Map with Aggregated Bike Trips":
    st.title("Interactive Map with Aggregated Bike Trips")
    st.markdown("Explore spatial patterns and identify high-traffic corridors for expansion planning.")

    # FIXED MAP PATH - Pointing to your notebooks folder
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        map_paths = [
            os.path.join(base_dir, "../notebooks/nyc_bike_trips_aggregated.html"),  # Your actual map location
            os.path.join(base_dir, "notebooks/nyc_bike_trips_aggregated.html"),
            os.path.join(base_dir, "nyc_bike_trips_aggregated.html"),
        ]
        
        html_content = None
        map_found = False
        
        for map_path in map_paths:
            if os.path.exists(map_path):
                try:
                    with open(map_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.sidebar.success(f"Map found: {os.path.basename(map_path)}")
                    map_found = True
                    break
                except Exception as e:
                    st.sidebar.warning(f"Could not read: {map_path}")
                    continue
        
        if html_content and map_found:
            st.components.v1.html(html_content, height=600, scrolling=True)
            st.success("✅ Interactive map loaded successfully!")
        else:
            st.error("""
            **Map Not Found on Streamlit Cloud**
            
            For Streamlit deployment, you need to:
            1. Ensure the map file is in your GitHub repository
            2. Add it to the notebooks folder in your repo
            3. The path should be: `notebooks/nyc_bike_trips_aggregated.html`
            
            **Current map search paths attempted:**
            - `../notebooks/nyc_bike_trips_aggregated.html`
            - `notebooks/nyc_bike_trips_aggregated.html` 
            - `nyc_bike_trips_aggregated.html`
            """)
        
    except Exception as e:
        st.error(f"Error loading map: {str(e)}")
        st.info("The dashboard charts are still fully functional.")
    
    # Interpretation section (REQUIRED)
    st.markdown("""
    ### Interpretation of Findings
    
    **Using the filter on the left hand side of the map** we can check whether the most popular start stations also appear in the most popular trips.
    
    **The most popular start stations** identified in our analysis can be cross-referenced with the geographic distribution shown on the map to understand spatial patterns and route preferences.
    
    **While having the aggregated bike trips filter enabled**, we can see spatial patterns that reveal high-frequency routes connecting key destinations throughout the city, with particular concentration in high-traffic areas including Manhattan's core business districts and popular tourist destinations.
    """)

###############################################################
# RECOMMENDATIONS PAGE
###############################################################

elif page == "Recommendations":
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