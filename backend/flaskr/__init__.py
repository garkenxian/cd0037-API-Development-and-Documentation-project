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

    # Setup CORS with configurable origins (default to all for dev, restrict for production)
    cors_origins = app.config.get('CORS_ORIGINS', '*')
    CORS(app, resources={r"/*": {"origins": cors_origins}})
    
    # Database tables are created in setup_db()

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
    def create_error_response(status_code, message):
        """
        Create standardized error response matching API specification.
        
        Schema: { "error": <code>, "message": "<message>", "success": false }
        
        Args:
            status_code: HTTP status code (int)
            message: Human-readable error message (str)
            
        Returns:
            Tuple of (jsonify dict, status_code)
        """
        error_messages = {
            400: "Bad Request",
            404: "Resource not found",
            409: "Conflict",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
            501: "Not Implemented"
        }
        
        if not message:
            message = error_messages.get(status_code, "An error occurred")
        
        return jsonify({
            "error": status_code,
            "message": message,
            "success": False
        }), status_code

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        message = "Bad Request"
        if error.description and error.description != "The browser (or proxy) sent a request that this server could not understand.":
            message = str(error.description)
        return create_error_response(400, message)

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        message = "Resource not found"
        if error.description and error.description != "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.":
            message = str(error.description)
        return create_error_response(404, message)

    @app.errorhandler(409)
    def conflict(error):
        """Handle 409 Conflict errors"""
        message = "Conflict"
        if error.description and error.description != "Conflict":
            message = str(error.description)
        return create_error_response(409, message)

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors"""
        message = "Unprocessable Entity"
        if error.description and error.description != "The request was well-formed but was unable to be followed due to semantic errors.":
            message = str(error.description)
        return create_error_response(422, message)

    @app.errorhandler(501)
    def not_implemented(error):
        """Handle 501 Not Implemented errors"""
        message = "Not Implemented"
        if error.description and error.description != "The method is not allowed for the requested URL.":
            message = str(error.description)
        return create_error_response(501, message)

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        message = "Internal Server Error"
        if error.description and error.description != "The server encountered an internal error and was unable to complete your request.":
            message = str(error.description)
        return create_error_response(500, message)

    return app

