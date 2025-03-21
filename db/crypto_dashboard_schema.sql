CREATE TABLE cryptocurrencies (
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


CREATE TABLE historical_data (
    id SERIAL PRIMARY KEY,
    cryptocurrency_id INT REFERENCES cryptocurrencies(id), 
    date DATE NOT NULL, 
    price DECIMAL(18,8) NOT NULL,
    market_cap DECIMAL(18,2) NOT NULL,
    volume DECIMAL(18,2) NOT NULL,
    UNIQUE(cryptocurrency_id, date)
);