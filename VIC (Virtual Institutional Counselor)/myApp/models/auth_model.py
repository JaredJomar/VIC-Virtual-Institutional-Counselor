# myApp/models/auth_model.py
import os
from dotenv import load_dotenv
import psycopg2
from config.environment import get_database_url
import bcrypt

# Force production environment
load_dotenv(".env.production", override=True)

class AuthModel:
    """Handles database operations related to user authentication."""
    
    def __init__(self):
        """Initialize with database configuration from environment."""
        try:
            self.db_url = get_database_url()
            if 'localhost' in self.db_url or 'mydatabase' in self.db_url:
                raise Exception("Local database connection not allowed in production")
            print("✅ Production database configuration initialized")
        except Exception as e:
            print(f"❌ ERROR: Database configuration failed: {e}")
            raise Exception("Production database configuration required")

    def execute_query(self, query, params=None):
        """Execute database query with improved error handling."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                db_info = conn.info
                if not hasattr(self, '_db_validated'):
                    print(f"📊 Connected to database: {db_info.dbname} at {db_info.host}")
                    self._db_validated = True
                
                with conn.cursor() as cur:
                    print(f"🚀 Executing query: {query}")
                    cur.execute(query, params)
                    conn.commit()
                    if cur.description:
                        results = cur.fetchall()
                        print("✅ Query executed successfully")
                        return results
                    return None
        except Exception as e:
            error_msg = f"❌ Database Error: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

    def register_user(self, username: str, password_hash: str) -> dict:
        """Register user with improved error handling and proper return value."""
        print(f"\n=== Registering user {username} in databases ===")
        
        # First check if user already exists
        existing_user = self.get_user_by_username(username)
        if (existing_user):
            print(f"⚠️ User {username} already exists")
            raise ValueError("Username already exists")

        query = """
            INSERT INTO users (username, password_hash, created_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            RETURNING id, username, created_at;
        """
        
        try:
            results = self.execute_query(query, (username, password_hash))
            
            if results and len(results) > 0:
                user_id, username, created_at = results[0]
                print(f"✅ User {username} registered successfully")
                return {
                    "success": True,
                    "message": "Registration successful",
                    "user": {
                        "id": user_id,
                        "username": username,
                        "created_at": created_at
                    }
                }
            else:
                raise ValueError("Failed to verify user registration")
            
        except Exception as e:
            error_msg = f"Registration failed: {str(e)}"
            print(f"❌ {error_msg}")
            raise ValueError(error_msg)

    def get_user_by_username(self, username: str) -> dict:
        """Get user from database."""
        query = """
            SELECT id, username, password_hash
            FROM users
            WHERE username = %s;
        """
        try:
            results = self.execute_query(query, (username,))
            
            if results and len(results) > 0:
                user_id, username, password_hash = results[0]
                return {
                    'id': user_id,
                    'username': username,
                    'password_hash': password_hash
                }
            return None
            
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    def get_user_by_id(self, user_id: int) -> dict:
        """
        Retrieve user information by their ID.

        Args:
            user_id (int): The unique identifier of the user to find

        Returns:
            dict: User information containing id, username, and created_at
                 Returns None if user not found
            
        Raises:
            Exception: For database connection or query errors
        """
        try:
            cur = self.db_connection.cursor()
            cur.execute("""
                SELECT id, username, created_at
                FROM users
                WHERE id = %s
            """, (user_id,))
            user = cur.fetchone()
            cur.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'created_at': user[2]
                }
            return None
        except Exception as e:
            raise Exception(f"Error retrieving user by ID: {str(e)}")

    def __del__(self):
        """Ensure database connection is closed when object is destroyed."""
        if hasattr(self, 'db_connection') and self.db_connection:
            self.db_connection.close()
