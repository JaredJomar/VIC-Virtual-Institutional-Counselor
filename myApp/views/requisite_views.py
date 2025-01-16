# myApp/views/requisite_views.py

from flask import Blueprint, request, jsonify, current_app
from myApp.controllers.requisite_controller import RequisiteController
from config.local_config import DATABASE_URL

requisite_blueprint = Blueprint('requisite_blueprint', __name__)
controller = RequisiteController()

@requisite_blueprint.before_request
def setup_controller():
    global controller
    if controller is None:
        db_url = current_app.config.get('DATABASE_URL')
        controller = RequisiteController(db_url)

def format_requisite_response(data):
    return jsonify(data), 200

def format_requisite_error(error_message):
    return jsonify({'error': error_message}), 400

@requisite_blueprint.route('/requisite', methods=['POST'])
def create_requisite():
    try:
        requisite_data = request.json
        requisite_id = controller.create_requisite(requisite_data)
        response = {
            "status": "success",
            "message": "Requisite created successfully",
            "data": {
                # "requisite_id": requisite_id,
                "classid": requisite_data["classid"],
                "reqid": requisite_data["reqid"],
                "prereq": requisite_data["prereq"]
            }
        }
        return jsonify(response), 201
    except Exception as e:
        return format_requisite_error(str(e))

@requisite_blueprint.route('/requisite', methods=['GET'])
def get_all_requisites():
    try:
        requisites = controller.get_all_requisites()
        if not requisites:
            return format_requisite_error("No requisites found.")
        return format_requisite_response(requisites)
    except Exception as e:
        return format_requisite_error(str(e))

@requisite_blueprint.route('/requisite/<int:classid>/<int:reqid>', methods=['GET'])
def get_requisite(classid, reqid):
    try:
        requisite = controller.get_requisite(classid, reqid)
        if requisite:
            return format_requisite_response(requisite)
        return format_requisite_error('Requisite not found')
    except Exception as e:
        return format_requisite_error(str(e))

@requisite_blueprint.route('/requisite/<int:classid>/<int:reqid>', methods=['PUT'])
def update_requisite(classid, reqid):
    try:
        requisite_data = request.json
        updated_rows = controller.update_requisite(classid, reqid, requisite_data)
        if updated_rows:
            response = {
                "status": "success",
                "message": "Requisite updated successfully",
                "data": {
                    "classid": classid,
                    "reqid": reqid,
                    "updated_data": requisite_data
                }
            }
            return jsonify(response), 200
        return format_requisite_error('Requisite not found')
    except Exception as e:
        return format_requisite_error(str(e))

@requisite_blueprint.route('/requisite/<int:classid>/<int:reqid>', methods=['DELETE'])
def delete_requisite(classid, reqid):
    try:
        deleted_rows = controller.delete_requisite(classid, reqid)
        if deleted_rows:
            response = {
                "status": "success",
                "message": "Requisite deleted successfully",
                "data": {
                    "classid": classid,
                    "reqid": reqid,
                    "rows_affected": deleted_rows
                }
            }
            return jsonify(response), 200
        return format_requisite_error('Requisite not found')
    except Exception as e:
        return format_requisite_error(str(e))
