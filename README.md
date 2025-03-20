# Cryptocurrency Market Dashboard

## Overview

This project is a cryptocurrency market dashboard that provides real-time and historical data for selected cryptocurrencies. The dashboard utilizes the CoinGecko API to fetch up-to-date information on cryptocurrency prices, market capitalization, and historical trends. It is designed to offer a clean and user-friendly interface for browsing and analyzing cryptocurrency data.

### Live Site

**Title:** Cryptocurrency Market Dashboard  
**URL:** https://crypto-dashboard-0b1k.onrender.com/

### Features

- **Real-Time Cryptocurrency Data:** Display the current prices and market cap for the top 10 cryptocurrencies, updated every 30 minutes.
- **Historical Data Visualization:** View historical price and market cap data for selected cryptocurrencies with interactive charts.
- **Cryptocurrency Management:** Add and edit cryptocurrency data manually, ensuring that the dashboard is customizable.
- **User Interface:** A clean and concise interface that makes it easy to navigate and explore cryptocurrency information.
- **Dropdown Selection for Trends:** Allows users to select a specific cryptocurrency from the top 10 to view detailed trend data.

### Reason for Feature Choices

These features were selected to provide users with both current and historical data in an accessible format,allowing users to make informed decisions. You can manage cryptocurrencies manually to ensure flexibility, while the interactive charts enhance data visualization, making it easier for users to analyze trends over time.

## Technologies Used

- **Backend:** Python with Flask
- **Database:** PostgreSQL with SQLAlchemy
- **Frontend:** HTML, CSS, JavaScript
- **API:** CoinGecko API
- **Hosting:** [Heroku or Render] (Specify which one you used)

## Database Schema

### Tables

- **cryptocurrencies**
  - `id` (SERIAL, Primary Key)
  - `coingecko_id` (VARCHAR(50), Unique, Not Null)
  - `name` (VARCHAR(255), Not Null)
  - `symbol` (VARCHAR(10), Not Null)
  - `current_price` (DECIMAL)
  - `market_cap` (DECIMAL)
  - `volume` (DECIMAL)
  - `last_updated` (TIMESTAMP, Default: CURRENT_TIMESTAMP)

- **historical_data**
  - `id` (SERIAL, Primary Key)
  - `cryptocurrency_id` (INT, Foreign Key)
  - `date` (DATE, Not Null)
  - `price` (DECIMAL)
  - UNIQUE (`cryptocurrency_id`, `date`)

## Setup

1. **Clone Repository**
    ```bash
    git clone https://github.com/hatchways-community/capstone-project-one-abf8076dc70c48ff8b62544bc1e76312.git
    cd crypto-market-dashboard
    ```
2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3. **Set Up Database**
    - Ensure PostgreSQL is installed and running.
    - Create a database and update your configuration in the `.env` file.
    - Run migrations:
    ```bash
    flask db upgrade
    ```
4. **Run the Application**
    ```bash
    flask run
    ```
