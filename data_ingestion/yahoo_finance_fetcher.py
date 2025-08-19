# In: data_ingestion/yahoo_finance_fetcher.py

import yfinance as yf
import pandas as pd

def fetch_ticker_data(tickers: list, period="1y", interval="1d"):
    """
    Fetches historical stock data for a list of tickers from Yahoo Finance.

    Args:
        tickers (list): A list of stock ticker symbols (e.g., ['AAPL', 'MSFT']).
        period (str): The period of data to download (e.g., "1y", "5d", "max").
        interval (str): The data interval (e.g., "1d", "1wk", "1h").

    Returns:
        pandas.DataFrame: A DataFrame containing the historical data,
                          or an empty DataFrame if fetching fails.
    """
    print(f"Fetching data for tickers: {tickers}...")
    try:
        data = yf.download(tickers, period=period, interval=interval)
        if data.empty:
            print(f"Warning: No data found for tickers {tickers}. Check if symbols are correct.")
            return pd.DataFrame()
        
        print("Data fetched successfully.")
        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

# This block allows you to test the function directly by running this file
if __name__ == '__main__':
    # Example tickers: Apple, Microsoft, and Reliance Industries (NSE)
    sample_tickers = ['AAPL', 'MSFT', 'RELIANCE.NS']
    
    stock_data = fetch_ticker_data(sample_tickers, period="1mo")
    
    if not stock_data.empty:
        print("\nSample of fetched data:")
        # Displaying data for 'Close' price for all tickers
        print(stock_data['Close'].head())