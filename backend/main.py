# In: backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import pandas as pd
import os
import psycopg2
import json
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.append('..')
from data_ingestion.yahoo_finance_fetcher import fetch_ticker_data
from data_ingestion.news_fetcher import fetch_news_headlines
from data_ingestion.fred_fetcher import fetch_macro_data
from backend.scoring_engine import engineer_features, calculate_credit_score

# Create an instance of the FastAPI application
app = FastAPI(
    title="Real-Time Explainable Credit Intelligence API",
    description="API for fetching real-time credit data and scores.",
    version="1.0.0"
)

# --- CORS MIDDLEWARE SETUP ---
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Establishes a robust database connection using individual .env variables."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

@app.get("/")
def read_root():
    """Root endpoint for the API. Provides a simple health check."""
    return {"status": "ok", "message": "Credit Intelligence API is running"}

@app.get("/data/{ticker}")
async def get_all_data(ticker: str):
    """Fetches all data, engineers features, calculates a score, checks for alerts, saves it, and returns the result."""
    print(f"Received request for ticker: {ticker}")
    
    # 1. Fetch data
    market_data = fetch_ticker_data([ticker], period="1y")
    news_data = fetch_news_headlines(query=f"{ticker} company")
    macro_data = fetch_macro_data()
    
    # 2. Pre-process data
    if isinstance(market_data.columns, pd.MultiIndex):
        market_data.columns = ['_'.join(col).strip() for col in market_data.columns.values]

    market_data_json, news_data_json = [], []
    if not market_data.empty:
        market_data_df = market_data.reset_index()
        market_data_df['Date'] = market_data_df['Date'].dt.strftime('%Y-%m-%d')
        market_data_json = market_data_df.to_dict(orient='records')
    if not news_data.empty:
        news_df_temp = news_data.copy()
        news_df_temp['publishedAt'] = pd.to_datetime(news_df_temp['publishedAt']).dt.strftime('%Y-%m-%d %H:%M:%S')
        news_data_json = news_df_temp.to_dict(orient='records')
        
    # 3. Engineer features
    features_df = engineer_features(ticker, market_data_json, news_data_json, macro_data)
    
    # 4. Calculate the score using the ML model
    credit_score_result = calculate_credit_score(features_df)
    
    # 5. Find the Key Driving Headline
    key_headline = "No significant news events found."
    if news_data_json:
        analyzer = SentimentIntensityAnalyzer()
        max_sentiment_score = -1
        for article in news_data_json:
            sentiment = analyzer.polarity_scores(article['title'])['compound']
            if abs(sentiment) > max_sentiment_score:
                max_sentiment_score = abs(sentiment)
                key_headline = article['title']
    credit_score_result['key_headline'] = key_headline
    
    # 6. Save to DB, check for alerts
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Alert Logic: Get the most recent score before this one
        query = "SELECT score FROM credit_scores WHERE ticker = %s ORDER BY created_at DESC LIMIT 1"
        cur.execute(query, (ticker.upper(),))
        previous_score = cur.fetchone()
        
        if previous_score and credit_score_result['score'] < previous_score[0] - 10: # Drop of >10 points
            credit_score_result['alert'] = f"Significant Score Drop from {previous_score[0]}"

        # Database Insert Logic
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
        print(f"Successfully saved score for {ticker} to the database.")
    except Exception as e:
        print(f"Database error: {e}")

    # 7. Return the final response
    return {
        "ticker": ticker,
        "credit_score": credit_score_result,
        "features": features_df.to_dict(orient='records')[0],
        "raw_data": {
            "market_data": market_data_json,
            "news": news_data_json,
            "macro_data": macro_data
        }
    }

@app.get("/history/{tickers}")
async def get_score_history(tickers: str):
    """Fetches historical scores for one or more comma-separated tickers."""
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(',')]
    history = {}
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        for ticker in ticker_list:
            history[ticker] = []
            select_query = "SELECT created_at, score FROM credit_scores WHERE ticker = %s ORDER BY created_at DESC LIMIT 30"
            cur.execute(select_query, (ticker,))
            
            records = cur.fetchall()
            ticker_history = [{"date": row[0].strftime('%Y-%m-%d %H:%M'), "score": row[1]} for row in records]
            history[ticker] = sorted(ticker_history, key=lambda x: x['date'])

        cur.close()
        conn.close()
        print(f"Successfully fetched historical records for {ticker_list}.")
    except Exception as e:
        print(f"Database history error: {e}")

    return history