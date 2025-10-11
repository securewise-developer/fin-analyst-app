#!/usr/bin/env python3
"""
Development server runner for Financial Analyst App.

This script starts the Flask development server with appropriate configuration.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.config import get_config


def main():
    """Run the development server."""
    # Set development environment
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # Get configuration
    config = get_config('development')
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("⚠️  Configuration Issues:")
        for error in errors:
            print(f"   - {error}")
        print()
    
    # Create and run app
    app = create_app(config)
    
    print("🚀 Starting Financial Analyst App...")
    print(f"   - Environment: development")
    print(f"   - Debug Mode: {config.DEBUG}")
    print(f"   - Data Provider: {'FMP' if config.have_fmp else 'Yahoo Finance'}")
    print(f"   - Slack: {'✅ Configured' if config.have_slack else '❌ Not configured'}")
    print(f"   - Server: http://localhost:8080")
    print()
    print("📡 Available Endpoints:")
    print("   - GET  /health              - Health check")
    print("   - GET  /api/v1/status       - Application status")
    print("   - POST /api/v1/analyze      - Run financial analysis")
    print()
    print("💡 Example analysis request:")
    print('   curl -X POST http://localhost:8080/api/v1/analyze \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"symbols": ["AAPL", "MSFT"], "detailed": true}\'')
    print()
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=config.DEBUG,
        use_reloader=True,
        use_debugger=config.DEBUG
    )


if __name__ == "__main__":
    main()
