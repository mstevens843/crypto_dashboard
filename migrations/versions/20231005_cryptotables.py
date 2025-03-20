"""Create crypto tables from raw SQL."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text  # ✅ Import text() to fix SQL execution

# Revision identifiers, used by Alembic
revision = '20231005_crypto'
down_revision = None  # or set this if you have an existing migration
branch_labels = None
depends_on = None

def upgrade():
    """Apply the migration: Create necessary tables if they don't exist."""
    op.execute(text("""
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
    """))

    op.execute(text("""
    CREATE TABLE IF NOT EXISTS historical_data (
        id SERIAL PRIMARY KEY,
        cryptocurrency_id INT REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        price DECIMAL(18,8) NOT NULL,
        market_cap DECIMAL(18,2) NOT NULL,
        volume DECIMAL(18,2) NOT NULL,
        UNIQUE(cryptocurrency_id, date)
    );
    """))

def downgrade():
    """Rollback the migration: Drop tables if needed."""
    op.execute(text("DROP TABLE IF EXISTS historical_data CASCADE;"))
    op.execute(text("DROP TABLE IF EXISTS cryptocurrencies CASCADE;"))
