import pandas as pd
import numpy as np
import machine_learning.ghcnd_fetch as fetch
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error


def clean_data(data):
    """
    Clean and prepare time series data for analysis.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Raw data with 'year', 'month', 'day', and 'value' columns
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned data with datetime index and resampled values
    """
    try:
        # Create a copy to avoid modifying the original data
        data = data.copy()
        
        # Create DATE column from year, month, and day
        data["DATE"] = pd.to_datetime(data[["year", "month", "day"]], errors="coerce")
        
        # Drop rows with invalid dates
        data = data.dropna(subset=["DATE"])
        
        # Drop rows with missing values
        data = data.dropna(subset=["value"])
        
        # Convert value column to float
        data['value'] = pd.to_numeric(data['value'], errors='coerce')
        data = data.dropna(subset=["value"])
        
        # Set DATE as index and keep only the value column
        data = data.set_index("DATE")[["value"]]
        
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
            cleaned_data,
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
        mse = mean_squared_error(cleaned_data, in_sample_predictions)
        rmse = np.sqrt(mse)
        print(f"Model RMSE: {rmse:.2f}")
        
        return forecast_series
        
    except Exception as e:
        print(f"Error in predict_time_series: {str(e)}")
        return None

