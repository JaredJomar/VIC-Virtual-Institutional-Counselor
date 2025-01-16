# myApp/controllers/chatbot_controller.py
from myApp.models.chatbot_model import ChatbotService
from sentence_transformers import SentenceTransformer
from myApp.models.chatbot_model import ChatbotModel
from config.local_config import DATABASE_URL
from datetime import datetime

class ChatbotController:
    """
    Chatbot controller to handle logic between the view and the model.
    """

    def __init__(self):
        self.chatbot_service = ChatbotService()
        self.model = ChatbotModel(DATABASE_URL)
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')

    def process_question(self, question: str, user_id: str = "anonymous") -> dict:
        """
        Process a question and return the chatbot's response.
        
        Args:
            question (str): The question from the user.
            user_id (str): The user ID (default: anonymous).
        
        Returns:
            dict: A dictionary containing the chatbot's answer.
        """
        try:
            response = self.chatbot_service.get_answer_from_ollama(question, user_id)
            return response
        except Exception as e:
            raise Exception(f"Error processing question: {str(e)}")

    def process_question_with_logging(self, question: str, user_id: str = "anonymous") -> dict:
        print("\n=== Processing Question in Controller ===")
        try:
            # 1. Generate and store embedding
            print(f"Processing for user {user_id}: {question}")
            embedding = self.embedding_model.encode(question).tolist()
            
            # 2. Store question with embedding
            question_id = self.chatbot_service.insert_question(
                question=question,
                embedding=embedding,
                user_id=user_id
            )
            print(f"Stored question with ID: {question_id}")

            # 3. Get answer from Ollama
            response = self.chatbot_service.get_answer_from_ollama(question, user_id)
            print(f"Got response: {response['answer'][:100]}...")

            # 4. Log interaction in chat_logs
            success = self.chatbot_service.log_chat_interaction(
                user_id=user_id,
                question=question,
                answer=response['answer']
            )
            if not success:
                print("Warning: Failed to log chat interaction")

            return response
            
        except Exception as e:
            print(f"Error in controller: {e}")
            raise

    def store_knowledge(self, content: str, user_id: int) -> dict:
        try:
            # Generate embedding for content
            embedding = self.embedding_model.encode(content).tolist()
            
            # Store knowledge with embedding and user attribution
            result = self.chatbot_service.store_knowledge(
                content=content,
                embedding=embedding,
                user_id=user_id
            )
            return result
        except Exception as e:
            raise Exception(f"Failed to store knowledge: {str(e)}")

    def store_knowledge(self, content, embedding=None):
        """Store knowledge content and its embedding in the database."""
        try:
            if not content or not isinstance(content, str):
                raise ValueError("Content must be a non-empty string")

            # Generate embedding if not provided
            if embedding is None:
                embedding = self.embedding_model.encode(content).tolist()

            # Validate embedding format
            if not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
                raise ValueError("Embedding must be a list of numbers")

            # Insert into database via model
            return self.model.insert_knowledge(content, embedding)
        except Exception as e:
            raise RuntimeError(f"Failed to store knowledge: {str(e)}")
