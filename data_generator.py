# In: data_generator.py

import os
import sys
import pandas as pd
import psycopg2
import json
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed # New import

# Add the project root to the Python path
sys.path.append('.')
from data_ingestion.yahoo_finance_fetcher import fetch_ticker_data
from data_ingestion.news_fetcher import fetch_news_headlines
from data_ingestion.fred_fetcher import fetch_macro_data
from backend.scoring_engine import engineer_features, calculate_credit_score

load_dotenv()

def get_db_connection():
    # ... (this function remains the same)
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

def generate_data_point(ticker: str):
    # ... (this function remains the same)
    try:
        print(f"--- Processing ticker: {ticker} ---")
        
        market_data = fetch_ticker_data([ticker], period="1y")
        news_data = fetch_news_headlines(query=f"{ticker} company")
        macro_data = fetch_macro_data()

        if market_data.empty or news_data.empty or not macro_data:
            print(f"Skipping {ticker} due to missing data.")
            return False, ticker

        if isinstance(market_data.columns, pd.MultiIndex):
            market_data.columns = ['_'.join(col).strip() for col in market_data.columns.values]

        market_data_json = market_data.reset_index().to_dict(orient='records')
        news_data_json = news_data.to_dict(orient='records')

        features = engineer_features(ticker, market_data_json, news_data_json, macro_data)
        credit_score_result = calculate_credit_score(features)
        
        conn = get_db_connection()
        cur = conn.cursor()
        insert_query = "INSERT INTO credit_scores (ticker, score, features, explanation) VALUES (%s, %s, %s, %s)"
        score_data = (ticker.upper(), credit_score_result['score'], json.dumps(features), json.dumps(credit_score_result['explanation']))
        cur.execute(insert_query, score_data)
        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully saved score for {ticker}.")
        return True, ticker

    except Exception as e:
        print(f"An error occurred while processing {ticker}: {e}")
        return False, ticker

# --- MODIFIED Main Execution Block ---
if __name__ == "__main__":
    target_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'JPM', 'V', 'PG', 'JNJ', 'UNH', 'HD', 'BAC']
    target_data_points = 150 # Reduced target for faster completion
    
    generated_count = 0
    
    # Create a list of tasks to run in a loop
    tasks = []
    while len(tasks) < target_data_points:
        tasks.extend(target_tickers)
    tasks = tasks[:target_data_points]
    
    # Use a ThreadPoolExecutor to run tasks in parallel
    # max_workers=4 means it will process up to 4 tickers at a time
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(generate_data_point, task) for task in tasks]
        
        for future in as_completed(futures):
            success, ticker = future.result()
            if success:
                generated_count += 1
                print(f"--> Progress: {generated_count} / {target_data_points} data points generated for {ticker}.")
            
    print(f"\nData generation complete. Total points generated: {generated_count}")