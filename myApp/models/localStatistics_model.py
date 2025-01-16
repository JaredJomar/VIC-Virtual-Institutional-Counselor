import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Establish a connection to the database.
    """
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

def get_top_rooms_by_capacity(building):
    """Get top 3 rooms with most capacity for a building."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        SELECT rid::text, room_number, capacity::text 
        FROM room 
        WHERE LOWER(building) = LOWER(%s) 
        ORDER BY capacity DESC 
        LIMIT 3
        """
        cur.execute(query, (str(building),))
        results = cur.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching top rooms by capacity: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def get_top_sections_by_ratio(building):
    """Get top 3 sections with highest student-to-capacity ratio per building."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Old Query: Missing avg calculation
        
        # query = """
        # WITH RoomSectionRatio AS (
        #     SELECT 
        #         s.sid::text,
        #         s.semester,
        #         r.building,
        #         ROUND((s.capacity::numeric / r.capacity::numeric * 100), 2) as ratio,
        #         r.room_number
        #     FROM section s
        #     JOIN room r ON s.roomid = r.rid
        #     WHERE r.building = %s
        #     GROUP BY s.sid, s.semester, r.building, r.capacity, r.room_number, s.capacity
        # )
        # SELECT sid, semester, ratio::text, room_number
        # FROM RoomSectionRatio
        # ORDER BY ratio DESC
        # LIMIT 3
        # """



        # New Query

        # Unnecessary
        # # query to get all unique rooms (rid's) of a specific building
        # query = """
        # (select distinct roomid 
        # from section
        # where building = %s)
        # as Building_Rooms
        # """

        # Unnecessary
        # # query to get sections of a specific room
        # query = """
        # (select sid 
        # from section
        # where roomid in Building_Rooms)
        # as Building_Room_Sections
        # """

        # # query to get average of sections' capacity (per room)
        # query = """
        # (select rid, avg(section.capacity) as section_capacity_avg
        # from section as S join room as R on S.roomid = R.rid
        # where building = %s
        # group by rid)
        # as Section_Avg
        # """

        # # query to get ratio of a room 
        # query = """
        # (select rid, (section_capacity_avg / room.capacity) as ratio
        # from Section_Avg natural inner join room) 
        # as Room_Ratio
        # """

        # # query to get all rooms' ratios from a building
        # # Should the final select include only the rid and ratio, 
        # # or the whole room record + ratio?
        # query = """
        # select rid, building, room_number, capacity, ratio
        # from Room_Ratio natural inner join R
        # group by rid
        # order desc
        # limit 3
        # """

        # Questions:
        # Should it be ratio of every section of each class per room, 
        # or just the ratio of every section per room?
        # Is it irrelevant of year and semester too?

        # sid,roomid,mid,cid,semester,years,capacity
        # rid,building,room_number,capacity

        query = """
        with 
        Section_Avg as (
            select rid, avg(S.capacity) as section_capacity_avg
            from section as S join room as R on S.roomid = R.rid
            where lower(building) = lower(%s)
            group by rid
        ),
        Room_Ratio as (
            select rid, section_capacity_avg, (round((section_capacity_avg / room.capacity) * 100, 0)) as ratio
            from Section_Avg natural inner join room
        ) 
        select rid, building, room_number, capacity, section_capacity_avg, ratio
        from Room_Ratio natural inner join room
        order by ratio desc
        limit 3
        """

        cur.execute(query, (str(building),))
        results = cur.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching top sections by ratio: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def get_top_classes_per_room(room_id):
    """Get top 3 most taught classes per room."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        SELECT 
            c.cid::text,
            c.cname,
            c.ccode,
            COUNT(DISTINCT CONCAT(s.years, s.semester)) as class_count
        FROM class c
        INNER JOIN section s ON s.cid = c.cid
        WHERE s.roomid = %s
        GROUP BY c.cid, c.cname, c.ccode
        ORDER BY class_count DESC, c.cname
        LIMIT 3
        """
        cur.execute(query, (room_id,))
        results = cur.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching top classes per room: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def get_top_classes_per_semester(year, semester):
    """Get top 3 most taught classes per semester."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        SELECT 
            c.cid::text,
            c.cname,
            COUNT(DISTINCT s.sid) as class_count
        FROM class c
        JOIN section s ON s.cid = c.cid
        WHERE s.years = %s 
        AND LOWER(s.semester) = LOWER(%s)
        GROUP BY c.cid, c.cname
        ORDER BY class_count DESC
        LIMIT 3
        """
        cur.execute(query, (str(year), semester))
        results = cur.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching top classes per semester: {e}")
        raise
    finally:
        cur.close()
        conn.close()