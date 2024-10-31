from flask import Flask
from flask_migrate import Migrate
from extensions import db
from socketio_events import socketio
from routes import main as main_blueprint
from utils import CONFIG
import event_listeners

def create_app():
    app = Flask(__name__)

    # Load database configuration from CONFIG
    username = CONFIG['postgresql']['username']
    password = CONFIG['postgresql']['password']
    db_name = CONFIG['postgresql']['dbname']
    db_hostname = CONFIG['docker']['postgres_service']
    db_port = CONFIG['docker']['postgres_port']

    # PostgreSQL configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@{db_hostname}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set up the SQLAlchemy ORM
    db.init_app(app)

    # Set up Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize SocketIO with the Flask app
    socketio.init_app(app)

    app.register_blueprint(main_blueprint)

    return app