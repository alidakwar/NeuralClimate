import os
import pandas as pd
import numpy as np
from pmdarima import auto_arima
from prophet import Prophet
import pickle
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

def calculate_metrics(y_true, y_pred):
    """Calculate RMSE, sMAPE, and R-squared"""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    # Calculate sMAPE
    smape = 100 * np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))
    r2 = r2_score(y_true, y_pred)
    return rmse, smape, r2

def cross_validate_model(model, data, n_splits=5):
    """Perform time series cross-validation"""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    rmse_scores = []
    mape_scores = []
    r2_scores = []
    
    # Reset index to avoid issues with splitting
    data = data.reset_index(drop=True)
    
    for train_idx, test_idx in tscv.split(data):
        train_data = data.iloc[train_idx].copy()
        test_data = data.iloc[test_idx].copy()
        
        if isinstance(model, Prophet):
            # For Prophet models, create a new instance for each fold
            if model.yearly_seasonality:
                if hasattr(model, 'seasonality_mode'):
                    current_model = Prophet(
                        yearly_seasonality=True,
                        seasonality_mode=model.seasonality_mode,
                        changepoint_prior_scale=model.changepoint_prior_scale
                    )
                else:
                    current_model = Prophet(yearly_seasonality=True)
            else:
                current_model = Prophet()
                
            # Prepare data for Prophet
            train_prophet = train_data[['ds', 'y']].copy()
            if 'lag1' in train_data.columns and hasattr(model, 'add_regressor'):
                current_model.add_regressor('lag1')
                train_prophet['lag1'] = train_data['lag1']
                
            if 'lag12' in train_data.columns and hasattr(model, 'add_regressor'):
                current_model.add_regressor('lag12')
                train_prophet['lag12'] = train_data['lag12']
                
            current_model.fit(train_prophet)
            
            future = current_model.make_future_dataframe(periods=len(test_data))
            if 'lag1' in test_data.columns and hasattr(model, 'add_regressor'):
                future['lag1'] = pd.concat([train_data['lag1'], test_data['lag1']]).reset_index(drop=True)
                
            if 'lag12' in test_data.columns and hasattr(model, 'add_regressor'):
                future['lag12'] = pd.concat([train_data['lag12'], test_data['lag12']]).reset_index(drop=True)
                
            forecast = current_model.predict(future)
            y_pred = forecast['yhat'][-len(test_data):]
            y_true = test_data['y']
        else:
            # For SARIMA models
            # Prepare exogenous variables if needed
            if hasattr(model, 'exogenous') and model.exogenous is not None:
                exog_cols = ['month', 'year', 'lag1', 'lag12']
                exog_train = train_data[exog_cols]
                exog_test = test_data[exog_cols]
                current_model = model.fit(train_data['y'], exogenous=exog_train)
                y_pred = current_model.predict(n_periods=len(test_data), exogenous=exog_test)
            else:
                current_model = model.fit(train_data['y'])
                y_pred = current_model.predict(n_periods=len(test_data))
            y_true = test_data['y']
        
        rmse, mape, r2 = calculate_metrics(y_true, y_pred)
        rmse_scores.append(rmse)
        mape_scores.append(mape)
        r2_scores.append(r2)
    
    return np.mean(rmse_scores), np.mean(mape_scores), np.mean(r2_scores)

def get_available_elements(data):
    """Get unique elements from the data."""
    if 'element' not in data.columns:
        raise ValueError("Data must contain an 'element' column")
    
    # Get unique elements that exist in the data
    elements = data['element'].unique()
    
    # Filter to only include TMIN and TMAX
    main_elements = ['TMAX', 'TMIN']
    return [elem for elem in elements if elem in main_elements]

def build_and_save_model(element, data):
    """Build and save models for a specific element using county data."""
    try:
        # Filter data for the specific element
        element_data = data[data['element'] == element].copy()
        if element_data.empty:
            print(f"No data available for element {element}")
            return None
            
        # Convert DATE to datetime and set as index
        element_data['DATE'] = pd.to_datetime(element_data['DATE'])
        element_data = element_data.set_index('DATE')
        
        # Keep only the value column for resampling
        element_data = element_data[['value']]
        
        # Resample to monthly frequency and forward fill missing values
        element_data = element_data.resample('M').mean()
        element_data = element_data.fillna(method='ffill')
        
        # Clean the data
        element_data = element_data.dropna()

        # Create model directory if it doesn't exist
        model_dir = os.path.join("models")
        os.makedirs(model_dir, exist_ok=True)

        # Prepare data for modeling
        prophet_data = element_data.reset_index()
        prophet_data = prophet_data.rename(columns={'DATE': 'ds', 'value': 'y'})
        
        # Add additional features
        prophet_data['month'] = prophet_data['ds'].dt.month
        prophet_data['year'] = prophet_data['ds'].dt.year
        prophet_data['lag1'] = prophet_data['y'].shift(1)
        prophet_data['lag12'] = prophet_data['y'].shift(12)
        
        # Drop rows with NaN values after adding lags
        prophet_data = prophet_data.dropna()
        
        # Split data into train and test sets
        train_size = int(len(prophet_data) * 0.8)
        train_data = prophet_data[:train_size].copy()
        test_data = prophet_data[train_size:].copy()
        
        print(f"\nData split information for {element}:")
        print(f"Total data points: {len(prophet_data)}")
        print(f"Training data points: {len(train_data)}")
        print(f"Testing data points: {len(test_data)}")
        
        # Initialize lists to store models and their metrics
        models = []
        model_names = []
        all_metrics = []
        cv_metrics = []
        
        # Model 1: Optimized Prophet with regressors
        print(f"\nTraining Prophet model for {element}...")
        model1 = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0
        )
        model1.add_regressor('lag1')
        model1.add_regressor('lag12')
        model1.fit(train_data)
        future1 = model1.make_future_dataframe(periods=len(test_data))
        future1['lag1'] = pd.concat([train_data['lag1'], test_data['lag1']]).reset_index(drop=True)
        future1['lag12'] = pd.concat([train_data['lag12'], test_data['lag12']]).reset_index(drop=True)
        forecast1 = model1.predict(future1)
        rmse1, mape1, r2_1 = calculate_metrics(test_data['y'].values, forecast1['yhat'][-len(test_data):].values)
        cv_rmse1, cv_mape1, cv_r2_1 = cross_validate_model(model1, prophet_data)
        models.append(model1)
        model_names.append("Prophet")
        all_metrics.append((rmse1, mape1, r2_1))
        cv_metrics.append((cv_rmse1, cv_mape1, cv_r2_1))
        
        # Model 2: Optimized SARIMA
        print(f"\nTraining SARIMA model for {element}...")
        model2 = auto_arima(
            train_data['y'],
            seasonal=True,
            m=12,
            start_p=1,
            start_q=1,
            max_p=3,
            max_q=3,
            max_P=2,
            max_Q=2,
            max_d=1,
            max_D=1,
            stepwise=True,
            suppress_warnings=True,
            error_action="ignore",
            trace=False,
            information_criterion='bic'
        )
        predictions2 = model2.predict(n_periods=len(test_data))
        rmse2, mape2, r2_2 = calculate_metrics(test_data['y'].values, predictions2)
        cv_rmse2, cv_mape2, cv_r2_2 = cross_validate_model(model2, prophet_data)
        models.append(model2)
        model_names.append("SARIMA")
        all_metrics.append((rmse2, mape2, r2_2))
        cv_metrics.append((cv_rmse2, cv_mape2, cv_r2_2))
        
        # Find best model based on RMSE
        rmse_scores = np.array([m[0] for m in all_metrics])
        best_model_idx = np.argmin(rmse_scores)
        
        # Save metrics to file
        metrics_df = pd.DataFrame({
            'Model': model_names,
            'RMSE': [m[0] for m in all_metrics],
            'MAPE': [m[1] for m in all_metrics],
            'R-squared': [m[2] for m in all_metrics],
            'CV_RMSE': [m[0] for m in cv_metrics],
            'CV_MAPE': [m[1] for m in cv_metrics],
            'CV_R-squared': [m[2] for m in cv_metrics]
        })
        
        metrics_file = os.path.join(model_dir, f"{element}_metrics.csv")
        metrics_df.to_csv(metrics_file, index=False)
        
        # Print results
        print(f"\n{element} Model Comparison:")
        print(metrics_df.to_string(index=False))
        print(f"\nBest model: {model_names[best_model_idx]}")
        print(f"Best model metrics:")
        print(f"RMSE: {all_metrics[best_model_idx][0]:.2f}")
        print(f"MAPE: {all_metrics[best_model_idx][1]:.2f}%")
        print(f"R-squared: {all_metrics[best_model_idx][2]:.4f}")
        print(f"\nCross-validation metrics:")
        print(f"CV RMSE: {cv_metrics[best_model_idx][0]:.2f}")
        print(f"CV MAPE: {cv_metrics[best_model_idx][1]:.2f}%")
        print(f"CV R-squared: {cv_metrics[best_model_idx][2]:.4f}")
        
        # Save the best model with compression
        best_model = models[best_model_idx]
        model_path = os.path.join(model_dir, f"{element}_best_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(best_model, f, protocol=pickle.HIGHEST_PROTOCOL)
            
        return best_model
            
    except Exception as e:
        print(f"Error building model for element {element}: {str(e)}")
        return None

def main():
    print("Loading Dallas County data...")
    try:
        # Load the county data
        county_data = pd.read_csv("data/dallas_stations_data.csv")
        if county_data is None or county_data.empty:
            print("Failed to load county data")
            return
            
        # Get available elements (TMIN and TMAX only)
        available_elements = get_available_elements(county_data)
        if not available_elements:
            print("No valid elements found in county data")
            return
            
        print(f"Found elements: {available_elements}")
        
        # Process both TMIN and TMAX
        for element in available_elements:
            print(f"\nBuilding models for {element}...")
            build_and_save_model(element, county_data)
            
        print("\nModel training complete!")
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main() 