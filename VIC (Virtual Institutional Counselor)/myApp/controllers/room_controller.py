# myApp/controllers/room_controller.py

from myApp.models.room_model import RoomModel

class RoomController:

    def __init__(self, db_url):
        self.db_url = db_url
        self.model = RoomModel(self.db_url)

    def convert_to_dict(self, room_id, room_building, room_number, room_capacity):
        new_dict = {
            "rid": room_id,
            "building": room_building,
            "room_number": room_number,
            "capacity": room_capacity
        }

        return new_dict


    def create_rooms(self, room_json):

        column_names = ["building", "room_number", "capacity"]

        # Validation
        for column_name in column_names:
    
            if column_name not in room_json:
                return f"Invalid Input, field {column_name} missing"
            
            column_value = room_json[column_name]

            if column_name in ["building", "room_number"] and not isinstance(column_value, str):
                return f"Invalid Input, {column_name} must be a string"
            
            elif column_name == "capacity" and not isinstance(column_value, int):
                return "Invalid Input, Capacity must be an integer"
            
            elif column_name == "capacity" and column_value < 0:
                return "Invalid Input, Capacity cannot be negative"
         
            
        building = room_json["building"]
        room_number = room_json["room_number"]
        capacity = room_json["capacity"]
 
        new_rid = self.model.insert_room(building, room_number, capacity)

        if new_rid == None:
            return None

        temp = self.convert_to_dict(new_rid, building, room_number, capacity)
        return temp
    

    def get_all_rooms(self):

        temp = self.model.fetch_all_rooms()

        if temp == None:
            return None
    
        rooms = []

        for record in temp:
            room = self.convert_to_dict(record[0], record[1], record[2], record[3])
            rooms.append(room)

        return rooms 


    def get_room_by_id(self, room_id):
        found_room = self.model.fetch_room(room_id)

        if found_room == None:
            return None

        temp = self.convert_to_dict(found_room[0], found_room[1], found_room[2], found_room[3],)
        return temp
    

    def update_room_by_id(self, room_id, room_json):

        column_names = ["building", "room_number", "capacity"]

        # Validation
        for column_name in column_names:
    
            if column_name not in room_json:
                return f"Invalid Input, field {column_name} missing"
            
            column_value = room_json[column_name]

            if column_name in ["building", "room_number"] and not isinstance(column_value, str):
                return f"Invalid Input, {column_name} must be a string"
            
            elif column_name == "capacity" and not isinstance(column_value, int):
                return "Invalid Input, Capacity must be an integer"
            
            elif column_name == "capacity" and column_value < 0:
                return "Invalid Input, Capacity cannot be negative"

        building = room_json["building"]
        room_number = room_json["room_number"]
        capacity = room_json["capacity"]

        if not building or not room_number or not capacity:
            return "invalid"

        temp = self.model.update_room(room_id, building, room_number, capacity)

        if temp == False:
            return None

        updated_room = self.convert_to_dict(room_id, building, room_number, capacity)
        return updated_room
    

    def delete_room_by_id(self, room_id):
        temp = self.model.delete_room(room_id)

        if temp == False:
            return None

        return temp
    