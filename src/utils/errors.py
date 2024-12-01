from flask import jsonify
from functools import wraps
from src.utils.logger import get_logger

logger = get_logger()

class MiiCoinError(Exception):
    """Base exception class for MiiCoin application"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class ValidationError(MiiCoinError):
    """Raised when input validation fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthenticationError(MiiCoinError):
    """Raised when authentication fails"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(MiiCoinError):
    """Raised when user doesn't have required permissions"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=403, payload=payload)

class ResourceNotFoundError(MiiCoinError):
    """Raised when requested resource is not found"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=404, payload=payload)

class APIError(MiiCoinError):
    """Raised when external API calls fail"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message, status_code=status_code, payload=payload)

def handle_error(error):
    """Generic error handler for all exceptions"""
    logger.error(f"Error: {str(error)}", exc_info=True)
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def setup_error_handlers(app):
    """Register error handlers with Flask app"""
    app.register_error_handler(MiiCoinError, handle_error)
    app.register_error_handler(404, lambda e: handle_error(ResourceNotFoundError("Resource not found")))
    app.register_error_handler(500, lambda e: handle_error(MiiCoinError("Internal server error")))

def error_handler(f):
    """Decorator for route error handling"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if isinstance(e, MiiCoinError):
                raise e
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}", exc_info=True)
            raise MiiCoinError(f"An unexpected error occurred: {str(e)}")
    return wrapped
