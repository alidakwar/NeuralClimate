import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir.parent))

# Define data directory paths
DATA_DIR = current_dir.parent / "data"
STATIONS_DIR = DATA_DIR / "stations"

# Enable dry-run mode
DRY_RUN = True

import pandas as pd
from ml.ghcnd_fetch import get_ghcnd_stations, get_ghcnd_data_by_station
from ml.time_series import clean_data
from app import get_stations_in_county
from tqdm import tqdm

def fetch_and_combine_dallas_data():
    # Get Dallas stations
    print("Fetching Dallas stations...")
    dallas_stations = get_stations_in_county("Dallas")
    if dallas_stations is None or dallas_stations.empty:
        print("No stations found for Dallas County")
        return
    
    print(f"Found {len(dallas_stations)} stations in Dallas County")
    
    if not DRY_RUN:
        # Create directories for the data if they don't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(STATIONS_DIR, exist_ok=True)
    else:
        print("[DRY RUN] Would create data directories")
    
    # Save station metadata
    stations_file = DATA_DIR / "dallas_stations_metadata.csv"
    if not DRY_RUN:
        dallas_stations.to_csv(stations_file, index=False)
        print(f"Saved station metadata to {stations_file}")
    else:
        print(f"[DRY RUN] Would save station metadata to {stations_file}")
    
    # Initialize an empty list to store all station data
    all_station_data = []
    
    # Fetch data for each station
    print("Fetching data for each station...")
    for _, station in tqdm(dallas_stations.iterrows(), total=len(dallas_stations)):
        station_id = station['ID']
        try:
            # Fetch data for the station
            station_data = get_ghcnd_data_by_station(station_id)
            if station_data is not None and not station_data.empty:
                # Add station ID as a column
                station_data['STATION_ID'] = station_id
                
                # Clean the data
                cleaned_data = clean_data(station_data)
                if cleaned_data is not None and not cleaned_data.empty:
                    # Reset index to get DATE back as a column
                    cleaned_data = cleaned_data.reset_index()
                    # Add station ID back
                    cleaned_data['STATION_ID'] = station_id
                    
                    # Save individual station data
                    station_file = STATIONS_DIR / f"{station_id}_data.csv"
                    if not DRY_RUN:
                        cleaned_data.to_csv(station_file, index=False)
                        print(f"Saved cleaned data for station {station_id} to {station_file}")
                    else:
                        print(f"[DRY RUN] Would save cleaned data for station {station_id} to {station_file}")
                    
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
    output_file = DATA_DIR / "dallas_stations_data.csv"
    if not DRY_RUN:
        combined_data.to_csv(output_file, index=False)
        print(f"Saved combined cleaned data for {len(all_station_data)} stations to {output_file}")
        print(f"Total records: {len(combined_data)}")
    else:
        print(f"[DRY RUN] Would save combined cleaned data for {len(all_station_data)} stations to {output_file}")
        print(f"Total records: {len(combined_data)}")

if __name__ == "__main__":
    fetch_and_combine_dallas_data() 