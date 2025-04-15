import pandas as pd
import machine_learning.ghcnd_fetch as fetch
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error


def clean_data(data):
    # Create a DATE column from year, month, and day columns.
    # Use errors='coerce' to handle any invalid date values.
    data["DATE"] = pd.to_datetime(data[["year", "month", "day"]], errors="coerce")

    # Drop rows where date conversion failed (NaT)
    data = data.dropna(subset=["DATE"])

    # Drop rows with missing temperature values in the 'value' column
    data = data.dropna(subset=["value"])

    # TODO: do proper unit conversion based on the 'unit' column
    data['value'] = data['value'].astype(float)

    # TODO: figure out if dropping NA then resampling is the right approach compared to resampling then dropping NA
    # Set DATE as the index and keep only the temperature values
    data = data.set_index("DATE")[["value"]]

    data = data.resample("M").mean()  # Resample to monthly frequency
    data = data.dropna()  # Drop any rows with NaN values after resampling
    return data
    

def predict_time_series(cleaned_data):
    # Fit the ARIMA model
    model = auto_arima(
        cleaned_data,
        seasonal=True,
        m=12,
        stepwise=True,
        suppress_warnings=True,
        trace=True,
    )
    # Forecast the next 12 months
    forecast = model.predict(n_periods=12)
    forecast_index = pd.date_range(
        start=cleaned_data.index[-1] + pd.DateOffset(months=1),
        periods=12,
        freq="M",
    )
    # Calculate Mean Squared Error (MSE) on the training data

    # Get the in-sample predictions
    in_sample_predictions = model.predict_in_sample()

    # Calculate MSE
    mse = mean_squared_error(cleaned_data, in_sample_predictions)
    print(f"Mean Squared Error (MSE): {mse}")
    forecast_series = pd.Series(forecast, index=forecast_index)
    return forecast_series

