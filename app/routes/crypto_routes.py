from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Cryptocurrency, HistoricalData
from app.services.coingecko_service import fetch_top_cryptos
from app.services.crypto_service import update_cryptocurrencies
from app.utils.helpers import format_currency, format_date  # Import helper functions


crypto_bp = Blueprint('crypto', __name__)

# Home Page - Displays all cryptocurrencies
@crypto_bp.route('/')
def index():
    cryptocurrencies = Cryptocurrency.query.all()
    return render_template('index.html', cryptocurrencies=cryptocurrencies, format_currency=format_currency)

# Update Prices - Fetch latest prices and update the database
@crypto_bp.route('/update_prices')
def update_prices():
    try:
        crypto_data = fetch_top_cryptos()
        update_cryptocurrencies(crypto_data)
        flash('Prices updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating prices: {str(e)}', 'danger')
    return redirect(url_for('crypto.index'))

# Cryptocurrency Details - Displays historical data for a single crypto
@crypto_bp.route('/currency/<string:coingecko_id>')
def currency_detail(coingecko_id):
    currency = Cryptocurrency.query.filter_by(coingecko_id=coingecko_id).first_or_404()
    historical_data = HistoricalData.query.filter_by(cryptocurrency_id=currency.id).order_by(HistoricalData.date.asc()).all()

    # Format historical dates before sending them to the template
    formatted_historical_data = [
        {'date': format_date(data.date.timestamp()), 'price': data.price, 'market_cap': data.market_cap}
        for data in historical_data
    ]

    return render_template('currency_details.html', currency=currency, historical_data=formatted_historical_data)

# Add/Edit Cryptocurrency
@crypto_bp.route('/manage_currency', methods=['GET', 'POST'])
@crypto_bp.route('/manage_currency/<int:id>', methods=['GET', 'POST'])
def manage_currency(id=None):
    currency = Cryptocurrency.query.get(id) if id else None

    if request.method == 'POST':
        try:
            coingecko_id = request.form['coingecko_id']

            # Fetch data from CoinGecko API
            crypto_data = fetch_top_cryptos()
            
            data = next((c for c in crypto_data if c['id'] == coingecko_id), None)
            if not data:
                flash(f"Failed to fetch data for {coingecko_id}", 'danger')
                return redirect(url_for('crypto.index'))

            # Extract relevant information
            name = data['name']
            current_price = data['current_price']
            market_cap = data['market_cap']
            volume = data['total_volume']

            if currency:  # Editing existing currency
                currency.name = name
                currency.coingecko_id = coingecko_id
                currency.current_price = current_price
                currency.market_cap = market_cap
                currency.volume = volume
            else:  # Adding new currency
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
            return redirect(url_for('crypto.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('manage_currency.html', currency=currency)

# Trends - Displays charts for historical price and market cap trends
@crypto_bp.route('/trends')
def trends():
    selected_crypto = request.args.get('crypto', 'bitcoin')

    # Query the top 10 cryptocurrencies for dropdown
    top_10_cryptos = Cryptocurrency.query.order_by(Cryptocurrency.market_cap.desc()).limit(10).all()

    # Fetch historical data for selected crypto
    historical_data = (HistoricalData.query
                       .join(Cryptocurrency)
                       .filter(Cryptocurrency.coingecko_id == selected_crypto)
                       .order_by(HistoricalData.date.asc())
                       .all())

    # Format historical dates
    dates = [format_date(data.date) for data in historical_data]  # Pass date directly
    prices = [data.price for data in historical_data]
    market_caps = [data.market_cap for data in historical_data]

    return render_template('trends.html', top_10_cryptos=top_10_cryptos, selected_crypto=selected_crypto, dates=dates, prices=prices, market_caps=market_caps)