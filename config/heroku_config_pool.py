import os
from dotenv import load_dotenv
from psycopg2 import pool, DatabaseError

# Load the .env file based on the current environment
env = os.getenv("FLASK_ENV", "development")
if env == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env.development")

# Define HEROKU_DB_URL at the module level
HEROKU_DB_URL = os.getenv("DATABASE_URL")

class DatabaseConfig:
    connection_pool = None  # Define a class-level connection pool

    @staticmethod
    def init_pool():
        """
        Initialize a connection pool for the database if not already initialized.
        """
        try:
            if not DatabaseConfig.connection_pool:
                DatabaseConfig.connection_pool = pool.SimpleConnectionPool(
                    1, 20, HEROKU_DB_URL
                )
                print("Database connection pool created successfully.")
        except DatabaseError as e:
            print(f"Error creating connection pool: {e}")
            DatabaseConfig.connection_pool = None

    @staticmethod
    def get_db_connection():
        """
        Get a connection from the pool.
        Returns:
            Connection: A database connection from the pool.
        """
        if not DatabaseConfig.connection_pool:
            DatabaseConfig.init_pool()
        try:
            conn = DatabaseConfig.connection_pool.getconn()
            print(f"Successfully connected to the database.")
            return conn
        except DatabaseError as e:
            print(f"Error obtaining a connection: {e}")
            return None

    @staticmethod
    def return_connection(conn):
        """
        Return a connection to the pool.
        Args:
            conn (Connection): The database connection to be returned.
        """
        if DatabaseConfig.connection_pool:
            DatabaseConfig.connection_pool.putconn(conn)

    @staticmethod
    def close_all_connections():
        """
        Close all connections in the pool.
        """
        if DatabaseConfig.connection_pool:
            DatabaseConfig.connection_pool.closeall()
            print("All database connections closed.")