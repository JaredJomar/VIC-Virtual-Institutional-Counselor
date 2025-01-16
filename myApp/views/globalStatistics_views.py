from flask import Blueprint, jsonify, request
import logging
from myApp.controllers.globalStatistics_controller import GlobalStatisticsController
from config.local_config import DATABASE_URL
from datetime import time

global_statistics_bp = Blueprint('global_statistics', __name__)
controller = GlobalStatisticsController(db_url=DATABASE_URL)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def format_time(obj):
    if isinstance(obj, time):
        return obj.strftime('%H:%M:%S')
    return obj

def format_statistics_response(data):
    if not data:
        return jsonify({'data': [], 'message': 'No data found'}), 200
    
    # Convert time objects in the data
    if isinstance(data, list):
        formatted_data = []
        for item in data:
            formatted_item = {k: format_time(v) for k, v in item.items()}
            formatted_data.append(formatted_item)
    else:
        formatted_data = {k: format_time(v) for k, v in data.items()}
    
    return jsonify({'data': formatted_data, 'message': 'Success'}), 200

def format_statistics_error(error_message):
    return jsonify({'error': error_message}), 400

@global_statistics_bp.route('/most/meeting', methods=['GET', 'POST'])
def top_meetings_with_most_sections():
    """Endpoint for top 5 meetings with the most sections."""
    try:
        results = controller.top_meetings_with_most_sections()
        return format_statistics_response(results)
    except Exception as e:
        logger.error(f"Error in top_meetings_with_most_sections endpoint: {e}")
        return format_statistics_error(str(e))

@global_statistics_bp.route('/most/prerequisite', methods=['GET', 'POST'])
def top_classes_most_prerequisites():
    """Endpoint for top 3 classes that appear the most as prerequisites."""
    try:
        results = controller.top_classes_most_prerequisites()
        return format_statistics_response(results)
    except Exception as e:
        logger.error(f"Error in top_classes_most_prerequisites endpoint: {e}")
        return format_statistics_error(str(e))

@global_statistics_bp.route('/least/classes', methods=['GET', 'POST'])
def top_classes_least_offered():
    """Endpoint for top 3 classes that were offered the least."""
    try:
        results = controller.top_classes_least_offered()
        return format_statistics_response(results)
    except Exception as e:
        logger.error(f"Error in top_classes_least_offered endpoint: {e}")
        return format_statistics_error(str(e))

@global_statistics_bp.route('/section/year', methods=['GET', 'POST'])
def total_sections_per_year():
    """Endpoint for total number of sections per year."""
    try:
        results = controller.total_sections_per_year()
        return format_statistics_response(results)
    except Exception as e:
        logger.error(f"Error in total_sections_per_year endpoint: {e}")
        return format_statistics_error(str(e))