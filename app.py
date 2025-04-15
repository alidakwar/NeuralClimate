import streamlit as st
import pandas as pd
import numpy as np
import tempfile
import os
import requests

# Import backend modules
import machine_learning.ghcnd_fetch as fetch
import machine_learning.ghcnd_parse
import machine_learning.time_series as time_series
# Set up the page configuration
st.set_page_config(page_title="NeuralClimate", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for basic styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .big-font {
        font-size:20px;
    }
    .header {
        font-size:30px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Title and Introduction
st.title("NeuralClimate")
st.subheader("Climate Change Analysis and Forecasting")
st.markdown("""
NeuralClimate delivers climate data analysis by directly integrating backend functions.
This version uses real data from NOAA datasets and displays all processed data, with location selection based on U.S. states.
""")

########################################
# Utility Functions

def wrap_parser_with_tempfile(raw_data, parser_func):
    """
    Writes raw text data to a temporary file, calls the parser, then deletes the file.
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding="utf-8") as tmp:
            tmp.write(raw_data)
            tmp_path = tmp.name
        df = parser_func(tmp_path)
        os.unlink(tmp_path)
        return df
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

def get_countries_data():
    try:
        response = requests.get("https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt")
        response.raise_for_status()
        raw_data = response.text
        df_countries = wrap_parser_with_tempfile(raw_data, fetch.ghcnd_parse.parse_countries_file)
        return df_countries
    except Exception as e:
        st.error(f"Error fetching countries data: {e}")
        return None

def get_inventory_data():
    try:
        response = requests.get("https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt")
        response.raise_for_status()
        raw_data = response.text
        df_inventory = wrap_parser_with_tempfile(raw_data, fetch.ghcnd_parse.parse_inventory_file)
        # Filter by 5 main elements (TMAX, TMIN, PRCP, SNOW, SNWD)
        # TODO: filter this by the selected state and forecast type
        df_inventory = df_inventory[df_inventory['element'].isin(['TMAX', 'TMIN', 'PRCP', 'SNOW', 'SNWD'])]

        return df_inventory
    except Exception as e:
        st.error(f"Error fetching inventory data: {e}")
        return None

def get_states_data():
    try:
        response = requests.get("https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-states.txt")
        response.raise_for_status()
        raw_data = response.text
        df_states = wrap_parser_with_tempfile(raw_data, fetch.ghcnd_parse.parse_states_file)
        return df_states
    except Exception as e:
        st.error(f"Error fetching states data: {e}")
        return None

def get_stations_data():
    try:
        df_stations = fetch.get_ghcnd_stations()
        return df_stations
    except Exception as e:
        st.error(f"Error fetching stations data: {e}")
        return None

def get_station_data(station_id):
    try:
        df_station = fetch.get_ghcnd_data_by_station(station_id)
        return df_station
    except Exception as e:
        st.error(f"Error fetching data for station {station_id}: {e}")
        return None

########################################
# Sidebar Configuration

st.sidebar.header("Configuration Options")
time_period = st.sidebar.slider("Select Time Period (Years from now)", min_value=1, max_value=100, value=10)

# Load states data (use caching if desired)
@st.cache_data(show_spinner=False)
def load_states():
    return get_states_data()

states_df = load_states()
if states_df is not None and not states_df.empty:
    # Build a mapping between state name and state code
    state_map = {row["state_name"]: row["state_code"] for _, row in states_df.iterrows()}
    state_names = list(state_map.keys())
    # Default to Texas if available
    default_index = state_names.index("Texas") if "Texas" in state_names else 0
    selected_state = st.sidebar.selectbox("Select U.S. State", state_names, index=default_index)
    selected_state_code = state_map[selected_state]
else:
    st.sidebar.error("Failed to load states data.")
    selected_state = None
    selected_state_code = None

# TODO: update this to use 5 main elements
forecast_type = st.sidebar.radio(
    "Forecast Type",
    (
        "Maximum Temperature (TMAX)",
        "Minimum Temperature (TMIN)",
        "Precipitation (PRCP)",
        "Snowfall (SNOW)",
        "Snow Depth (SNWD)",
    ),
)


# # Display a map of stations from the inventory data
# st.markdown("### Station Map")

# # Load inventory data
# df_inventory = get_inventory_data()
# if df_inventory is not None and not df_inventory.empty:
#     # Ensure latitude and longitude columns are present
#     if "latitude" in df_inventory.columns and "longitude" in df_inventory.columns:
#         # Map forecast type to colors
#         color_map = {
#             "TMAX": "red",
#             "TMIN": "blue",
#             "PRCP": "green",
#             "SNOW": "purple",
#             "SNWD": "orange",
#         }
#         df_inventory["color"] = df_inventory["element"].map(color_map)

#         # Display map
#         st.map(df_inventory[["latitude", "longitude"]])

#         # Add legend
#         st.markdown("#### Legend")
#         for element, color in color_map.items():
#             st.markdown(f"<span style='color:{color};'>⬤</span> {element}", unsafe_allow_html=True)

#         # Allow station selection by clicking
#         selected_station = st.selectbox(
#             "Select a Station by ID",
#             df_inventory["id"].unique(),
#             format_func=lambda x: f"{x} ({df_inventory[df_inventory['id'] == x]['element'].iloc[0]})"
#         )
#     else:
#         st.error("Inventory data is missing latitude or longitude columns.")
# else:
#     st.error("Failed to load inventory data.")
########################################
# Display Backend Data

st.markdown("## Backend Data Integration (For Demo Purposes)")
st.write("Data sets parsed from NOAA through backend functions:")

# Countries Data
if st.button("Load Countries Data"):
    df_countries = get_countries_data()
    if df_countries is not None:
        st.write("### Countries Data", df_countries)
    else:
        st.error("Failed to load countries data.")

# Inventory Data
if st.button("Load Inventory Data"):
    df_inventory = get_inventory_data()
    if df_inventory is not None:
        st.write("### Inventory Data", df_inventory)
    else:
        st.error("Failed to load inventory data.")

# States Data
if st.button("Load States Data"):
    df_states = get_states_data()
    if df_states is not None:
        st.write("### States Data", df_states)
    else:
        st.error("Failed to load states data.")

# Stations Data (filtered by selected state)
if st.button("Load Stations Data"):
    df_stations = get_stations_data()
    if df_stations is not None:
        if selected_state_code:
            df_stations = df_stations[df_stations["STATE"] == selected_state_code]
        st.write(f"### Stations Data for {selected_state}", df_stations)
    else:
        st.error("Failed to load stations data.")

# Daily Data for a Selected Station
st.markdown("### Daily Data for a Selected Station")

# Fetch stations data
df_stations = get_stations_data()
if df_stations is not None:
    # If a state is selected, filter the stations by state code
    if selected_state_code:
        df_stations = df_stations[df_stations["STATE"] == selected_state_code]
    
    if not df_stations.empty:
        # Create dropdown options that combine Station ID with its NAME (location info)
        station_options = df_stations.apply(lambda row: f"{row['ID']} - {row['NAME']}", axis=1).tolist()
        selected_station = st.selectbox("Select a Station", station_options)
    
        if st.button("Load Station Daily Data"):
            # The station ID is the first part of the selected string
            station_id = selected_station.split(" - ")[0].strip()
            if not station_id:
                st.error("Please select a valid station.")
            else:
                df_station = get_station_data(station_id)
                if df_station is not None and not df_station.empty:
                    st.write(f"### Daily Data for Station {station_id}", df_station)
                else:
                    st.error(f"No daily data found for station {station_id} or an error occurred.")
    else:
        st.error("No stations available for the selected state.")
else:
    st.error("Failed to load stations data.")


########################################
# Forecast Simulation Section
st.markdown("### Visualize Station Data")

if df_stations is not None and not df_stations.empty:
    if selected_station:
        station_id = selected_station.split(" - ")[0].strip()
        df_station = get_station_data(station_id)
        if df_station is not None and not df_station.empty:
            # Filter data for visualization
            df_station = df_station[df_station['element'] == 'TMAX']
            cleaned_df_station = time_series.clean_data(df_station)
            st.line_chart(cleaned_df_station, y='value', use_container_width=True)
        else:
            st.error("Failed to fetch or process station data.")
    else:
        st.error("Please select a station to visualize data.")
else:
    st.error("No stations data available.")


# Generate predictions for the next 12 months using the time series model
if df_station is not None and not df_station.empty:
    try:
        # Clean and prepare the data for the time series model
        cleaned_df_station = time_series.clean_data(df_station)
        predictions = time_series.predict_time_series(cleaned_df_station)

        # Create a DataFrame for the predictions
        prediction_months = pd.date_range(start=cleaned_df_station.index[-1], periods=12, freq='M')
        prediction_df = pd.DataFrame({"Month": prediction_months, "Predicted Value": predictions}).set_index("Month")

        # Plot the predictions
        st.markdown("### Predictions for the Next 12 Months")
        st.line_chart(prediction_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating predictions: {e}")
else:
    st.error("No station data available for predictions.")


# Experimental feature meant to compare actual values with our predicted values, not completed yet!
# Compute dynamic Average Temperature from the selected station's data (TMAX)
# avg_temp = "N/A"  # Default value in case data is missing
# if df_station is not None and not df_station.empty:
# Filter data for TMAX measurements
#    temp_data = df_station[df_station['element'] == 'TMAX']
#    if not temp_data.empty:
#        # Choose the most recent year available
#        most_recent_year = temp_data['year'].max()
#        recent_temp_data = temp_data[temp_data['year'] == most_recent_year]
#        # Calculate the average temperature and convert from tenths of °C to °C
#        avg_temp_value = recent_temp_data['value'].mean() / 10
#        avg_temp = round(avg_temp_value, 2)

# st.markdown("## Regional Climate Analysis")
# st.markdown(f"Analysis based on selected station: {selected_station}")
# results = pd.DataFrame({
#    "Metric": ["Average Temperature", "Flood Risk", "CO2 Levels"],
#    "Current": [avg_temp, 1.2, 410],
#    "Predicted": [
#        chart_data[y_label].iloc[-1] if forecast_type in ["Temperature", "Combined"] else 16,
#        chart_data[y_label].iloc[-1] if forecast_type == "Flood Risk" else 1.5,
#        chart_data[y_label].iloc[-1] if forecast_type == "CO2 Levels" else 420
#    ]
# })
# st.table(results)

# st.markdown("### Future Projection Comparison")
# if forecast_type == "Combined":
#     metrics = ["Temperature", "Flood Risk", "CO2 Levels"]
#     projections = [chart_data[y_label].iloc[-1] + np.random.uniform(-1, 1) for _ in metrics]
#     comparison_df = pd.DataFrame({
#         "Metric": metrics,
#         "Projection": projections
#     }).set_index("Metric")
#     st.bar_chart(comparison_df)
# else:
#     st.markdown("Select 'Combined' forecast type in the sidebar to see a multi-metric comparison chart.")

st.markdown("### About NeuralClimate")
st.markdown("""
NeuralClimate integrates historical climate data and sophisticated statistical modeling
to deliver insightful projections. This version directly leverages backend functions for data integration,
including state-based filtering of station data.
""")
