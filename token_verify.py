from google.oauth2 import id_token
from google.auth.transport import requests as googlerequests
from functools import wraps
from flask import request, jsonify
import logging
import time
from flask_socketio import disconnect
from utils import CONFIG
import cachecontrol
import requests as req

# Load CLIENT_ID
CLIENT_ID = CONFIG['google']['clientid']

# Create a cached session
gsession  = req.session()
gcached_session  = cachecontrol.CacheControl(gsession)
grequest  = googlerequests.Request(session=gcached_session)

def verify_google_token(token, retries=3, delay=2):
    for attempt in range(retries):
        try:
            # Verify the token using the cached session
            id_info = id_token.verify_oauth2_token(token, grequest, CLIENT_ID)

            # Return the email if the token is valid
            logging.info("Token is valid.")
            return id_info['email']
        
        except ValueError as e:
            # Log the error and number of attempts
            logging.error(f"Invalid token on attempt {attempt + 1}: {e}")

            # If the token is expired, return "expired"
            if "Token expired" in str(e):
                return "expired"
            
            # If the token is invalid, return "invalid"
            if "Invalid token" in str(e):
                return "invalid"
            
            # retry the token verification
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)

            # log the error if the token verification fails after multiple attempts
            else:
                logging.error("Token verification failed after multiple attempts.")
                return "invalid"
        except Exception as e:
            # Log any other exceptions and return "invalid"
            logging.error(f"Unexpected error during token verification: {e}")
            return "invalid"
            
def google_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')

            if auth_header is None or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Token is missing or invalid'}), 401

            token = auth_header.split(' ')[1]

            verified_email = verify_google_token(token)
            if verified_email == "expired":
                return jsonify({'error': 'Token is expired'}), 401
            elif verified_email == "invalid":
                return jsonify({'error': 'Invalid token'}), 401

            # Pass the verified email to the route function
            return f(verified_email, *args, **kwargs)
        except Exception as e:
            logging.error(f"Unexpected error in token verification: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function

def socketio_token_required(token):

    # If the token is missing, disconnect the client
    if not token:
        disconnect()
        return
    
    verified_email = verify_google_token(token)
    
    # Pass the verified email to the socketio connection function
    return (verified_email)