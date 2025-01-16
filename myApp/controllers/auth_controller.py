# myApp/controllers/auth_controller.py
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from myApp.models.auth_model import AuthModel
from flask import request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

class AuthController:
    def __init__(self):
        """Initialize AuthController with model and JWT configuration."""
        self.auth_model = AuthModel()
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')  # Use environment variable
        self.jwt_expiration = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify if a password matches its hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    def _generate_jwt_token(self, user_id: int, username: str) -> str:
        """Generate a JWT token for authenticated users."""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=self.jwt_expiration)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def register_user(self, username: str, password: str) -> dict:
        """
        Register a new user with hashed password.
        
        Args:
            username: The desired username
            password: The plain text password
            
        Returns:
            dict: Success message with username
            
        Raises:
            ValueError: If username already exists
            Exception: For other registration errors
        """
        try:
            # Hash password before storing
            password_hash = self._hash_password(password)
            
            # Attempt to register user
            if self.auth_model.register_user(username, password_hash):
                return {
                    'message': f'User {username} registered successfully',
                    'username': username
                }
        except ValueError as ve:
            raise ValueError(f"Registration failed: {str(ve)}")
        except Exception as e:
            raise Exception(f"Registration error: {str(e)}")

    def authenticate_user(self, username: str, password: str) -> dict:
        """
        Authenticate user and generate JWT token.
        
        Args:
            username: The username to authenticate
            password: The password to verify
            
        Returns:
            dict: User info and JWT token if successful
            
        Raises:
            ValueError: If credentials are invalid
            Exception: For other authentication errors
        """
        try:
            # Get user from database
            user = self.auth_model.get_user_by_username(username)
            if not user:
                raise ValueError("Invalid username or password")

            # Verify password
            if not self._verify_password(password, user['password_hash']):
                raise ValueError("Invalid username or password")

            # Generate token
            token = self._generate_jwt_token(user['id'], user['username'])
            
            return {
                'message': 'Authentication successful',
                'token': token,
                'username': username
            }

        except ValueError as ve:
            raise ValueError(str(ve))
        except Exception as e:
            raise Exception(f"Authentication error: {str(e)}")

    def validate_token(self, token=None):
        """
        Validate JWT token from Authorization header or direct token.
        
        Args:
            token: Optional token string for direct validation
            
        Returns:
            dict: Decoded token payload containing user_id and username
            
        Raises:
            ValueError: If token is invalid or missing
        """
        if token is None:
            # Check for Authorization header if no token provided
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                raise ValueError('Authorization header is missing')
                
            # Check Bearer token format
            parts = auth_header.split()
            if parts[0].lower() != 'bearer' or len(parts) != 2:
                raise ValueError('Invalid Authorization header format. Use: Bearer <token>')
                
            token = parts[1]
        
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256']
            )
            return payload
            
        except ExpiredSignatureError:
            raise ValueError('Token has expired')
        except InvalidTokenError as e:
            raise ValueError(f'Invalid token: {str(e)}')
