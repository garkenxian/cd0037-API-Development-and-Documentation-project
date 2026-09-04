"""
Flask Application Factory and Setup
Implements application initialization with blueprint-based routing
"""

from flask import Flask, jsonify
from flask_cors import CORS

from data_access import setup_db, db
from controllers import users_bp, categories_bp, questions_bp, games_bp


def create_app(test_config=None):
    """
    Create and configure the Flask application
    
    Args:
        test_config: Optional test configuration dictionary
        
    Returns:
        Configured Flask application with all blueprints registered
    """
    # Create and configure the app
    app = Flask(__name__)

    # Setup database
    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    # Setup CORS - Allow requests from all origins
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Create database tables
    with app.app_context():
        db.create_all()

    # Register response middleware
    @app.after_request
    def after_request(response):
        """Set CORS headers on all responses"""
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # Register blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(games_bp)
    # Register error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({"error": "Bad Request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors"""
        return jsonify({"error": "Unprocessable Entity"}), 422

    @app.errorhandler(501)
    def not_implemented(error):
        """Handle 501 Not Implemented errors"""
        return jsonify({"error": "Not Implemented"}), 501

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        return jsonify({"error": "Internal Server Error"}), 500

    return app

