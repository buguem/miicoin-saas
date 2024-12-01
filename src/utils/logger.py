import os
import logging
from logging.handlers import RotatingFileHandler
from flask import current_app

def setup_logger(app):
    """Set up logger for the application."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Set up file handler
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Get the logger
    logger = logging.getLogger('miicoin')
    logger.setLevel(logging.DEBUG)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def get_logger():
    """Get the logger instance."""
    return logging.getLogger('miicoin')
