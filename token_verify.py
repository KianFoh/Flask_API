from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
from flask import request, jsonify
import json


# Load CLIENT_ID
with open('config.json') as config_file:
    config = json.load(config_file)
    
CLIENT_ID = config['google']['clientid']

def verify_google_token(token):
    try:
        # Verify the token and return the email if successful
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        # Get the user's email.
        email = idinfo['email']
        return email
    
    # Invalid token
    except ValueError:        
        return None

def google_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if token is None:
            return jsonify({'error': 'Token is missing'}), 401

        verified_email = verify_google_token(token)
        if not verified_email:
            return jsonify({'error': 'Invalid token'}), 401

        # Pass the verified email to the route function
        return f(verified_email, *args, **kwargs)
    return decorated_function
