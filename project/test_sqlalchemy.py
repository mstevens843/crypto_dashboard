from sqlalchemy import create_engine

try:
    # Create an in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')
    
    # Test connection and print a success message
    print("SQLAlchemy is working!")
except Exception as e:
    print(f"An error occurred: {e}")
