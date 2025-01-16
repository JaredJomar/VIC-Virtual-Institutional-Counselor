# config/environment.py
import os
from dotenv import load_dotenv

# Force production environment
load_dotenv(".env.production", override=True)

# Set this to True as we want to use production database
USE_HEROKU = True

def validate_db_connection(url, source="unknown"):
    """Validate database connection"""
    import psycopg2
    from urllib.parse import urlparse
    
    if 'localhost' in url or 'mydatabase' in url:
        print("❌ Error: Local database connection not allowed in production")
        return False
        
    try:
        parsed = urlparse(url)
        valid_hosts = ['rds.amazonaws.com', 'herokuapp.com', 'postgres.render.com']
        if not any(host in parsed.hostname for host in valid_hosts):
            print(f"❌ Error: Invalid production database host: {parsed.hostname}")
            return False
            
        conn = psycopg2.connect(url)
        db_info = conn.info
        db_host = db_info.host
        db_name = db_info.dbname
        conn.close()
        
        print(f"✅ Connected to {source} database at {db_host} (database: {db_name})")
        return True
    except Exception as e:
        print(f"❌ Database connection error ({source}): {str(e)}")
        return False

def get_database_url():
    """Get database URL with validation"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("❌ DATABASE_URL not set in production environment")
        
    if 'localhost' in db_url or 'mydatabase' in db_url:
        raise Exception("❌ Local database not allowed in production")
        
    if validate_db_connection(db_url, "Production"):
        print("🌐 Using Production database")
        return db_url
    
    raise Exception("❌ Production database connection required")