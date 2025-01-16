# myApp.views.class_views.py

from flask import Blueprint, request, jsonify, current_app
from myApp.controllers.class_controller import ClassController

class_blueprint = Blueprint('class', __name__)
controller = None

@class_blueprint.before_request
def setup_controller():
    global controller
    if controller is None:
        db_url = current_app.config.get('DATABASE_URL')
        controller = ClassController(db_url)

def format_class_response(data):
    return jsonify(data), 200

def format_class_error(error_message):
    return jsonify({'error': error_message}), 400

@class_blueprint.route('/class', methods=['POST'])
def create_class():
    try:
        class_data = request.json
        class_id = controller.create_class(class_data)
        response = {
            "status": "success",
            "message": "Class created successfully",
            "data": {
                "cid": class_id,
                "requested_data": class_data
            }
        }
        return jsonify(response), 201
    except Exception as e:
        return format_class_error(str(e))

@class_blueprint.route('/class', methods=['GET'])
def get_all_classes():
    try:
        classes = controller.get_all_classes()
        if not classes:
            return format_class_error("No classes found.")
        return format_class_response(classes)
    except Exception as e:
        return format_class_error(str(e))

@class_blueprint.route('/class/<int:class_id>', methods=['GET'])
def get_class(class_id):
    try:
        class_data = controller.get_class(class_id)
        if class_data:
            return format_class_response(class_data)
        return format_class_error('Class not found')
    except Exception as e:
        return format_class_error(str(e))

@class_blueprint.route('/class/<int:class_id>', methods=['PUT'])
def update_class(class_id):
    try:
        class_data = request.json
        updated_rows = controller.update_class(class_id, class_data)
        if updated_rows:
            response = {
                "status": "success",
                "message": "Class updated successfully",
                "data": {
                    "cid": class_id,
                    "updated_data": class_data
                }
            }
            return jsonify(response), 200
        return format_class_error('Class not found')
    except Exception as e:
        return format_class_error(str(e))

@class_blueprint.route('/class/<int:class_id>', methods=['DELETE'])
def delete_class(class_id):
    try:
        deleted_rows = controller.delete_class(class_id)
        if deleted_rows:
            response = {
                "status": "success",
                "message": "Class deleted successfully",
                "data": {
                    "cid": class_id,
                    "rows_affected": deleted_rows
                }
            }
            return jsonify(response), 200
        return format_class_error('Class not found')
    except Exception as e:
        return format_class_error(str(e))