# myApp/views/meeting_views.py

from flask import Blueprint, request, jsonify
from myApp.controllers.meeting_controller import MeetingController
from config.local_config import DATABASE_URL
from datetime import datetime

meeting_blueprint = Blueprint('meeting', __name__)
controller = MeetingController()

def format_meeting_response(data):
    return jsonify(data), 200

def format_meeting_error(error_message):
    return jsonify({'error': error_message}), 400

@meeting_blueprint.route('/meeting', methods=['POST'])
def create_meeting():
    if not request.is_json:
        return jsonify({"error": "Invalid content type. Expected application/json."}), 400
    
    meeting_data = request.get_json()
    required_fields = ['ccode', 'cdays', 'starttime', 'endtime']
    missing_fields = [field for field in required_fields if field not in meeting_data or not meeting_data[field]]
    
    if missing_fields:
        return jsonify({"error": f"Missing or empty fields: {', '.join(missing_fields)}"}), 400

    try:
        datetime.strptime(meeting_data['starttime'], "%H:%M:%S")
        datetime.strptime(meeting_data['endtime'], "%H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid time format. Expected HH:MM:SS."}), 400

    try:
        result = controller.create_meeting(meeting_data)
        response = {
            "status": "success",
            "message": "Meeting created successfully",
            "data": {
                "mid": result,
                "meeting": meeting_data
            }
        }
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@meeting_blueprint.route('/meeting', methods=['GET'])
def get_all_meetings():
    try:
        meetings = controller.get_all_meetings()
        response = {
            "status": "success",
            "message": "Meetings retrieved successfully",
            "data": meetings
        }
        return jsonify(response), 200
    except Exception as e:
        return format_meeting_error(str(e))

@meeting_blueprint.route('/meeting/<int:meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    try:
        meeting = controller.get_meeting(meeting_id)
        if meeting:
            response = {
                "status": "success",
                "message": "Meeting retrieved successfully",
                "data": meeting
            }
            return jsonify(response), 200
        return format_meeting_error('Meeting not found')
    except Exception as e:
        return format_meeting_error(str(e))

@meeting_blueprint.route('/meeting/<int:meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    try:
        meeting_data = request.json
        try:
            datetime.strptime(meeting_data['starttime'], "%H:%M:%S")
            datetime.strptime(meeting_data['endtime'], "%H:%M:%S")
        except ValueError:
            return jsonify({"error": "Invalid time format. Expected HH:MM:SS."}), 400

        updated_rows = controller.update_meeting(meeting_id, meeting_data)
        if updated_rows:
            response = {
                "status": "success",
                "message": "Meeting updated successfully",
                "data": {
                    "meeting_id": meeting_id,
                    "updated_data": meeting_data
                }
            }
            return jsonify(response), 200
        return format_meeting_error('Meeting not found')
    except Exception as e:
        return format_meeting_error(str(e))

@meeting_blueprint.route('/meeting/<int:meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    try:
        deleted_rows = controller.delete_meeting(meeting_id)
        if deleted_rows:
            response = {
                "status": "success",
                "message": "Meeting deleted successfully",
                "data": {
                    "meeting_id": meeting_id
                }
            }
            return jsonify(response), 200
        return format_meeting_error('Meeting not found')
    except Exception as e:
        return format_meeting_error(str(e))
