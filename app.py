# Dependencies
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# PostgreSQL info
username = 'Clarivate'
password = 'Clarivate231'
db_name = 'Clarivate Employee Privilege'

# PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@localhost/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up the SQLAlchemy ORM
db = SQLAlchemy(app)

# Set up Flask-Migrate
migrate = Migrate(app, db)


# Import your models
from models import *

if __name__ == '__main__':
    app.run(debug=True)

