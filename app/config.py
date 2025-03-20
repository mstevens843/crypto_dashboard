import os

class Config:
    """Base config"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")

    # Determine which database URL to use
    DATABASE_URL = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL if DATABASE_URL else "sqlite:///default.db"
