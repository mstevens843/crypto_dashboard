from app.utils.helpers import safe_request 

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
HISTORICAL_DATA_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

def fetch_top_cryptos():
    """Fetch top 10 cryptocurrencies from CoinGecko API with rate limit handling."""
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
    
    print("Fetching latest cryptocurrency data...")
    data = safe_request(COINGECKO_API_URL, params=params)
    
    if not data:
        print("❌ Failed to fetch top cryptocurrencies. Using last known data if available.")
        return []
    
    print(f"✅ Successfully retrieved {len(data)} cryptocurrencies.")
    return data

def fetch_historical_data(coingecko_id, days=30):
    """Fetch historical market data (price, market cap, volume) for a given cryptocurrency."""
    url = HISTORICAL_DATA_URL.format(id=coingecko_id)
    params = {"vs_currency": "usd", "days": days}

    data = safe_request(url, params=params)

    if not data:
        print(f"❌ Failed to fetch historical data for {coingecko_id}.")
    else:
        print(f"✅ Successfully retrieved historical data for {coingecko_id}.")

    return data

def fetch_crypto_by_id(coingecko_id):
    """Fetch specific cryptocurrency details using CoinGecko ID."""
    params = {"vs_currency": "usd", "ids": coingecko_id}

    data = safe_request(COINGECKO_API_URL, params=params)

    if not data:
        print(f"❌ Failed to fetch details for {coingecko_id}.")
    else:
        print(f"✅ Successfully fetched details for {coingecko_id}.")

    return data[0] if data else None  # Return the first result if available
