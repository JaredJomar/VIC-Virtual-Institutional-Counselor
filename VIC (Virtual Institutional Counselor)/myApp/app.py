from myApp.views.class_views import class_blueprint  # Class entity blueprint
from myApp.views.requisite_views import requisite_blueprint  # Requisite entity blueprint
from myApp.views.section_views import section_blueprint  # Section entity blueprint
from myApp.views.meeting_views import meeting_blueprint  # Meeting entity blueprint
from myApp.views.room_views import room_blueprint  # Room entity blueprint
from myApp.views.localStatistics_views import statistics_bp  # Local statistics blueprint
from myApp.views.syllabus_views import syllabus_blueprint  # Local syllabuses blueprint
from myApp.views.globalStatistics_views import global_statistics_bp  # Global statistics blueprint
from myApp.views.chatbot_views import chatbot_blueprint  # Chatbot blueprint
from myApp.views.auth_views import auth_blueprint  # Add this import
from myApp.extensions import get_db_connection  # Import the database connection function
from myApp.chatbot import chat
from flask import Flask, jsonify
import os


def ask_database_choice():
    """
    Prompt the user to select the database to use.

    Returns:
        str: The user's choice as a string ("1" for local, "2" for Heroku).
    """
    # Commenting out the interactive input for Heroku deployment
    # print("Select the database to use:")
    # print("1. Local database (development)")
    # print("2. Heroku database (production)")
    # choice = input("Enter the number (1 or 2): ").strip()
    # return choice

    # Automatically choose Heroku database in Heroku environment
    if os.getenv('HEROKU_ENV'):
        return '2'
    else:
        return '1'


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    if os.getenv("DATABASE_CHOICE") is None:
        choice = ask_database_choice()
        os.environ["DATABASE_CHOICE"] = choice
    else:
        choice = os.getenv("DATABASE_CHOICE")

    # Set environment and load config
    if choice == "1":
        os.environ["FLASK_ENV"] = "development"
        from config.local_config import LocalConfig
        config = LocalConfig()
    else:
        os.environ["FLASK_ENV"] = "production"
        from config.heroku_config import DatabaseConfig
        config = DatabaseConfig()

    # Set up database configuration
    db_url = config.get_db_url()
    if not db_url:
        raise ValueError("Database URL is not properly configured")

    # Store configuration in app config
    app.config["DATABASE_URL"] = db_url
    app.config["DB_CONNECTION"] = config.get_db_connection()
    
    # Make DATABASE_URL available globally
    os.environ["DATABASE_URL"] = db_url
    
    print(f"Using the {'local' if choice == '1' else 'Heroku'} database.")

    # Register blueprints
    app.register_blueprint(class_blueprint, url_prefix='/no-pensamos-repetir-npr/')  # Register the class blueprint
    app.register_blueprint(requisite_blueprint, url_prefix='/no-pensamos-repetir-npr/')  # Register the requisite blueprint
    app.register_blueprint(section_blueprint, url_prefix='/no-pensamos-repetir-npr/')  # Register the section blueprint
    app.register_blueprint(meeting_blueprint, url_prefix='/no-pensamos-repetir-npr/')  # Register the meeting blueprint
    app.register_blueprint(room_blueprint, url_prefix='/no-pensamos-repetir-npr/')  # Register the room blueprint
    app.register_blueprint(statistics_bp, url_prefix='/no-pensamos-repetir-npr/')  # Register the local statistics blueprint
    app.register_blueprint(global_statistics_bp, url_prefix='/no-pensamos-repetir-npr/')  # Register the global statistics blueprint
    app.register_blueprint(syllabus_blueprint, url_prefix='/no-pensamos-repetir-npr/')  # Register the syllabus blueprint
    app.register_blueprint(chatbot_blueprint, url_prefix='/no-pensamos-repetir-npr/')  # Register the chatbot blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/no-pensamos-repetir-npr/auth')  # Add this line

    # Configure port binding for Heroku
    port = int(os.getenv("PORT", 5000))
    if os.getenv('HEROKU_ENV'):
        os.environ['BIND'] = f'0.0.0.0:{port}'

    # Basic test route
    @app.route("/")
    def index():
        """
        Basic test route to check if the app is running.

        Returns:
            Response: JSON response with a welcome message and the current environment.
        """
        env = os.getenv("FLASK_ENV", "development")
        return jsonify({
            "message": "Welcome to the App API!",
            "environment": env
        })

    return app

# Application instance for gunicorn
app = create_app()

if __name__ == "__main__":
    is_production = os.getenv("FLASK_ENV") == "production"
    port = int(os.getenv("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False if is_production else True
    )
