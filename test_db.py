from app import db
from models import Cryptocurrency

try:
    db.session.execute('SELECT 1')
    print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")