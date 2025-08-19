# In: backend/scoring_engine.py

import pandas as pd

# The function now takes the ticker as an argument
def engineer_features(ticker: str, market_data: list, news_data: list, filings_data: list) -> dict:
    """
    Takes raw data and engineers a set of features for scoring.
    """
    features = {}

    if market_data:
        market_df = pd.DataFrame(market_data)
        # --- THIS IS THE FIX ---
        # It now uses the provided ticker to find the correct column name dynamically
        close_column_name = f'Close_{ticker.upper()}'
        
        if close_column_name in market_df.columns:
            market_df['Close_'] = pd.to_numeric(market_df[close_column_name])
            features['volatility_30d'] = market_df['Close_'].pct_change().rolling(window=30).std().iloc[-1]
            
            price_90d_ma = market_df['Close_'].rolling(window=90).mean().iloc[-1]
            current_price = market_df['Close_'].iloc[-1]
            features['trend_90d'] = current_price / price_90d_ma
        else:
            print(f"Warning: Column '{close_column_name}' not found in market data.")

    if news_data:
        features['news_volume_7d'] = len(news_data)

    if filings_data:
        features['filings_count_90d'] = len(filings_data)

    return features


def calculate_credit_score(features: dict) -> dict:
    """
    Calculates a credit score based on a dictionary of engineered features.
    Score is on a scale of 0-100 (100 is best).
    """
    score = 100
    explanation = []

    volatility = features.get('volatility_30d', 0)
    if volatility > 0.03:
        score -= 25
        explanation.append(f"High 30-day volatility ({volatility:.2f}) indicates increased market risk.")
    elif volatility > 0.015:
        score -= 10
        explanation.append(f"Moderate 30-day volatility ({volatility:.2f}) suggests some market uncertainty.")

    trend = features.get('trend_90d', 1)
    if trend < 0.9:
        score -= 20
        explanation.append(f"Stock is in a significant downtrend (trading at {trend:.2f} of its 90-day average).")

    news_volume = features.get('news_volume_7d', 0)
    if news_volume > 15:
        score -= 5
        explanation.append(f"High volume of recent news ({news_volume}) suggests a major ongoing event.")
        
    return {"score": max(0, score), "explanation": explanation}