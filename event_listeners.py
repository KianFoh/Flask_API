# event_listeners.py
from sqlalchemy import event
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from models import Merchants, Users, AdminEmails
from socketio_events import notify_user_update

# Event listener to check the number of merchants in a category before deleting a merchant
@event.listens_for(Session, 'before_flush')
def check_and_delete_category(session, flush_context, instances):
    try:
        for instance in session.deleted:
            # Check if the instance is a Merchant
            if isinstance(instance, Merchants):
                category = instance.category
                if len(category.merchants) == 1:
                    session.delete(category)
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error in check_and_delete_category: {e}")

# Event listener to set isadmin to True if user email is in admin emails
@event.listens_for(Session, 'before_flush')
def set_user_isadmin(session, flush_context, instances):
    try:
        for instance in session.new:
            # Check if the instance is a User
            if isinstance(instance, Users):
                admin_email = session.query(AdminEmails).filter_by(email=instance.email).first()
                if admin_email:
                    instance.isadmin = True

            # Check if the instance is an AdminEmail
            if isinstance(instance, AdminEmails):
                user = session.query(Users).filter_by(email=instance.email).first()
                if user:
                    user.isadmin = True
                    session.add(user)
            
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error in set_user_isadmin: {e}")