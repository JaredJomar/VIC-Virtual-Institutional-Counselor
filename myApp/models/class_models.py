# myApp.models.class_models.py

import psycopg2

class ClassModel:
    def __init__(self, db_url):
        self.db_url = db_url

    def insert_class(self, class_data):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO class (cname, ccode, cdesc, term, years, cred, csyllabus)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING cid
                        """,
                        (class_data['cname'], class_data['ccode'], class_data['cdesc'],
                         class_data['term'], class_data['years'], class_data['cred'], class_data['csyllabus'])
                    )
                    return cur.fetchone()[0]
        except psycopg2.Error as e:
            print(f"Error inserting class: {e}")
            return None

    def fetch_class(self, class_id):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM class WHERE cid = %s", (class_id,))
                    result = cur.fetchone()
                    if result:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, result))
                    return None
        except psycopg2.Error as e:
            print(f"Error fetching class: {e}")
            return None

    def fetch_all_classes(self):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM class")
                    results = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in results]
        except psycopg2.Error as e:
            print(f"Error fetching all classes: {e}")
            return []

    def update_class(self, class_id, class_data):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE class SET cname = %s, ccode = %s, cdesc = %s, term = %s, 
                        years = %s, cred = %s, csyllabus = %s WHERE cid = %s
                        """,
                        (class_data['cname'], class_data['ccode'], class_data['cdesc'],
                         class_data['term'], class_data['years'], class_data['cred'], class_data['csyllabus'], class_id)
                    )
                    return cur.rowcount
        except psycopg2.Error as e:
            print(f"Error updating class: {e}")
            return 0

    def delete_class(self, class_id):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM class WHERE cid = %s", (class_id,))
                    rows_deleted = cur.rowcount
            self.reset_class_sequence()
            return rows_deleted
        except psycopg2.Error as e:
            print(f"Error deleting class: {e}")
            return 0

    def reset_class_sequence(self):
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Get the maximum id in the class table
                    cur.execute("SELECT COALESCE(MAX(cid), 1) FROM class")
                    max_id = cur.fetchone()[0]
                    # Reset the sequence to the maximum id
                    cur.execute("SELECT setval('class_cid_seq', %s, true)", (max_id,))
                    conn.commit()
        except psycopg2.Error as e:
            print(f"Error resetting class sequence: {e}")