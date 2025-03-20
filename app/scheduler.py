from apscheduler.schedulers.background import BackgroundScheduler
from app.services.crypto_service import update_cryptocurrencies
from app.services.coingecko_service import fetch_top_cryptos
from flask import current_app

# Create a scheduler instance
scheduler = BackgroundScheduler()

def scheduled_update():
    with current_app.app_context():
        crypto_data = fetch_top_cryptos()
        update_cryptocurrencies(crypto_data)

def start_scheduler(app):
    """Start the background scheduler for periodic updates."""
    global scheduler

    if not scheduler.running:  # Prevent multiple scheduler instances
        scheduler.add_job(scheduled_update, 'interval', minutes=30)
        scheduler.start()

    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        """Shutdown scheduler on app teardown."""
        if scheduler.running:
            scheduler.shutdown()
