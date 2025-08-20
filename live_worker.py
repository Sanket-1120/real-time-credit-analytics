# In: live_worker.py

import os
import sys
import pandas as pd
import psycopg2
import json
import time
from dotenv import load_dotenv

# Add the project root to the Python path to allow imports
sys.path.append('.')
from data_ingestion.yahoo_finance_fetcher import fetch_ticker_data
from data_ingestion.news_fetcher import fetch_news_headlines
from data_ingestion.fred_fetcher import fetch_macro_data
from backend.scoring_engine import engineer_features, calculate_credit_score

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """Establishes a robust database connection using individual .env variables."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

def generate_live_data_point(ticker: str):
    """
    Fetches the latest data for a single ticker, calculates a score using the ML model,
    and saves it to the database.
    """
    try:
        print(f"\n--- Processing live data for ticker: {ticker} ---")
        
        # 1. Fetch live data
        market_data = fetch_ticker_data([ticker], period="1y")
        news_data = fetch_news_headlines(query=f"{ticker} company")
        macro_data = fetch_macro_data()

        if market_data.empty or news_data.empty or not macro_data:
            print(f"Skipping {ticker} due to missing live data.")
            return False

        # 2. Pre-process data
        if isinstance(market_data.columns, pd.MultiIndex):
            market_data.columns = ['_'.join(col).strip() for col in market_data.columns.values]
        market_data_json = market_data.reset_index().to_dict(orient='records')
        news_data_json = news_data.to_dict(orient='records')

        # 3. Engineer features for the ML model
        features_df = engineer_features(ticker, market_data_json, news_data_json, macro_data)
        
        # 4. Calculate score using the ML model
        credit_score_result = calculate_credit_score(features_df)
        
        # 5. Save the new score to the database
        conn = get_db_connection()
        cur = conn.cursor()
        insert_query = "INSERT INTO credit_scores (ticker, score, features, explanation) VALUES (%s, %s, %s, %s)"
        score_data = (
            ticker.upper(),
            credit_score_result['score'],
            json.dumps(features_df.to_dict(orient='records')[0]),
            json.dumps(credit_score_result['explanation'])
        )
        cur.execute(insert_query, score_data)
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Successfully saved new live score for {ticker}.")
        return True

    except Exception as e:
        print(f"❌ An error occurred while processing {ticker}: {e}")
        return False

# --- Main Execution Loop ---
if __name__ == "__main__":
    target_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    # This loop will run forever to continuously update scores
    while True:
        print(f"\n--- Starting new scoring cycle at {time.ctime()} ---")
        for ticker in target_tickers:
            generate_live_data_point(ticker)
            # Pause between tickers to respect API rate limits
            time.sleep(15) 
            
        # Wait for 5 minutes before starting the next full cycle
        print("\n--- Cycle complete. Waiting for 15 minutes... ---")
        time.sleep(300)