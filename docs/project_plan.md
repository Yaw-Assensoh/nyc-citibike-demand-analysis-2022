# NYC CitiBike 2022 Demand Analysis - Project Plan

## Research Questions

### 1. Station Popularity & Distribution
**Question:** What are the most popular starting stations and are they evenly distributed?
**Visualization:** Bar chart showing top 15 stations by trip count

### 2. Seasonal & Temporal Patterns  
**Question:** How do ridership patterns change by month and season? Is there weather correlation?
**Visualization:** Line chart with dual y-axes showing monthly trips and average temperature

### 3. Route Analysis & Geographic Insights
**Question:** What are the most common bike routes between stations?
**Visualization:** Interactive map showing popular routes and station distribution

### 4. User Behavior Analysis
**Question:** What's the ratio of subscribers vs. casual users and how do their patterns differ?
**Visualization:** Pie charts and comparative bar charts by user type

## Data Loading Code Explanation

The data loading code uses several efficient techniques:

1. **List Comprehension with glob**: Discovers all CSV files matching patterns
2. **Generator Expression**: Efficiently reads files one at a time using `(pd.read_csv(f) for f in filepaths)`
3. **pd.concat()**: Vertically joins all dataframes while preserving column structure
4. **Error Handling**: Continues processing if individual files have issues

This approach is memory-efficient for large datasets and handles the split monthly files effectively.

## Methodology
- Data sourced from Citi Bike System Data (2022)
- Weather data integrated from NOAA API (LaGuardia Airport)
- Analysis conducted using Python pandas, matplotlib, seaborn, and plotly
- Dashboard built with Streamlit for stakeholder presentation

## GitHub Repository
https://github.com/Yaw-Assensoh/nyc-citibike-demand-analysis-2022