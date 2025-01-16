# # myApp/models/requisite_model.py

import psycopg2

class RequisiteModel:
    def __init__(self, db_url):
        self.db_url = db_url

    def insert_requisite(self, requisite_data):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO requisite (classid, reqid, prereq)
                        VALUES (%s, %s, %s) RETURNING reqid
                        """,
                        (requisite_data['classid'], requisite_data['reqid'], requisite_data['prereq'])
                    )
                    return cur.fetchone()[0]
        except psycopg2.Error as e:
            print(f"Error inserting requisite: {e}")
            return None

    def fetch_requisite(self, classid, reqid):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM requisite WHERE classid = %s AND reqid = %s;",
                        (classid, reqid)
                    )
                    result = cur.fetchone()
                    if result:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, result))
                    return None
        except psycopg2.Error as e:
            print(f"Error fetching requisite: {e}")
            return None

    def fetch_all_requisites(self):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM requisite;")
                    results = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in results]
        except psycopg2.Error as e:
            print(f"Error fetching all requisites: {e}")
            return []

    def update_requisite(self, classid, reqid, requisite_data):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE requisite SET prereq = %s 
                        WHERE classid = %s AND reqid = %s
                        """,
                        (requisite_data['prereq'], classid, reqid)
                    )
                    return cur.rowcount
        except psycopg2.Error as e:
            print(f"Error updating requisite: {e}")
            return 0

    def delete_requisite(self, classid, reqid):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM requisite WHERE classid = %s AND reqid = %s;",
                        (classid, reqid)
                    )
                    rows_deleted = cur.rowcount
            self.reset_requisite_sequence()
            return rows_deleted
        except psycopg2.Error as e:
            print(f"Error deleting requisite: {e}")
            return 0

    def reset_requisite_sequence(self):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Get the maximum reqid in the requisite table
                    cur.execute("SELECT COALESCE(MAX(reqid), 1) FROM requisite")
                    max_id = cur.fetchone()[0]
                    # Reset the sequence to the maximum id
                    cur.execute("SELECT setval('requisite_reqid_seq', %s, true)", (max_id,))
                    conn.commit()
        except psycopg2.Error as e:
            print(f"Error resetting requisite sequence: {e}")
