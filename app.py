from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
import locale
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from sqlalchemy import func
import datetime
import time

print("Flask app has started!")

app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy with Flask app
from project.models import db, Cryptocurrency, HistoricalData
db.init_app(app)

# Set the locale for currency formatting
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def format_currency(value):
    return locale.currency(value, grouping=True)

app.jinja_env.filters['format_currency'] = format_currency

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FUNCTION TO FETCH AND POPULATE TOP 10 CRYPTOCURRENCIES
def populate_top_10():
    logger.debug("Starting to populate the top 10 cryptocurrencies...")

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            
            for i, coin in enumerate(data):
                print(f"Processing coin: {coin['name']}")

                # Check if this coin already exists
                currency = Cryptocurrency.query.filter_by(coingecko_id=coin['id']).first()

                if not currency:
                    # Create new entry if cryptocurrency does not exist
                    currency = Cryptocurrency(
                        coingecko_id=coin['id'],
                        name=coin['name'],
                        current_price=coin['current_price'],
                        market_cap=coin['market_cap'],
                        volume=coin['total_volume'],
                        last_updated=db.func.current_timestamp()
                    )
                    db.session.add(currency)
                else:
                    # Only update the database if price has changed to minimize writes
                    if currency.current_price != coin['current_price']:
                        currency.current_price = coin['current_price']
                        currency.market_cap = coin['market_cap']
                        currency.volume = coin['total_volume']
                        currency.last_updated = db.func.current_timestamp()

                db.session.commit()

                # Fetch historical data for past 30 days, but avoid unnecessary API calls
                historical_url = f"https://api.coingecko.com/api/v3/coins/{coin['id']}/market_chart"
                historical_params = {"vs_currency": "usd", "days": "30"}
                historical_response = requests.get(historical_url, params=historical_params)

                if historical_response.status_code == 200:
                    historical_data = historical_response.json()
                    
                    for day_data in historical_data['prices']:
                        date = datetime.datetime.fromtimestamp(day_data[0] / 1000.0).date()
                        price = day_data[1]

                        existing_data = HistoricalData.query.filter_by(cryptocurrency_id=currency.id, date=date).first()

                        if not existing_data:
                            historical_entry = HistoricalData(
                                cryptocurrency_id=currency.id,
                                date=date,
                                price=price,
                                market_cap=next((item[1] for item in historical_data['market_caps'] if item[0] == day_data[0]), None),
                                volume=next((item[1] for item in historical_data['total_volumes'] if item[0] == day_data[0]), None)
                            )
                            db.session.add(historical_entry)

                elif historical_response.status_code == 429:
                    # Rate limit exceeded: Introduce a longer delay
                    print("Rate limit exceeded. Pausing for 90 seconds.")
                    time.sleep(90)  # Wait before retrying
                    continue  # Retry the current coin
                else:
                    print(f"Failed to fetch historical data: {historical_response.status_code}")

                db.session.commit()

                # Introduce a delay every 3 API calls to prevent rate limits
                if (i + 1) % 3 == 0:
                    print("Pausing to prevent rate limits...")
                    time.sleep(10)

            print("Top 10 cryptocurrencies and historical data populated successfully.")

        else:
            print(f"Failed to fetch data: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Create a function to create db tables and populate data
def create_tables():
    with app.app_context():
        db.create_all()
        print("Tables created.")
        
        # Test a simple query
        try:
            test_query = db.session.execute('SELECT 1')
            print("Database connection is working.")
        except Exception as e:
            print(f"Database connection failed: {e}")

        try:
            with app.app_context():
                print("Calling populate_top_10 function...")
                populate_top_10()
        except Exception as e:
            print(f"An error occurred when calling populate_top_10: {e}")

# Function to be scheduled for periodic updates
def scheduled_update():
    with app.app_context():
        populate_top_10()

# Run the app
if __name__ == "__main__":
    print("Running the app and creating tables...")
    create_tables()  # Create tables and populate data if they don't exist.
    
    # Set up the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_update, 'interval', minutes=30)  # Update every 30 minutes
    scheduler.start()
    
    try:
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

# ROUTES

# Display overview of crypto data
@app.route('/')
def index():
    cryptocurrencies = Cryptocurrency.query.all()
    return render_template('index.html', cryptocurrencies=cryptocurrencies)

# Show info about specific crypto
@app.route('/currency/<string:coingecko_id>')
def currency_detail(coingecko_id):
    currency = Cryptocurrency.query.filter_by(coingecko_id=coingecko_id).first_or_404()
    historical_data = HistoricalData.query.filter_by(cryptocurrency_id=currency.id).order_by(HistoricalData.date.asc()).all()
    return render_template('currency_details.html', currency=currency, historical_data=historical_data)

# Combined Add/Edit Currency Route
@app.route('/manage_currency', methods=['GET', 'POST'])
@app.route('/manage_currency/<int:id>', methods=['GET', 'POST'])
def manage_currency(id=None):
    currency = Cryptocurrency.query.get(id) if id else None
    
    if request.method == 'POST':
        try:
            coingecko_id = request.form['coingecko_id']
            
            # Fetch data from CoinGecko API
            url = f"https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": coingecko_id
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()[0]  # Get the first item from the list

                # Extract relevant information
                name = data['name']
                current_price = data['current_price']
                market_cap = data['market_cap']
                volume = data['total_volume']

                if currency:  # If editing
                    currency.name = name
                    currency.coingecko_id = coingecko_id
                    currency.current_price = current_price
                    currency.market_cap = market_cap
                    currency.volume = volume
                else:  # If adding new
                    currency = Cryptocurrency(
                        name=name,
                        coingecko_id=coingecko_id,
                        current_price=current_price,
                        market_cap=market_cap,
                        volume=volume
                    )
                    db.session.add(currency)

                db.session.commit()
                flash(f'Cryptocurrency {"updated" if id else "added"} successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash(f"Failed to fetch data from CoinGecko API: {response.status_code}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('manage_currency.html', currency=currency)


# DATA VISUALIZATION ROUTE

# Display charts showing price changes over time
@app.route('/trends')
def trends():
    # Get the selected cryptocurrency from the query parameters, default to 'bitcoin'
    selected_crypto = request.args.get('crypto', 'bitcoin')

    # Query the top 10 cryptocurrencies to populate the dropdown
    top_10_cryptos = Cryptocurrency.query.order_by(Cryptocurrency.market_cap.desc()).limit(10).all()

    # Fetch the historical data for the selected cryptocurrency
    historical_data = (db.session.query(
        HistoricalData.date,
        HistoricalData.price,
        HistoricalData.market_cap
    )
    .join(Cryptocurrency)
    .filter(Cryptocurrency.coingecko_id == selected_crypto)
    .order_by(HistoricalData.date.asc())
    .all())

    dates = [data.date.strftime('%Y-%m-%d') for data in historical_data]
    prices = [data.price for data in historical_data]
    market_caps = [data.market_cap for data in historical_data]

    return render_template('trends.html', top_10_cryptos=top_10_cryptos, selected_crypto=selected_crypto, dates=dates, prices=prices, market_caps=market_caps)

# API CALL FOR DATA UPDATE

# Update prices: route to manually trigger an update of crypto prices through the API
@app.route('/update_prices')
def update_prices():
    try:
        from utils import update_cryptocurrency_prices  # Import the function here to avoid circular imports
        update_cryptocurrency_prices()  # Assuming function to handle API call and update db
        flash('Prices updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating prices: {str(e)}', 'danger')
    return redirect(url_for('index'))

# ABOUT PAGE

# Provide info about the dashboard, how to use it, sources of data, etc.
@app.route('/about')
def about():
    return render_template('about.html')

# Dedicated route to display historical data for all cryptocurrencies, allowing users to see trends across multiple currencies.
@app.route('/historical')
def historical():
    historical_data = HistoricalData.query.order_by(HistoricalData.date.asc()).all()
    return render_template('historical.html', historical_data=historical_data)
