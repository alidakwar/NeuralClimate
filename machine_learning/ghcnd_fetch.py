import requests
import ghcnd_parse as ghcnd_parse
import csv
import os
import pandas as pd
from io import StringIO


def get_ghcnd_countries():
    # Fetch data from the GHCN-D countries dataset
    url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text
        df = ghcnd_parse.parse_countries_file(data)
        return df
    else:
        raise Exception(
            f"Failed to fetch data. HTTP Status Code: {response.status_code}"
        )


def get_ghcnd_inventory():
    # Fetch data from the GHCN-D inventory dataset
    url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text
        df = ghcnd_parse.parse_inventory_file(data)
        return df
    else:
        raise Exception(
            f"Failed to fetch data. HTTP Status Code: {response.status_code}"
        )


def get_ghcnd_states():
    # Fetch data from the GHCN-D states dataset
    url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-states.txt"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text
        df = ghcnd_parse.parse_states_file(data)
        return df
    else:
        raise Exception(
            f"Failed to fetch data. HTTP Status Code: {response.status_code}"
        )


def get_ghcnd_stations():
    # Fetch data from the GHCN-D stations dataset
    url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.csv"
    column_names = [
        "ID",
        "LATITUDE",
        "LONGITUDE",
        "ELEVATION",
        "STATE",
        "NAME",
        "GSN FLAG",
        "HCN/CRN FLAG",
        "WMO ID",
    ]
    try:
        stations_df = pd.read_csv(url, names=column_names, on_bad_lines="skip")
        return stations_df
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch data from {url}. Error: {e}")
    except pd.errors.ParserError as e:
        raise Exception(f"Failed to parse the CSV data. Error: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred. Error: {e}")


def get_ghcnd_data_by_station(station_id):
    # Construct the URL for the .dly file.
    url = f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly"
    print(f"Downloading data from: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error downloading file: {e}")
        return

    # Split the downloaded text into lines and parse it.
    lines = response.text.splitlines()
    df = ghcnd_parse.dly_to_dataframe_from_lines(lines)
    return df
