# NeuralClimate

NeuralClimate is a Web application that provides climate change analysis and forecasts future climate change. NeuralClimate uses historical data and statistical modeling techniques which include machine learning and traditional regression.

## Data Source

NeuralClimate uses climate data from NOAA's Global Historical Climatology Network Daily (GHCN-D) dataset. The application currently focuses on Dallas County, Texas, and includes the following climate elements:
- Maximum Temperature (TMAX)
- Minimum Temperature (TMIN)
- Precipitation (PRCP)
- Snowfall (SNOW)
- Snow Depth (SNWD)

## Features

- Interactive climate data visualization
- Time series forecasting using ARIMA and Prophet models
- Historical climate data analysis
- Station-based data filtering
- Interactive maps showing station locations
- Customizable forecast periods (1-25 years)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NeuralClimate.git
cd NeuralClimate
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Data Setup

1. Run the data fetching script to download and process climate data:
```bash
python scripts/fetch_data.py
```

2. Train the forecasting models:
```bash
python scripts/train_models.py
```

## Running the Application

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Project Structure

```
NeuralClimate/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── data/                 # Data directory
│   ├── counties/        # County-specific data
│   └── stations/        # Station-specific data
├── models/              # Trained forecasting models
├── scripts/             # Utility scripts
│   ├── fetch_data.py    # Data fetching script
│   ├── train_models.py  # Model training script
│   └── ml/             # Machine learning utilities
└── README.md           # This file
```