from flask import Blueprint, jsonify, request
from myApp.controllers.localStatistics_controller import StatisticsController
from config.local_config import DATABASE_URL

statistics_bp = Blueprint('statistics', __name__)
controller = StatisticsController(db_url=DATABASE_URL)

def format_statistics_response(data):
    return jsonify(data), 200

def format_statistics_error(error_message):
    return jsonify({'error': error_message}), 400

@statistics_bp.route('/room/<building>/capacity', methods=['POST'])
def top_rooms_by_capacity(building):
    try:
        results = controller.room_capacity(building)
        if not results:
            return format_statistics_error("Building does not exist or no rooms found.")
        return format_statistics_response(results)
    except Exception as e:
        return format_statistics_error(str(e))

@statistics_bp.route('/room/<building>/ratio', methods=['POST'])
def top_rooms_by_ratio(building):
    try:
        results = controller.room_ratio(building)
        if not results:
            return format_statistics_error("Building does not exist or no sections found.")
        return format_statistics_response(results)
    except Exception as e:
        return format_statistics_error(str(e))

@statistics_bp.route('/room/<int:room_id>/classes', methods=['POST'])
def top_classes_by_room(room_id):
    try:
        results = controller.room_classes(str(room_id).strip())
        if not results:
            return format_statistics_error("No classes found for this room.")
        return format_statistics_response(results)
    except Exception as e:
        return format_statistics_error(str(e))

@statistics_bp.route('/classes/<int:year>/<semester>', methods=['POST'])
def top_classes_by_semester(year, semester):
    try:
        results = controller.classes_by_semester(year, semester.lower())
        if not results:
            return format_statistics_error("No classes found for this semester.")
        return format_statistics_response(results)
    except Exception as e:
        return format_statistics_error(str(e))
