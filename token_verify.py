from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
from flask import request, jsonify
import json
import logging
import time

# Load CLIENT_ID
with open('config.json') as config_file:
    config = json.load(config_file)
    
CLIENT_ID = config['google']['clientid']

def verify_google_token(token, retries=3, delay=2, clock_skew_in_seconds=1):
    for attempt in range(retries):
        try:
            # Verify the token
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            # Check if the token is used too early
            current_time = int(time.time())
            if id_info['iat'] > current_time + clock_skew_in_seconds:
                raise ValueError(f"Token used too early, {id_info['iat']} > {current_time + clock_skew_in_seconds}")

            logging.info("Token is valid.")
            return id_info['email']
        except ValueError as e:
            # Invalid token
            logging.error(f"Invalid token on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error("Token verification failed after multiple attempts.")
                return None
            
def google_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header is None or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token is missing or invalid'}), 401

        token = auth_header.split(' ')[1]

        verified_email = verify_google_token(token)
        if not verified_email:
            return jsonify({'error': 'Invalid token'}), 401

        # Pass the verified email to the route function
        return f(verified_email, *args, **kwargs)
    return decorated_function
