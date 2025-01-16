# myApp/controllers/meeting_controller.py
from myApp.models.meeting_model import MeetingModel
from config.local_config import DATABASE_URL

class MeetingController:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = DATABASE_URL
        self.model = MeetingModel(db_url)

    def create_meeting(self, meeting_data):
        try:
            return self.model.create_meeting(meeting_data)
        except Exception as e:
            raise e

    def get_all_meetings(self):
        try:
            meetings = self.model.fetch_all_meetings()
            if not meetings:
                raise ValueError("No meetings found.")
            return meetings
        except Exception as e:
            raise e

    def get_meeting(self, mid):
        try:
            meeting = self.model.fetch_meeting(mid)
            if not meeting:
                raise ValueError("Meeting not found.")
            return meeting
        except Exception as e:
            raise e

    def update_meeting(self, mid, meeting_data):
        try:
            updated_rows = self.model.update_meeting(mid, meeting_data)
            if not updated_rows:
                raise ValueError("Meeting not found.")
            return updated_rows
        except Exception as e:
            raise e

    def delete_meeting(self, mid):
        try:
            deleted_rows = self.model.delete_meeting(mid)
            if not deleted_rows:
                raise ValueError("Meeting not found.")
            return deleted_rows
        except Exception as e:
            raise e