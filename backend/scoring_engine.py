# In: backend/scoring_engine.py

import pandas as pd
import joblib
import shap
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    model = joblib.load('credit_model.pkl')
    explainer = shap.TreeExplainer(model)
    MODEL_FEATURES = model.feature_names_in_
    print("✅ Model and SHAP explainer loaded successfully.")
    print(f"Model expects features: {MODEL_FEATURES}")
except Exception as e:
    model = None
    explainer = None
    MODEL_FEATURES = []
    print(f"❌ Model loading failed: {e}. Scoring will be disabled.")


def engineer_features(ticker: str, market_data: list, news_data: list, macro_data: dict) -> pd.DataFrame:
    latest_market_data = pd.DataFrame(market_data).iloc[-1]
    
    features = {
        'Open': latest_market_data.get(f'Open_{ticker.upper()}'),
        'High': latest_market_data.get(f'High_{ticker.upper()}'),
        'Low': latest_market_data.get(f'Low_{ticker.upper()}'),
        'Close': latest_market_data.get(f'Close_{ticker.upper()}'),
        'Volume': latest_market_data.get(f'Volume_{ticker.upper()}'),
    }

    if news_data:
        news_df = pd.DataFrame(news_data)
        analyzer = SentimentIntensityAnalyzer()
        
        NEGATIVE_KEYWORDS = ['layoffs', 'debt', 'downgrade', 'lawsuit', 'investigation', 'recall', 'outage', 'cuts', 'fine']
        POSITIVE_KEYWORDS = ['expansion', 'profit', 'upgrade', 'hiring', 'record', 'partnership', 'launch', 'beats', 'growth']

        news_df['sentiment'] = news_df['title'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
        features['sentiment'] = news_df['sentiment'].mean()
        features['positive_events'] = sum(1 for title in news_df['title'] if any(kw in title.lower() for kw in POSITIVE_KEYWORDS))
        features['negative_events'] = sum(1 for title in news_df['title'] if any(kw in title.lower() for kw in NEGATIVE_KEYWORDS))

    if macro_data:
        features.update(macro_data)
        
    features_df = pd.DataFrame([features])
    
    for col in MODEL_FEATURES:
        if col not in features_df.columns:
            features_df[col] = 0
            
    return features_df[MODEL_FEATURES]


def calculate_credit_score(features_df: pd.DataFrame) -> dict:
    if model is None or features_df.empty:
        return {"score": -1, "explanation": "Model not loaded or features missing."}

    predicted_value = model.predict(features_df)[0]
    
    score = 50 + (predicted_value * 2000)
    score = max(0, min(100, score))
    
    shap_values = explainer.shap_values(features_df)
    
    feature_names = features_df.columns
    contributions = {name: round(val, 5) for name, val in zip(feature_names, shap_values[0])}
    
    explanation = {
        "base_value": round(explainer.expected_value[0], 5),
        "prediction": round(predicted_value, 5),
        "contributions": contributions
    }
    
    return {"score": int(score), "explanation": explanation}