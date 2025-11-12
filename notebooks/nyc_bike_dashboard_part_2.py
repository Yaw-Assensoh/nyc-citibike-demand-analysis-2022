"""
Part_2 Streamlit dashboard for NYC Citi Bike Strategy
Uses relative dataset and map paths (../data/...) suitable for deployment to Streamlit Cloud.
This script is a refactor of the original dashboard into a multipage Streamlit app
with clearly separated pages: Intro, Line Chart, Top Stations, Map, Extra Analysis,
and Recommendations.

Author: Part_2 refactor
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# -------------------------------
# Relative paths (for Streamlit Cloud compatibility)
# -------------------------------
PATHS = {
    'map_html': '../data/maps/nyc_bike_trips_aggregated.html',
    'sample_csv': '../data/processed/nyc_citibike_2022_sample.csv',
    'processed_csv': '../data/processed/nyc_citibike_2022_processed.csv',
    'daily_agg': '../data/processed/daily_aggregated_data.csv',
    'top_routes': '../data/processed/top_routes_analysis.csv',
    'daily_agg_full': '../data/processed/daily_aggregated_data_full.csv',
    'station_pairs': '../data/processed/aggregated_station_pairs.csv',
    'station_activity_full': '../data/processed/station_activity_full.csv',
    'reduced_csv': '../data/processed/nyc_citibike_reduced.csv',
    'top_20': '../data/processed/top_20_stations.csv',
    'high_freq_routes': '../data/processed/high_frequency_routes.csv',
    'top_20_full': '../data/processed/top_20_stations_full.csv',
    'monthly_full': '../data/processed/monthly_trips_full.csv'
}

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(page_title='NYC Citi Bike Strategy Dashboard - Part 2', layout='wide')

st.title('NYC Citi Bike Strategy Dashboard — Part 2')

# Sidebar: pages
pages = [
    'Intro',
    'Daily Trips vs Temperature (Line Chart)',
    'Top 20 Stations (Bar Chart)',
    'Geographic Map (kepler.gl)',
    'Additional Analysis',
    'Recommendations'
]
page = st.sidebar.selectbox('Select a page', pages)

# Sidebar: data info and controls
st.sidebar.header('Data & Controls')
recreate_sample = st.sidebar.checkbox('Recreate sample from processed (if available)', value=False)

# -------------------------------
# Helper: load or create sample (must be under ~25 MB)
# -------------------------------
@st.cache_data
def load_or_create_sample(sample_path, processed_path, recreate=False, seed=32, max_mb=25):
    if os.path.exists(sample_path) and not recreate:
        df = pd.read_csv(sample_path, parse_dates=True)
        return df

    if os.path.exists(processed_path):
        df_full = pd.read_csv(processed_path)
        df_sample = df_full.sample(frac=0.02, random_state=seed)
        size_bytes = df_sample.memory_usage(deep=True).sum()
        est_csv_bytes = size_bytes * 1.5
        rows = df_sample.shape[0]
        while est_csv_bytes > max_mb * 1024 * 1024 and rows > 1000:
            rows = int(rows * 0.8)
            df_sample = df_sample.sample(n=rows, random_state=seed)
            size_bytes = df_sample.memory_usage(deep=True).sum()
            est_csv_bytes = size_bytes * 1.5
        df_sample.to_csv(sample_path, index=False)
        return df_sample

    raise FileNotFoundError(f"Neither sample nor processed file found: {sample_path} | {processed_path}")

# Load sample
df = pd.DataFrame()
try:
    df = load_or_create_sample(PATHS['sample_csv'], PATHS['processed_csv'], recreate=recreate_sample)
    st.sidebar.success("Sample loaded successfully.")
except Exception as e:
    st.sidebar.error(f"Could not load or create sample: {e}")

# Load supporting aggregated data
def safe_read_csv(p):
    try:
        return pd.read_csv(p, parse_dates=['date'] if 'daily' in os.path.basename(p) else None)
    except Exception:
        return None

daily_agg = safe_read_csv(PATHS['daily_agg']) or safe_read_csv(PATHS['daily_agg_full'])
top_20 = safe_read_csv(PATHS['top_20']) or safe_read_csv(PATHS['top_20_full'])

# -------------------------------
# Page Implementations
# -------------------------------

def intro_page():
    st.header('Introduction')
    st.markdown(
        """
        This dashboard provides actionable business intelligence for NYC Citi Bike.
        It identifies seasonal demand trends, top-performing stations, spatial trip patterns,
        and operational recommendations. The structure allows decision-makers to assess
        both short-term and strategic actions to enhance system efficiency.
        """
    )
    st.markdown('**Data sources:**')
    for k, p in PATHS.items():
        st.markdown(f'- `{k}`: `{p}`')


def line_chart_page():
    st.header('Daily Trips vs Temperature')
    st.markdown('Dual-axis chart illustrating the relationship between daily trips and temperature.')

    if daily_agg is None or daily_agg.empty:
        st.info('Daily aggregated data unavailable at configured paths.')
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=daily_agg['date'], y=daily_agg['daily_trips'], name='Daily Trips'), secondary_y=False)
    if 'temperature' in daily_agg.columns:
        fig.add_trace(go.Scatter(x=daily_agg['date'], y=daily_agg['temperature'], name='Temperature'), secondary_y=True)

    fig.update_layout(height=600, template='plotly_white')
    fig.update_yaxes(title_text='Daily Trips', secondary_y=False)
    fig.update_yaxes(title_text='Temperature (°F)', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('''
    **Interpretation:** Demand increases in warmer months, confirming a clear seasonal pattern.
    Operations should scale bikes back during colder months while ensuring sufficient supply on mild days.
    ''')


def bar_chart_page():
    st.header('Top 20 Most Popular Stations')
    st.markdown('Visualization of stations ranked by trip count.')

    if top_20 is None or top_20.empty:
        st.info('Top stations data unavailable.')
        return

    display = top_20.head(20)
    fig = go.Figure(go.Bar(x=display['start_station_name'], y=display['trip_count']))
    fig.update_layout(height=600, xaxis_tickangle=-45, template='plotly_white')
    fig.update_yaxes(title_text='Trips')
    fig.update_xaxes(title_text='Station')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('''
    **Interpretation:** The busiest stations are clustered near Midtown and transit hubs, suggesting
    targeted redistribution and maintenance prioritization for these high-traffic locations.
    ''')


def map_page():
    st.header('Geographic Distribution (kepler.gl)')
    st.markdown('Interactive visualization showing spatial patterns of aggregated trips.')

    map_path = PATHS['map_html']
    if os.path.exists(map_path):
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                html = f.read()
            st.components.v1.html(html, height=700, scrolling=True)
        except Exception as e:
            st.error(f'Error reading map HTML: {e}')
    else:
        st.info('Map HTML not found at configured path:')
        st.write(map_path)

    st.markdown('''
    **Interpretation:** Trip density is highest near the Hudson and East Rivers, indicating potential
    for additional stations along the waterfront to serve commuting and recreational demand.
    ''')


def extra_analysis_page():
    st.header('Additional Analysis: Peak Hours and Redistribution')
    st.markdown('This section provides insights into temporal demand variations for operational planning.')

    if df.empty:
        st.info('Sample data unavailable for additional analysis.')
        return

    if 'start_time' in df.columns:
        try:
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['hour'] = df['start_time'].dt.hour
            hourly = df.groupby('hour').size().reset_index(name='trips')
            fig = go.Figure(go.Bar(x=hourly['hour'], y=hourly['trips']))
            fig.update_layout(title='Trips by Hour (Sample)', xaxis_title='Hour of Day', yaxis_title='Trips')
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info('`start_time` column not suitable for hourly analysis.')
    else:
        st.info('Hourly analysis requires `start_time` column in the dataset.')

    st.markdown('''
    **Operational Recommendations:**
    - Schedule redistribution before morning (7–9 AM) and evening (4–7 PM) peaks.
    - Prioritize servicing top stations during low-demand hours.
    - Apply dynamic rebalancing to maintain consistent availability.
    ''')


def recommendations_page():
    st.header('Recommendations')
    st.markdown('''
    1. **Seasonal Scaling:** Reduce deployed bikes between November and April in alignment with demand patterns.
    2. **Station Expansion:** Add new stations along the waterfront corridors where persistent high trip densities are observed.
    3. **Redistribution Efficiency:** Implement pre-peak-hour redistribution to ensure station balance.
    4. **Maintenance Optimization:** Rotate maintenance schedules to minimize downtime at the top 20 busiest stations.
    5. **Dynamic Incentives:** Introduce return incentives to understocked stations during peak demand.
    ''')

# -------------------------------
# Page Routing
# -------------------------------
if page == 'Intro':
    intro_page()
elif page == 'Daily Trips vs Temperature (Line Chart)':
    line_chart_page()
elif page == 'Top 20 Stations (Bar Chart)':
    bar_chart_page()
elif page == 'Geographic Map (kepler.gl)':
    map_page()
elif page == 'Additional Analysis':
    extra_analysis_page()
elif page == 'Recommendations':
    recommendations_page()

# Sidebar footer
st.sidebar.markdown('---')
st.sidebar.markdown('Script: `nyc_bike_dashboard_Part_2.py` — Relative path version for Streamlit Cloud deployment.')
