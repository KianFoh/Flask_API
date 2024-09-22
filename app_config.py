import json
from flask import Flask
from flask_migrate import Migrate
from extensions import db
from socketio_events import socketio
from routes import main as main_blueprint
import event_listeners

def create_app():
    app = Flask(__name__)

    # Load database configuration from config.json
    with open('./config.json') as config_file:
        config = json.load(config_file)

    username = config['postgresql']['username']
    password = config['postgresql']['password']
    db_name = config['postgresql']['dbname']

    # PostgreSQL configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@localhost/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set up the SQLAlchemy ORM
    db.init_app(app)

    # Set up Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize SocketIO with the Flask app
    socketio.init_app(app)


    app.register_blueprint(main_blueprint)

    return app