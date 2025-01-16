# myApp/views/chatbot_views.py
from flask import Blueprint, request, jsonify
from myApp.controllers.chatbot_controller import ChatbotController
from myApp.controllers.auth_controller import AuthController

# Create blueprint for chatbot routes
chatbot_blueprint = Blueprint('chatbot', __name__)

# Initialize chatbot controller
chatbot_controller = ChatbotController()
auth_controller = AuthController()

@chatbot_blueprint.route('/chatbot', methods=['POST'])
def chat():
    print("\n=== Chatbot API Request ===")
    try:
        data = request.get_json()
        print(f"Received request data: {data}")
        
        if not data or 'question' not in data:
            return jsonify({'status': 'error', 'message': 'Missing question'}), 400

        user_id = data.get('user_id', 'anonymous')
        question = data['question']
        
        print(f"\nProcessing question from {user_id}:\n{question}")
        
        # Process question and verify storage
        try:
            response = chatbot_controller.process_question_with_logging(question, user_id)
            print(f"Generated response: {response}")
            
            # Verify data was stored
            if 'error' in response:
                print(f"Error in response: {response['error']}")
                return jsonify({'status': 'error', 'message': response['error']}), 500
                
            return jsonify({
                'status': 'success',
                'data': response,
                'user_id': user_id,
                'question_stored': True
            }), 200

        except Exception as e:
            print(f"Error in controller: {str(e)}")
            raise

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@chatbot_blueprint.route('/knowledge', methods=['POST'])
def store_knowledge():
    # Validate auth token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid token'}), 401

    token = auth_header.split(' ')[1]
    try:
        # Validate token and get user info
        user_info = auth_controller.validate_token(token)
        
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400

        # Store knowledge with user attribution
        result = chatbot_controller.store_knowledge(
            content=data['content'],
            user_id=user_info['user_id']
        )
        return jsonify(result), 201

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
