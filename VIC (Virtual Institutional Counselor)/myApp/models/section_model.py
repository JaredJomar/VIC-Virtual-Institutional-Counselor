# myApp/models/section_model.py

import psycopg2

class SectionModel:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_next_sid(self):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT MAX(sid) FROM section")
                    max_sid = cur.fetchone()[0]
                    return (max_sid or 0) + 1
        except psycopg2.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def master_id_exists(self, master_id):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM meeting WHERE mid = %s", (master_id,))
                    return cur.fetchone() is not None
        except psycopg2.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def check_schedule_conflict(self, room_id, meeting_id, section_id=None):
        """Check if there's a scheduling conflict for the given room and meeting"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT COUNT(*) FROM section s1
                        JOIN meeting m1 ON s1.mid = m1.mid
                        JOIN meeting m2 ON %s = m2.mid
                        WHERE s1.roomid = %s
                        AND s1.mid != %s
                        AND (
                            (m1.starttime, m1.endtime) OVERLAPS 
                            (m2.starttime, m2.endtime)
                        )
                        AND EXISTS (
                            SELECT 1
                            FROM unnest(string_to_array(m1.cdays, '')) AS day1(day)
                            JOIN unnest(string_to_array(m2.cdays, '')) AS day2(day)
                                ON day1.day = day2.day
                        )
                    """
                    params = [meeting_id, room_id, meeting_id]
                    
                    if section_id:
                        query += " AND s1.sid != %s"
                        params.append(section_id)
                    
                    cur.execute(query, tuple(params))
                    count = cur.fetchone()[0]
                    return count > 0
        except psycopg2.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def validate_semester(self, class_id, semester):
        """Validate that the section's semester matches the class's term"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT term FROM class WHERE cid = %s",
                        (class_id,)
                    )
                    result = cur.fetchone()
                    if not result:
                        raise ValueError(f"Class ID {class_id} not found")
                    
                    class_term = result[0].lower()
                    section_semester = semester.lower()
                    
                    # Check if semester matches class term
                    if class_term == 'fall' and section_semester != 'fall':
                        raise ValueError("This class can only be taught in Fall semester")
                    elif class_term == 'spring' and section_semester != 'spring':
                        raise ValueError("This class can only be taught in Spring semester")
                    return True
        except psycopg2.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def insert_section(self, section_data):
        try:
            if 'master_id' in section_data and not self.master_id_exists(section_data['master_id']):
                raise ValueError(f"Master ID {section_data['master_id']} does not exist.")
            
            # Validate semester
            self.validate_semester(section_data['class_id'], section_data['semester'])
            
            # Check for schedule conflicts
            if self.check_schedule_conflict(section_data['room_id'], section_data.get('master_id')):
                raise ValueError("Schedule conflict: Room is already booked for this time slot")
            
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    next_sid = self.get_next_sid()
                    cur.execute(
                        """
                        INSERT INTO section (
                            sid,
                            roomid, 
                            mid,
                            cid, 
                            semester, 
                            years, 
                            capacity
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s) 
                        RETURNING sid
                        """,
                        (
                            next_sid,
                            section_data['room_id'],
                            section_data.get('master_id'),  # Use get to handle optional field
                            section_data['class_id'],
                            section_data['semester'],
                            section_data['year'],
                            section_data['capacity']
                        )
                    )
                    return cur.fetchone()[0]
        except psycopg2.Error as e:
            raise Exception(f"Database error: {str(e)}")
        except KeyError as e:
            raise Exception(f"Missing required field: {str(e)}")

    def fetch_all_sections(self):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT sid as section_id, 
                               roomid as room_id,
                               mid as master_id, 
                               cid as class_id, 
                               semester, 
                               years as year, 
                               capacity 
                        FROM section;
                    """)
                    columns = [desc[0] for desc in cur.description]
                    results = cur.fetchall()
                    return [dict(zip(columns, row)) for row in results]
        except psycopg2.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def fetch_section(self, section_id):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT sid as section_id, 
                               roomid as room_id,
                               mid as master_id, 
                               cid as class_id, 
                               semester, 
                               years as year, 
                               capacity 
                        FROM section WHERE sid = %s;
                    """, (section_id,))
                    columns = [desc[0] for desc in cur.description]
                    result = cur.fetchone()
                    return dict(zip(columns, result)) if result else None
        except psycopg2.Error as e:
            print(f"Error fetching section: {e}")

    def update_section(self, section_id, section_data):
        try:
            if 'master_id' in section_data and not self.master_id_exists(section_data['master_id']):
                raise ValueError(f"Master ID {section_data['master_id']} does not exist.")
            
            # Validate semester
            self.validate_semester(section_data['class_id'], section_data['semester'])
            
            # Check for schedule conflicts
            if self.check_schedule_conflict(section_data['room_id'], section_data.get('master_id'), section_id):
                raise ValueError("Schedule conflict: Room is already booked for this time slot")
            
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE section 
                        SET roomid = %s, 
                            mid = %s,
                            cid = %s,
                            semester = %s, 
                            years = %s,
                            capacity = %s
                        WHERE sid = %s
                        """,
                        (
                            section_data['room_id'],
                            section_data.get('master_id'),  # Use get to handle optional field
                            section_data['class_id'],
                            section_data['semester'],
                            section_data['year'],
                            section_data['capacity'],
                            section_id,
                        )
                    )
                    return cur.rowcount
        except psycopg2.Error as e:
            raise Exception(f"Database error: {str(e)}")

    def delete_section(self, section_id):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # First get the section details before deleting
                    cur.execute("DELETE FROM section WHERE sid = %s RETURNING sid;", (section_id,))
                    deleted_id = cur.fetchone()
                    return deleted_id[0] if deleted_id else None
        except psycopg2.Error as e:
            raise Exception(f"Database error: {str(e)}")
