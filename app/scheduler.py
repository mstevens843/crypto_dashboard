from apscheduler.schedulers.background import BackgroundScheduler
from app.services.crypto_service import update_cryptocurrencies
from app.services.coingecko_service import fetch_top_cryptos
from flask import current_app

# Create a scheduler instance
scheduler = BackgroundScheduler()

def scheduled_update():
    """Fetches the latest cryptocurrency data and updates the database."""
    with current_app.app_context():
        crypto_data = fetch_top_cryptos()
        update_cryptocurrencies(crypto_data)

def start_scheduler(app):
    """Starts the background scheduler for periodic cryptocurrency updates."""
    global scheduler

    if not scheduler.running:
        print("Starting APScheduler...")
        scheduler.start()
        print("APScheduler is now running.")

    # Ensure the scheduled job exists
    existing_jobs = scheduler.get_jobs()
    if not any(job.id == "crypto_update" for job in existing_jobs):
        print("Adding scheduled cryptocurrency update job...")
        scheduler.add_job(scheduled_update, 'interval', minutes=30, id="crypto_update")

    # Run an initial update on startup
    with app.app_context():
        print("Running initial cryptocurrency update on startup...")
        scheduled_update()

    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        """Shuts down the scheduler when the app is terminated."""
        if scheduler.running:
            print("Shutting down APScheduler...")
            scheduler.shutdown()
