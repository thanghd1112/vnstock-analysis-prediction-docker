# VNStock Analysis & Prediction (Dockerized Streamlit App)

An **interactive analytics and forecasting web application** for the Vietnam stock market, built with **Python** and **Streamlit**, and packaged with **Docker** for easy deployment.

## Key Features

- **Stock Analysis**: Visualize historical stock data with technical indicators (SMA, RSI, MACD, Bollinger Bands)
- **Prediction**: Forecast short-term stock prices using ARIMA models
- **Sentiment Analysis**: Fetch Vietnamese financial news and analyze sentiment 
- **Docker Support**: Run anywhere with a single `docker run` command

## Tech Stack

- **Python, Streamlit, Pandas, Plotly** - Core framework and data visualization
- **vnstock** - Vietnam stock market data provider
- **underthesea** - Vietnamese NLP sentiment analysis
- **statsmodels** - ARIMA time series forecasting
- **Docker** - Containerized deployment

## Requirements

- Python 3.11+
- Operating System: Windows/macOS/Linux

## Local Installation and Setup

### Windows

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app/app.py
```

### macOS/Linux

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app/app.py
```

## Running with Docker

```bash
# Build the Docker image
docker build -t vn-stock-app .

# Run the container
docker run --rm -p 8501:8501 vn-stock-app
```

**Access the application**: Open your browser and navigate to `http://localhost:8501`

## Data Notes

- Stock price data is fetched using `vnstock` with Vietnamese stock codes (e.g., VNM, HPG, VIC, FPT)
- Historical data availability depends on the `vnstock` API
- Sentiment analysis works best with Vietnamese language financial news

## Project Structure

```
.
├── app/
│   ├── app.py                    # Main Streamlit application
│   ├── components/
│   │   ├── analysis.py           # Stock analysis components
│   │   ├── comparison.py         # Stock comparison features
│   │   ├── sentiment.py          # Sentiment analysis module
│   │   ├── forecasting.py        # Price prediction models
│   │   └── ...
│   └── services/
│       ├── data.py                # Data fetching services
│       ├── indicators.py          # Technical indicators calculation
│       └── ...
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
└── README.md                      # Project documentation
```

## Usage

1. **Select a stock**: Enter a Vietnamese stock code (e.g., VNM, HPG, VIC)
2. **Choose date range**: Select the time period for historical data
3. **View analysis**: Explore charts with technical indicators
4. **Check predictions**: Review ARIMA-based price forecasts
5. **Analyze sentiment**: Read sentiment analysis from Vietnamese financial news

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on the project repository.

---

**Note**: This application is for educational and research purposes only. Stock market predictions are inherently uncertain and should not be used as the sole basis for investment decisions.