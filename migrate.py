# migrate.py
from app_config import create_app
from flask_migrate import upgrade, migrate, init
import os

app = create_app()

with app.app_context():
    # Initialize the migration repository if it doesn't exist
    if not os.path.exists('migrations'):
        init()

    # Create a new migration
    migrate(message="Initial Migration")

    # Apply the migration
    upgrade()