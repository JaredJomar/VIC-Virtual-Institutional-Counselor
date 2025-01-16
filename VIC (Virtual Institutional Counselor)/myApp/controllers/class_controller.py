# myApp.controllers.class_controller.py

from myApp.models.class_models import ClassModel
from config.local_config import DATABASE_URL

class ClassController:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = DATABASE_URL
        self.model = ClassModel(db_url)

    def create_class(self, class_data):
        try:
            return self.model.insert_class(class_data)
        except Exception as e:
            raise e

    def get_class(self, class_id):
        try:
            class_data = self.model.fetch_class(class_id)
            if not class_data:
                raise ValueError("Class not found.")
            return class_data
        except Exception as e:
            raise e

    def get_all_classes(self):
        try:
            classes = self.model.fetch_all_classes()
            if not classes:
                raise ValueError("No classes found.")
            return classes
        except Exception as e:
            raise e

    def update_class(self, class_id, class_data):
        try:
            updated_rows = self.model.update_class(class_id, class_data)
            if not updated_rows:
                raise ValueError("Class not found.")
            return updated_rows
        except Exception as e:
            raise e

    def delete_class(self, class_id):
        try:
            deleted_rows = self.model.delete_class(class_id)
            if not deleted_rows:
                raise ValueError("Class not found.")
            return deleted_rows
        except Exception as e:
            raise e
