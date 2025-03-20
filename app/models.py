from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cryptocurrency(db.Model):
    __tablename__ = 'cryptocurrencies'
    id = db.Column(db.Integer, primary_key=True)
    coingecko_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    current_price = db.Column(db.Numeric(18, 2), nullable=False)
    market_cap = db.Column(db.Numeric(18, 2), nullable=False)
    volume = db.Column(db.Numeric(18, 2), nullable=False)
    circulating_supply = db.Column(db.Numeric(18, 0), nullable=False)
    total_supply = db.Column(db.Numeric(18, 0))
    max_supply = db.Column(db.Numeric(18, 0))
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())

class HistoricalData(db.Model):
    __tablename__ = 'historical_data'
    
    id = db.Column(db.Integer, primary_key=True)
    cryptocurrency_id = db.Column(db.Integer, db.ForeignKey('cryptocurrencies.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Numeric(18, 8), nullable=False)
    market_cap = db.Column(db.Numeric(18, 2), nullable=False)
    volume = db.Column(db.Numeric(18, 2), nullable=False)

    # ✅ Explicitly name the UNIQUE constraint
    __table_args__ = (
        db.UniqueConstraint('cryptocurrency_id', 'date', name='historical_data_cryptocurrency_id_date_key'),
    )

