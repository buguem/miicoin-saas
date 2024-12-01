from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    name = db.Column(db.String(100))
    google_id = db.Column(db.String(100), unique=True)
    profile_pic = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relations
    api_keys = db.relationship('ApiKey', backref='user', lazy=True)
    trading_signals = db.relationship('TradingSignal', backref='user', lazy=True)
    
    def set_password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False
    
    @staticmethod
    def get_or_create_google_user(google_data):
        user = User.query.filter_by(google_id=google_data['sub']).first()
        if not user:
            user = User.query.filter_by(email=google_data['email']).first()
            if not user:
                user = User(
                    email=google_data['email'],
                    name=google_data['name'],
                    google_id=google_data['sub'],
                    profile_pic=google_data.get('picture')
                )
                db.session.add(user)
            else:
                user.google_id = google_data['sub']
                user.name = google_data['name']
                user.profile_pic = google_data.get('picture')
            db.session.commit()
        return user

class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exchange = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(100), nullable=False)
    api_secret = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<ApiKey {self.exchange}>'

class TradingSignal(db.Model):
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    signal_type = db.Column(db.String(10), nullable=False)  # 'BUY' or 'SELL'
    entry_price = db.Column(db.Float, nullable=False)
    target_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    timeframe = db.Column(db.String(10))  # e.g., '1h', '4h', '1d'
    status = db.Column(db.String(20), default='pending')  # pending, executed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<TradingSignal {self.symbol} {self.signal_type}>'

# Modèle pour suivre les performances des signaux
class SignalPerformance(db.Model):
    __tablename__ = 'signal_performances'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.Integer, db.ForeignKey('trading_signals.id'), nullable=False)
    exit_price = db.Column(db.Float)
    profit_loss = db.Column(db.Float)  # en pourcentage
    exit_reason = db.Column(db.String(50))  # 'target_hit', 'stop_loss', 'manual'
    closed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SignalPerformance {self.signal_id} P/L: {self.profit_loss}%>'
