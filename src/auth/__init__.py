from flask_login import LoginManager
from src.models import User
from src.utils.logger import get_logger

logger = get_logger()

def init_auth(app):
    """Initialise l'authentification pour l'application"""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Charge l'utilisateur depuis la base de données"""
        return User.query.get(int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        """Gère les accès non autorisés"""
        logger.warning("Tentative d'accès non autorisé")
        return {
            'status': 'error',
            'message': 'Authentification requise'
        }, 401
    
    return login_manager
