"""
Financial Analyst App

A comprehensive financial analysis and trading monitoring application.
"""

from flask import Flask
from app.config import Config
import logging


def create_app(config_class=Config):
    """Application factory pattern for creating Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "fin-analyst-app"}
    
    return app
