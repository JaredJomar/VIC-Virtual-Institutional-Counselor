# myApp/extensions.py

import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    """
    Establish a connection to the database specified by the environment.
    
    Returns:
        connection: A connection object for PostgreSQL.
    """
    choice = os.getenv("DATABASE_CHOICE")
    
    if choice == "1":  # Local database
        from config.local_config import LocalConfig
        db_url = LocalConfig.get_db_connection()
    elif choice == "2":  # Heroku database
        from config.heroku_config import DatabaseConfig
        db_url = DatabaseConfig.get_db_connection()
    else:
        raise ValueError("Invalid DATABASE_CHOICE environment variable. Set it to '1' for local or '2' for Heroku.")

    if not db_url:
        raise ValueError("Database URL not configured properly.")
    
    connection = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return connection
