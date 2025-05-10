import streamlit as st
import pandas as pd
import numpy as np

# Set up the page configuration
st.set_page_config(page_title="NeuralClimate", layout="wide", initial_sidebar_state="expanded")

# Optional: Custom CSS to enhance visual appeal
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .big-font {
        font-size:20px 
    }
    .header {
        font-size:30px 
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Title and Description
st.title("NeuralClimate")
st.subheader("Climate Change Analysis and Forecasting")

st.markdown("""
NeuralClimate is a cutting-edge web application that provides in-depth climate change analysis and forecasts future trends. Leveraging historical data and advanced modeling techniques—including machine learning and traditional regression—NeuralClimate predicts patterns such as temperature increases, rising flood risks, and other significant environmental shifts.
""")

st.markdown("### Explore the Future Climate Trends")
st.markdown("Use the sidebar to select different time periods, regions, and forecast parameters to generate intuitive visualizations.")

# Sidebar configuration
st.sidebar.header("Configuration Options")

# Time period selection: number of years for projection
time_period = st.sidebar.slider("Select Time Period (Years from now)", min_value=1, max_value=100, value=10)

# Region selection
region = st.sidebar.selectbox("Select Region", 
                              ["Global", "North America", "Europe", "Asia", "Africa", "South America", "Oceania"])

# Forecast type selection
forecast_type = st.sidebar.radio("Forecast Type", ("Temperature", "Flood Risk", "CO2 Levels", "Combined"))

# Generate dummy data for the line chart based on forecast type
years = np.arange(2020, 2020 + time_period)
if forecast_type == "Temperature":
    # Simulate a gradual temperature increase with noise
    data = np.linspace(15, 15 + 0.03 * time_period, time_period) + np.random.normal(0, 0.5, time_period)
    y_label = "Temperature (°C)"
elif forecast_type == "Flood Risk":
    # Simulate a risk score increasing over time
    data = np.linspace(1, 1 + 0.05 * time_period, time_period) + np.random.normal(0, 0.1, time_period)
    y_label = "Flood Risk Score"
elif forecast_type == "CO2 Levels":
    # Simulate rising CO2 levels in parts per million
    data = np.linspace(400, 400 + 2 * time_period, time_period) + np.random.normal(0, 5, time_period)
    y_label = "CO2 (ppm)"
else:
    # For combined, we'll default to a temperature-like metric for the main chart
    data = np.linspace(15, 15 + 0.03 * time_period, time_period) + np.random.normal(0, 0.5, time_period)
    y_label = "Combined Metric"

# Create a DataFrame for the chart and display the line chart
chart_data = pd.DataFrame({
    "Year": years,
    y_label: data
}).set_index("Year")

st.line_chart(chart_data)

# Regional Climate Analysis Section
st.markdown("## Regional Climate Analysis")
st.markdown(f"Analysis for: **{region}**")

# Create a dummy results table for demonstration purposes
results = pd.DataFrame({
    "Metric": ["Average Temperature", "Flood Risk", "CO2 Levels"],
    "Current": [15, 1.2, 410],
    "Predicted": [
        chart_data[y_label].iloc[-1] if forecast_type in ["Temperature", "Combined"] else 16, 
        chart_data[y_label].iloc[-1] if forecast_type == "Flood Risk" else 1.5, 
        chart_data[y_label].iloc[-1] if forecast_type == "CO2 Levels" else 420
    ]
})
st.table(results)

# Additional Graphs Section: Multi-metric comparison when "Combined" is selected
st.markdown("### Future Projection Comparison")
if forecast_type == "Combined":
    metrics = ["Temperature", "Flood Risk", "CO2 Levels"]
    # Create dummy projections for each metric with slight variations
    projections = [chart_data[y_label].iloc[-1] + np.random.uniform(-1, 1) for _ in metrics]
    comparison_df = pd.DataFrame({
        "Metric": metrics,
        "Projection": projections
    }).set_index("Metric")
    st.bar_chart(comparison_df)
else:
    st.markdown("Select 'Combined' forecast type in the sidebar to see a multi-metric comparison chart.")

# About Section
st.markdown("### About NeuralClimate")
st.markdown("""
NeuralClimate leverages historical climate data and sophisticated statistical modeling techniques to deliver insightful projections. This application is designed to empower researchers, policymakers, and the public with tools to assess regional climate risks and prepare for future environmental changes.
""")
