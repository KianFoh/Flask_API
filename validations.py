# valid.py
from flask import jsonify
from models import Users, AdminEmails
from extensions import db
from utils import VALID_EMAIL_DOMAIN

class Valid:
    @staticmethod
    def user_exists(email):
        user = Users.query.filter_by(email=email).first()
        if user:
            return jsonify({'user': {'username': user.username, 'email': user.email, 'admin': user.isadmin}}), 200
        return None

    @staticmethod
    def admin_email_exists(email):
        existing_admin = AdminEmails.query.filter_by(email=email).first()
        if existing_admin:
            return jsonify({'error': 'Email already exists in admin list'}), 400
        return None
    
    @staticmethod
    def user_is_admin(email):
        user = Users.query.filter_by(email=email).first()
        if user and user.isadmin:
            return jsonify({'error': 'Require admin access'}), 403
        return None
    
    @staticmethod
    def missing_email(email):
        if email is None:
            return jsonify({'error': 'Missing Email'}), 400
        return None

    @staticmethod
    def email_format_and_domain(email):
        if '@' not in email:
            return jsonify({'error': 'Invalid email'}), 400
        domain = email.split('@')[1]
        if domain != VALID_EMAIL_DOMAIN:
            return jsonify({'error': f'Invalid email domain. Only {VALID_EMAIL_DOMAIN} is accepted.'}), 400
        return None

    @staticmethod
    def create_new_user(username, email, isadmin):
        new_user = Users(username=username, email=email, isadmin=isadmin)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'user': {'username': new_user.username, 'email': new_user.email, 'admin': new_user.isadmin}}), 201

    @staticmethod
    def create_new_admin_email(email):
        new_admin = AdminEmails(email=email)
        db.session.add(new_admin)
        db.session.commit()
        return new_admin

    @staticmethod
    def update_user_to_admin(email):
        user = Users.query.filter_by(email=email).first()
        if user:
            user.isadmin = True
            db.session.commit()
            return user
        return None
    
