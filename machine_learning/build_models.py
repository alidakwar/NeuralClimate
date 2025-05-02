import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
from pmdarima import auto_arima
import pickle
from machine_learning.time_series import clean_data
import machine_learning.ghcnd_fetch as fetch
import machine_learning.ghcnd_parse

def get_station_elements(data):
    """Get unique elements from the data."""
    if 'element' not in data.columns:
        raise ValueError("Data must contain an 'element' column")
    
    # Get unique elements that exist in the data
    station_elements = data['element'].unique()
    
    # Filter to only include the main elements that exist in the data
    main_elements = ['TMAX', 'TMIN', 'PRCP', 'SNOW', 'SNWD']
    return [elem for elem in station_elements if elem in main_elements]

def build_and_save_model(station_id, element, data):
    """Build and save an ARIMA model for a specific station and element."""
    try:
        # Clean and prepare data
        cleaned_data = clean_data(data)
        if cleaned_data is None:
            print(f"Failed to clean data for station {station_id}, element {element}")
            return None
            
        prepared_data = cleaned_data
        if prepared_data is None:
            print(f"Failed to prepare data for station {station_id}, element {element}")
            return None
            
        # Filter data for the specific element
        element_data = prepared_data[prepared_data['element'] == element]
        if element_data.empty:
            print(f"No data available for station {station_id}, element {element}")
            return None
            
        # Extract just the values for the ARIMA model
        values = element_data['value'].values
        
        # Fit the ARIMA model
        model = auto_arima(
            values,  # Pass just the values array
            seasonal=True,
            m=12,
            stepwise=True,
            suppress_warnings=True,
            error_action="ignore",
            trace=False
        )
        
        # Create model directory if it doesn't exist
        model_dir = os.path.join("models", station_id)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save the model
        model_path = os.path.join(model_dir, f"{element}_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
            
        print(f"Successfully built and saved model for station {station_id}, element {element}")
        return model
        
    except Exception as e:
        print(f"Error building model for station {station_id}, element {element}: {str(e)}")
        return None

def main():
    # Load Dallas stations
    stations_df = pd.read_csv("data/dallas_stations_metadata.csv")
    
    # Process each station
    for _, station in stations_df.iterrows():
        station_id = station['ID']
        print(f"\nProcessing station: {station_id}")
        
        
        # Load station data
        try:
            station_data = pd.read_csv(f"data/stations/{station_id}_data.csv")
        except FileNotFoundError:
            print(f"Data file not found for station {station_id}")
            continue
        # Get available elements for this station
        available_elements = get_station_elements(station_data)
        if not available_elements:
            print(f"No valid elements found for station {station_id}")
            continue
            
        # Build models for each element
        for element in available_elements:
            build_and_save_model(station_id, element, station_data)

if __name__ == "__main__":
    main() 