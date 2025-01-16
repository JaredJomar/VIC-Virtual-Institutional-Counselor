# config/heroku_config.py

import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

load_dotenv(".env.production")

class DatabaseConfig:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not set in .env.production")
        
        # Verify this is a production database
        parsed = urlparse(self.db_url)
        if not parsed.hostname or not any(host in parsed.hostname for host in ['rds.amazonaws.com', 'herokuapp.com', 'postgres.render.com']):
            raise ValueError("DATABASE_URL does not point to a production database")

    def get_db_url(self):
        return self.db_url

    def get_db_connection(self):
        try:
            conn = psycopg2.connect(self.db_url)
            print(f"Successfully connected to the Heroku database")
            return conn
        except psycopg2.DatabaseError as e:
            print(f"Error connecting to the Heroku database: {e}")
            return None