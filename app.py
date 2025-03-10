from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
import locale
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from sqlalchemy import func
import datetime
import time
import os
from flask_migrate import Migrate, upgrade  # Import Flask-Migrate and upgrade

print("Flask app has started!")

app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy with Flask app
from project.models import db, Cryptocurrency, HistoricalData
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# ======== MIGRATIONS ON STARTUP ======== #
with app.app_context():
    try:
        print("Running database migrations...")
        upgrade()
        print("✅ Database migrations applied successfully.")
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")


# ======== SET LOCALE ======== #
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')

def format_currency(value):
    return locale.currency(value, grouping=True)

app.jinja_env.filters['format_currency'] = format_currency

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# ======== POPULATE TOP 10 ======== #
def populate_top_10():
    logger.debug("📊 Populating top 10 cryptocurrencies...")

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            for i, coin in enumerate(data):
                print(f"🔹 Processing: {coin['name']}")

                currency = Cryptocurrency.query.filter_by(coingecko_id=coin['id']).first()
                if not currency:
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
                    if currency.current_price != coin['current_price']:
                        currency.current_price = coin['current_price']
                        currency.market_cap = coin['market_cap']
                        currency.volume = coin['total_volume']
                        currency.last_updated = db.func.current_timestamp()

                db.session.commit()

                # ====== HISTORICAL DATA ====== #
                hist_url = f"https://api.coingecko.com/api/v3/coins/{coin['id']}/market_chart"
                hist_params = {"vs_currency": "usd", "days": "30"}
                hist_resp = requests.get(hist_url, params=hist_params)

                if hist_resp.status_code == 200:
                    hist_data = hist_resp.json()

                    for day_data in hist_data['prices']:
                        date = datetime.datetime.fromtimestamp(day_data[0] / 1000.0).date()
                        price = day_data[1]

                        existing_data = HistoricalData.query.filter_by(cryptocurrency_id=currency.id, date=date).first()
                        if not existing_data:
                            historical_entry = HistoricalData(
                                cryptocurrency_id=currency.id,
                                date=date,
                                price=price,
                                market_cap=next((m[1] for m in hist_data['market_caps'] if m[0] == day_data[0]), None),
                                volume=next((v[1] for v in hist_data['total_volumes'] if v[0] == day_data[0]), None)
                            )
                            db.session.add(historical_entry)

                elif hist_resp.status_code == 429:
                    print("⚠️ Rate limit exceeded. Pausing for 90 seconds.")
                    time.sleep(90)
                    continue

                db.session.commit()

                # Introduce a delay every 3 API calls to prevent rate limits
                if (i + 1) % 3 == 0:
                    print("⏳ Pausing to prevent rate limits...")
                    time.sleep(10)

            print("✅ Top 10 cryptocurrencies populated successfully.")
        else:
            print(f"❌ Failed to fetch data: {response.status_code}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")


# ======== ROUTES ======== #
@app.route('/')
def index():
    cryptocurrencies = Cryptocurrency.query.all()
    return render_template('index.html', cryptocurrencies=cryptocurrencies)

@app.route('/currency/<string:coingecko_id>')
def currency_detail(coingecko_id):
    currency = Cryptocurrency.query.filter_by(coingecko_id=coingecko_id).first_or_404()
    historical_data = (HistoricalData.query
                       .filter_by(cryptocurrency_id=currency.id)
                       .order_by(HistoricalData.date.asc())
                       .all())
    return render_template('currency_details.html', currency=currency, historical_data=historical_data)

@app.route('/manage_currency', methods=['GET', 'POST'])
@app.route('/manage_currency/<int:id>', methods=['GET', 'POST'])
def manage_currency(id=None):
    currency = Cryptocurrency.query.get(id) if id else None
    if request.method == 'POST':
        try:
            coingecko_id = request.form['coingecko_id']
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {"vs_currency": "usd", "ids": coingecko_id}
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()[0]
                name = data['name']
                current_price = data['current_price']
                market_cap = data['market_cap']
                volume = data['total_volume']

                if currency:
                    currency.name = name
                    currency.coingecko_id = coingecko_id
                    currency.current_price = current_price
                    currency.market_cap = market_cap
                    currency.volume = volume
                else:
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
                flash(f"❌ Failed to fetch data from CoinGecko API: {response.status_code}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error: {str(e)}', 'danger')
    return render_template('manage_currency.html', currency=currency)

@app.route('/trends')
def trends():
    selected_crypto = request.args.get('crypto', 'bitcoin')
    top_10_cryptos = (Cryptocurrency.query
                      .order_by(Cryptocurrency.market_cap.desc())
                      .limit(10).all())

    historical_data = (db.session.query(HistoricalData.date, HistoricalData.price, HistoricalData.market_cap)
                       .join(Cryptocurrency)
                       .filter(Cryptocurrency.coingecko_id == selected_crypto)
                       .order_by(HistoricalData.date.asc())
                       .all())

    return render_template('trends.html',
                           top_10_cryptos=top_10_cryptos,
                           selected_crypto=selected_crypto,
                           historical_data=historical_data)

@app.route('/update_prices')
def update_prices():
    try:
        from utils import update_cryptocurrency_prices
        update_cryptocurrency_prices()
        flash('Prices updated successfully!', 'success')
    except Exception as e:
        flash(f'❌ Error updating prices: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/historical')
def historical():
    historical_data = HistoricalData.query.order_by(HistoricalData.date.asc()).all()
    return render_template('historical.html', historical_data=historical_data)


# ======== STARTUP: SCHEDULER + RUN ======== #
if __name__ == "__main__":
    # Start scheduler for periodic updates
    scheduler = BackgroundScheduler()
    scheduler.add_job(populate_top_10, 'interval', minutes=30)
    scheduler.start()

    # Finally run Flask
    try:
        print("🟢 Starting Flask app...")
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("🛑 Scheduler shutdown.")
