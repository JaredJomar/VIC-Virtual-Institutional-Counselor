# myApp/models/syllabus_model.py

import psycopg2
from psycopg2.extras import execute_batch

class SyllabusModel:
    def __init__(self, db_url):
        self.db_url = db_url

    def insert_fragment(self, fragment_data):
        """
        Inserts a syllabus fragment into the database.
        """
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO syllabus (chunkid, courseid, embedding, chunk)
                        VALUES (%s, %s, %s::vector, %s) RETURNING chunkid
                        """,
                        (fragment_data['chunkid'], fragment_data['courseid'],
                        f"[{', '.join(map(str, fragment_data['embedded_text']))}]", fragment_data['chunk'])
                    )
                    return cur.fetchone()[0]
        except psycopg2.Error as e:
            print(f"Error inserting fragment: {e}")
            return None

        
    def bulk_insert_fragments(self, fragments):
        """
        Inserts multiple fragments into the database in a single transaction.
        """
        query = """
            INSERT INTO syllabus (chunkid, courseid, embedding, chunk)
            VALUES (%s, %s, %s::vector, %s)
        """
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    data = [
                        (f["chunkid"], f["courseid"],
                        f"[{', '.join(map(str, f['embedded_text']))}]", f["chunk"])
                        for f in fragments
                    ]
                    execute_batch(cur, query, data)
                    conn.commit()
        except psycopg2.Error as e:
            print(f"Error during bulk insert: {e}")


    def fetch_fragment(self, chunkid):
        """
        Fetches a specific syllabus fragment by chunkid.
        """
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM syllabus WHERE chunkid = %s;", (chunkid,))
                    result = cur.fetchone()
                    if result:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, result))
                    return None
        except psycopg2.Error as e:
            print(f"Error fetching fragment: {e}")
            return None

    def fetch_all_fragments(self):
        """
        Fetches all syllabus fragments from the database.
        """
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM syllabus;")
                    results = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in results]
        except psycopg2.Error as e:
            print(f"Error fetching all fragments: {e}")
            return []

    def delete_fragment(self, chunkid):
        """
        Deletes a specific syllabus fragment by chunkid.
        """
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM syllabus WHERE chunkid = %s;", (chunkid,))
                    return cur.rowcount
        except psycopg2.Error as e:
            print(f"Error deleting fragment: {e}")
            return 0

    def fetch_similar_fragments(self, embedding, top_n=5):
        """
        Fetch the top N most relevant fragments based on embedding similarity.
        Args:
            embedding (list): Embedding of the question.
            top_n (int): Number of fragments to retrieve.
        Returns:
            list: List of fragments with their content.
        """
        query = """
            SELECT chunk, embedding <-> %s::vector AS similarity
            FROM syllabus
            ORDER BY similarity
            LIMIT %s;
        """
        embedding_str = f"[{', '.join(map(str, embedding))}]"  # Format the embedding as a vector string
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (embedding_str, top_n))
                rows = cur.fetchall()
        return [{"chunk": row[0], "similarity": row[1]} for row in rows]

