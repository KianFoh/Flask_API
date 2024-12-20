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
connected_clients = {}

@socketio.on('connect')
def handle_connect(auth):
    sid = request.sid
    email = request.args.get('email')
    token = request.args.get('token')

    # Token verification
    verified_email = socketio_token_required(token)
    if verified_email == "expired" or verified_email != email:
        emit('error', {'message': 'Invalid token or email mismatch'}, to=sid)
        disconnect(sid)
        return False

    # Store client info and join room
    connected_clients[sid] = email
    try:
        join_room(verified_email, sid=sid)
        logging.info(f"Client connected: {verified_email} (sid: {sid})")
    except Exception as e:
        logging.error(f"Error joining room for {verified_email} (sid: {sid}): {e}")
        disconnect(sid)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    email = connected_clients.pop(sid, None)
    if email:
        try:
            leave_room(email, sid=sid)
            logging.info(f"Client disconnected: {email} (sid: {sid})")
        except Exception as e:
            logging.error(f"Error leaving room for {email} (sid: {sid}): {e}")
    else:
        logging.warning(f"Disconnected client with unknown email (sid: {sid})")

# Emit admin status updates
def admin_status_update(user):
    socketio.emit('admin_status_update', {'isadmin': user.isadmin}, room=user.email)

# Emit category updates
def add_category_update(category):
    data = {'ID': category.id, 'Name': category.name}
    socketio.emit('category_added', {'Categories': data})

def delete_category_update(category):
    socketio.emit('category_deleted', {'Categories': category.id})

# Emit merchant updates
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