# Dependencies
from flask import request, jsonify, Blueprint
from flask_migrate import Migrate
import json
from token_verify import google_token_required
import logging
from extensions import db

# Import your models
from models import *


main = Blueprint('main', __name__)

# Create a new user
@main.route('/users', methods=['POST'])
@google_token_required
def create_user(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /users called by: {verified_email}")

    data = request.get_json()
    username = data.get('name')
    email = data.get('email')

    # Check if the user already exists
    user = Users.query.filter_by(email=email).first()
    if user:
        return jsonify({'user': {'username': user.username, 'email': user.email, 'admin': user.isadmin}}), 200

    try:
        # Check if the user is an admin
        admin = AdminEmails.query.filter_by(email=email).first()

        # Create a new user
        if admin:
            new_user = Users(username=username, email=email, isadmin=True)
        else:
            new_user = Users(username=username, email=email, isadmin=False)
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'user': {'username': new_user.username, 'email': new_user.email, 'admin': new_user.isadmin}}), 201
    
    except Exception as e:
        db.session.rollback()  # Rollback the session to prevent the user from being added
        return jsonify({'error': str(e)}), 500

# Add admin email
@main.route('/add_admin', methods=['POST'])
@google_token_required
def add_admin(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /add_admin called by: {verified_email}")

    print(request.data)
    email = request.data.decode('utf-8')

    user = Users.query.filter_by(email=verified_email).first()

    # Check if the user exists
    if user:
        # Check if the user is an admin
        if user.isadmin:
            return jsonify({'error': 'User is not an admin'}), 403
        
    # Check if the email already exists in the AdminEmails table
    existing_admin = AdminEmails.query.filter_by(email=email).first()
    if existing_admin:
        return jsonify({'error': 'Email already exists in admin list'}), 400

    # Create a new admin email
    new_admin = AdminEmails(email=email)
    db.session.add(new_admin)
    db.session.commit()

    

    return jsonify({'admin_email': new_admin.email}), 201