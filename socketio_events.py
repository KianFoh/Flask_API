import dis
from shlex import join
from flask_socketio import SocketIO, join_room, leave_room, disconnect, emit
from flask import request
from models import Users
from token_verify import socketio_token_required
import logging

# Initialize SocketIO
socketio = SocketIO(transports=['websocket', 'polling'])

# SocketIO event listeners
@socketio.on('connect')
def handle_connect(auth):
    email = request.args.get('email')
    token = request.args.get('token')

    # Verify token
    verified_email = socketio_token_required(token)
    if verified_email == "expired":
        logging.error(f"Token verification failed for email: {email}")
        disconnect()
        return False

    if verified_email != email:
        logging.error(f"Email mismatch: {verified_email} != {email}")
        disconnect()
        return False

    try:
        join_room(verified_email)
        logging.info(f"Client connected: {verified_email}")
    except Exception as e:
        logging.error(f"Error joining room for {verified_email}: {e}")
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    email = request.args.get('email')
    if email:
        try:
            leave_room(email)
            logging.info(f"Client disconnected: {email}")
        except Exception as e:
            logging.error(f"Error leaving room for {email}: {e}")
    else:
        print("Disconnect request missing email")

def admin_status_update(user):
    socketio.emit('admin_status_update', {'isadmin': user.isadmin}, room=user.email)    

def add_category_update(category):
    data = {'ID': category.id, 'Name': category.name}
    socketio.emit('category_added', {'Categories': data})

def delete_category_update(category):
    socketio.emit('category_deleted', {'Categories': category.id})

# Function to emit merchant data via Socket.IO
def add_merchant_update(merchant):
    data = {
        'ID': merchant.id,
        'Name': merchant.name,
        'Category': merchant.category.name,
        'Image': merchant.images[0].image_url if merchant.images and len(merchant.images) > 0 else ""
    }
    socketio.emit('merchant_added', {'Merchants': data})

def delete_merchant_update(merchantID):
    socketio.emit('merchant_deleted', {'Merchants': merchantID})

def edit_merchant_update(merchant):
    data = {
        'ID': merchant.id,
        'Name': merchant.name,
        'Category': merchant.category.name,
        'Image': merchant.images[0].image_url if merchant.images and len(merchant.images) > 0 else ""
    }
    socketio.emit('merchant_edited', {'Merchants': data})