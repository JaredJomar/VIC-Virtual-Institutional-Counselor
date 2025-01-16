# myApp/controllers/syllabus_controller.py

from myApp.models.syllabus_model import SyllabusModel
from myApp.models.chatbot_model import ChatbotModel  # Add this import
from myApp.filehandler import process_files
from config.local_config import DATABASE_URL

class SyllabusController:
    def __init__(self, db_url):
        self.db_url = db_url
        self.model = ChatbotModel(db_url)
        self.syllabus_model = SyllabusModel(db_url)  # Add this for syllabus-specific operations

    def create_fragment(self, fragment_data):
        """
        Creates a new syllabus fragment in the database.
        """
        return self.model.insert_fragment(fragment_data)

    def get_fragment(self, chunkid):
        """
        Retrieves a specific syllabus fragment by chunkid.
        """
        return self.model.fetch_fragment(chunkid)

    def get_all_fragments(self):
        """
        Retrieves all syllabus fragments from the database.
        """
        return self.model.fetch_all_fragments()

    def delete_fragment(self, chunkid):
        """
        Deletes a specific syllabus fragment by chunkid.
        """
        return self.model.delete_fragment(chunkid)
    
    def fetch_similar_fragments(self, embedding, top_n=5):
        """
        Fetch similar fragments based on Q&A context
        """
        return self.model.fetch_similar_fragments(embedding)

    
    def process_and_load_syllabus(self):
        """
        Processes syllabus files and loads them into the database.
        """
        process_files()

    def get_relevant_syllabus(self, embedding, limit=2):
        """Fetch relevant syllabus content based on embedding similarity."""
        try:
            # Use syllabus model for syllabus operations
            return self.syllabus_model.get_relevant_syllabus(embedding, limit)
        except Exception as e:
            print(f"Error fetching syllabus data: {e}")
            return []
