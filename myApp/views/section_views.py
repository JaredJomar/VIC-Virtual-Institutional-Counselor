# myApp/views/section_views.py

from flask import Blueprint, jsonify, request
from myApp.controllers.section_controller import SectionController

section_blueprint = Blueprint('section_blueprint', __name__)
controller = SectionController()

def format_section_response(data, message="Success"):
    response = {
        "message": message,
        "data": data
    }
    return jsonify(response), 200

def format_section_error(error_message):
    return jsonify({'error': error_message}), 400

@section_blueprint.route('/section', methods=['POST'])
def create_section():
    try:
        section_data = request.get_json()
        section_id = controller.create_section(section_data)
        response = {
            "message": "Section created successfully",
            "data": {"section_id": section_id}
        }
        return jsonify(response), 201
    except Exception as e:
        return format_section_error(str(e))

@section_blueprint.route('/section', methods=['GET'])
def get_all_sections():
    try:
        sections = controller.get_all_sections()
        return format_section_response(
            sections if sections else [],
            message="Sections retrieved successfully"
        )
    except Exception as e:
        return format_section_error(str(e))

@section_blueprint.route('/section/<int:section_id>', methods=['GET'])
def get_section(section_id):
    try:
        section = controller.get_section(section_id)
        if section:
            return format_section_response(
                section,
                message="Section retrieved successfully"
            )
        return format_section_error('Section not found')
    except Exception as e:
        return format_section_error(str(e))

@section_blueprint.route('/section/<int:section_id>', methods=['PUT'])
def update_section(section_id):
    try:
        section_data = request.get_json()
        updated = controller.update_section(section_id, section_data)
        if updated:
            response = {
                "message": "Section updated successfully",
                "data": section_data
            }
            return jsonify(response), 200
        return format_section_error('Section not found')
    except Exception as e:
        return format_section_error(str(e))

@section_blueprint.route('/section/<int:section_id>', methods=['DELETE'])
def delete_section(section_id):
    try:
        deleted_id = controller.delete_section(section_id)
        if deleted_id:
            response = {
                "message": "Section deleted successfully",
                "data": {
                    "section_id": deleted_id
                }
            }
            return jsonify(response), 200
        return format_section_error('Section not found')
    except Exception as e:
        return format_section_error(str(e))
