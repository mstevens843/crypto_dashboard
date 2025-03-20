# Import Blueprints so they are registered when `app.routes` is imported
from flask import Blueprint
from app.routes.crypto_routes import crypto_bp
from app.routes.general_routes import general_bp

# Expose the Blueprints at the package level
__all__ = ["crypto_bp", "general_bp"]