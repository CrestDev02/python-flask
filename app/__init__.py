"""
Main application setup and initialization module.

This script configures and initializes the Flask application, setting up logging, extensions, and blueprints.
"""

import logging
import os
import sys
import traceback

import yaml
from logging.handlers import TimedRotatingFileHandler
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

# Configure base and media directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
os.makedirs(MEDIA_DIR, exist_ok=True)

# Load configuration from YAML file
def load_config():
    """
    Load configuration settings from a YAML file.
    :return: Dictionary with configuration settings.
    """
    config_file_path = os.path.join(BASE_DIR, 'config', 'config.yml')
    try:
        with open(config_file_path, 'r') as config_file:
            return yaml.safe_load(config_file)  # Use safe_load for security
    except Exception as e:
        logging.error(f'Error loading configuration file: {e}')
        raise

config_contents = load_config()

# Configure logging
def setup_logging():
    """
    Set up logging configuration with timed rotation for log files.
    """
    log_file_path = config_contents.get('LOG_FILE_PATH', 'app.log')  # Use config for log file path
    log_format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set default log level

    # Create log formatters
    formatter = logging.Formatter(log_format)

    # File handler for rotating logs daily
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when='midnight',
        interval=1,
        backupCount=7
    )
    file_handler.setFormatter(formatter)

    # Console handler (optional)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()


def create_app():
    """
    Create and configure the Flask application.
    :return: Configured Flask application instance.
    """
    try:
        application = Flask(__name__, instance_relative_config=True)
        application.config.from_mapping(config_contents)
        configure_app(application)
        initialize_extensions(application)
        register_blueprints(application)
        setup_swagger(application)

        return application
    except Exception as e:
        logger.error(f'Failed to create Flask app instance: {e}')
        raise


def initialize_extensions(application):
    """
    Initialize extensions.
    :param application:
    :return:
    """
    try:
        db.init_app(application)
        migrate = Migrate(app=application, db=db, compare_type=True)
        return db, migrate

    except Exception as e:
        logger.error(f'Failed to initialize extensions: {e}')
        raise


def register_blueprints(application):
    """
    Registers blueprints.
    :param application:
    :return: None
    """
    try:
        from app.views import v1_blueprints

        application.register_blueprint(v1_blueprints, url_prefix='/api/v1')
    except Exception as e:
        log_traceback('Error registering blueprints', e)
        raise


def setup_swagger(application):
    """
    Set up Swagger UI for API documentation.
    :param application: Flask application instance.
    """
    try:
        swagger_url = '/api-docs/'
        api_url = f'/static/api_docs/{config_contents.get("SWAGGER_FILE_NAME", "api_docs.yaml")}'
        swagger_config = {'app_name': 'My Flask Application'}
        swagger_blueprint = get_swaggerui_blueprint(
            base_url=swagger_url,
            api_url=api_url,
            config=swagger_config
        )
        swagger_blueprint.name = 'api-docs'
        application.register_blueprint(swagger_blueprint, url_prefix=swagger_url)
    except Exception as e:
        logger.error(f'Error setting up Swagger UI: {e}')
        raise


def configure_app(application):
    """
    Apply configuration settings to the Flask app from the provided data.
    :param application: Flask application instance.
    """
    try:
        for key, value in config_contents.items():
            application.config[key] = value
    except Exception as e:
        logger.error(f'Error configuring app: {e}')
        raise


def log_traceback(context, exception):
    """
    Log detailed traceback information for debugging purposes.
    :param context: Context or section where the error occurred.
    :param exception: Exception instance to extract traceback from.
    """
    tb = traceback.extract_tb(sys.exc_info()[2])
    error_message = f'{context}: {exception}\n'
    error_message += 'Traceback Details:\n'
    for file, line_no, func, text in tb:
        error_message += f'File "{file}", line {line_no}, in {func}\n'
        error_message += f'    {text}\n'
    logger.error(error_message)


app = Flask(__name__)
app.json.sort_keys = False
configure_app(application=app)
db = SQLAlchemy(app, session_options={'expire_on_commit': False})
migrate = Migrate(app=app, db=db, compare_type=True)