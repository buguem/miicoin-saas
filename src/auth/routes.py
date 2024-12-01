from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from src.models import db, User
from src.utils.errors import ValidationError, AuthenticationError
from src.utils.logger import get_logger
from werkzeug.security import generate_password_hash

logger = get_logger()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Route pour l'inscription des utilisateurs"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not all(k in data for k in ['email', 'password', 'name']):
            raise ValidationError("Email, mot de passe et nom sont requis")
            
        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=data['email']).first():
            raise ValidationError("Cet email est déjà utilisé")
            
        # Créer le nouvel utilisateur
        user = User(
            email=data['email'],
            name=data['name']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Nouvel utilisateur créé: {user.email}")
        return jsonify({
            'status': 'success',
            'message': 'Inscription réussie',
            'user_id': user.id
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Erreur de validation lors de l'inscription: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {str(e)}")
        db.session.rollback()
        raise

@auth_bp.route('/login', methods=['POST'])
def login():
    """Route pour la connexion des utilisateurs"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not all(k in data for k in ['email', 'password']):
            raise ValidationError("Email et mot de passe sont requis")
            
        # Rechercher l'utilisateur
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            raise AuthenticationError("Email ou mot de passe incorrect")
            
        # Connecter l'utilisateur
        login_user(user)
        user.last_login = db.func.now()
        db.session.commit()
        
        logger.info(f"Connexion réussie pour: {user.email}")
        return jsonify({
            'status': 'success',
            'message': 'Connexion réussie',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        })
        
    except (ValidationError, AuthenticationError) as e:
        logger.warning(f"Erreur lors de la connexion: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {str(e)}")
        raise

@auth_bp.route('/logout')
@login_required
def logout():
    """Route pour la déconnexion"""
    try:
        user_email = current_user.email
        logout_user()
        logger.info(f"Déconnexion réussie pour: {user_email}")
        return jsonify({
            'status': 'success',
            'message': 'Déconnexion réussie'
        })
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {str(e)}")
        raise

@auth_bp.route('/profile')
@login_required
def profile():
    """Route pour accéder au profil utilisateur"""
    try:
        return jsonify({
            'status': 'success',
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'profile_pic': current_user.profile_pic,
                'created_at': current_user.created_at,
                'last_login': current_user.last_login
            }
        })
    except Exception as e:
        logger.error(f"Erreur lors de l'accès au profil: {str(e)}")
        raise

@auth_bp.route('/profile/update', methods=['PUT'])
@login_required
def update_profile():
    """Route pour mettre à jour le profil utilisateur"""
    try:
        data = request.get_json()
        
        if 'name' in data:
            current_user.name = data['name']
        if 'password' in data:
            current_user.set_password(data['password'])
            
        db.session.commit()
        logger.info(f"Profil mis à jour pour: {current_user.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Profil mis à jour avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du profil: {str(e)}")
        db.session.rollback()
        raise
