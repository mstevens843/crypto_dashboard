import requests
from models import Cryptocurrency, HistoricalData
from app import db

def populate_top_10():
    try:
        print("Starting to populate the top 10 cryptocurrencies...")

        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}

        response = requests.get(url, params=params)
        print(f"API response status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for coin in data:
                print(f"Processing coin: {coin['name']}")

                currency = Cryptocurrency.query.filter_by(coingecko_id=coin['id']).first()
                if not currency:
                    currency = Cryptocurrency(
                        coingecko_id=coin['id'],
                        name=coin['name'],
                        current_price=coin['current_price'],
                        market_cap=coin['market_cap'],
                        volume=coin['total_volume'],
                        circulating_supply=coin['circulating_supply'],
                        total_supply=coin['total_supply'],
                        max_supply=coin['max_supply'],
                        last_updated=db.func.current_timestamp()
                    )
                    db.session.add(currency)
                    print(f"Added {coin['name']} to the database.")
                else:
                    currency.current_price = coin['current_price']
                    currency.market_cap = coin['market_cap']
                    currency.volume = coin['total_volume']
                    currency.circulating_supply = coin['circulating_supply']
                    currency.total_supply = coin['total_supply']
                    currency.max_supply = coin['max_supply']
                    currency.last_updated = db.func.current_timestamp()
                    print(f"Updated {coin['name']} in the database.")

                # Store historical data
                historical_data = HistoricalData(
                    cryptocurrency_id=currency.id,
                    date=db.func.current_date(),
                    price=coin['current_price'],
                    market_cap=coin['market_cap'],
                    volume=coin['total_volume']
                )
                db.session.add(historical_data)
                print(f"Added historical data for {coin['name']}.")

            db.session.commit()
            print("Top 10 cryptocurrencies populated successfully.")

        else:
            print(f"Failed to fetch data: {response.status_code}")
            raise Exception(f"Error fetching data: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")