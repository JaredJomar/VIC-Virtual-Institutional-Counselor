import logging
from myApp.models.localStatistics_model import (
    get_top_rooms_by_capacity,
    get_top_sections_by_ratio,
    get_top_classes_per_room,
    get_top_classes_per_semester
)

class StatisticsController:
    def __init__(self, db_url):
        self.db_url = db_url

    @staticmethod
    def room_capacity(building):
        """Get top 3 rooms with most capacity."""
        try:
            rooms = get_top_rooms_by_capacity(building)
            if not rooms:
                raise ValueError("Building does not exist or no rooms found.")
            return rooms
        except Exception as e:
            logging.error(f"Error in room_capacity: {e}")
            raise e

    @staticmethod
    def room_ratio(building):
        """Get top 3 sections with highest ratio."""
        try:
            sections = get_top_sections_by_ratio(building)
            if not sections:
                raise ValueError("Building does not exist or no sections found.")
            return sections
        except Exception as e:
            logging.error(f"Error in room_ratio: {e}")
            raise e

    @staticmethod
    def room_classes(room_id):
        """Get top 3 most taught classes per room."""
        try:
            classes = get_top_classes_per_room(room_id)
            if not classes:
                raise ValueError("No classes found for this room.")
            return classes
        except Exception as e:
            logging.error(f"Error in room_classes: {e}")
            raise e

    @staticmethod
    def classes_by_semester(year, semester):
        """Get top 3 most taught classes per semester."""
        try:
            classes = get_top_classes_per_semester(year, semester)
            if not classes:
                raise ValueError("No classes found for this semester.")
            return classes
        except Exception as e:
            logging.error(f"Error in classes_by_semester: {e}")
            raise e