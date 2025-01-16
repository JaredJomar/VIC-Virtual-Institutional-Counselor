# myApp/views/room_views.py

from flask import Blueprint, request, jsonify
from myApp.controllers.room_controller import RoomController
from config.local_config import DATABASE_URL

room_blueprint = Blueprint('room_blueprint', __name__)
controller = RoomController(db_url=DATABASE_URL)


@room_blueprint.route("/room", methods=["POST"])
def create_room():
    if request.method == "POST":
            temp = controller.create_rooms(request.json)
            
            if type(temp) == str:
                return jsonify(temp), 400

            elif temp:
                return jsonify(f"Room {temp} created successfully"), 200
        
            else:
                return jsonify("Error creating room."), 502
                 
    else:
        return jsonify("No valid method or input attached."), 500
    

@room_blueprint.route("/room", methods=["GET"]) 
def get_all_rooms():
    if request.method == "GET":
            temp = controller.get_all_rooms()

            if temp:
                return jsonify(temp), 200
        
            else:
                return jsonify("Error getting rooms"), 502
                
    else:
        return jsonify("No valid method or input attached."), 500
    

@room_blueprint.route("/room/<int:room_id>", methods=["GET"]) 
def get_room_by_id(room_id):
    if request.method == "GET":
            temp = controller.get_room_by_id(room_id)

            if temp:
                return jsonify(temp), 200
    
            else:
                return jsonify(f"rid {room_id} not found"), 404

    else:
        return jsonify("No valid method or input attached."), 500
    

@room_blueprint.route("/room/<int:room_id>", methods=["PUT"])
def update_room_by_id(room_id):
    if request.method == "PUT":
            temp = controller.update_room_by_id(room_id, request.json)

            if temp == "Invalid":
                return jsonify(UpdateStatus = "Invalid Input"), 400

            elif temp:
                return jsonify(UpdateStatus = f"Room {temp} was updated successfully"), 200
            
            else:
                return jsonify(UpdateStatus = f"Room with rid = {room_id} was not found."), 404
            
    else:
        return jsonify("No valid method or input attached."), 500


@room_blueprint.route("/room/<int:room_id>", methods=["DELETE"])
def delete_room_by_id(room_id):
    if request.method == "DELETE":
            temp = controller.delete_room_by_id(room_id)

            if temp:
                return jsonify(DeleteStatus = f"Room {room_id} deleted successfully"), 200
        
            else:
                return jsonify(DeleteStatus = f"Room with rid = {room_id} was not found."), 404
                
    else:
        return jsonify("No valid method or input attached."), 500
