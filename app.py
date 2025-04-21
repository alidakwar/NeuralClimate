import streamlit as st
import pandas as pd
import numpy as np
import tempfile
import os
import requests
from datetime import datetime, timedelta

# Import backend modules
import machine_learning.ghcnd_fetch as fetch
import machine_learning.ghcnd_parse
import machine_learning.time_series as time_series

def get_available_elements(df_station):
    """Get available forecast types for the station."""
    if df_station is None or df_station.empty:
        return []
    
    # Get unique elements from the dataframe
    available_elements = df_station['element'].unique()
    
    # Map element codes to display names
    element_map = {
        "TMAX": "Maximum Temperature (TMAX)",
        "TMIN": "Minimum Temperature (TMIN)",
        "PRCP": "Precipitation (PRCP)"
    }
    
    # Filter to only include the main elements we want
    filtered_elements = [elem for elem in available_elements if elem in element_map]
    
    # Convert element codes to display names
    display_elements = [element_map.get(elem, elem) for elem in filtered_elements]
    
    return display_elements

# Set up the page configuration
st.set_page_config(
    page_title="NeuralClimate",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create tabs for main content
tab1, tab2 = st.tabs(["Weather Predictions", "About"])

with tab1:
    # Initialize session state
    if 'current_station' not in st.session_state:
        st.session_state.current_station = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None
    if 'available_elements' not in st.session_state:
        st.session_state.available_elements = []

    # Main title
    st.title("NeuralClimate - Weather Predictions")

    # Sidebar Configuration
    with st.sidebar:
        st.header("Configuration")

        # Time period selection
        time_period = st.slider(
            "Select Time Period (Years from now)",
            min_value=1,
            max_value=100,
            value=10
        )

        # Load states data with caching
        @st.cache_data(show_spinner=False)
        def load_states():
            try:
                return fetch.get_ghcnd_states()
            except Exception as e:
                st.error(f"Error loading states data: {str(e)}")
                return None

        # Load stations data with caching
        @st.cache_data(show_spinner=False)
        def load_stations(state_code=None):
            try:
                df_stations = fetch.get_ghcnd_stations()
                if state_code and df_stations is not None:
                    return df_stations[df_stations["STATE"] == state_code]
                return df_stations
            except Exception as e:
                st.error(f"Error loading stations data: {str(e)}")
                return None

        # Load station data with caching
        @st.cache_data(show_spinner=False)
        def load_station_data(station_id):
            try:
                return fetch.get_ghcnd_data_by_station(station_id)
            except Exception as e:
                st.error(f"Error loading station data: {str(e)}")
                return None

        # State selection
        states_df = load_states()
        if states_df is None or states_df.empty:
            st.error("Failed to load states data. Please try again.")
            st.stop()

        state_map = {row["state_name"]: row["state_code"] for _, row in states_df.iterrows()}
        state_names = list(state_map.keys())
        default_index = state_names.index("Texas") if "Texas" in state_names else 0
        selected_state = st.selectbox("Select U.S. State", state_names, index=default_index)
        selected_state_code = state_map[selected_state]

        # Station selection
        df_stations = load_stations(selected_state_code)
        if df_stations is None or df_stations.empty:
            st.error(f"No stations found for state: {selected_state}")
            st.stop()

        station_options = df_stations.apply(
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

        station_id = selected_station.split(" - ")[0].strip()

        # Load station data
        with st.spinner("Loading station data..."):
            df_station = load_station_data(station_id)
            if df_station is None or df_station.empty:
                st.error("Failed to load station data. Please try again.")
                st.stop()

            st.session_state.current_station = station_id
            st.session_state.current_data = df_station

            # Get available elements for this station
            available_elements = get_available_elements(df_station)
            st.session_state.available_elements = available_elements

            if not available_elements:
                st.error("No forecast data available for this station")
                st.stop()

            # Forecast type selection
            forecast_type = st.radio(
                "Forecast Type",
                available_elements,
            )

    # Main content area
    if forecast_type:
        # Filter data based on forecast type
        element_map = {
            "Maximum Temperature (TMAX)": "TMAX",
            "Minimum Temperature (TMIN)": "TMIN",
            "Precipitation (PRCP)": "PRCP"
        }

        selected_element = element_map.get(forecast_type, "TMAX")
        df_station_filtered = df_station[df_station['element'] == selected_element]

        if df_station_filtered.empty:
            st.error(f"No data available for {selected_element} at this station.")
            st.stop()

        # Clean and prepare data
        cleaned_df_station = time_series.clean_data(df_station_filtered)
        if cleaned_df_station is None or cleaned_df_station.empty:
            st.error("Failed to process station data.")
            st.stop()

        # Display station info
        st.info(f"Station: {station_id} - {len(df_station_filtered)} data points for {selected_element}")

        # Prepare chart data
        chart_data = cleaned_df_station.copy()
        
        # Customize chart based on forecast type
        if selected_element == "TMAX" or selected_element == "TMIN":
            # Temperature charts (in tenths of degrees Celsius)
            # Convert to actual temperature values for better readability
            chart_data['value'] = chart_data['value'] / 10.0
            y_axis_label = "Temperature (°C)"
            y_axis_range = [
                chart_data['value'].min() - 5, 
                chart_data['value'].max() + 5
            ]
        elif selected_element == "PRCP":
            # Precipitation (in tenths of millimeters)
            # Convert to millimeters for better readability
            chart_data['value'] = chart_data['value'] / 10.0
            y_axis_label = "Precipitation (mm)"
            y_axis_range = [0, chart_data['value'].max() * 1.2]
        else:
            # Default case
            y_axis_label = f"{selected_element} Value"
            y_axis_range = None
        
        # Display chart with custom configuration
        st.subheader(f"{forecast_type} Trends")
        
        # Use plotly for more control over the chart
        import plotly.express as px
        import plotly.graph_objects as go
        
        # Create a figure with custom y-axis range
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_data.index,
            y=chart_data['value'],
            mode='lines',
            name=selected_element,
            line=dict(color='#1f77b4', width=2)
        ))
        
        # Set y-axis range if specified
        if y_axis_range:
            fig.update_layout(yaxis_range=y_axis_range)
        
        # Update layout for better appearance
        fig.update_layout(
            title=f"{forecast_type} Over Time",
            xaxis_title="Date",
            yaxis_title=y_axis_label,
            template="plotly_white",
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics with appropriate units
        st.subheader("Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if selected_element in ["TMAX", "TMIN"]:
                st.metric(
                    f"Average {selected_element}",
                    f"{chart_data['value'].mean():.1f}°C",
                    f"{chart_data['value'].mean() - chart_data['value'].iloc[0]:.1f}°C"
                )
            elif selected_element == "PRCP":
                st.metric(
                    f"Average {selected_element}",
                    f"{chart_data['value'].mean():.1f} mm",
                    f"{chart_data['value'].mean() - chart_data['value'].iloc[0]:.1f} mm"
                )
            else:
                st.metric(
                    f"Average {selected_element}",
                    f"{chart_data['value'].mean():.1f}",
                    f"{chart_data['value'].mean() - chart_data['value'].iloc[0]:.1f}"
                )
        
        with col2:
            if selected_element in ["TMAX", "TMIN"]:
                st.metric(
                    f"Maximum {selected_element}",
                    f"{chart_data['value'].max():.1f}°C",
                    f"{chart_data['value'].max() - chart_data['value'].mean():.1f}°C"
                )
            elif selected_element == "PRCP":
                st.metric(
                    f"Maximum {selected_element}",
                    f"{chart_data['value'].max():.1f} mm",
                    f"{chart_data['value'].max() - chart_data['value'].mean():.1f} mm"
                )
            else:
                st.metric(
                    f"Maximum {selected_element}",
                    f"{chart_data['value'].max():.1f}",
                    f"{chart_data['value'].max() - chart_data['value'].mean():.1f}"
                )
        
        with col3:
            if selected_element in ["TMAX", "TMIN"]:
                st.metric(
                    f"Minimum {selected_element}",
                    f"{chart_data['value'].min():.1f}°C",
                    f"{chart_data['value'].min() - chart_data['value'].mean():.1f}°C"
                )
            elif selected_element == "PRCP":
                st.metric(
                    f"Minimum {selected_element}",
                    f"{chart_data['value'].min():.1f} mm",
                    f"{chart_data['value'].min() - chart_data['value'].mean():.1f} mm"
                )
            else:
                st.metric(
                    f"Minimum {selected_element}",
                    f"{chart_data['value'].min():.1f}",
                    f"{chart_data['value'].min() - chart_data['value'].mean():.1f}"
                )
        
        # Generate predictions
        try:
            st.write("Attempting to generate predictions...")
            # Apply the same unit conversion to predictions if needed
            predictions = time_series.predict_time_series(cleaned_df_station, n_periods=time_period)
            
            if predictions is not None:
                st.write("Predictions generated successfully!")
                # Convert predictions to the same scale as the chart data
                if selected_element in ["TMAX", "TMIN"]:
                    predictions = predictions / 10.0
                elif selected_element == "PRCP":
                    predictions = predictions / 10.0
                
                st.subheader(f"Predictions for {selected_element} (Next {time_period} Years)")
                
                # Create prediction chart with plotly
                pred_fig = go.Figure()
                
                # Add historical data
                pred_fig.add_trace(go.Scatter(
                    x=chart_data.index,
                    y=chart_data['value'],
                    mode='lines',
                    name='Historical',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                # Add prediction data
                pred_fig.add_trace(go.Scatter(
                    x=predictions.index,
                    y=predictions,
                    mode='lines',
                    name='Prediction',
                    line=dict(color='#ff7f0e', width=2, dash='dash')
                ))
                
                # Set y-axis range if specified
                if y_axis_range:
                    pred_fig.update_layout(yaxis_range=y_axis_range)
                
                # Update layout for better appearance
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
                
                st.subheader("Prediction Statistics")
                
                col1, col2 = st.columns(2)
                with col1:
                    if selected_element in ["TMAX", "TMIN"]:
                        st.metric(
                            "Predicted Average",
                            f"{predictions.mean():.1f}°C",
                            f"{predictions.mean() - chart_data['value'].mean():.1f}°C"
                        )
                    elif selected_element == "PRCP":
                        st.metric(
                            "Predicted Average",
                            f"{predictions.mean():.1f} mm",
                            f"{predictions.mean() - chart_data['value'].mean():.1f} mm"
                        )
                    else:
                        st.metric(
                            "Predicted Average",
                            f"{predictions.mean():.1f}",
                            f"{predictions.mean() - chart_data['value'].mean():.1f}"
                        )
                
                with col2:
                    if selected_element in ["TMAX", "TMIN"]:
                        st.metric(
                            "Predicted Change",
                            f"{predictions.iloc[-1] - predictions.iloc[0]:.1f}°C",
                            "Total Change"
                        )
                    elif selected_element == "PRCP":
                        st.metric(
                            "Predicted Change",
                            f"{predictions.iloc[-1] - predictions.iloc[0]:.1f} mm",
                            "Total Change"
                        )
                    else:
                        st.metric(
                            "Predicted Change",
                            f"{predictions.iloc[-1] - predictions.iloc[0]:.1f}",
                            "Total Change"
                        )
            else:
                st.write("Predictions returned None. Check the time_series.py file for errors.")
        except Exception as e:
            st.error(f"Error generating predictions: {str(e)}")
            
        # Display data table
        st.subheader("Data Table")
        
        # Create a more detailed display dataframe
        display_data = pd.DataFrame()
        display_data['Date'] = chart_data.index.strftime('%Y-%m-%d')
        display_data['Value'] = chart_data['value'].values
        
        # Add month and year columns for better organization
        display_data['Year'] = chart_data.index.year
        display_data['Month'] = chart_data.index.month
        
        # Reorder columns for better display
        display_data = display_data[['Date', 'Year', 'Month', 'Value']]
        
        # Add a note about data quality
        st.info(f"Showing {len(display_data)} data points for {selected_element}")
        
        # Apply styling with explicit color gradient
        styled_df = display_data.style.format({
            'Value': '{:.2f}'
        })
        
        # Apply background gradient to the Value column
        styled_df = styled_df.background_gradient(
            cmap='Blues',
            subset=['Value'],
            vmin=display_data['Value'].min(),
            vmax=display_data['Value'].max()
        )
        
        # Display the styled dataframe
        st.dataframe(styled_df, height=300, use_container_width=True)

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
