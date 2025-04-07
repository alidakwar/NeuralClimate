import pandas as pd


def parse_countries_file(input_path):
    """
    Parse the GHCND countries file and convert it to a pandas DataFrame.

    Args:
        input_path (str): Path to the input ghcnd-countries.txt file

    Returns:
        pd.DataFrame: A DataFrame containing the parsed countries data
    """
    countries_data = []

    # Read and parse the input file
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():  # Skip empty lines
                code = line[0:2].strip()
                name = line[3:].strip()
                countries_data.append([code, name])

    # Create a pandas DataFrame
    df = pd.DataFrame(countries_data, columns=["country_code", "country_name"])
    return df


def parse_inventory_file(input_path):
    """
    Parse the GHCND inventory file and convert it to a pandas DataFrame.

    Args:
        input_path (str): Path to the input ghcnd-inventory.txt file

    Returns:
        pd.DataFrame: A DataFrame containing the parsed inventory data
    """
    inventory_data = []

    # Read and parse the input file
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():  # Skip empty lines
                # Parse fixed-width fields
                station_id = line[0:11].strip()
                latitude = float(line[12:20].strip())
                longitude = float(line[21:30].strip())
                element = line[31:35].strip()
                first_year = int(line[36:40].strip())
                last_year = int(line[41:45].strip())

                inventory_data.append(
                    [station_id, latitude, longitude, element, first_year, last_year]
                )

    # Create a pandas DataFrame
    df = pd.DataFrame(
        inventory_data,
        columns=["id", "latitude", "longitude", "element", "first_year", "last_year"],
    )
    return df


# Convert states text file to pandas DataFrame
def parse_states_file(input_path):
    """
    Parse the GHCND states file and convert it to a pandas DataFrame.

    Args:
        input_path (str): Path to the input ghcnd-states.txt file

    Returns:
        pd.DataFrame: A DataFrame containing the parsed states data
    """
    states_data = []

    # Read and parse the input file
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():  # Skip empty lines
                code = line[0:2].strip()
                name = line[3:].strip()
                states_data.append([code, name])

    # Create a pandas DataFrame
    df = pd.DataFrame(states_data, columns=["state_code", "state_name"])
    return df


#  Processing for GHCN-Daily data
def parse_dly_line(line):
    """
    Parse one line from a GHCN-Daily .dly file.
    Each line has fixed-width columns:
      - Columns 1-11: Station ID
      - Columns 12-15: Year
      - Columns 16-17: Month
      - Columns 18-21: Element
      - Then for each day (1 to 31):
          * Columns 22-26, 30-34, ...: Value (integer, -9999 if missing)
          * Next column: Measurement flag (MFLAG)
          * Next column: Quality flag (QFLAG)
          * Next column: Source flag (SFLAG)
    Returns a dictionary with parsed data.
    """
    record = {}
    record["id"] = line[0:11]
    record["year"] = int(line[11:15])
    record["month"] = int(line[15:17])
    record["element"] = line[17:21]

    daily_values = []
    # Each day occupies 8 characters starting at column 22 (index 21)
    for day in range(31):
        start = 21 + day * 8
        value_str = line[start : start + 5]
        try:
            value = int(value_str)
        except ValueError:
            value = None

        mflag = line[start + 5]
        qflag = line[start + 6]
        sflag = line[start + 7]

        # A value of -9999 is considered missing
        if value == -9999:
            value = None

        daily_values.append(
            {
                "day": day + 1,
                "value": value,
                "mflag": mflag.strip() or None,
                "qflag": qflag.strip() or None,
                "sflag": sflag.strip() or None,
            }
        )
    record["daily_values"] = daily_values
    return record


def parse_dly_lines(lines):
    """
    Parse a list of lines from a GHCN-Daily .dly file.
    Returns a list of dictionaries, one per record (month) in the file.
    """
    records = []
    for line in lines:
        if len(line) < 269:  # Valid lines have at least 269 characters.
            continue
        record = parse_dly_line(line)
        records.append(record)
    return records


def dly_to_dataframe_from_lines(lines):
    """
    Convert the parsed .dly file (given as lines) into a pandas DataFrame.
    Each row represents a single day's observation.
    """
    records = parse_dly_lines(lines)
    rows = []
    for rec in records:
        station_id = rec["id"]
        year = rec["year"]
        month = rec["month"]
        element = rec["element"]
        for day_rec in rec["daily_values"]:
            row = {
                "station_id": station_id,
                "year": year,
                "month": month,
                "day": day_rec["day"],
                "element": element,
                "value": day_rec["value"],
                "mflag": day_rec["mflag"],
                "qflag": day_rec["qflag"],
                "sflag": day_rec["sflag"],
            }
            rows.append(row)
    df = pd.DataFrame(rows)
    return df
