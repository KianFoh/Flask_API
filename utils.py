# utils.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def load_config():
    config = {
        'api': {
            'hostname': os.getenv('API_HOSTNAME'),
            'port': os.getenv('API_PORT')
        },
        'postgresql': {
            'dbname': os.getenv('POSTGRES_DBNAME'),
            'username': os.getenv('POSTGRES_USERNAME'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'hostname': os.getenv('POSTGRES_HOSTNAME'),
            'port': os.getenv('POSTGRES_PORT')
        },
        'google': {
            'clientid': os.getenv('GOOGLE_CLIENTID')
        }
    }

    # Check for missing environment variables
    for section, values in config.items():
        for key, value in values.items():
            if value is None:
                raise ValueError(f"Environment variable for {section}.{key} not set")

    return config

# Load the configuration once and store it in a global variable
CONFIG = load_config()