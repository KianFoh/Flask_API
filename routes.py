# routes.py
import re
from flask import request, jsonify, Blueprint
from flask_migrate import Migrate
import logging
from extensions import db
import socketio_events
from token_verify import google_token_required
from validations import Valid
import pandas as pd
from flask import send_file
from io import BytesIO

# Import your models
from models import *

main = Blueprint('main', __name__)

# Create a new user
@main.route('/user', methods=['POST'])
@google_token_required
def create_user(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /user POST called by: {verified_email}")

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
@main.route('/user', methods=['GET'])
@google_token_required
def user_info(verified_email):
    
    # Log the API call with the verified email
    logging.info(f"API /user GET called by: {verified_email}")

    email = request.args.get('email')

    if email is None:
        return jsonify({'error': 'Email is required'}), 400
    if email != verified_email:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get the user info
    user = Users.query.filter_by(email=verified_email).first()

    if user:
        return jsonify({'user': {'username': user.username, 'email': user.email, 'admin': user.isadmin}}), 200
    
    return jsonify({'error': 'User not found'}), 404

# Add admin email
@main.route('/admin', methods=['POST'])
@google_token_required
def add_admin(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /admin POST called by: {verified_email}")

    email = request.data.decode('utf-8')

    # Validate if the email is missing
    response = Valid.missing_field(email, 'Email')
    if response:
        return response

    # Validate if the user is an admin
    response = Valid.user_is_admin(verified_email)
    if response:
        return response

    # Validate if the email already exists in the AdminEmails table
    admin_email = Valid.check_admin_email_exists(email)
    if admin_email:
        return jsonify({'error': 'Email is already in the database'}), 400

    # Validate email format and domain
    response = Valid.email_format_and_domain(email)
    if response:
        return response

    # Create a new admin email
    new_admin = Valid.create_new_admin_email(email)

    # Update the user to be an admin
    user = Valid.update_user_to_admin(email)
    if user:
        socketio_events.admin_status_update(user)

    return jsonify({'admin_email': new_admin.email}), 201

# Remove admin email
@main.route('/admin', methods=['DELETE'])
@google_token_required
def remove_admin(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /admin DELETE called by: {verified_email}")

    email = request.args.get('email')

    # Validate if the email is missing
    response = Valid.missing_field(email, 'Email')
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
        socketio_events.admin_status_update(user)

    return jsonify({'message': 'Admin email removed successfully'}), 200

# Add admin email
@main.route('/add_request_merchant', methods=['POST'])
@google_token_required
def add_request_merchant(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /request_merchant POST called by: {verified_email}")

    data = request.get_json()
    name = data.get('name')
    type = data.get('type')
    contact = data.get('contact')

    # Validate if name is missing
    response = Valid.missing_field(name, 'Name')
    if response:
        return response

    # Validate if type is missing
    response = Valid.missing_field(type, 'Type of business')
    if response:
        return response
    
    # Validate if contact is missing
    response = Valid.missing_field(contact, 'Contact')
    if response:
        return response
    
    # Validate if contact is a valid phone number
    response = Valid.valid_phone_number(contact, 'Contact')
    if response:
        return response
    
    # Create a new merchant request
    new_request = RequestsMerchants(
        name=name,
        category=type,
        contact_no=contact, 
        requester_email=verified_email
    )
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'Success': 'Request Merchat added'}), 201

# Add merchant
@main.route('/merchant', methods=['POST'])
@google_token_required
def add_merchant(verified_email):
    logging.info(f"API /merchant POST called by: {verified_email}")

    # Validate if the user is an admin
    if Valid.user_is_admin(verified_email):
        return jsonify({'error': 'Only administrators are authorized to add new merchants'}), 403

    data = request.get_json()
    image_urls = data.get('Images', [])
    merchant_name = data.get('Name')
    merchant_type = data.get('Category')
    merchant_address = data.get('Addresses', [])
    discount = data.get('Discount')
    extra_info = data.get('More Info')
    terms_conditions = data.get('Terms')

    # Validate input fields
    required_fields = [
        (merchant_name, 'Name'),
        (merchant_type, 'Category'),
        (merchant_address[0] if merchant_address else None, 'Address'),
        (discount, 'Discount'),
        (terms_conditions, 'Terms')
    ]
    for field, name in required_fields:
        response = Valid.missing_field(field, name)
        if response:
            return response

    if Valid.merchant_exists(merchant_name):
        return jsonify({'error': 'Merchant with this name already exists'}), 400

    merchant_name = merchant_name.capitalize()
    merchant_type = merchant_type.capitalize()

    # Find or create the category
    category = Categories.query.filter_by(name=merchant_type).first()
    if not category:
        category = Categories(name=merchant_type)
        db.session.add(category)
        db.session.commit()
        socketio_events.add_category_update(category)

    # Create new merchant
    new_merchant = Merchants(
        name=merchant_name,
        category_id=category.id,
        discount=discount,
        more_info=extra_info,
        terms=terms_conditions
    )
    db.session.add(new_merchant)
    db.session.commit()

    # Add addresses
    for address in merchant_address:
        if not address or address.strip() == "":
            continue
        new_address = Addresses(
            merchant_id=new_merchant.id,
            address=address
        )
        db.session.add(new_address)

    # Add image URLs
    for url in image_urls:
        if not url or url.strip() == "":
            continue
        new_image = MerchantImages(
            merchant_id=new_merchant.id,
            image_url=url
        )
        db.session.add(new_image)

    db.session.commit()

    # Emit the new merchant data via Socket.IO
    socketio_events.add_merchant_update(new_merchant)

    return jsonify({'Success': 'Merchant added'}), 201

# Delete Merchant
@main.route('/merchant', methods=['DELETE'])
@google_token_required
def delete_merchant(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /merchant DELETE called by: {verified_email}")

    merchant_id = request.args.get('id')

    reponse = Valid.user_is_admin(verified_email)
    if reponse:
        return reponse

    # Query merchant by ID
    merchant = Merchants.query.filter_by(id=merchant_id).first()

    # Check if merchant exists
    if not merchant:
        return jsonify({'error': 'Merchant not found'}), 404

    # Delete merchant
    db.session.delete(merchant)
    db.session.commit()

    socketio_events.delete_merchant_update(merchant_id)

    return jsonify({'message': 'Merchant deleted successfully'}), 200


# Edit merchant
@main.route('/merchant', methods=['PUT'])
@google_token_required
def edit_merchant(verified_email):
    logging.info(f"API /merchant PUT called by: {verified_email}")

    # Validate if the user is an admin
    if Valid.user_is_admin(verified_email):
        return jsonify({'error': 'Only administrators are authorized to edit merchant'}), 403

    data = request.get_json()
    id = data.get('ID')
    image_urls = data.get('Images', [])
    merchant_name = data.get('Name')
    merchant_type = data.get('Category')
    merchant_address = data.get('Addresses', [])
    discount = data.get('Discount')
    extra_info = data.get('More Info')
    terms_conditions = data.get('Terms')

    # Validate input fields
    required_fields = [
        (merchant_name, 'Name'),
        (merchant_type, 'Category'),
        (merchant_address[0] if merchant_address else None, 'Address'),
        (discount, 'Discount'),
        (terms_conditions, 'Terms')
    ]
    for field, name in required_fields:
        response = Valid.missing_field(field, name)
        if response:
            return response

    if Valid.merchant_id(id) or Valid.merchant_exists(merchant_name, id):
        return response

    merchant_name = merchant_name.capitalize()
    merchant_type = merchant_type.capitalize()

    merchant = Merchants.query.get(id)
    if not merchant:
        return jsonify({'error': 'Merchant not found'}), 404

    old_category_id = merchant.category_id

    # Find or create the category
    category = Categories.query.filter_by(name=merchant_type).first()
    if not category:
        category = Categories(name=merchant_type)
        db.session.add(category)
        db.session.commit()
        socketio_events.add_category_update(category)

    # Update merchant details
    merchant.name = merchant_name
    merchant.category_id = category.id
    merchant.discount = discount
    merchant.more_info = extra_info
    merchant.terms = terms_conditions

    # Update addresses
    existing_addresses = Addresses.query.filter_by(merchant_id=merchant.id).all()
    for i, address in enumerate(merchant_address):
        if not address or address.strip() == "":
            continue
        if i < len(existing_addresses):
            existing_addresses[i].address = address
        else:
            new_address = Addresses(merchant_id=merchant.id, address=address)
            db.session.add(new_address)

    # Remove extra addresses if any
    for i in range(len(merchant_address), len(existing_addresses)):
        db.session.delete(existing_addresses[i])

    # Update image URLs
    existing_images = MerchantImages.query.filter_by(merchant_id=merchant.id).all()
    for i, url in enumerate(image_urls):
        if not url or url.strip() == "":
            continue
        if i < len(existing_images):
            existing_images[i].image_url = url
        else:
            new_image = MerchantImages(merchant_id=merchant.id, image_url=url)
            db.session.add(new_image)

    # Remove extra images if any
    for i in range(len(image_urls), len(existing_images)):
        db.session.delete(existing_images[i])

    db.session.commit()

    # Check if the old category has no merchants related to it
    if old_category_id != category.id:
        old_category = Categories.query.get(old_category_id)
        if old_category and not old_category.merchants:
            db.session.delete(old_category)
            db.session.commit()
            socketio_events.delete_category_update(old_category)

    socketio_events.edit_merchant_update(merchant)
    return jsonify({'Success': 'Merchant Edited'}), 200

# Export RequestsMerchants to Excel
@main.route('/export_request_merchants', methods=['GET'])
@google_token_required
def export_request_merchants(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /export_request_merchants GET called by: {verified_email}")

    # Query all requests merchants data
    requests_merchants = RequestsMerchants.query.all()

    # Check if data is queried correctly
    if not requests_merchants:
        return jsonify({'error': 'No data found'}), 404

    # Convert data to a list of dictionaries
    data = [
        {
            'ID': rm.id,
            'Name': rm.name,
            'Category': rm.category,
            'Contact No': rm.contact_no,
            'Requester Email': rm.requester_email
        }
        for rm in requests_merchants
    ]

    # Check if data is converted correctly
    if not data:
        return jsonify({'error': 'Data conversion failed'}), 500

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Check if DataFrame is created correctly
    if df.empty:
        return jsonify({'error': 'DataFrame is empty'}), 500

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='RequestsMerchants', header=True)

    output.seek(0)

    return send_file(output, download_name='requests_merchants.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Get categories
@main.route('/categories', methods=['GET'])
@google_token_required
def get_categories(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /categories GET called by: {verified_email}")

    # Query all categories
    categories = Categories.query.order_by(Categories.id.asc()).all()

    # Convert data to a list of dictionaries
    data = [
        {
            'ID': c.id,
            'Name': c.name
        }
        for c in categories
    ]   

    return jsonify({'Categories': data}), 200

# Get merchants
@main.route('/merchants', methods=['GET'])
@google_token_required
def get_merchants(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /merchants GET called by: {verified_email}")

    # Query all merchants
    merchants = Merchants.query.order_by(Merchants.id.asc()).all()

    # Convert data to a list of dictionaries
    data = [
        {
            'ID': merchant.id,
            'Name': merchant.name,
            'Category': merchant.category.name, 
            'Image': merchant.images[0].image_url if merchant.images and len(merchant.images) > 0 else ""
        }
        for merchant in merchants
    ]

    return jsonify({'Merchants': data}), 200

# Get merchant by ID
@main.route('/merchant', methods=['GET'])
@google_token_required
def get_merchant(verified_email):
    # Log the API call with the verified email
    logging.info(f"API /merchant GET called by: {verified_email}")

    merchant_id = request.args.get('id')

    # Validate if merchant_id is missing
    response = Valid.missing_field(merchant_id, 'ID')
    if response:
        return response

    # Query merchant by ID
    merchant = Merchants.query.filter_by(id=merchant_id).first()

    # Check if merchant exists
    if not merchant:
        return jsonify({'error': 'Merchant not found'}), 404

    # Convert data to a dictionary
    data = {
        'ID': merchant.id,
        'Name': merchant.name,
        'Category': merchant.category.name,
        'Discount': merchant.discount,
        'More Info': merchant.more_info,
        'Terms': merchant.terms,
        'Images': [image.image_url for image in merchant.images],
        'Addresses': [address.address for address in merchant.addresses]
    }

    return jsonify({'Merchant': data}), 200

