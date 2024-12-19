# Apply eventlet monkey patching first
import eventlet
eventlet.monkey_patch()

from app_config import create_app
from socketio_events import socketio
import logging
from utils import CONFIG

# Create the app
app = create_app()

# Ensure that the app context is used where needed
with app.app_context():
    # Set the logging level for Werkzeug to WARNING to suppress detailed HTTP request logs
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)

    # Configure logging for your application
    logging.basicConfig(level=logging.INFO)

# Gunicorn will manage starting the app with Eventlet workers