from app.utils.helpers import safe_request 

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
HISTORICAL_DATA_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

def fetch_top_cryptos():
    """Fetch top 10 cryptocurrencies from CoinGecko API."""
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
    
    return safe_request(COINGECKO_API_URL, params=params)

def fetch_historical_data(coingecko_id, days=30):
    """Fetch historical market data (price, market cap, volume) for a given cryptocurrency."""
    url = HISTORICAL_DATA_URL.format(id=coingecko_id)
    params = {"vs_currency": "usd", "days": days}

    return safe_request(url, params=params)

def fetch_crypto_by_id(coingecko_id):
    """Fetch specific cryptocurrency details using CoinGecko ID."""
    params = {"vs_currency": "usd", "ids": coingecko_id}

    data = safe_request(COINGECKO_API_URL, params=params)
    return data[0] if data else None  # Return the first result if available
