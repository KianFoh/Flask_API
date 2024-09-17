# Dependencies
from flask import Flask, request, jsonify
from flask_migrate import Migrate
import json
from token_verify import google_token_required
import logging
from extensions import db

app = Flask(__name__)

# PostgreSQL info
# Load database configuration from config.json
with open('./config.json') as config_file:
    config = json.load(config_file)

username = config['postgresql']['username']
password = config['postgresql']['password']
db_name = config['postgresql']['dbname']

# PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@localhost/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up the SQLAlchemy ORM
db.init_app(app)

# Set up Flask-Migrate
migrate = Migrate(app, db)


# Import your models
from models import *

# Create a new user
@app.route('/users', methods=['POST'])
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
        # Create a new user
        new_user = Users(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()
        user = Users.query.filter_by(email=email).first()
        return jsonify({'user': {'username': user.username, 'email': user.email, 'admin': user.isadmin}}), 201
    
    except Exception as e:
        db.session.rollback()  # Rollback the session to avoid any partial commits
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

