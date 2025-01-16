# myApp/models/meeting_model.py
import psycopg2.extras
import psycopg2
from datetime import datetime

class MeetingModel:
    def __init__(self, db_url):
        self.db_url = db_url

    def create_meeting(self, meeting_data):
        # Remove default date
        start_time = meeting_data['starttime']
        end_time = meeting_data['endtime']

        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                # Check if a meeting with the same ccode and time range already exists
                cur.execute(
                    """
                    SELECT mid FROM meeting
                    WHERE cdays = %s AND starttime = %s AND endtime = %s
                    """,
                    (meeting_data['cdays'], start_time, end_time)
                )
                existing_meeting = cur.fetchone()

                if existing_meeting:
                    # Meeting already exists, return an error message or code
                    return {"error": "Meeting with the specified details already exists."}

                # If no duplicate is found, proceed with insertion
                cur.execute(
                    """
                    INSERT INTO meeting (ccode, cdays, starttime, endtime)
                    VALUES (%s, %s, %s, %s) RETURNING mid
                    """,
                    (
                        meeting_data['ccode'],
                        meeting_data['cdays'],
                        start_time,
                        end_time
                    )
                )
                return cur.fetchone()[0]

    def delete_meeting(self, meeting_id):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Delete all related records in section
                    cur.execute("DELETE FROM section WHERE mid = %s;", (meeting_id,))
                    
                    # Then delete the meeting itself
                    cur.execute("DELETE FROM meeting WHERE mid = %s;", (meeting_id,))
                    rows_deleted = cur.rowcount

                    # Reset the sequence if deletion occurred
                    if rows_deleted:
                        cur.execute("SELECT setval('meeting_mid_seq', COALESCE((SELECT MAX(mid) FROM meeting), 1))")

                    return rows_deleted
        except psycopg2.Error as e:
            print(f"Error deleting meeting: {e}")
            return 0
    
    def fetch_all_meetings(self):
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM meeting;")
                results = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                
                # Convert each row to a dictionary, format time fields as strings
                formatted_results = []
                for row in results:
                    row_dict = dict(zip(columns, row))
                    # Format time fields as strings
                    if 'starttime' in row_dict:
                        row_dict['starttime'] = row_dict['starttime'].strftime("%H:%M:%S")
                    if 'endtime' in row_dict:
                        row_dict['endtime'] = row_dict['endtime'].strftime("%H:%M:%S")
                    formatted_results.append(row_dict)
                
                return formatted_results

    def fetch_meeting(self, mid):
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM meeting WHERE mid = %s;", (mid,))
                result = cur.fetchone()
                if result:
                    columns = [desc[0] for desc in cur.description]
                    meeting = dict(zip(columns, result))
                    # Format time fields as strings
                    if 'starttime' in meeting:
                        meeting['starttime'] = meeting['starttime'].strftime("%H:%M:%S")
                    if 'endtime' in meeting:
                        meeting['endtime'] = meeting['endtime'].strftime("%H:%M:%S")
                    return meeting
                return None

    def update_meeting(self, mid, meeting_data):
        # Remove default date
        start_time = meeting_data['starttime']
        end_time = meeting_data['endtime']

        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE meeting
                    SET ccode = %s, cdays = %s, starttime = %s, endtime = %s
                    WHERE mid = %s
                    """,
                    (
                        meeting_data['ccode'],
                        meeting_data['cdays'],
                        start_time,
                        end_time,
                        mid
                    )
                )
                return cur.rowcount

    def reset_meeting_sequence(self):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Get the maximum id in the meeting table
                    cur.execute("SELECT COALESCE(MAX(mid), 1) FROM meeting")
                    max_id = cur.fetchone()[0]
                    # Reset the sequence to the maximum id
                    cur.execute("SELECT setval('meeting_mid_seq', %s, true)", (max_id,))
                    conn.commit()
        except psycopg2.Error as e:
            print(f"Error resetting meeting sequence: {e}")