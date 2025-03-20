from app.models import db, Cryptocurrency, HistoricalData
from sqlalchemy import func
import time  
from app.services.coingecko_service import fetch_historical_data, fetch_top_cryptos  
from app.utils.helpers import format_date 

def update_cryptocurrencies():
    """Fetch and update the top 10 cryptocurrencies from CoinGecko API."""
    while True:  # Loop to retry if rate-limited
        crypto_data = fetch_top_cryptos()  

        if crypto_data:
            break  # Exit loop if request succeeds

        print("Rate limit exceeded. Pausing for 60 seconds before retrying...")
        time.sleep(60)  # **Wait before retrying**

    existing_cryptos = {c.coingecko_id: c for c in Cryptocurrency.query.all()}
    new_cryptos = []

    for coin in crypto_data:
        print(f"Processing coin: {coin['name']}")

        currency = existing_cryptos.get(coin['id'])
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
                last_updated=func.current_timestamp()
            )
            db.session.add(currency)
        else:
            currency.current_price = coin['current_price']
            currency.market_cap = coin['market_cap']
            currency.volume = coin['total_volume']
            currency.circulating_supply = coin['circulating_supply']
            currency.total_supply = coin['total_supply']
            currency.max_supply = coin['max_supply']
            currency.last_updated = func.current_timestamp()

        # **Fetch historical data for 30 days**
        update_historical_data(coin['id'], currency.id)

        db.session.commit()  # Commit after processing each coin

def update_historical_data(coingecko_id, crypto_id):
    """Fetch and store historical market data for a cryptocurrency."""
    print(f"Fetching historical data for {coingecko_id}...")
    historical_data = fetch_historical_data(coingecko_id)

    if not historical_data or 'prices' not in historical_data:
        print(f"Failed to fetch historical data for {coingecko_id}.")
        return

    new_entries = []
    for day_data in historical_data['prices']:
        date = format_date(day_data[0])  
        price = day_data[1]
        market_cap = next((item[1] for item in historical_data['market_caps'] if item[0] == day_data[0]), None)
        volume = next((item[1] for item in historical_data['total_volumes'] if item[0] == day_data[0]), None)

        existing_data = HistoricalData.query.filter_by(cryptocurrency_id=crypto_id, date=date).first()
        if not existing_data:
            new_entries.append(HistoricalData(
                cryptocurrency_id=crypto_id,
                date=date,
                price=price,
                market_cap=market_cap,
                volume=volume
            ))

    if new_entries:
        db.session.bulk_save_objects(new_entries)
        db.session.commit()
    else:
        print(f"Historical data for {coingecko_id} already up to date.")

def create_tables():
    """Create database tables and populate data if they don't exist."""
    with db.session.begin():
        db.create_all()
        print("Tables created.")

        try:
            db.session.execute('SELECT 1')
            print("Database connection is working.")
        except Exception as e:
            print(f"Database connection failed: {e}")

        try:
            print("Populating top 10 cryptocurrencies...")
            update_cryptocurrencies()
        except Exception as e:
            print(f"An error occurred when populating cryptocurrencies: {e}")
