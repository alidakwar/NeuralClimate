import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
scripts_dir = Path(__file__).resolve().parent / "scripts"
sys.path.append(str(scripts_dir))

# Define data directory paths
DATA_DIR = Path(__file__).resolve().parent / "data"
COUNTIES_DIR = DATA_DIR / "counties"
STATIONS_DIR = DATA_DIR / "stations"

import streamlit as st
import pandas as pd
import numpy as np
import tempfile
import requests
from datetime import datetime, timedelta
import folium
from folium import plugins
import geopandas as gpd
from streamlit_folium import folium_static
import warnings
import plotly.graph_objects as go
import plotly.express as px

# Suppress future warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Import backend modules
from ml.ghcnd_fetch import get_ghcnd_stations, get_ghcnd_data_by_station
from ml.ghcnd_parse import dly_to_dataframe_from_lines
from ml.time_series import clean_data, predict_time_series, validate_time_series_data


def get_available_elements(df_station, main_only=False):
    """Get available forecast types for the station."""
    if df_station is None or df_station.empty or 'element' not in df_station.columns:
        return []
    
    # Get unique elements from the dataframe
    available_elements = df_station['element'].unique()
    
    # Map element codes to display names
    element_map = {
        "TMAX": "Maximum Temperature (TMAX)",
        "TMIN": "Minimum Temperature (TMIN)",
        "PRCP": "Precipitation (PRCP)",
        "SNOW": "Snowfall (SNOW)",
        "SNWD": "Snow Depth (SNWD)",
        "AWND": "Average Wind Speed (AWND)",
        "PGTM": "Peak Gust Time (PGTM)",
        "PSUN": "Percent of Possible Sunshine (PSUN)",
        "TSUN": "Total Sunshine (TSUN)",
        "WESD": "Water Equivalent of Snow on Ground (WESD)",
        "WESF": "Water Equivalent of Snowfall (WESF)"
    }
    
    # Filter to only include the main elements we want
    if main_only:
        filtered_elements = ["TMAX", "TMIN", "PRCP", "SNOW", "SNWD"]
        available_elements = [e for e in available_elements if e in filtered_elements]
    
    # Map codes to display names, only for elements that have a mapping
    return [element_map.get(e, e) for e in available_elements if e in element_map]

@st.cache_data(show_spinner=False)
def load_county_boundaries():
    """Load Texas county boundaries from local GeoJSON file."""
    try:
        import json
        
        # Load the GeoJSON file
        with open(COUNTIES_DIR / "counties.geojson", 'r') as f:
            geojson_data = json.load(f)
        
        # Load the CSV file with additional county information
        county_info = pd.read_csv(COUNTIES_DIR / "counties.csv")
        
        # Create a dictionary to store the merged data
        features = []
        for feature in geojson_data['features']:
            county_name = feature['properties']['CNTY_NM']
            # Find matching county info using 'County Name' column
            county_data = county_info[county_info['County Name'] == county_name]
            if not county_data.empty:
                # Update properties with additional info
                feature['properties'].update({
                    'AREA_SQ_MI': county_data['Shape__Area'].iloc[0] if 'Shape__Area' in county_data.columns else 'N/A'
                })
            features.append(feature)
        
        # Create new GeoJSON with merged data
        merged_geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        return merged_geojson
    except Exception as e:
        st.error(f"Error loading county boundaries: {str(e)}")
        return None

@st.cache_data(show_spinner=False)
def get_stations_in_county(county_name):
    """Get all stations within a county."""
    try:
        # Only handle Dallas county now
        if county_name.upper() != "DALLAS":
            st.error("Only Dallas County data is available")
            return None
        
        try:
            # Read from the metadata file
            stations_df = pd.read_csv(DATA_DIR / "dallas_stations_metadata.csv")
            return stations_df
        except Exception as e:
            st.error(f"Error reading Dallas stations metadata: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"Error getting stations in county: {str(e)}")
        return None

def create_county_map(selected_station_id=None):
    """Create a Folium map with Texas county boundaries."""
    # Load county boundaries
    counties = load_county_boundaries()
    if counties is None:
        return None
    
    # Dallas County coordinates
    dallas_center = [32.7767, -96.7970]  # Dallas, TX coordinates
    
    # Create a map centered on Dallas
    m = folium.Map(location=dallas_center, zoom_start=9)
    
    # Create the GeoJson layer
    geojson_layer = folium.GeoJson(
        counties,
        name='Texas Counties',
        style_function=lambda x: {
            'fillColor': '#ff0000' if x['properties']['CNTY_NM'] == "Dallas" else '#ffffff',
            'color': '#000000',
            'weight': 1,
            'fillOpacity': 0.3 if x['properties']['CNTY_NM'] == "Dallas" else 0.1
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['CNTY_NM', 'AREA_SQ_MI'],
            aliases=['County: ', 'Area (sq mi): '],
            localize=True
        ),
        popup=folium.GeoJsonPopup(
            fields=['CNTY_NM', 'AREA_SQ_MI'],
            aliases=['County: ', 'Area (sq mi): '],
            localize=True
        )
    )
    
    # Add the layer to the map
    geojson_layer.add_to(m)
    
    # If Dallas County is selected, add its stations to the map
    stations_df = get_stations_in_county("Dallas")
    if stations_df is not None and not stations_df.empty:
        # Add stations as markers
        for _, station in stations_df.iterrows():
            is_selected = selected_station_id and station['ID'] == selected_station_id
            folium.CircleMarker(
                location=[station['LATITUDE'], station['LONGITUDE']],
                radius=6 if is_selected else 3,  # Larger radius for selected station
                color='blue' if is_selected else 'red',  # Different color for selected station
                fill=True,
                fill_color='blue' if is_selected else 'red',
                popup=f"Station: {station['ID']}<br>Name: {station['NAME']}"
            ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

@st.cache_data(show_spinner=False)
def load_dallas_data():
    """Load Dallas County station data from CSV."""
    try:
        return pd.read_csv(DATA_DIR / "dallas_stations_data.csv")
    except Exception as e:
        st.error(f"Error loading Dallas data: {str(e)}")
        return None

@st.cache_data(show_spinner=False)
def load_model(element_type):
    """Load the appropriate model for the given element type."""
    try:
        model_path = f"models/{element_type}_best_model.pkl"
        if not os.path.exists(model_path):
            return None
        import pickle
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading model for {element_type}: {str(e)}")
        return None

def create_forecast_plot(df, element_type, time_period):
    """Create a forecast plot for the given data and element type."""
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Prepare data for plotting
    chart_data = df.copy()
    
    # Customize chart based on element type
    if element_type in ["TMAX", "TMIN"]:
        y_axis_label = "Temperature (°C)"
        y_axis_range = [
            chart_data['value'].min() - 5, 
            chart_data['value'].max() + 5
        ]
    elif element_type == "PRCP":
        y_axis_label = "Precipitation (mm)"
        y_axis_range = [0, chart_data['value'].max() * 1.2]
    elif element_type == "SNOW":
        y_axis_label = "Snowfall (mm)"
        y_axis_range = [0, chart_data['value'].max() * 1.2]
    else:
        y_axis_label = f"{element_type} Value"
        y_axis_range = None
    
    # Create the plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['value'],
        mode='lines',
        name=element_type,
        line=dict(color='#1f77b4', width=2)
    ))
    
    if y_axis_range:
        fig.update_layout(yaxis_range=y_axis_range)
    
    fig.update_layout(
        title=f"{element_type} Over Time",
        xaxis_title="Date",
        yaxis_title=y_axis_label,
        template="plotly_white",
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def display_statistics(df, element_type):
    """Display statistics for the given data and element type."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if element_type in ["TMAX", "TMIN"]:
            st.metric(
                f"Average {element_type}",
                f"{df['value'].mean():.2f}°C",
                f"{df['value'].mean() - df['value'].iloc[0]:.2f}°C"
            )
        elif element_type == "PRCP":
            st.metric(
                f"Average {element_type}",
                f"{df['value'].mean():.2f} mm",
                f"{df['value'].mean() - df['value'].iloc[0]:.2f} mm"
            )
        elif element_type == "SNOW":
            st.metric(
                f"Average {element_type}",
                f"{df['value'].mean():.2f} mm",
                f"{df['value'].mean() - df['value'].iloc[0]:.2f} mm"
            )
        else:
            st.metric(
                f"Average {element_type}",
                f"{df['value'].mean():.2f}",
                f"{df['value'].mean() - df['value'].iloc[0]:.2f}"
            )
    
    with col2:
        if element_type in ["TMAX", "TMIN"]:
            st.metric(
                f"Maximum {element_type}",
                f"{df['value'].max():.2f}°C",
                f"{df['value'].max() - df['value'].mean():.2f}°C"
            )
        elif element_type == "PRCP":
            st.metric(
                f"Maximum {element_type}",
                f"{df['value'].max():.2f} mm",
                f"{df['value'].max() - df['value'].mean():.2f} mm"
            )
        elif element_type == "SNOW":
            st.metric(
                f"Maximum {element_type}",
                f"{df['value'].max():.2f} mm",
                f"{df['value'].max() - df['value'].mean():.2f} mm"
            )
        else:
            st.metric(
                f"Maximum {element_type}",
                f"{df['value'].max():.2f}",
                f"{df['value'].max() - df['value'].mean():.2f}"
            )
    
    with col3:
        if element_type in ["TMAX", "TMIN"]:
            st.metric(
                f"Minimum {element_type}",
                f"{df['value'].min():.2f}°C",
                f"{df['value'].min() - df['value'].mean():.2f}°C"
            )
        elif element_type == "PRCP":
            st.metric(
                f"Minimum {element_type}",
                f"{df['value'].min():.2f} mm",
                f"{df['value'].min() - df['value'].mean():.2f} mm"
            )
        elif element_type == "SNOW":
            st.metric(
                f"Minimum {element_type}",
                f"{df['value'].min():.2f} mm",
                f"{df['value'].min() - df['value'].mean():.2f} mm"
            )
        else:
            st.metric(
                f"Minimum {element_type}",
                f"{df['value'].min():.2f}",
                f"{df['value'].min() - df['value'].mean():.2f}"
            )

def display_predictions(cleaned_df, predictions, element_type, forecast_type, y_axis_label):
    """Display predictions with visualization and statistics."""
    if predictions is not None:
        # Get last 5 years of data
        five_years_ago = cleaned_df.index[-1] - pd.DateOffset(years=5)
        recent_data = cleaned_df[cleaned_df.index >= five_years_ago]
        
        # Create prediction plot
        pred_fig = go.Figure()
        
        # Combine historical and prediction data for a smooth transition
        # Include the last historical point in the prediction trace
        historical_trace = go.Scatter(
            x=recent_data.index,
            y=recent_data['value'],
            mode='lines',
            name='Historical (Last 5 Years)',
            line=dict(color='#1f77b4', width=2)
        )
        
        prediction_trace = go.Scatter(
            x=[recent_data.index[-1]] + list(predictions.index),  # Include last historical point
            y=[recent_data['value'].iloc[-1]] + list(predictions.values),  # Include last historical value
            mode='lines',
            name='Prediction',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        )
        
        # Add traces to figure
        pred_fig.add_trace(historical_trace)
        pred_fig.add_trace(prediction_trace)
        
        # Update layout
        pred_fig.update_layout(
            title=f"{forecast_type} Predictions",
            xaxis_title="Date",
            yaxis_title=y_axis_label,
            template="plotly_white",
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        # Display the prediction chart
        st.plotly_chart(pred_fig, use_container_width=True)
        
        # Calculate sMAPE for the overlapping period
        last_historical = recent_data['value'].iloc[-1]
        first_prediction = predictions.iloc[0]
        smape = 200 * abs(first_prediction - last_historical) / (abs(last_historical) + abs(first_prediction))
        
        # Display prediction statistics
        st.subheader("Prediction Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Predicted Average",
                f"{predictions.mean():.2f}",
                f"{predictions.mean() - recent_data['value'].mean():.2f}"
            )
        with col2:
            st.metric(
                "Predicted Change",
                f"{predictions.iloc[-1] - predictions.iloc[0]:.2f}",
                "Total Change"
            )
        with col3:
            st.metric(
                "Transition sMAPE",
                f"{smape:.2f}%",
                "Forecast Accuracy"
            )
    else:
        st.warning("No predictions were generated")

# Set up the page configuration
st.set_page_config(
    page_title="NeuralClimate",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("NeuralClimate - Texas Climate Analysis")
    
    # Initialize session state
    if 'current_station' not in st.session_state:
        st.session_state.current_station = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None
    if 'available_elements' not in st.session_state:
        st.session_state.available_elements = []
    if 'forecast_type' not in st.session_state:
        st.session_state.forecast_type = None
    if 'last_station' not in st.session_state:
        st.session_state.last_station = None

    # Sidebar Configuration
    with st.sidebar:
        st.header("Configuration")

        # Time period selection
        time_period = st.slider(
            "Select Time Period (Months from now)",
            min_value=1,
            max_value=100,
            value=10,
            key="time_period"
        )

        # Load Dallas stations with caching
        @st.cache_data(show_spinner=True)
        def load_dallas_stations():
            try:
                return pd.read_csv(DATA_DIR / "dallas_stations_metadata.csv")
            except Exception as e:
                st.error(f"Error loading Dallas stations: {str(e)}")
                return None

        # Load station data with caching
        @st.cache_data(show_spinner=True)
        def load_station_data(station_id):
            try:
                # Try to load from local file first
                try:
                    data = pd.read_csv(STATIONS_DIR / f"{station_id}_data.csv")
                    if data is None or data.empty:
                        st.error(f"No data found for station {station_id}")
                        return None
                    
                    # Convert date to datetime if it's not already
                    date_col = 'DATE' if 'DATE' in data.columns else 'date'
                    if not pd.api.types.is_datetime64_any_dtype(data[date_col]):
                        data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
                    
                    # Set date as index and keep value and element columns
                    data = data.set_index(date_col)[['value', 'element']]
                    
                    return data
                    
                except FileNotFoundError:
                    st.error(f"Data file not found for station {station_id}")
                    return None
                except Exception as e:
                    st.error(f"Error loading local station data: {str(e)}")
                    return None
            except Exception as e:
                st.error(f"Error loading station data: {str(e)}")
                return None

        # Station selection
        with st.spinner("Loading Dallas stations..."):
            df_stations = load_dallas_stations()
            if df_stations is None or df_stations.empty:
                st.error("Failed to load Dallas stations. Please ensure the data files are present.")
                st.stop()

        # Add "Entire County" option at the top
        station_options = ["Entire County"] + df_stations.apply(
            lambda row: f"{row['ID']} - {row['NAME']} ({row['STATE']})",
            axis=1
        ).tolist()

        selected_station = st.selectbox(
            "Select a Station",
            station_options,
            key="station_select"
        )

        if not selected_station:
            st.error("Please select a station")
            st.stop()

        # Handle "Entire County" selection
        if selected_station == "Entire County":
            station_id = "ENTIRE_COUNTY"
            # Load consolidated county data
            df_station = load_dallas_data()
            # For entire county, we'll use the main elements only
            available_elements = get_available_elements(df_station, main_only=True)
        else:
            station_id = selected_station.split(" - ")[0].strip()
            # Load individual station data
            df_station = load_station_data(station_id)
            # For individual stations, show all available elements
            available_elements = get_available_elements(df_station, main_only=True)

        if df_station is None or df_station.empty:
            st.error("Failed to load data. Please try again.")
            st.stop()

        # Check if station has changed and reset forecast type if needed
        if st.session_state.last_station != station_id:
            st.session_state.forecast_type = None
            st.session_state.last_station = station_id

        st.session_state.current_station = station_id
        st.session_state.current_data = df_station
        st.session_state.available_elements = available_elements

        if not available_elements:
            st.error("No forecast data available")
            st.stop()

        # Forecast type selection
        forecast_type = st.radio(
            "Forecast Type",
            available_elements,
            key="forecast_type",
            index=0 if st.session_state.forecast_type not in available_elements else available_elements.index(st.session_state.forecast_type)
        )
    
    # Create tabs
    tab1, tab2 = st.tabs(["Weather Predictions", "About"])
    
    with tab1:
        st.header("Dallas County Weather Analysis")
        
        # Create and display the county map first
        county_map = create_county_map(station_id if station_id != "ENTIRE_COUNTY" else None)
        if county_map is not None:
            folium_static(county_map)
        else:
            st.error("Failed to load county boundaries. Please try again later.")
        
        # Display analysis title based on selection
        if station_id == "ENTIRE_COUNTY":
            st.subheader("Dallas County Analysis")
        else:
            st.subheader(f"Station {station_id} Analysis")
        
        # Use the forecast type from the sidebar
        forecast_type = st.session_state.get('forecast_type')
        if not forecast_type:
            st.error("Please select a forecast type in the sidebar")
            st.stop()
        
        # Map display names to element codes
        element_map = {
            "Maximum Temperature (TMAX)": "TMAX",
            "Minimum Temperature (TMIN)": "TMIN",
            "Precipitation (PRCP)": "PRCP",
            "Snowfall (SNOW)": "SNOW",
            "Snow Depth (SNWD)": "SNWD"
        }
        
        selected_element = element_map.get(forecast_type)
        if not selected_element:
            st.error(f"Invalid forecast type: {forecast_type}")
            st.stop()
        
        # Filter data for selected element
        df_filtered = df_station[df_station['element'] == selected_element]
        if df_filtered.empty:
            st.error(f"No data available for {selected_element}")
            st.stop()
        
        # Clean and prepare data
        cleaned_df = clean_data(df_filtered)
        if cleaned_df is None or cleaned_df.empty:
            st.error("Failed to process data")
            st.stop()
        
        # Display the forecast plot
        st.subheader(f"{forecast_type} Trends")
        fig = create_forecast_plot(cleaned_df, selected_element, time_period)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        st.subheader("Statistics")
        display_statistics(cleaned_df, selected_element)

        # Check if 'ENTIRE_COUNTY' is the selected option and element is TMAX or TMIN
        if station_id != "ENTIRE_COUNTY" or selected_element not in ["TMAX", "TMIN"]:
            st.stop()
            
        # Validate the data before making predictions
        if not validate_time_series_data(cleaned_df, station_id, selected_element):
            st.error("The data for this station and element is not suitable for prediction. Please select a different station or element.")
            st.stop()
        
        # Load and apply model if available
        model = load_model(selected_element)
        if model:
            try:
                # Prepare data for prediction
                prediction_data = cleaned_df
                if prediction_data is None or prediction_data.empty:
                    st.error("Failed to prepare data for prediction")
                    st.stop()
                
                # Convert time_period to integer and ensure it's positive
                n_periods = max(1, int(time_period))
                
                # Generate predictions using the loaded model
                predictions_array = model.predict(n_periods=n_periods)
                
                # Create datetime index for predictions
                last_date = prediction_data.index[-1]
                prediction_dates = pd.date_range(
                    start=last_date + pd.DateOffset(months=1),
                    periods=n_periods,
                    freq="ME"
                )
                
                # Convert predictions array to pandas Series with datetime index
                if isinstance(predictions_array, pd.Series):
                    # If it's already a Series, just update the index
                    predictions = predictions_array.copy()
                    predictions.index = prediction_dates
                else:
                    # If it's a numpy array, create a new Series
                    predictions = pd.Series(predictions_array, index=prediction_dates)
                
                # Display predictions
                st.subheader("Model Predictions")
                display_predictions(cleaned_df, predictions, selected_element, forecast_type, cleaned_df['value'].mean())
            except Exception as e:
                st.error(f"Error making predictions with loaded model: {str(e)}")
        else:
            st.error("No pre-trained model found for this element type.")
    
    with tab2:
        # About Section
        st.title("About NeuralClimate")
        st.write("""
        NeuralClimate delivers advanced climate data analysis by directly integrating backend functions.
        This version uses real data from NOAA datasets and displays all processed data, with location 
        selection based on U.S. states.
        
        NeuralClimate integrates historical climate data and sophisticated statistical modeling
        to deliver insightful projections. This version directly leverages backend functions for data integration,
        including state-based filtering of station data.
        """)

if __name__ == "__main__":
    main()

