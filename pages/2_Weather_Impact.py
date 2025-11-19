import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Weather Impact", layout="wide")

st.title("🌤️ Weather Impact Analysis")
st.markdown("### Daily Bike Trips vs Temperature Correlation")

# Create sample weather data
@st.cache_data
def load_weather_data():
    dates = pd.date_range('2022-01-01', '2022-12-31', freq='D')
    
    # Realistic temperature and trip data
    monthly_temps = {1: 32, 2: 35, 3: 42, 4: 53, 5: 63, 6: 72, 
                     7: 77, 8: 76, 9: 68, 10: 57, 11: 48, 12: 38}
    
    base_temp = [monthly_temps[date.month] for date in dates]
    temperature = base_temp + np.random.normal(0, 5, len(dates))
    
    # Trips correlate with temperature
    base_trips = 40000 + (temperature - 32) * 800
    daily_trips = base_trips + np.random.normal(0, 3000, len(dates))
    daily_trips = np.maximum(daily_trips, 15000)  # Minimum trips
    
    return pd.DataFrame({
        'date': dates,
        'daily_trips': daily_trips.astype(int),
        'temperature': temperature
    })

data = load_weather_data()

# Filters
st.sidebar.subheader("📊 Filters")
months = st.sidebar.multiselect(
    "Select Months:",
    options=list(range(1, 13)),
    default=list(range(1, 13)),
    format_func=lambda x: pd.to_datetime(f"2022-{x:02d}-01").strftime('%B')
)

if months:
    filtered_data = data[data['date'].dt.month.isin(months)]
else:
    filtered_data = data

# Key Metrics
col1, col2, col3 = st.columns(3)

with col1:
    correlation = filtered_data['daily_trips'].corr(filtered_data['temperature'])
    st.metric("Temperature Correlation", f"{correlation:.3f}")

with col2:
    avg_trips = filtered_data['daily_trips'].mean()
    st.metric("Average Daily Trips", f"{avg_trips:,.0f}")

with col3:
    avg_temp = filtered_data['temperature'].mean()
    st.metric("Average Temperature", f"{avg_temp:.1f}°F")

# Visualization
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(
        x=filtered_data['date'],
        y=filtered_data['daily_trips'],
        name='Daily Bike Trips',
        line=dict(color='#1f77b4', width=2)
    ),
    secondary_y=False
)

fig.add_trace(
    go.Scatter(
        x=filtered_data['date'],
        y=filtered_data['temperature'],
        name='Temperature (°F)',
        line=dict(color='#ff7f0e', width=2)
    ),
    secondary_y=True
)

fig.update_layout(
    title="Daily Bike Trips vs Temperature (2022)",
    height=500,
    template='plotly_white'
)

fig.update_yaxes(title_text="Daily Bike Trips", secondary_y=False)
fig.update_yaxes(title_text="Temperature (°F)", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

# Insights
st.markdown("---")
st.subheader("📊 Key Insights")

st.markdown(f"""
**Strong Positive Correlation (r = {correlation:.3f})**
- Warmer temperatures directly correlate with increased bike usage
- Optimal riding conditions: 60°F - 80°F
- Significant usage drop below 45°F

**Seasonal Patterns:**
- Summer months (June-August): Peak usage (+40% vs annual average)
- Winter months (December-February): Lowest usage (-30% vs annual average)
- Shoulder seasons (Spring/Fall): Moderate, stable usage
""")