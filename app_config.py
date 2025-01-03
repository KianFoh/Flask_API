from flask import Flask
from flask_migrate import Migrate
from extensions import db
from socketio_events import socketio
from routes import main as main_blueprint
from utils import CONFIG
import event_listeners
import logging

def create_app():
    app = Flask(__name__)

    # Load database configuration from CONFIG
    username = CONFIG['postgresql']['username']
    password = CONFIG['postgresql']['password']
    db_name = CONFIG['postgresql']['dbname']
    db_hostname = CONFIG['postgresql']['hostname']
    db_port = CONFIG['postgresql']['port']

    # PostgreSQL configuration
    print(f'postgresql://{username}:{password}@{db_hostname}:{db_port}/{db_name}')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{db_hostname}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set up the SQLAlchemy ORM
    db.init_app(app)

    # Set up Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize SocketIO with the Flask app
    socketio.init_app(app)

    app.register_blueprint(main_blueprint)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return app