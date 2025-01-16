# config/local_config.py

import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env.development
load_dotenv(".env.development")

# Export DATABASE_URL at module level for backwards compatibility
DATABASE_URL = os.getenv("DATABASE_URL")

class LocalConfig:
    def __init__(self):
        self.db_url = DATABASE_URL
        if not self.db_url:
            raise ValueError("DATABASE_URL not set in .env.development")

    def get_db_url(self):
        return self.db_url

    def get_db_connection(self):
        try:
            conn = psycopg2.connect(self.db_url)
            print(f"Successfully connected to the local database")
            return conn
        except psycopg2.DatabaseError as e:
            print(f"Error connecting to the local database: {e}")
            return None