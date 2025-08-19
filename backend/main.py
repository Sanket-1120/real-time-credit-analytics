# In: backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import pandas as pd
import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()

sys.path.append('..')
from data_ingestion.yahoo_finance_fetcher import fetch_ticker_data
from data_ingestion.news_fetcher import fetch_news_headlines
from data_ingestion.sec_edgar_fetcher import fetch_sec_filings
from backend.scoring_engine import engineer_features, calculate_credit_score

app = FastAPI(title="Real-Time Explainable Credit Intelligence API", version="1.0.0")

origins = ["http://localhost:5173", "http://localhost:5174"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db_connection():
    # --- THIS IS THE FIX FOR THE DATABASE CONNECTION ---
    # It reads the separate variables from the .env file
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Credit Intelligence API is running"}

@app.get("/data/{ticker}")
async def get_all_data(ticker: str):
    print(f"Received request for ticker: {ticker}")
    
    market_data = fetch_ticker_data([ticker], period="1y")
    news_data = fetch_news_headlines(query=f"{ticker} company")
    filings_data = fetch_sec_filings(ticker=ticker, filing_type="10-Q", num_filings=5)
    
    if isinstance(market_data.columns, pd.MultiIndex):
        market_data.columns = ['_'.join(col).strip() for col in market_data.columns.values]

    market_data_json = []
    if not market_data.empty:
        market_data_df = market_data.reset_index()
        market_data_df['Date'] = market_data_df['Date'].dt.strftime('%Y-%m-%d')
        market_data_json = market_data_df.to_dict(orient='records')

    news_data_json = []
    if not news_data.empty:
        news_data['publishedAt'] = pd.to_datetime(news_data['publishedAt']).dt.strftime('%Y-%m-%d %H:%M:%S')
        news_data_json = news_data.to_dict(orient='records')

    filings_data_json = []
    if not filings_data.empty:
        filings_data['filingDate'] = filings_data['filingDate'].dt.strftime('%Y-%m-%d')
        filings_data_json = filings_data.to_dict(orient='records')
        
    # --- THIS IS THE FIX FOR THE SCORING ENGINE ---
    # Pass the ticker to the engineer_features function
    features = engineer_features(
        ticker, # Pass the ticker here
        market_data=market_data_json, 
        news_data=news_data_json, 
        filings_data=filings_data_json
    )
    
    credit_score_result = calculate_credit_score(features)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        insert_query = "INSERT INTO credit_scores (ticker, score, features, explanation) VALUES (%s, %s, %s, %s)"
        score_data = (ticker.upper(), credit_score_result['score'], json.dumps(features), json.dumps(credit_score_result['explanation']))
        cur.execute(insert_query, score_data)
        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully saved score for {ticker} to the database.")
    except Exception as e:
        print(f"Database error: {e}")

    return {"ticker": ticker, "credit_score": credit_score_result, "features": features, "raw_data": {"market_data": market_data_json, "news": news_data_json, "filings": filings_data_json}}

@app.get("/history/{ticker}")
async def get_score_history(ticker: str):
    history = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        select_query = "SELECT created_at, score FROM credit_scores WHERE ticker = %s ORDER BY created_at DESC LIMIT 30"
        cur.execute(select_query, (ticker.upper(),))
        records = cur.fetchall()
        for row in records:
            history.append({"date": row[0].strftime('%Y-%m-%d %H:%M'), "score": row[1]})
        cur.close()
        conn.close()
        print(f"Successfully fetched {len(history)} historical records for {ticker}.")
    except Exception as e:
        print(f"Database history error: {e}")

    return sorted(history, key=lambda x: x['date'])