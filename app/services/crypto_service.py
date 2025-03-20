from app.models import db, Cryptocurrency, HistoricalData
from sqlalchemy import func
import time
import datetime  
from app.services.coingecko_service import fetch_historical_data, fetch_top_cryptos  
from app.utils.helpers import format_date 

def update_cryptocurrencies():
    """Fetch and update the top 10 cryptocurrencies from CoinGecko API."""
    retry_attempts = 3  # Limit retry attempts to avoid infinite loop

    for attempt in range(retry_attempts):
        crypto_data = fetch_top_cryptos()
        if crypto_data:
            break  # Exit loop if request succeeds
        print(f"Rate limit exceeded. Retrying in 60 seconds... (Attempt {attempt + 1}/{retry_attempts})")
        time.sleep(60)  # **Wait before retrying**
    else:
        print("❌ Failed to fetch top cryptocurrencies after multiple attempts.")
        return

    existing_cryptos = {c.coingecko_id: c for c in Cryptocurrency.query.all()}
    new_cryptos = []

    for coin in crypto_data:
        print(f"🔄 Processing coin: {coin['name']} ({coin['id']})")

        currency = existing_cryptos.get(coin['id'])
        if not currency:
            print(f"➕ Adding new cryptocurrency: {coin['name']}")
            currency = Cryptocurrency(
                coingecko_id=coin['id'],
                name=coin['name'],
                current_price=coin['current_price'],
                market_cap=coin['market_cap'],
                volume=coin['total_volume'],
                circulating_supply=coin['circulating_supply'],
                total_supply=coin.get('total_supply'),
                max_supply=coin.get('max_supply'),
                last_updated=datetime.datetime.utcnow()  # ✅ Fix: Use actual timestamp
            )
            db.session.add(currency)
        else:
            print(f"🔄 Updating {coin['name']} in database.")
            currency.current_price = coin['current_price']
            currency.market_cap = coin['market_cap']
            currency.volume = coin['total_volume']
            currency.circulating_supply = coin['circulating_supply']
            currency.total_supply = coin.get('total_supply')
            currency.max_supply = coin.get('max_supply')
            currency.last_updated = datetime.datetime.utcnow()  # ✅ Fix

        new_cryptos.append(currency)

    db.session.commit()  # ✅ Fix: Commit only once after the loop
    print("✅ Cryptocurrency updates complete.")

    # Fetch historical data
    for coin in new_cryptos:
        update_historical_data(coin.coingecko_id, coin.id)

def update_historical_data(coingecko_id, crypto_id):
    """Fetch and store historical market data for a cryptocurrency."""
    print(f"📊 Fetching historical data for {coingecko_id}...")
    historical_data = fetch_historical_data(coingecko_id)

    if not historical_data or 'prices' not in historical_data:
        print(f"❌ No historical data found for {coingecko_id}.")
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
        print(f"📝 Inserting {len(new_entries)} historical data entries for {coingecko_id}.")
        db.session.bulk_save_objects(new_entries)
        db.session.commit()
    else:
        print(f"✅ Historical data for {coingecko_id} is already up to date.")

def create_tables():
    """Create database tables and populate data if they don't exist."""
    from app import create_app  # ✅ Fix: Import app factory

    app = create_app()
    with app.app_context():  # ✅ Fix: Ensure app context exists
        db.create_all()
        print("🛠️ Tables created successfully.")

        try:
            db.session.execute('SELECT 1')
            print("✅ Database connection successful.")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

        try:
            print("📊 Populating top 10 cryptocurrencies...")
            update_cryptocurrencies()
        except Exception as e:
            print(f"❌ Error populating cryptocurrencies: {e}")
