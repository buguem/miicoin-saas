from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models import db, ApiKey, User
from src.utils.logger import get_logger
from cryptography.fernet import Fernet
import os

logger = get_logger()
api_keys_bp = Blueprint('api_keys', __name__)

# Initialisation du chiffrement des clés API
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

# Constants for validation
VALID_EXCHANGES = ['binance', 'kucoin', 'ftx']
API_KEY_MIN_LENGTH = 16
API_SECRET_MIN_LENGTH = 32

class ValidationError(Exception):
    pass

def encrypt_string(text):
    """Chiffre une chaîne de caractères"""
    return cipher_suite.encrypt(text.encode()).decode()

def decrypt_string(encrypted_text):
    """Déchiffre une chaîne de caractères"""
    return cipher_suite.decrypt(encrypted_text.encode()).decode()

def validate_api_credentials(exchange, api_key, api_secret):
    """Validate API credentials format and requirements"""
    if exchange not in VALID_EXCHANGES:
        raise ValidationError(f"Exchange non supporté. Exchanges valides: {', '.join(VALID_EXCHANGES)}")
    
    if len(api_key) < API_KEY_MIN_LENGTH:
        raise ValidationError(f"La clé API doit contenir au moins {API_KEY_MIN_LENGTH} caractères")
    
    if len(api_secret) < API_SECRET_MIN_LENGTH:
        raise ValidationError(f"Le secret API doit contenir au moins {API_SECRET_MIN_LENGTH} caractères")
    
    # Exchange-specific validations
    if exchange == 'binance':
        if not api_key.isalnum():
            raise ValidationError("La clé API Binance doit être alphanumérique")

@api_keys_bp.route('/api-keys', methods=['POST'])
@jwt_required()
def add_api_key():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['exchange', 'api_key', 'api_secret']
    if not all(k in data for k in required_fields):
        return jsonify({
            'error': 'Données manquantes',
            'details': f"Champs requis: {', '.join(required_fields)}"
        }), 400
    
    try:
        # Validate API credentials
        validate_api_credentials(
            data['exchange'],
            data['api_key'],
            data['api_secret']
        )
        
        # Check for existing API key for this exchange
        existing_key = ApiKey.query.filter_by(
            user_id=current_user_id,
            exchange=data['exchange']
        ).first()
        
        if existing_key:
            return jsonify({
                'error': 'Clé API existante',
                'details': f"Une clé API pour {data['exchange']} existe déjà"
            }), 409
        
        # Encrypt API credentials
        encrypted_key = encrypt_string(data['api_key'])
        encrypted_secret = encrypt_string(data['api_secret'])
        
        api_key = ApiKey(
            user_id=current_user_id,
            exchange=data['exchange'],
            api_key=encrypted_key,
            api_secret=encrypted_secret,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        logger.info(f"Nouvelle clé API ajoutée pour l'utilisateur {current_user_id} (exchange: {data['exchange']})")
        return jsonify({
            'message': 'Clé API ajoutée avec succès',
            'exchange': data['exchange']
        }), 201
    
    except ValidationError as e:
        logger.warning(f"Validation error for user {current_user_id}: {str(e)}")
        return jsonify({
            'error': 'Erreur de validation',
            'details': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de la clé API: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Erreur serveur',
            'details': 'Une erreur est survenue lors de l\'ajout de la clé API'
        }), 500

@api_keys_bp.route('/api-keys', methods=['GET'])
@jwt_required()
def get_api_keys():
    current_user_id = get_jwt_identity()
    api_keys = ApiKey.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([{
        'id': key.id,
        'exchange': key.exchange,
        'is_active': key.is_active,
        'created_at': key.created_at.isoformat(),
        'last_used': key.last_used.isoformat() if key.last_used else None
    } for key in api_keys]), 200

@api_keys_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@jwt_required()
def delete_api_key(key_id):
    current_user_id = get_jwt_identity()
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user_id).first()
    
    if not api_key:
        return jsonify({'error': 'Clé API non trouvée'}), 404
    
    try:
        db.session.delete(api_key)
        db.session.commit()
        logger.info(f"Clé API {key_id} supprimée pour l'utilisateur {current_user_id}")
        return jsonify({'message': 'Clé API supprimée avec succès'}), 200
    
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la clé API: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la suppression de la clé API'}), 500

@api_keys_bp.route('/api-keys/<int:key_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_api_key(key_id):
    current_user_id = get_jwt_identity()
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user_id).first()
    
    if not api_key:
        return jsonify({'error': 'Clé API non trouvée'}), 404
    
    try:
        api_key.is_active = not api_key.is_active
        db.session.commit()
        status = "activée" if api_key.is_active else "désactivée"
        logger.info(f"Clé API {key_id} {status} pour l'utilisateur {current_user_id}")
        return jsonify({'message': f'Clé API {status} avec succès'}), 200
    
    except Exception as e:
        logger.error(f"Erreur lors de la modification de la clé API: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la modification de la clé API'}), 500
