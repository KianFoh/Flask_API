from app_config import create_app
from socketio_events import socketio
import logging

app = create_app()

if __name__ == '__main__':
    # Set the logging level for Werkzeug to WARNING to suppress detailed HTTP request logs
        # log = logging.getLogger('werkzeug')
        # log.setLevel(logging.WARNING)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)