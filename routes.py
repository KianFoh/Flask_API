# routes.py
import re
from flask import request, jsonify, Blueprint
from flask_migrate import Migrate
import logging
from extensions import db
from socketio_events import admin_status_update
from token_verify import google_token_required
from validations import Valid

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

    # Validate email format and domain
    response = Valid.email_format_and_domain(email)
    if response:
        return response

    # Validate if the user already exists
    response = Valid.user_exists(email)
    if response:
        return response
    
    try:
        # Check if the user is an admin
        admin = AdminEmails.query.filter_by(email=email).first()
        isadmin = bool(admin)

        # Create a new user
        return Valid.create_new_user(username, email, isadmin)
    
    except Exception as e:
        db.session.rollback()  # Rollback the session to prevent the user from being added
        return jsonify({'error': str(e)}), 500
    
# Get user info
@main.route('/user_info', methods=['GET'])
@google_token_required
def user_info(verified_email):
    email = request.args.get('email')

    if email is None:
        return jsonify({'error': 'Email is required'}), 400
    if email != verified_email:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Log the API call with the verified email
    logging.info(f"API /user_info called by: {verified_email}")
    
    # Get the user info
    user = Users.query.filter_by(email=verified_email).first()

    if user:
        return jsonify({'user': {'username': user.username, 'email': user.email, 'admin': user.isadmin}}), 200
    
    return jsonify({'error': 'User not found'}), 404

# Add admin email
@main.route('/add_admin', methods=['POST'])
@google_token_required
def add_admin(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /add_admin called by: {verified_email}")

    email = request.data.decode('utf-8')

    # Validate if the email is missing
    response = Valid.missing_email(email)
    if response:
        return response

    # Validate if the user is an admin
    response = Valid.user_is_admin(verified_email)
    if response:
        return response

    # Validate if the email already exists in the AdminEmails table
    response = Valid.admin_email_exists(email)
    if response:
        return response

    # Validate email format and domain
    response = Valid.email_format_and_domain(email)
    if response:
        return response

    # Create a new admin email
    new_admin = Valid.create_new_admin_email(email)

    # Update the user to be an admin
    user = Valid.update_user_to_admin(email)
    if user:
        admin_status_update(user)

    return jsonify({'admin_email': new_admin.email}), 201

# Remove admin email
@main.route('/remove_admin', methods=['DELETE'])
@google_token_required
def remove_admin(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /remove_admin called by: {verified_email}")

    email = request.args.get('email')

    # Validate if the email is missing
    response = Valid.missing_email(email)
    if response:
        return response

    # Validate if the user is an admin
    response = Valid.user_is_admin(verified_email)
    if response:
        return response

    # Check if the admin email exists
    admin_email = Valid.check_admin_email_exists(email)
    if not admin_email:
        return jsonify({'error': 'Admin email not found'}), 404

    # Remove the admin email
    db.session.delete(admin_email)
    db.session.commit()

    # Check if user with admin email exists
    user = Users.query.filter_by(email=email).first()
    if user:
        user.isadmin = False
        db.session.commit()
        admin_status_update(user)

    return jsonify({'message': 'Admin email removed successfully'}), 200

# Add merchant
@main.route('/add_merchant', methods=['POST'])
@google_token_required
def add_merchant(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /add_merchant called by: {verified_email}")

    data = request.get_json()
    image_url = data.get('image_url')
    merchant_name = data.get('name')
    merchant_type = data.get('type')
    merchant_address = data.get('address')
    discount = data.get('discount')
    extra_info = data.get('extra_info')
    terms_conditions = data.get('terms_conditions')

    # Validate if the user is an admin
    response = Valid.user_is_admin(verified_email)
    if response:
        return response

    # Create a new merchant
    new_merchant = Merchants(
        image_url=image_url,
        name=merchant_name,
        type=merchant_type,
        address=merchant_address,
        discount=discount,
        extra_info=extra_info,
        terms_conditions=terms_conditions
    )
    db.session.add(new_merchant)
    db.session.commit()

    return jsonify({'merchant': {
        'image_url': new_merchant.image_url,
        'name': new_merchant.name,
        'type': new_merchant.type,
        'address': new_merchant.address,
        'discount': new_merchant.discount,
        'extra_info': new_merchant.extra_info,
        'terms_conditions': new_merchant.terms_conditions
    }}), 201

