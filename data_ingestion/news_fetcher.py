# In: data_ingestion/news_fetcher.py

import os
import pandas as pd
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fetch_news_headlines(query: str, language='en', page_size=20):
    """
    Fetches news headlines for a given query using the NewsAPI.

    Args:
        query (str): The search term (e.g., "Apple Inc", "Reliance Industries").
        language (str): The language of the articles (e.g., 'en').
        page_size (int): The number of results to return per page.

    Returns:
        pandas.DataFrame: A DataFrame containing news articles,
                          or an empty DataFrame if fetching fails.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("Error: NEWS_API_KEY not found. Please set it in your .env file.")
        return pd.DataFrame()

    newsapi = NewsApiClient(api_key=api_key)
    print(f"Fetching news for query: '{query}'...")

    try:
        # Fetch the latest articles related to the query
        response = newsapi.get_everything(q=query,
                                          language=language,
                                          sort_by='publishedAt', # Get the most recent articles
                                          page_size=page_size)

        if response['status'] == 'ok':
            articles = response['articles']
            # Convert the list of articles to a DataFrame
            df = pd.DataFrame(articles)
            print(f"Successfully fetched {len(articles)} articles.")
            # Select and reorder important columns
            return df[['publishedAt', 'title', 'description', 'source', 'url']]
        else:
            print(f"Error fetching news: {response.get('message')}")
            return pd.DataFrame()

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

# This block allows you to test the function directly
if __name__ == '__main__':
    # Example query
    sample_query = "Tesla Inc"
    
    news_data = fetch_news_headlines(sample_query)
    
    if not news_data.empty:
        print("\nSample of fetched news headlines:")
        # Print the title and published date of the first 5 articles
        print(news_data[['publishedAt', 'title']].head())