import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection(db_url=None):
    """
    Establish a connection to the database.
    """
    if not db_url:
        db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not set.")
        raise ValueError("DATABASE_URL environment variable not set.")
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        logger.info("Successfully connected to the database.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise

def get_top_meetings_by_sections(db_url=None):
    """Get top 5 meetings with the most sections."""
    conn = get_db_connection(db_url)
    cur = conn.cursor()
    try:
        query = """
            SELECT m.mid, m.ccode, m.starttime, m.endtime, m.cdays, 
                   COUNT(s.*) as section_count
            FROM meeting m
            JOIN section s ON m.mid = s.mid
            GROUP BY m.mid, m.ccode, m.starttime, m.endtime, m.cdays
            ORDER BY section_count DESC
            LIMIT 5;
        """
        cur.execute(query)
        results = cur.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching top meetings by sections: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def get_top_classes_most_prerequisites(db_url=None):
    """Get top 3 classes that appear the most as prerequisites."""
    conn = get_db_connection(db_url)
    cur = conn.cursor()
    try:
        query = """
            SELECT c.cid, c.cname, c.ccode, COUNT(r.*) as prereq_count
            FROM class c
            JOIN requisite r ON c.cid = r.reqid
            WHERE r.prereq = true
            GROUP BY c.cid, c.cname, c.ccode
            ORDER BY prereq_count DESC
            LIMIT 3;
        """
        cur.execute(query)
        results = cur.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching top classes most prerequisites: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def get_top_classes_least_offered(db_url=None):
    """Get top 3 classes that were offered the least."""
    conn = get_db_connection(db_url)
    cur = conn.cursor()
    try:
        #Should this include classes that weren't offered at all? 
        # Or just classes that were offered, but very little?

        # Added: 
        # Order by c.cid as well, so that it order by least count and lowest cid
        query = """
            SELECT c.cid, c.cname, c.ccode, COUNT(s.*) as offer_count
            FROM class c
            LEFT JOIN section s ON c.cid = s.cid
            GROUP BY c.cid, c.cname, c.ccode
            HAVING COUNT(s.*) > 0
            ORDER BY offer_count, c.cid
            LIMIT 3;
        """
        cur.execute(query)
        results = cur.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching top classes least offered: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def get_total_sections_per_year(db_url=None):
    """Get total number of sections per year."""
    conn = get_db_connection(db_url)
    cur = conn.cursor()
    try:
        query = """
            SELECT years::text AS year, COUNT(*) AS total_sections
            FROM section
            GROUP BY years
            ORDER BY year;
        """
        cur.execute(query)
        results = cur.fetchall()
        return [dict(row) for row in results]  # Use dict() since we're using RealDictCursor
    except Exception as e:
        logger.error(f"Error fetching total sections per year: {e}")
        raise
    finally:
        cur.close()
        conn.close()