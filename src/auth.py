from flask import Blueprint, request, jsonify, redirect, url_for, flash, current_app, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from src.models import db, User
from src.utils.logger import get_logger
from oauthlib.oauth2 import WebApplicationClient
import requests

logger = get_logger()
auth_bp = Blueprint('auth', __name__)

def init_auth(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validation des données
    if not all(k in data for k in ['email', 'username', 'password']):
        return jsonify({'error': 'Données manquantes'}), 400
    
    # Vérification si l'utilisateur existe déjà
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email déjà utilisé'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 400
    
    # Création du nouvel utilisateur
    user = User(
        email=data['email'],
        username=data['username']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        logger.info(f"Nouvel utilisateur créé: {user.email}")
        
        # Création du token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Inscription réussie',
            'access_token': access_token
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de l\'inscription'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Données manquantes'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        logger.info(f"Connexion réussie: {user.email}")
        
        return jsonify({
            'message': 'Connexion réussie',
            'access_token': access_token
        }), 200
    
    return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Déconnexion réussie'}), 200

@auth_bp.route('/profile')
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return jsonify({
        'email': user.email,
        'username': user.username,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    }), 200

oauth_client = None

def get_google_provider_cfg():
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

@auth_bp.record_once
def on_load(state):
    global oauth_client
    oauth_client = WebApplicationClient(state.app.config['GOOGLE_CLIENT_ID'])

@auth_bp.route('/login/google')
def google_login():
    # Configuration OAuth 2.0 Google
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Générer l'URL de redirection Google
    request_uri = oauth_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route('/login/google/callback')
def google_callback():
    # Récupérer le code d'autorisation Google
    code = request.args.get("code")
    
    # Récupérer les endpoints Google
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Préparer et envoyer la requête pour échanger le code contre un token
    token_url, headers, body = oauth_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    )

    # Analyser la réponse du token
    oauth_client.parse_request_body_response(token_response.text)
    
    # Récupérer les informations de profil de l'utilisateur
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = oauth_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers)
    
    if userinfo_response.json().get("email_verified"):
        google_data = userinfo_response.json()
        user = User.get_or_create_google_user(google_data)
        
        # Connexion de l'utilisateur
        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    else:
        flash("L'email Google n'est pas vérifié.", "danger")
        return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
            
        flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
