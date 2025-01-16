# myApp/views/auth_views.py
from flask import Blueprint, request, jsonify
from myApp.controllers.auth_controller import AuthController

# Create blueprint for authentication routes
auth_blueprint = Blueprint('auth', __name__)
auth_controller = AuthController()

@auth_blueprint.route('/register', methods=['POST'])
def register():
    """Handle user registration"""
    try:
        data = request.get_json()
        
        # Validate input data
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'error': 'Username and password are required'
            }), 400
            
        username = data['username'].strip()
        password = data['password']
        
        # Validate username and password
        if not username or not password:
            return jsonify({
                'error': 'Username and password cannot be empty'
            }), 400
            
        # Attempt to register user
        result = auth_controller.register_user(username, password)
        return jsonify(result), 201
        
    except ValueError as ve:
        return jsonify({
            'error': str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    """Handle user authentication"""
    try:
        data = request.get_json()
        
        # Validate input data
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'error': 'Username and password are required'
            }), 400
            
        username = data['username'].strip()
        password = data['password']
        
        # Validate username and password
        if not username or not password:
            return jsonify({
                'error': 'Username and password cannot be empty'
            }), 400
            
        # Attempt to authenticate user
        result = auth_controller.authenticate_user(username, password)
        return jsonify(result), 200
        
    except ValueError as ve:
        return jsonify({
            'error': str(ve)
        }), 401
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@auth_blueprint.route('/protected', methods=['GET'])
def protected_route():
    """
    Protected route that requires valid JWT token.
    Returns user information if token is valid.
    """
    try:
        # Validate token and get payload
        payload = auth_controller.validate_token()
        
        return jsonify({
            'message': 'Access granted',
            'user': {
                'id': payload['user_id'],
                'username': payload['username']
            }
        }), 200
        
    except ValueError as ve:
        return jsonify({
            'error': 'Unauthorized',
            'message': str(ve)
        }), 401
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Error handlers
@auth_blueprint.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400

@auth_blueprint.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'message': str(error)
    }), 401

@auth_blueprint.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error)
    }), 500
