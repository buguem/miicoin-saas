from flask import Flask, render_template, jsonify, request
from src.api.routes import api_bp
from src.auth.routes import auth_bp
from src.models import db
from src.utils.logger import setup_logger
from src.utils.errors import setup_error_handlers, MiiCoinError, ResourceNotFoundError
from src.auth import init_auth
from config import config
import os

def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Set up logging
    logger = setup_logger(app)
    
    # Initialize authentication
    init_auth(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Set up error handlers
    setup_error_handlers(app)
    
    # Register HTML error handlers for non-API routes
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            raise ResourceNotFoundError("API endpoint not found")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            raise MiiCoinError("Internal server error")
        return render_template('errors/500.html'), 500
    
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=True)
