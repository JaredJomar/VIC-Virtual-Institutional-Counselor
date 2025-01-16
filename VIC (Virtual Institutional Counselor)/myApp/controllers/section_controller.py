# myApp/controllers/section_controller.py

from myApp.models.section_model import SectionModel
from config.local_config import DATABASE_URL

class SectionController:
    def __init__(self):
        self.model = SectionModel(DATABASE_URL)

    def create_section(self, section_data):
        try:
            return self.model.insert_section(section_data)
        except Exception as e:
            raise e

    def get_all_sections(self):
        try:
            return self.model.fetch_all_sections()
        except Exception as e:
            raise e

    def get_section(self, section_id):
        try:
            section = self.model.fetch_section(section_id)
            if not section:
                raise ValueError("Section not found.")
            return section
        except Exception as e:
            raise e

    def update_section(self, section_id, section_data):
        try:
            updated_rows = self.model.update_section(section_id, section_data)
            if not updated_rows:
                raise ValueError("Section not found.")
            return updated_rows
        except Exception as e:
            raise e

    def delete_section(self, section_id):
        try:
            deleted_rows = self.model.delete_section(section_id)
            if not deleted_rows:
                raise ValueError("Section not found.")
            return deleted_rows
        except Exception as e:
            raise e
