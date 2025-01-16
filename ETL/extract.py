import pandas as pd
import json
import sqlite3
import xml.etree.ElementTree as ET
from functools import wraps

class Extract:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def handle_errors(f):
        """Error handling decorator for extraction methods."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except FileNotFoundError as e:
                print(f"Error: File not found - {e}")
            except pd.errors.EmptyDataError:
                print(f"Error: The file {args[1]} is empty.")
            except pd.errors.ParserError as e:
                print(f"Error: CSV file {args[1]} is malformed - {e}")
            except json.JSONDecodeError as e:
                print(f"Error: Malformed JSON file {args[1]} - {e}")
            except sqlite3.DatabaseError as e:
                print(f"Error: Database issue with file {args[1]} - {e}")
            except ET.ParseError as e:
                print(f"Error: Malformed XML file {args[1]} - {e}")
            except UnicodeDecodeError as e:
                print(f"Error: Encoding issue in file {args[1]} - {e}")
            except KeyError as e:
                print(f"Error: Missing expected column or key - {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        return decorated_function

    @handle_errors
    def extract_csv(self, file_name):
        """Extracts data from a CSV file and removes any incomplete records."""
        file_path = self.data_dir + file_name
        df = pd.read_csv(file_path)
        # Drop rows with any empty or null values
        return df.dropna()

    @handle_errors
    def extract_json(self, file_name):
        """Extracts data from a JSON file and flattens nested structures."""
        file_path = self.data_dir + file_name
        with open(file_path, 'r') as f:
            data = json.load(f)

            # Prepare a list to hold the flattened data
            flattened_data = []

            # Loop through each building and its rooms
            for building, rooms in data.items():
                for room in rooms:
                    # Add a new dictionary with building name and room details
                    flattened_data.append({
                        'rid': room['id'],
                        'building': building,
                        'number': room['number'],
                        'capacity': room['capacity']
                    })

            # Create a DataFrame from the flattened data
            df = pd.DataFrame(flattened_data)
            # Drop rows with any empty or null values
            return df.dropna()

    @handle_errors
    def extract_db(self, file_name):
        """Extracts data from a SQLite database and removes any incomplete records."""
        file_path = self.data_dir + file_name
        conn = sqlite3.connect(file_path)
        query = "SELECT * FROM requisites"
        df = pd.read_sql_query(query, conn)
        conn.close()
        # Drop rows with any empty or null values
        return df.dropna()

    @handle_errors
    def extract_xml(self, file_name):
        """Extracts data from an XML file and removes incomplete records."""
        file_path = self.data_dir + file_name
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Wrap the content in a root element to make it valid XML
        wrapped_content = f"<AllCourses>{content}</AllCourses>"

        # Parse the wrapped XML
        root = ET.fromstring(wrapped_content)

        courses = []
        for course in root.findall('Courses'):
            # Extract data for each course
            class_info = {
                'classid': course.find('classid').text if course.find('classid') is not None else None,
                'cred': course.find('cred').text if course.find('cred') is not None else None,
                'description': course.find('description').text if course.find('description') is not None else None,
                'syllabus': course.find('syllabus').text if course.find('syllabus') is not None else None,
                'term': course.find('term').text if course.find('term') is not None else None,
                'years': course.find('years').text if course.find('years') is not None else None,
                'classes': {
                    'code': course.find('classes/code').text if course.find('classes/code') is not None else None,
                    'name': course.find('classes/name').text if course.find('classes/name') is not None else None,
                }
            }

            # Check if the class_info has any None values, only append full records
            if all(class_info.values()) and all(class_info['classes'].values()):
                courses.append(class_info)

        # Convert to DataFrame and drop any empty records
        df_courses = pd.DataFrame(courses)
        return df_courses.dropna()

    def extract_all(self):
        """Extracts data from all sources (CSV, JSON, SQLite, XML) and returns DataFrames."""
        courses_df = self.extract_xml('courses.xml')
        meetings_df = self.extract_csv('meeting.csv')
        requisites_df = self.extract_db('requisites.db')
        rooms_df = self.extract_json('rooms.json')
        sections_df = self.extract_csv('sections.csv')

        print("[ETL] Extraction complete.")

        return courses_df, meetings_df, requisites_df, rooms_df, sections_df
