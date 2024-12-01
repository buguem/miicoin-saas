from flask import current_app, url_for
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
from src.utils.logger import get_logger

logger = get_logger()

def get_google_provider_cfg():
    """Récupère la configuration du fournisseur Google"""
    try:
        return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la configuration Google: {str(e)}")
        raise

def get_google_client():
    """Crée et retourne un client OAuth2 pour Google"""
    return WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

def get_google_auth_url():
    """Génère l'URL d'authentification Google"""
    try:
        client = get_google_client()
        google_provider_cfg = get_google_provider_cfg()
        
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=url_for('auth.google_callback', _external=True),
            scope=['openid', 'email', 'profile'],
        )
        
        return request_uri
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'URL d'authentification Google: {str(e)}")
        raise

def get_google_tokens(code):
    """Échange le code d'autorisation contre des tokens"""
    try:
        client = get_google_client()
        google_provider_cfg = get_google_provider_cfg()
        
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=code,
            redirect_url=url_for('auth.google_callback', _external=True),
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
        )
        
        return client.parse_request_body_response(json.dumps(token_response.json()))
    except Exception as e:
        logger.error(f"Erreur lors de l'échange des tokens Google: {str(e)}")
        raise

def get_google_user_info(tokens):
    """Récupère les informations de l'utilisateur Google"""
    try:
        google_provider_cfg = get_google_provider_cfg()
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        
        uri, headers, body = get_google_client().add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        if userinfo_response.json().get("email_verified"):
            return userinfo_response.json()
        else:
            logger.warning("L'email Google n'est pas vérifié")
            return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations utilisateur Google: {str(e)}")
        raise
