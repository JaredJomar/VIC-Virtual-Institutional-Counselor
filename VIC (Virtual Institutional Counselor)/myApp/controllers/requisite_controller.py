# myApp/controllers/requisite_controller.py

from myApp.models.requisite_model import RequisiteModel
from config.local_config import DATABASE_URL

class RequisiteController:
    def __init__(self):
        self.model = RequisiteModel(DATABASE_URL)

    def create_requisite(self, requisite_data):
        return self.model.insert_requisite(requisite_data)

    def get_all_requisites(self):
        return self.model.fetch_all_requisites()

    def get_requisite(self, classid, reqid):
        return self.model.fetch_requisite(classid, reqid)

    def update_requisite(self, classid, reqid, prereq):
        return self.model.update_requisite(classid, reqid, prereq)

    def delete_requisite(self, classid, reqid):
        return self.model.delete_requisite(classid, reqid)
