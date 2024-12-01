import os
from datetime import timedelta

class Config:
    # Configuration de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/miicoin_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configuration Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    
    # Configuration du logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/miicoin.log'
    
    # Configuration des clés API
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'encryption-key-change-in-production'
    
    # Configuration des échanges crypto supportés
    SUPPORTED_EXCHANGES = [
        'binance',
        'ftx',
        'kraken',
        'coinbase'
    ]
    
    # Configuration des paires de trading supportées
    SUPPORTED_PAIRS = [
        'BTC/USDT',
        'ETH/USDT',
        'BNB/USDT',
        'SOL/USDT',
        'ADA/USDT'
    ]
    
    # Limites de l'API
    API_RATE_LIMIT = 100  # requêtes par minute
    API_RATE_LIMIT_WINDOW = 60  # secondes
    
    # Configuration des websockets
    WEBSOCKET_PING_INTERVAL = 30  # secondes
    WEBSOCKET_PING_TIMEOUT = 10  # secondes
    
    # Configuration des signaux de trading
    SIGNAL_VALIDITY_DURATION = 300  # secondes (5 minutes)
    MIN_SIGNAL_INTERVAL = 60  # secondes entre les signaux
    
    # Configuration de la gestion des risques
    MAX_POSITION_SIZE = 0.1  # 10% du portefeuille maximum par position
    STOP_LOSS_DEFAULT = 0.02  # 2% de stop loss par défaut
    TAKE_PROFIT_DEFAULT = 0.06  # 6% de take profit par défaut
    MAX_OPEN_POSITIONS = 5  # nombre maximum de positions ouvertes
    
    @staticmethod
    def init_app(app):
        """Initialisation de l'application avec la configuration"""
        # Création du dossier de logs si nécessaire
        os.makedirs('logs', exist_ok=True)
        
        # Configuration du logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )
        
        file_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('MiiCoin startup')
