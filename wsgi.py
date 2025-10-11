"""
WSGI entry point for production deployment.

This module provides the WSGI application object for production servers like Gunicorn.
"""

import os
from app import create_app
from app.config import get_config

# Get environment-specific configuration
env = os.getenv('FLASK_ENV', 'production')
config = get_config(env)

# Create application instance
application = create_app(config)

if __name__ == "__main__":
    # For development only - use scripts/run_server.py instead
    application.run(debug=config.DEBUG, port=8080)
