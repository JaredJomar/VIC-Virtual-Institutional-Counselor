# myApp/views/syllabus_view.py

from flask import Blueprint, request, jsonify, current_app
from myApp.controllers.syllabus_controller import SyllabusController
from config.local_config import DATABASE_URL


syllabus_blueprint = Blueprint('syllabus_blueprint', __name__)
controller = SyllabusController(db_url=DATABASE_URL)

# @syllabus_blueprint.before_request
# def setup_controller():
#     global controller
#     if controller is None:
#         db_url = current_app.config.get('DATABASE_URL')
#         if not db_url:
#             raise ValueError("DATABASE_URL not configured")
#         controller = SyllabusController(db_url)

def format_response(data):
    return jsonify(data), 200

def format_error(error_message):
    return jsonify({'error': error_message}), 400

@syllabus_blueprint.route('/syllabus', methods=['POST'])
def create_fragment():
    try:
        fragment_data = request.json
        chunkid = controller.create_fragment(fragment_data)
        response = {
            "status": "success",
            "message": "Fragment created successfully",
            "data": {
                "chunkid": chunkid,
                **fragment_data
            }
        }
        return jsonify(response), 201
    except Exception as e:
        return format_error(str(e))

@syllabus_blueprint.route('/syllabus', methods=['GET'])
def get_all_fragments():
    try:
        fragments = controller.get_all_fragments()
        if not fragments:
            return format_error("No fragments found.")
        return format_response(fragments)
    except Exception as e:
        return format_error(str(e))

@syllabus_blueprint.route('/syllabus/<string:chunkid>', methods=['GET'])
def get_fragment(chunkid):
    try:
        fragment = controller.get_fragment(chunkid)
        if fragment:
            return format_response(fragment)
        return format_error("Fragment not found.")
    except Exception as e:
        return format_error(str(e))

@syllabus_blueprint.route('/syllabus/<string:chunkid>', methods=['DELETE'])
def delete_fragment(chunkid):
    try:
        deleted_rows = controller.delete_fragment(chunkid)
        if deleted_rows:
            response = {
                "status": "success",
                "message": "Fragment deleted successfully",
                "data": {
                    "chunkid": chunkid,
                    "rows_affected": deleted_rows
                }
            }
            return jsonify(response), 200
        return format_error("Fragment not found.")
    except Exception as e:
        return format_error(str(e))
