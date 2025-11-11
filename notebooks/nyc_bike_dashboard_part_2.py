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
    # Using the same deployment-ready paths as your original
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load reduced dataset
    reduced_data_path = os.path.join(base_dir, "nyc_citibike_reduced.csv")
    
    try:
        df = pd.read_csv(reduced_data_path)
        df['started_at'] = pd.to_datetime(df['started_at'])
        
        # Create daily aggregated data (same as your original)
        df['date'] = df['started_at'].dt.date
        daily_aggregated = df.groupby('date').agg({
            'trip_count': 'sum'
        }).reset_index()
        daily_aggregated.columns = ['date', 'daily_trips']
        daily_aggregated['date'] = pd.to_datetime(daily_aggregated['date'])
        
        # Create temperature data (same synthetic approach as your original)
        np.random.seed(42)
        daily_aggregated['month'] = daily_aggregated['date'].dt.month
        
        # NYC average temperatures by month (same as your original)
        monthly_temps = {1: 32, 2: 35, 3: 42, 4: 53, 5: 63, 6: 72, 
                         7: 77, 8: 76, 9: 68, 10: 57, 11: 48, 12: 38}
        
        daily_aggregated['base_temp'] = daily_aggregated['month'].map(monthly_temps)
        daily_aggregated['temperature'] = daily_aggregated['base_temp'] + np.random.normal(0, 5, len(daily_aggregated))
        daily_aggregated = daily_aggregated.drop('base_temp', axis=1)
        
        return df, daily_aggregated
        
    except FileNotFoundError:
        st.error("Reduced data file not found. Please ensure 'nyc_citibike_reduced.csv' is in the working directory.")
        return None, None

# Load the data
df, daily_data = load_dashboard_data()

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
    
    # Display data metrics (same as original sidebar)
    if df is not None:
        st.sidebar.header("Data Overview")
        st.sidebar.metric("Total Stations", df['start_station_name'].nunique())
        st.sidebar.metric("Date Range", f"{df['started_at'].min().date()} to {df['started_at'].max().date()}")
        st.sidebar.metric("Total Trips", f"{df['trip_count'].sum():,}")

###############################################################
# WEATHER IMPACT ANALYSIS PAGE
###############################################################

elif page == "Weather Impact Analysis":
    st.title(" Weather Impact Analysis")
    st.markdown("### Daily Bike Trips vs Temperature Correlation")
    
    if daily_data is not None:
        # Create dual-axis line chart (SAME STRUCTURE AS ORIGINAL)
        fig_line = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Daily trips trace (same as original)
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
        
        # Temperature trace (same as original)
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
        
        # Layout (same as original)
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
        
        As temperatures plunge during winter months, so does bike usage, with a noticeable decline starting in November and reaching the lowest points in January and February. Conversely, as temperatures rise in spring and summer, bike usage increases significantly, peaking during the warmest months.
        
        **This insight indicates that the shortage problem may be prevalent merely in the warmer months, approximately from May to October,** when demand surges due to favorable weather conditions. The seasonal pattern suggests opportunities for strategic operational scaling.
        """)
        
        # Seasonal metrics (same approach as original)
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate approximate seasonal averages based on the data
        if daily_data is not None:
            daily_data['season'] = daily_data['date'].dt.month.apply(lambda x: 'Winter' if x in [12,1,2] else 
                                                                   'Spring' if x in [3,4,5] else 
                                                                   'Summer' if x in [6,7,8] else 'Fall')
            seasonal_avg = daily_data.groupby('season')['daily_trips'].mean()
            
            with col1:
                st.metric("Winter Average", f"{seasonal_avg.get('Winter', 0):,.0f}")
            with col2:
                st.metric("Spring Average", f"{seasonal_avg.get('Spring', 0):,.0f}")
            with col3:
                st.metric("Summer Average", f"{seasonal_avg.get('Summer', 0):,.0f}")
            with col4:
                st.metric("Fall Average", f"{seasonal_avg.get('Fall', 0):,.0f}")

###############################################################
# MOST POPULAR STATIONS PAGE
###############################################################

elif page == "Most Popular Stations":
    st.title(" Most Popular Bike Stations")
    st.markdown("### Top 20 Most Popular Stations Analysis")
    
    if df is not None:
        # Season filter in sidebar (NEW FILTER FUNCTIONALITY)
        st.sidebar.subheader("Season Filter")
        season_filter = st.sidebar.multiselect(
            label='Select the season', 
            options=df['season'].unique(),
            default=df['season'].unique()
        )
        
        # Filter data based on selection
        df_filtered = df[df['season'].isin(season_filter)]
        
        # Total rides metric connected to filter
        total_rides = float(df_filtered['trip_count'].sum())
        st.metric(label='Total Bike Rides', value=f"{total_rides:,}")
        
        # Top stations analysis (SAME AS ORIGINAL)
        station_trips = df_filtered.groupby('start_station_name', as_index=False)['trip_count'].sum()
        top_20_stations = station_trips.nlargest(20, 'trip_count')
        
        # Create bar chart (SAME AS ORIGINAL)
        fig_bar = go.Figure(go.Bar(
            x=top_20_stations['start_station_name'],
            y=top_20_stations['trip_count'],
            marker={
                'color': top_20_stations['trip_count'], 
                'colorscale': 'Blues',
            }
        ))
        
        # Customize layout (SAME AS ORIGINAL)
        fig_bar.update_layout(
            title=f"Top 20 Most Popular Bike Stations in NYC ({', '.join(season_filter)})",
            xaxis_title='Start Stations',
            yaxis_title='Number of Trips',
            width=1000,
            height=600,
            xaxis_tickangle=-45,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Interpretation section (REQUIRED)
        st.markdown("""
        ###  Interpretation of Findings
        
        **From the bar chart it is clear that there are some start stations that are more popular than others** - in the top positions we can see stations like W 21 St & 6 Ave, West St & Chambers St, and Broadway & W 58 St consistently attracting high usage.
        
        **There is a significant jump between the highest and lowest bars of the plot** indicating clear user preferences for certain stations over others. This concentration of demand at specific locations likely contributes to the availability challenges experienced by customers.
        
        **This is a finding that we could cross reference with the interactive map** that you can access through the sidebar select box to understand whether these popular start stations also account for the most commonly taken trips throughout the city.
        """)
        
        # Display top stations summary (same as original approach)
        st.subheader("Top 5 Stations Summary")
        top_5 = top_20_stations.head(5).copy()
        top_5['trip_count'] = top_5['trip_count'].apply(lambda x: f"{x:,}")
        st.table(top_5)

###############################################################
# INTERACTIVE MAP PAGE
###############################################################

elif page == "Interactive Map with Aggregated Bike Trips":
    st.title(" Interactive Map with Aggregated Bike Trips")
    st.markdown("### Geographic Distribution of Bike Trips")
    
    # Map visualization (SAME AS ORIGINAL)
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
            **Interactive Map Visualization**
            
            To view the interactive map, ensure the map file is available in one of these locations:
            - `nyc_bike_trips_aggregated.html` (same directory)
            - `maps/nyc_bike_trips_aggregated.html`
            - `../maps/nyc_bike_trips_aggregated.html`
            
            The map displays aggregated bike trips across NYC, showing spatial patterns and high-traffic corridors.
            """)
        
    except Exception as e:
        st.info("Map visualization not available. The dashboard will still function with the analytical charts above.")
    
    # Interpretation section (REQUIRED)
    st.markdown("""
    ###  Interpretation of Findings
    
    **Using the filter on the left hand side of the map** we can check whether the most popular start stations also appear in the most popular trips.
    
    **The most popular start stations are**: W 21 St & 6 Ave, West St & Chambers St, and Broadway & W 58 St. 
    
    **While having the aggregated bike trips filter enabled**, we can see that even though certain stations are popular start points, they don't necessarily account for all the most commonly taken trips. The spatial analysis reveals that high-frequency routes connect various key destinations throughout the city.
    
    **The most common routes** are predominantly located in high-traffic areas including Midtown Manhattan, Downtown financial districts, and popular tourist destinations, with particular concentration along major corridors and transportation hubs.
    """)

###############################################################
# RECOMMENDATIONS PAGE
###############################################################

else:
    st.title(" Recommendations and Conclusions")
    st.markdown("### Strategic Insights and Actionable Recommendations")
    
    st.markdown("""
    ## Executive Summary
    
    Our comprehensive analysis of NYC Citi Bike usage patterns, seasonal trends, and geographic distribution 
    reveals key insights for addressing bike availability challenges and supporting strategic growth initiatives.
    """)
    
    st.markdown("""
    ##  Key Recommendations
    
    ### 1. Seasonal Operational Scaling
    **Implement dynamic resource allocation based on demand patterns:**
    - Scale back bike deployment by **40-50% between November and April**
    - Maintain full fleet availability during peak months (**May through October**)
    - Implement gradual transition periods in spring and fall
    
    ### 2. High-Demand Station Optimization
    **Focus resources on consistently popular locations:**
    - Enhance maintenance schedules for the top 20 stations identified in our analysis
    - Implement predictive bike redistribution to high-demand areas
    - Deploy additional operational staff during peak usage hours
    
    ### 3. Strategic Geographic Expansion
    **Target high-potential areas for station deployment:**
    - Use geographic heat maps to identify underserved corridors
    - Focus expansion along high-traffic routes identified in the spatial analysis
    - Consider areas with growing residential and commercial development
    
    ### 4. Data-Driven Operations
    **Leverage analytics for operational efficiency:**
    - Develop predictive algorithms for bike availability forecasting
    - Implement dynamic pricing strategies to balance demand
    - Enhance real-time monitoring and redistribution systems
    """)
    
    st.markdown("""
    ## Expected Outcomes
    
    - **Significant reduction** in bike availability complaints during peak seasons
    - **Improved operational efficiency** through seasonal resource allocation
    - **Enhanced customer satisfaction** through better bike availability
    - **Strategic growth** through data-informed expansion decisions
    """)
    
    # Answer stakeholder questions proactively
    st.markdown("""
    ##  Addressing Key Stakeholder Questions
    
    **How much would you recommend scaling bikes back between November and April?**
    > Based on our temperature and usage correlation analysis, we recommend scaling back operations by 40-50% during the November-April period, with the most significant reductions in January and February when demand is lowest.
    
    **How could you determine how many more stations to add along the water?**
    > Using our geographic analysis and trip density patterns, we would identify high-demand corridors near waterways, analyze current station coverage gaps, and use spatial clustering to determine optimal locations for new station deployment.
    
    **What are some ideas for ensuring bikes are always stocked at the most popular stations?**
    > Implement predictive redistribution algorithms, dynamic pricing incentives for returning bikes to high-demand areas, enhanced maintenance schedules, and real-time monitoring systems with automated alerts for low inventory situations.
    """)

###############################################################
# FOOTER (Same as original)
###############################################################

st.sidebar.markdown("---")
st.sidebar.markdown("**NYC Citi Bike Analysis**")
st.sidebar.markdown("Data Source: NYC Citi Bike 2021-2022")
st.sidebar.markdown("Analysis Period: Jan 2021 - Dec 2022")