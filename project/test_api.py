import requests

def test_api_call():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}

    response = requests.get(url, params=params)
    print(f"API response status code: {response.status_code}")
    print(response.json())

test_api_call()