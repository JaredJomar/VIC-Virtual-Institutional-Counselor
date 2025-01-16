import sys
import os
import threading  # Add this import statement
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract import Extract
from transform import Transform
from load import Load
from config.local_config import DATABASE_URL as LOCALHOST_DB_URL
from config.heroku_config import HEROKU_DB_URL

def ask_database_choice():
    """Prompt the user to select between local or Heroku database."""
    print("Select the database you want to use:")
    print("1. Local database (development)")
    print("2. Heroku database (production)")

    def get_input():
        nonlocal choice
        choice = input("Enter the number (1 or 2): ").strip()

    choice = None
    input_thread = threading.Thread(target=get_input)
    input_thread.start()
    input_thread.join(timeout=10)

    if choice is None or choice not in ['1', '2']:
        print("\nNo valid selection received. Using Heroku database as the default.")
        return '2'
    else:
        return choice

def ensure_directories_exist(*directories):
    """Ensure that the required directories exist, if not, create them."""
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist. Creating it.")
            os.makedirs(directory)

if __name__ == "__main__":
    # Step 1: Select the database environment
    choice = ask_database_choice()

    if choice == '1':
        db_url = LOCALHOST_DB_URL
        ENV = 'development'
        print("Using local database for development.")
    else:
        db_url = HEROKU_DB_URL
        ENV = 'production'
        print("Using Heroku database for production.")

    # Step 2: Ensure required directories exist
    data_dir = "ETL/Files/"
    syllabus_dir = "syllabuses/"
    ensure_directories_exist(data_dir, syllabus_dir)

    try:
        # Step 3: Extract data from the files
        print("[ETL] Starting data extraction...")
        extractor = Extract(data_dir)
        courses_df, meetings_df, requisites_df, rooms_df, sections_df = extractor.extract_all()

        # Step 4: Transform the extracted data
        print("[ETL] Starting data transformation...")
        transformer = Transform(courses_df, meetings_df, requisites_df, rooms_df, sections_df, syllabus_dir=syllabus_dir)
        courses_df, meetings_df, requisites_df, rooms_df, sections_df = transformer.transform_all()

        # Step 5: Load the transformed data into the selected database
        print("[ETL] Starting data load process...")
        loader = Load(db_url)
        loader.create_tables()
        loader.load_all(courses_df, meetings_df, requisites_df, rooms_df, sections_df)
        print(f"[ETL] Data successfully loaded into the {ENV} database.")
    
    except Exception as e:
        print(f"[ETL] An error occurred during the ETL process: {str(e)}")
