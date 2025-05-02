import pandas as pd
import os
from app import get_stations_in_county
import machine_learning.ghcnd_fetch as fetch
import machine_learning.time_series as time_series

from tqdm import tqdm

def fetch_and_combine_dallas_data():
    # Get Dallas stations
    print("Fetching Dallas stations...")
    dallas_stations = get_stations_in_county("Dallas")
    if dallas_stations is None or dallas_stations.empty:
        print("No stations found for Dallas County")
        return
    
    print(f"Found {len(dallas_stations)} stations in Dallas County")
    
    # Create directories for the data if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/stations", exist_ok=True)
    
    # Save station metadata
    stations_file = "data/dallas_stations_metadata.csv"
    dallas_stations.to_csv(stations_file, index=False)
    print(f"Saved station metadata to {stations_file}")
    
    # Initialize an empty list to store all station data
    all_station_data = []
    
    # Fetch data for each station
    print("Fetching data for each station...")
    for _, station in tqdm(dallas_stations.iterrows(), total=len(dallas_stations)):
        station_id = station['ID']
        try:
            # Fetch data for the station
            station_data = fetch.get_ghcnd_data_by_station(station_id)
            if station_data is not None and not station_data.empty:
                # Add station ID as a column
                station_data['STATION_ID'] = station_id
                
                # Clean the data
                cleaned_data = time_series.clean_data(station_data)
                if cleaned_data is not None and not cleaned_data.empty:
                    # Reset index to get DATE back as a column
                    cleaned_data = cleaned_data.reset_index()
                    # Add station ID back
                    cleaned_data['STATION_ID'] = station_id
                    
                    # Save individual station data
                    station_file = f"data/stations/{station_id}_data.csv"
                    cleaned_data.to_csv(station_file, index=False)
                    print(f"Saved cleaned data for station {station_id} to {station_file}")
                    
                    all_station_data.append(cleaned_data)
        except Exception as e:
            print(f"Error fetching data for station {station_id}: {str(e)}")
            continue
    
    if not all_station_data:
        print("No data was fetched for any stations")
        return
    
    # Combine all station data
    print("Combining station data...")
    combined_data = pd.concat(all_station_data, ignore_index=True)
    
    # Save to CSV
    output_file = "data/dallas_stations_data.csv"
    combined_data.to_csv(output_file, index=False)
    print(f"Saved combined cleaned data for {len(all_station_data)} stations to {output_file}")
    print(f"Total records: {len(combined_data)}")

if __name__ == "__main__":
    fetch_and_combine_dallas_data() 