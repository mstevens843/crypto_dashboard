"""Create crypto tables from raw SQL."""

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic
revision = '20231005_crypto'
down_revision = None  # or set this if you have an existing migration
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS cryptocurrencies (
        id SERIAL PRIMARY KEY,
        coingecko_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        current_price DECIMAL(18,2) NOT NULL,
        market_cap DECIMAL(18,2) NOT NULL,
        volume DECIMAL(18,2) NOT NULL,
        circulating_supply DECIMAL(18,0) NOT NULL,
        total_supply DECIMAL(18,0),
        max_supply DECIMAL(18,0),
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS historical_data (
        id SERIAL PRIMARY KEY,
        cryptocurrency_id INT REFERENCES cryptocurrencies(id),
        date DATE NOT NULL,
        price DECIMAL(18,8) NOT NULL,
        market_cap DECIMAL(18,2) NOT NULL,
        volume DECIMAL(18,2) NOT NULL,
        UNIQUE(cryptocurrency_id, date)
    );
    """)

def downgrade():
    op.execute("""
    DROP TABLE IF EXISTS historical_data;
    DROP TABLE IF EXISTS cryptocurrencies;
    """)
