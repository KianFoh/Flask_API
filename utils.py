# utils.py
import json

def load_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config['validation']['email_domain']

# Load the domain once and store it in a global variable
VALID_EMAIL_DOMAIN = load_config()