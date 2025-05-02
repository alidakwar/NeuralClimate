import pandas as pd
import numpy as np
from machine_learning import ghcnd_fetch as fetch
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error


def clean_data(data):
    """
    Clean and prepare time series data for analysis and prediction.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Raw data with either:
        - 'year', 'month', 'day', and 'value' columns, or
        - 'DATE' column and 'value' column, or
        - datetime index and 'value' column
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned data with datetime index and resampled values
    """
    try:
        # Create a copy to avoid modifying the original data
        data = data.copy()
        
        # Handle different input formats
        if 'year' in data.columns and 'month' in data.columns and 'day' in data.columns:
            # Create DATE column from year, month, and day
            data["DATE"] = pd.to_datetime(data[["year", "month", "day"]], errors="coerce")
            data = data.dropna(subset=["DATE"])
            data = data.set_index("DATE")
        elif 'DATE' in data.columns:
            # Convert DATE to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(data['DATE']):
                data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')
            data = data.dropna(subset=["DATE"])
            data = data.set_index("DATE")
        elif not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have either year/month/day columns, a DATE column, or a datetime index")
        
        # Ensure value column exists and is numeric
        if 'value' not in data.columns:
            raise ValueError("Data must contain a 'value' column")
        
        # Convert value column to float and drop any invalid values
        data['value'] = pd.to_numeric(data['value'], errors='coerce')
        data = data.dropna(subset=["value"])
        
        # Keep only the value column
        data = data[["value"]]
        
        # Resample to monthly frequency and handle missing values
        data = data.resample("ME").mean()  # Using ME instead of M for month end
        
        # Forward fill any remaining missing values
        data = data.fillna(method='ffill')
        
        # If there are still missing values, backward fill
        data = data.fillna(method='bfill')
        
        return data
        
    except Exception as e:
        print(f"Error in clean_data: {str(e)}")
        return None

# Keep these functions for backward compatibility but mark them as deprecated
def clean_data_for_visualization(data):
    """Deprecated: Use clean_data instead"""
    return clean_data(data)

def prepare_data_for_prediction(cleaned_data):
    """Deprecated: Use clean_data instead"""
    return cleaned_data

def validate_time_series_data(element_data, station_id, element, min_points=36, max_years_since_last=3):
    """
    Validate time series data for ARIMA modeling.
    
    Parameters:
    -----------
    element_data : pd.DataFrame
        DataFrame containing the time series data with datetime index and 'value' column
    station_id : str
        Station identifier
    element : str
        Weather element (TMAX, TMIN, PRCP, etc.)
    min_points : int
        Minimum number of data points required (default: 36 for 3 years of monthly data)
    max_years_since_last: int
        Maximum allowed years between last data point and current date (default: 3)
        
    Returns:
    --------
    bool : True if data is valid for ARIMA modeling, False otherwise
    """
    # Check for empty data
    if element_data.empty:
        print(f"No data available for station {station_id}, element {element}")
        return False

    # Check for required columns
    if  'value' not in element_data.columns:
        print(f"Missing required columns for station {station_id}, element {element}")
        print(element_data.columns)
        return False

    # Check for enough data points
    if len(element_data) < min_points:
        print(f"Not enough data points for station {station_id}, element {element}. "
              f"Found {len(element_data)}, need at least {min_points}")
        return False

    # Check data recency
    try:
        last_date = element_data.index.max()
        if last_date < (pd.Timestamp.today() - pd.DateOffset(years=max_years_since_last)):
            print(f"Data for station {station_id}, element {element} is not recent enough. "
                  f"Last date: {last_date.strftime('%Y-%m-%d')}")
            return False
    except Exception as e:
        print(f"Error processing dates for station {station_id}, element {element}")
        return False

    # # Check for missing values
    # if element_data['value'].isnull().sum() > 0:
    #     print(f"Data contains missing values for station {station_id}, element {element}")
    #     return False

    # Check for constant or zero variance
    if element_data['value'].nunique() <= 1:
        print(f"Data is constant or has no variance for station {station_id}, element {element}")
        return False

    return True

def predict_time_series(cleaned_data, n_periods=12):
    """
    Generate predictions using ARIMA model.
    
    Parameters:
    -----------
    cleaned_data : pandas.DataFrame
        Cleaned time series data with datetime index
    n_periods : int, optional
        Number of periods to forecast (default: 12 months)
        
    Returns:
    --------
    pandas.Series
        Forecasted values with datetime index
    """
    try:
        if cleaned_data is None or cleaned_data.empty:
            raise ValueError("No valid data provided for prediction")
            
        # Ensure data is properly formatted
        if not isinstance(cleaned_data.index, pd.DatetimeIndex):
            raise ValueError("Data must have a DatetimeIndex")
        
            
        # Convert years to months for prediction
        n_months = n_periods * 12
            
        # Fit the ARIMA model with error handling
        model = auto_arima(
            cleaned_data['value'],  # Only use the value column
            seasonal=True,
            m=12,
            stepwise=True,
            suppress_warnings=True,
            error_action="ignore",
            trace=False
        )
        
        # Generate forecast
        forecast = model.predict(n_periods=n_months)
        
        # Create forecast index
        last_date = cleaned_data.index[-1]
        forecast_index = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=n_months,
            freq="ME"
        )
        
        # Create forecast series
        forecast_series = pd.Series(forecast, index=forecast_index)
        
        # Calculate and print model metrics
        in_sample_predictions = model.predict_in_sample()
        mse = mean_squared_error(cleaned_data['value'], in_sample_predictions)
        rmse = np.sqrt(mse)
        print(f"Model RMSE: {rmse:.2f}")
        
        return forecast_series
        
    except Exception as e:
        print(f"Error in predict_time_series: {str(e)}")
        return None

