import streamlit as st

st.set_page_config(
    page_title="Urban Mobility Insights",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚲 Urban Mobility Insights")
st.markdown("### NYC Citi Bike Analysis 2022 - Interactive Dashboard")

st.markdown("""
Welcome to the interactive dashboard for analyzing NYC Citi Bike usage patterns, 
seasonal trends, and operational optimization opportunities.

**Use the sidebar to navigate between different analysis sections.**
""")

# Display key information
st.info("""
🔍 **Analysis Sections Available via Sidebar:**
- **Overview**: Executive summary and key metrics
- **Weather Impact**: Temperature and seasonal usage patterns  
- **Popular Stations**: Top stations and demand concentration
- **Spatial Analysis**: Geographic distribution and hotspots
- **Recommendations**: Strategic insights and solutions
""")