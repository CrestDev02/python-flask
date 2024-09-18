"""
Main entry point for the Flask application.

This script initializes the Flask application by calling `create_app` from the `app` module and runs it.
It also sets up environment-specific configurations and ensures that the application runs with proper settings.
"""

import os
import logging
from app import create_app

# Configure logging for the application startup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main entry point to start the Flask application.

    Reads environment variables to configure the application and starts the Flask development server.
    """
    # Fetch the environment from environment variables or default to 'development'
    environment = os.environ.get('FLASK_ENV', 'development')
    logging.info(f'Starting application in {environment} mode')

    # Create a Flask application instance
    app = create_app()

    # Run the application
    try:
        app.run(host='0.0.0.0', debug=(environment != 'production'))
    except Exception as e:
        logging.error(f'Application encountered an error: {e}')
        raise

if __name__ == '__main__':
    main()
