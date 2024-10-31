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
    if __name__ == '__main__':
        # Set the logging level for Werkzeug to WARNING to suppress detailed HTTP request logs
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
        
        # Get host and port from CONFIG
        host = CONFIG['api']['hostname']
        port = int(CONFIG['docker']['flaskapi_port'])
        
        # Run the app with socketio
        socketio.run(app, host=host, port=port, debug=False)