# ETL.load.py 
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import psycopg2
import logging
from tqdm import tqdm
from config.local_config import DATABASE_URL
# from config.heroku_config import HEROKU_DB_URL
from dotenv import load_dotenv
# from myApp.filehandler import process_files

def ask_database_choice():
    """Prompt the user to select between local or Heroku database."""
    while True:
        print("\nSelect the database you want to use:")
        print("1. Local database (development)")
        print("2. Heroku database (production)")
        choice = input("Enter 1 or 2: ").strip()
        if choice in ["1", "2"]:
            return choice
        print("Invalid choice. Please enter 1 or 2.")

class Load:
    def __init__(self, max_workers=5):
        choice = ask_database_choice()
        env = "development"
        
        if choice == "2":
            try:
                load_dotenv(".env.production", override=True)
                self.db_url = os.getenv("DATABASE_URL")  # Try direct environment variable first
                if not self.db_url:
                    self.db_url = DATABASE_URL  # Fallback to imported config
                if not self.db_url:
                    raise ValueError("No Heroku DATABASE_URL found in environment or config")
                
                print(f"Attempting to connect to Heroku database...")
                env = "production"
                self._test_connection()
                print("Successfully connected to Heroku database!")
            except Exception as e:
                print(f"Error connecting to Heroku: {str(e)}")
                print("Falling back to local database...")
                load_dotenv(".env.development", override=True)
                self.db_url = DATABASE_URL
                env = "development"
        else:
            load_dotenv(".env.development", override=True)
            self.db_url = DATABASE_URL
            if not self.db_url:
                raise ValueError("DATABASE_URL is not configured properly")

        # Ensure proper URL format
        if self.db_url.startswith("postgres://"):
            self.db_url = self.db_url.replace("postgres://", "postgresql://", 1)

        print(f"\nConnecting to {env} database...")
        self._test_connection()
        
        self.max_workers = max_workers
        self.setup_logging()
        self.meeting_id_map = {}

    def _test_connection(self):
        """Test database connection and raise error if unsuccessful"""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT current_database();")
                    db_name = cur.fetchone()[0]
                    cur.execute("SELECT version();")
                    version = cur.fetchone()[0]
                    print(f"Connected to database: {db_name}")
                    print(f"PostgreSQL version: {version.split()[1]}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('etl.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _check_vector_installed(self, cur):
        """Check if pgvector extension is already installed"""
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_available_extensions 
                WHERE name = 'vector' AND installed_version IS NOT NULL
            );
        """)
        return cur.fetchone()[0]

    def _install_vector(self, cur):
        """Attempt to install pgvector extension"""
        try:
            # First check if it's available but not installed
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_available_extensions WHERE name = 'vector'
                );
            """)
            is_available = cur.fetchone()[0]

            if not is_available:
                self.logger.warning("pgvector extension is not available in the system.")
                self.logger.warning("Please install it using your system's package manager:")
                self.logger.warning("Ubuntu/Debian: sudo apt-get install postgresql-14-vector")
                self.logger.warning("RHEL/CentOS: sudo yum install postgresql-14-vector")
                self.logger.warning("MacOS: brew install pgvector")
                return False

            # If available, try to install it
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            return True

        except Exception as e:
            self.logger.error(f"Failed to install pgvector: {str(e)}")
            return False

    def create_tables(self):
        """Create the necessary tables for the project with proper sequences."""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                # Drop all tables with proper CASCADE
                # cur.execute("DROP TABLE IF EXISTS chat_logs CASCADE;")
                # cur.execute("DROP TABLE IF EXISTS questions CASCADE;")
                # cur.execute("DROP TABLE IF EXISTS knowledge_base CASCADE;")
                # cur.execute("DROP TABLE IF EXISTS syllabus CASCADE;")
                cur.execute("DROP TABLE IF EXISTS requisite CASCADE;")
                cur.execute("DROP TABLE IF EXISTS section CASCADE;")
                cur.execute("DROP TABLE IF EXISTS room CASCADE;")
                cur.execute("DROP TABLE IF EXISTS meeting CASCADE;")
                cur.execute("DROP TABLE IF EXISTS class CASCADE;")
                # cur.execute("DROP TABLE IF EXISTS users CASCADE;")

                # Create 'class' table
                cur.execute("""
                    CREATE TABLE class (
                        cid serial PRIMARY KEY,
                        cname varchar,
                        ccode varchar,
                        cdesc varchar,
                        term varchar,
                        years varchar,
                        cred int,
                        csyllabus varchar
                    );
                """)
                # Set sequence to start at 2
                cur.execute("ALTER SEQUENCE class_cid_seq RESTART WITH 2;")

                cur.execute("""
                    CREATE TABLE requisite (
                        classid integer REFERENCES class(cid),
                        reqid integer REFERENCES class(cid),
                        prereq boolean,
                        PRIMARY KEY (classid, reqid),
                        CONSTRAINT valid_class_ids CHECK (classid >= 2 AND reqid >= 2)
                    );
                """)

                cur.execute("""
                    CREATE TABLE room (
                        rid serial PRIMARY KEY,
                        building varchar,
                        room_number varchar,
                        capacity int
                    );
                """)

                cur.execute("""
                    CREATE TABLE meeting (
                        mid serial PRIMARY KEY,
                        ccode varchar,
                        starttime time,
                        endtime time,
                        cdays varchar(5)
                    );
                """)

                cur.execute("""
                    CREATE TABLE section (
                        sid serial PRIMARY KEY,
                        roomid int REFERENCES room(rid),
                        cid int REFERENCES class(cid),
                        mid int REFERENCES meeting(mid),
                        semester varchar,
                        years varchar,
                        capacity int,
                        CONSTRAINT valid_class_id CHECK (cid >= 2)
                    );
                """)

                # # Create users table
                # cur.execute("""
                #     CREATE TABLE users (
                #         id SERIAL PRIMARY KEY,  -- Unique identifier for each user
                #         username VARCHAR(255) UNIQUE NOT NULL,  -- Unique username for authentication
                #         password_hash TEXT NOT NULL,  -- Securely stored password hash
                #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- User account creation timestamp
                #     );
                #     -- Add index on username for faster lookups
                #     CREATE INDEX idx_username ON users(username);
                # """)

                # # Handle pgvector installation
                # vector_available = self._check_vector_installed(cur)
                # if not vector_available:
                #     self.logger.info("pgvector not installed. Attempting to install...")
                #     vector_available = self._install_vector(cur)

                # # Create vector-dependent tables
                # if vector_available:

                #     cur.execute("""
                #         CREATE TABLE syllabus (
                #             chunkid serial PRIMARY KEY,
                #             courseid int REFERENCES class(cid),
                #             embedding vector(768),  -- Use pgvector for embeddings
                #             chunk text,
                #             CONSTRAINT valid_course_id CHECK (courseid >= 2)
                #         );
                #     """)

                #     # Create knowledge_base with vector support
                #     cur.execute("""
                #         CREATE TABLE knowledge_base (
                #             id serial PRIMARY KEY,
                #             content text NOT NULL,
                #             embedding vector(768) NOT NULL
                #         );
                #     """)

                #     # Create questions table with vector support
                #     cur.execute("""
                #         CREATE TABLE questions (
                #             id serial PRIMARY KEY,
                #             question text NOT NULL,
                #             embedding vector(768) NOT NULL
                #         );
                #     """)
                # else:
                #     # Create tables without vector support
                #     cur.execute("""
                #         CREATE TABLE knowledge_base (
                #             id serial PRIMARY KEY,
                #             content text NOT NULL
                #         );
                #     """)

                #     cur.execute("""
                #         CREATE TABLE questions (
                #             id serial PRIMARY KEY,
                #             question text NOT NULL
                #         );
                #     """)

                # # Create chat_logs table for interaction history
                # cur.execute("""
                #     CREATE TABLE chat_logs (
                #         id serial PRIMARY KEY,
                #         user_id varchar NOT NULL,
                #         question text NOT NULL,
                #         answer text NOT NULL,
                #         timestamp timestamp DEFAULT CURRENT_TIMESTAMP
                #     );
                # """)

                conn.commit()
                self.logger.info("Tables created successfully.")

    def load_all(self):
        """Modified load_all method with better error handling"""
        try:
            # Load corrected CSV files from FixedData folder
            data_path = 'ETL/FixedData'
            courses_df = pd.read_csv(f'{data_path}/class.csv')
            meetings_df = pd.read_csv(f'{data_path}/meeting.csv')
            requisites_df = pd.read_csv(f'{data_path}/requisite.csv')
            rooms_df = pd.read_csv(f'{data_path}/room.csv')
            sections_df = pd.read_csv(f'{data_path}/section.csv')

            print(f"Loaded {len(requisites_df)} requisites")
            print(f"Loaded {len(courses_df)} courses")
            print(f"Loaded {len(meetings_df)} meetings")
            print(f"Loaded {len(rooms_df)} rooms")
            print(f"Loaded {len(sections_df)} sections")


            # Process syllabus files. This will return the embedded text and
            # the chunk of text. See filehandler.py for more info
            # syllabi_data = process_files()
            # print(f"Processed {len(syllabi_data)} syllabus files.")
            
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    print("Starting data load...")
                    self._load_classes(courses_df, cur)
                    print("Classes loaded successfully")
                    self._load_rooms(rooms_df, cur)
                    print("Rooms loaded successfully")
                    self._load_meetings(meetings_df, cur)
                    print("Meetings loaded successfully")
                    self._load_requisites(requisites_df, cur)
                    print("Requisites loaded successfully")
                    self._load_sections(sections_df, cur)
                    print("Sections loaded successfully")
                    # self._load_syllabi(syllabi_data, cur)  # Updated syllabi loading
                    # print("Syllabi loaded successfully.")
                    conn.commit()
                    print("All data committed to database successfully!")
                    
        except Exception as e:
            print(f"Error during data load: {str(e)}")
            raise

    def _load_classes(self, courses_df, cur):
        for _, row in courses_df.iterrows():
            try:
                cur.execute(
                    """
                    INSERT INTO class (cname, ccode, cdesc, term, years, cred, csyllabus)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (row['cname'], row['ccode'], row['cdesc'], row['term'], 
                    row['years'], row['cred'], row['csyllabus'])
                )
            except Exception as e:
                print(f"Error inserting into class: {e}")

    def _load_rooms(self, rooms_df, cur):
        for _, row in tqdm(rooms_df.iterrows(), total=len(rooms_df), desc="[ETL] Loading rooms"):
            cur.execute(
                """
                INSERT INTO room (building, room_number, capacity)
                VALUES (%s, %s, %s) RETURNING rid
                """,
                (row['building'], row['room_number'], row['capacity'])
            )
            row['rid'] = cur.fetchone()[0]

    def _load_meetings(self, meetings_df, cur):
        """Load meetings data and store the mapping of meeting IDs"""
        self.meeting_id_map.clear()  # Clear existing mappings
        for _, row in tqdm(meetings_df.iterrows(), total=len(meetings_df), desc="[ETL] Loading meetings"):
            starttime = row['starttime']
            endtime = row['endtime']
            
            cur.execute(
                """
                INSERT INTO meeting (ccode, starttime, endtime, cdays)
                VALUES (%s, %s, %s, %s) RETURNING mid
                """,
                (row['ccode'], starttime, endtime, row['cdays'])
            )
            # row['mid'] = cur.fetchone()[0]
            new_mid = cur.fetchone()[0]
            original_mid = row['mid'] if 'mid' in row else len(self.meeting_id_map)
            self.meeting_id_map[original_mid] = new_mid

    def _load_requisites(self, requisites_df, cur):
        for _, row in tqdm(requisites_df.iterrows(), total=len(requisites_df), desc="[ETL] Loading requisites"):
            cur.execute(
                """
                INSERT INTO requisite (classid, reqid, prereq)
                VALUES (%s, %s, %s)
                """,
                (row['classid'], row['reqid'], bool(row['prereq']))
                  )

    def _load_sections(self, sections_df, cur):
        for _, row in tqdm(sections_df.iterrows(), total=(len(sections_df)), desc="[ETL] Loading sections"):
            meeting_id = self.meeting_id_map.get(row['mid'])
            if meeting_id is not None:
                cur.execute(
                    """
                    INSERT INTO section (roomid, cid, mid, semester, years, capacity)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING sid
                    """,
                    (row['roomid'], row['cid'], row['mid'], row['semester'], row['years'], row['capacity'])
                )
                row['sid'] = cur.fetchone()[0]

    def _load_syllabi(self, syllabi_data, cur):
        """Load syllabus fragments into the database."""
        for syllabus in syllabi_data:
            file_name = syllabus["file_name"]
            print(f"Processing syllabus for file: {file_name}")

            # Fetch courseid for the syllabus based on file_name
            cur.execute("SELECT cid FROM class WHERE cname = %s AND ccode = %s", (file_name[:4], file_name[5:9]))
            course_row = cur.fetchone()
            if not course_row:
                print(f"No matching course found for file: {file_name}. Skipping.")
                continue
            
            courseid = course_row[0]

            # Insert fragments into the syllabus table
            for fragment in syllabus["fragments"]:
                try:
                    cur.execute(
                        """
                        INSERT INTO syllabus (courseid, embedding, chunk)
                        VALUES (%s, %s, %s)
                        """,
                        (courseid, fragment["embedding"], fragment["chunk"])  # Pass the embedding as a vector
                    )
                except Exception as e:
                    print(f"Error inserting fragment for {file_name}: {e}")
        print("Syllabi loading completed.")


    def clean_duplicate_sections(self):
        """Remove duplicate sections based on specifications"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                # Remove sections with duplicate SIDs
                cur.execute("""
                    WITH duplicate_sids AS (
                        SELECT sid
                        FROM section
                        GROUP BY sid
                        HAVING COUNT(*) > 1
                    )
                    DELETE FROM section
                    WHERE sid IN (SELECT sid FROM duplicate_sids);
                """)

                # Remove sections with same room, time but different semester/year (keep lower sid)
                cur.execute("""
                    WITH duplicate_schedules AS (
                        SELECT s1.sid
                        FROM section s1
                        JOIN section s2 ON s1.roomid = s2.roomid 
                            AND s1.mid = s2.mid
                            AND (s1.semester != s2.semester OR s1.years != s2.years)
                            AND s1.sid > s2.sid
                    )
                    DELETE FROM section
                    WHERE sid IN (SELECT sid FROM duplicate_schedules);
                """)

                conn.commit()
                # self.logger.info("Duplicate sections cleaned successfully")

    def reset_sequences(self):
        """Reset all sequences to proper values after data loading"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                tables = ['class', 'meeting', 'room', 'section', 'syllabus', 
                         'knowledge_base', 'chat_logs', 'questions']
                for table in tables:
                    id_column = 'id' if table in ['knowledge_base', 'chat_logs', 'questions'] else 'cid' if table == 'class' else 'mid' if table == 'meeting' else 'rid' if table == 'room' else 'sid' if table == 'section' else 'chunkid'
                    cur.execute(f"""
                        SELECT setval('{table}_{id_column}_seq', 
                            COALESCE((SELECT MAX({id_column}) FROM {table}), 1), 
                            true);
                    """)
                conn.commit()
                # self.logger.info("[ETL] Sequences reset successfully")

if __name__ == "__main__":
    try:
        loader = Load()
        print("\nCreating tables...")
        loader.create_tables()
        print("\nLoading data...")
        loader.load_all()
        # print("\nCleaning duplicate sections...")
        # loader.clean_duplicate_sections()
        # print("\nResetting sequences...")
        # loader.reset_sequences()
        print("\nETL process completed successfully!")
    except Exception as e:
        print(f"\nError during ETL process: {str(e)}")
        raise