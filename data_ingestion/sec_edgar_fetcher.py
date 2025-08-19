# In: data_ingestion/sec_edgar_fetcher.py

import os
import pandas as pd
import requests
from sec_edgar_api import EdgarClient
from dotenv import load_dotenv

load_dotenv()

# --- MODIFIED HELPER FUNCTION TO GET CIK MAPPING ---
def _get_ticker_to_cik_map():
    """
    Fetches the official Ticker-CIK mapping from the SEC and creates a dictionary.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://www.sec.gov/files/company_tickers.json"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        all_companies = response.json()
        
        # This now creates a more robust map for lookup
        # It stores CIK and the primary ticker for each company entry
        cik_map = {
            str(company['cik_str']): {
                'ticker': company.get('ticker', 'N/A'), 
                'title': company.get('title', 'N/A')
            }
            for company in all_companies.values()
        }
        return cik_map
    except Exception as e:
        print(f"Failed to fetch or process Ticker-CIK map: {e}")
        return None

# --- MODIFIED MAIN FUNCTION ---
def fetch_sec_filings(ticker: str, filing_type="10-K", num_filings=3):
    user_name = os.getenv("EDGAR_USER_NAME")
    user_email = os.getenv("EDGAR_USER_EMAIL")

    if not user_name or not user_email:
        print("Error: EDGAR_USER_NAME and EDGAR_USER_EMAIL not found in .env file.")
        return pd.DataFrame()

    cik_map = _get_ticker_to_cik_map()
    if not cik_map:
        return pd.DataFrame()

    # --- NEW, MORE ROBUST CIK LOOKUP LOGIC ---
    cik = None
    # Search the entire map to find a match for the ticker, case-insensitive
    search_ticker = ticker.upper()
    for cik_val, company_info in cik_map.items():
        if company_info['ticker'] == search_ticker:
            cik = str(cik_val).zfill(10)
            break
    
    # If no exact match, try a partial match on the company title (e.g., for GOOG vs GOOGL)
    if not cik:
        for cik_val, company_info in cik_map.items():
            if search_ticker in company_info['title'].upper():
                 cik = str(cik_val).zfill(10)
                 print(f"Ticker {search_ticker} not found. Found partial match in title: '{company_info['title']}'. Using CIK {cik}.")
                 break

    if not cik:
        print(f"Error: Could not find CIK for ticker '{ticker}'.")
        return pd.DataFrame()

    edgar_client = EdgarClient(user_agent=f"{user_name} {user_email}")
    print(f"Fetching {filing_type} filings for CIK: {cik}...")

    try:
        submissions = edgar_client.get_submissions(cik=cik)
        filings_df = pd.DataFrame(submissions['filings']['recent'])
        filtered_filings = filings_df[filings_df['form'] == filing_type].copy()

        if filtered_filings.empty:
            print(f"No {filing_type} filings found for {ticker}.")
            return pd.DataFrame()
        
        filtered_filings['filingDate'] = pd.to_datetime(filtered_filings['filingDate'])
        recent_filings = filtered_filings.sort_values(by='filingDate', ascending=False).head(num_filings)

        print(f"Successfully fetched and filtered {len(recent_filings)} {filing_type} filings.")
        return recent_filings[['filingDate', 'form', 'accessionNumber', 'primaryDocument']]

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()