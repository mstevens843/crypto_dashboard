import locale
import logging
import datetime
import requests
import time



def format_currency(value):
    """Formats currency manually instead of using locale.currency()."""
    return f"${value:,.2f}"


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_logger():
    """Returns a configured logger instance."""
    return logger


def safe_request(url, params=None, retries=3, wait=5):
    """
    Makes a GET request with retry logic and dynamic wait handling.

    - `url`: API endpoint
    - `params`: Query parameters
    - `retries`: Number of retry attempts (default: 3)
    - `wait`: Default wait time (seconds) between retries (default: 5)

    Returns JSON response or raises an exception.
    """
    for attempt in range(retries):
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:  # Rate limit exceeded
            retry_after = int(response.headers.get("Retry-After", wait))  # Use API's suggested wait time
            print(f"⚠️ Rate limit exceeded. Retrying in {retry_after} seconds... (Attempt {attempt+1}/{retries})")
            time.sleep(retry_after)

        else:
            print(f"API request failed with status {response.status_code}: {response.text}")

    raise Exception(f"Failed to fetch data from {url} after {retries} retries")


def format_date(date_value):
    """Converts a datetime.date or timestamp to a readable date format (YYYY-MM-DD)."""
    
    if isinstance(date_value, datetime.date):  
        return date_value.strftime('%Y-%m-%d')  # Format date object
    
    elif isinstance(date_value, (int, float)):  
        # Convert timestamp if it's in milliseconds (more than year 3000)
        if date_value > 1e10:  
            date_value = date_value / 1000  # Convert milliseconds to seconds
        
        return datetime.datetime.fromtimestamp(date_value).strftime('%Y-%m-%d')

    raise ValueError(f"Unsupported date format provided: {date_value}")
