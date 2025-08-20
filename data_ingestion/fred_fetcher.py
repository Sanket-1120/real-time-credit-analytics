# In: data_ingestion/fred_fetcher.py

import os
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv

load_dotenv()

def fetch_macro_data():
    """
    Fetches key macroeconomic indicators from the FRED API.
    """
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        print("Error: FRED_API_KEY not found in .env file.")
        return None

    fred = Fred(api_key=api_key)
    
    # Define the series IDs for key economic indicators
    series_ids = {
        'GDP': 'GDP',                             # Gross Domestic Product
        'CPI': 'CPIAUCSL',                        # Consumer Price Index (Inflation)
        'FEDFUNDS': 'FEDFUNDS',                   # Federal Funds Effective Rate
        'UNRATE': 'UNRATE',                       # Unemployment Rate
        'BAMLH0A0HYM2': 'BAMLH0A0HYM2'             # High-Yield Index Spread (Credit Risk)
    }
    
    try:
        # Fetch the most recent value for each series
        macro_data = {}
        for name, series_id in series_ids.items():
            data = fred.get_series_latest_release(series_id)
            macro_data[name] = data.iloc[-1] # Get the most recent value
            
        print("Successfully fetched macroeconomic data from FRED.")
        return macro_data
        
    except Exception as e:
        print(f"Failed to fetch FRED data: {e}")
        return None

# For direct testing
if __name__ == '__main__':
    data = fetch_macro_data()
    if data:
        print("\nLatest Macroeconomic Data:")
        print(pd.Series(data))