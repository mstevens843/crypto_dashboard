from flask import Flask
from flask_migrate import Migrate  # Added Flask-Migrate
from app.config import Config
from app.models import db
from app.routes.crypto_routes import crypto_bp
from app.routes.general_routes import general_bp
from app.scheduler import start_scheduler
from app.utils.helpers import format_currency, get_logger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)  # Ensuring Flask-Migrate is initialized

    # Initialize Logging
    logger = get_logger()
    logger.info("Flask app is starting...")

    # Ensure Database Tables Exist
    with app.app_context():
        db.create_all()
        logger.info("Database tables created (if they didn't already exist).")

    # Register Jinja filter for currency formatting
    app.jinja_env.filters['format_currency'] = format_currency  

    # Register Blueprints
    app.register_blueprint(crypto_bp)
    app.register_blueprint(general_bp)

    # Start the scheduler
    start_scheduler(app)

    return app
