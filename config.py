import os

class Config:
    # Use the database URL from Render, fallback to local DB if not set
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://my_crypto_dashboard_user:Qe2kIZPT9mj3kO5vD47qqUaTvRIAQfvd@dpg-cv7dq4d2ng1s7384o710-a/my_crypto_dashboard"
    )

    # ✅ **Fix SSL issue for Render inside the class**
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://"
        ) + "?sslmode=require"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security key for session handling
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "8f2c1e89b3d74a6c9e12f7845ad5e3c497b8e7f2630a4d5c86f2b9a6e1d4f7c2"
    )
