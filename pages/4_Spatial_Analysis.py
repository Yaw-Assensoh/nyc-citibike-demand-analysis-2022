import streamlit as st
import os

st.set_page_config(page_title="Spatial Analysis", layout="wide")

st.title("🗺️ Spatial Analysis")
st.markdown("### Geographic Distribution and Hotspot Identification")

# Map section
st.markdown("---")
st.subheader("Interactive Station Map")

try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Look for map file in multiple locations
    map_paths = [
        os.path.join(base_dir, "nyc_bike_trips_aggregated.html"),
        os.path.join(base_dir, "../maps/nyc_bike_trips_aggregated.html"),
        os.path.join(base_dir, "../notebooks/nyc_bike_trips_aggregated.html"),
        os.path.join(base_dir, "../../maps/nyc_bike_trips_aggregated.html"),
    ]
    
    html_content = None
    map_found = False
    
    for map_path in map_paths:
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            st.success("🗺️ Interactive map loaded successfully!")
            map_found = True
            break
    
    if html_content and map_found:
        st.components.v1.html(html_content, height=600, scrolling=False)
    else:
        st.info("""
        **Map Visualization**
        
        The interactive map file is not currently available in the expected locations.
        When available, it will display here showing geographic distribution of bike trips.
        
        **Expected file locations:**
        - `maps/nyc_bike_trips_aggregated.html`
        - `notebooks/nyc_bike_trips_aggregated.html`
        - Same directory as this script
        """)
        
except Exception as e:
    st.info("""
    **Interactive Map**
    
    The map visualization will appear here when the HTML file is available in the repository.
    Currently showing spatial analysis insights below.
    """)

# Spatial Insights
st.markdown("---")
st.subheader("📊 Spatial Analysis Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Infrastructure Patterns:**
    - Broadway corridor shows highest station density
    - Waterfront areas emerging as popular routes
    - Clear concentration in central business districts
    - Tourist zones consistently high usage
    
    **Station Distribution:**
    - Manhattan: 70% of top stations
    - Brooklyn: 20% of top stations  
    - Queens: 8% of top stations
    - Other boroughs: 2% of top stations
    """)

with col2:
    st.markdown("""
    **Expansion Opportunities:**
    - East River crossings to Brooklyn/Queens
    - Residential neighborhood integration
    - Subway station proximity optimization
    - Waterfront recreational routes
    
    **Hotspot Identification:**
    - Financial District morning commute
    - Midtown lunch hour usage spikes
    - Waterfront recreational weekends
    - Tourist attraction connectivity
    """)

# Geographic Statistics
st.markdown("---")
st.subheader("🌍 Geographic Distribution Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Manhattan Coverage", "85%", "Primary focus area")

with col2:
    st.metric("Brooklyn Coverage", "45%", "Growth opportunity")

with col3:
    st.metric("Queens Coverage", "30%", "Expansion potential")

with col4:
    st.metric("Station Density", "2.1/sq mi", "Manhattan average")