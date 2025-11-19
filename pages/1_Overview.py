import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Overview", layout="wide")

st.title("🏠 Executive Overview")
st.markdown("### Key Performance Indicators and Business Context")

# Load data function (we'll improve this later)
@st.cache_data
def load_overview_data():
    # Sample data - replace with your actual data loading
    dates = pd.date_range('2022-01-01', '2022-12-31', freq='D')
    daily_trips = np.random.randint(30000, 80000, len(dates))
    
    return pd.DataFrame({
        'date': dates,
        'daily_trips': daily_trips
    })

data = load_overview_data()

# Key Metrics
st.markdown("---")
st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_trips = data['daily_trips'].sum()
    st.metric("Total Trips (2022)", f"{total_trips:,}")

with col2:
    avg_daily = data['daily_trips'].mean()
    st.metric("Average Daily Trips", f"{avg_daily:,.0f}")

with col3:
    peak_daily = data['daily_trips'].max()
    st.metric("Peak Daily Trips", f"{peak_daily:,}")

with col4:
    st.metric("Analysis Period", "Full Year 2022")

# Business Context
st.markdown("---")
st.subheader("🎯 Business Challenge")

st.markdown("""
NYC Citi Bike is experiencing customer complaints about bike availability issues during peak hours and in high-demand areas. 
This comprehensive analysis examines usage patterns, seasonal impacts, and geographic distribution to provide data-driven solutions.

**Primary Objectives:**
- Identify patterns in bike usage and demand fluctuations
- Understand seasonal and weather impacts on ridership  
- Pinpoint high-demand stations and usage corridors
- Provide strategic recommendations for operational optimization
""")

# Navigation Guide
st.markdown("---")
st.subheader("🧭 Dashboard Navigation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🌤️ Weather Impact Analysis**
    - Temperature and seasonal usage patterns
    - Correlation between weather and ridership
    - Seasonal scaling recommendations
    
    **📍 Popular Stations**  
    - Top 20 stations by usage volume
    - Demand concentration analysis
    - Maintenance prioritization
    """)

with col2:
    st.markdown("""
    **🗺️ Spatial Analysis**
    - Geographic distribution of trips
    - Station density mapping
    - Expansion opportunity identification
    
    **💡 Recommendations**
    - Data-driven strategic solutions
    - Operational optimization plans
    - Stakeholder Q&A
    """)