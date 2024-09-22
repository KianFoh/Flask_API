import dis
from shlex import join
from flask_socketio import SocketIO, join_room, leave_room, disconnect, emit
from flask import request
from models import Users
from token_verify import socketio_token_required

# Initialize SocketIO
socketio = SocketIO()



# SocketIO event listeners
@socketio.on('connect')
def handle_connect():
    email = request.args.get('email')
    token = request.args.get('token')
    verified_email = socketio_token_required(token)
    if verified_email == email:
        join_room(verified_email)
        print(f'Client connected: {verified_email}')
    else:
        print('Invalid token')
        return False


@socketio.on('disconnect')
def handle_disconnect():
    email = request.args.get('email')
    leave_room(email)
    print(f'Client disconnected: {email}')

def notify_user_update(user_id):
    user = Users.query.get(user_id)
    if user:
        socketio.emit('user_update', {'isadmin': user.isadmin}, room=user.email)