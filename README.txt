Docker

* Run docker compose build image and run as containers
docker-compose up --build -d

* Check docker compose status
docker-compose ps

* Check docker compose status including offline
docker-compose ps -a

* Start docker compose containers
docker-compose start

* Stop docker compose containers
docker-compose stop

* Delete docker containers
docker-compose down

Extra notes:

* List docker images
docker images

* Delete docker image
docker rmi <image_id_or_name>

* List docker volumes
docker volume ls

* Deleting Docker Volumes
docker volume rm <volume_name>

Setup

* Step 1: Install database and setup

You need to install PostgreSQL db recommed using PostgreSQL 16

replace the username, password, dbname

Example:
username = 'Clarivate'
password = 'Clarivate231'
db_name = 'Clarivate Employee Privilege'

* Step 2: install python & python dependency

development python version: Python 3.12.2

Recommend to setup virtualenv using:
virtualenv==20.25.1

Deploy for production using:

# For Linux 
gunicorn==23.0.0

# For Window  
waitress==3.0.0

install all dependecy in requirement.txt
pip install -r requirements.txt

* Step 3: Setup Flask Migrate to update DB for changes in models.py

# Run this to Initial directory for storing migration files
flask db init

# Create migration scripts
flask db migrate -m "Initial Migration"

# Run this command to apply the scripts
    flask db upgrade

Extra notes:

* Flask Migrate commands

1) Initial Migration
flask db init
flask db migrate -m "Initial Migration"

* Extra command for migration

2) Detect changes in models and generate migration scripts
flask db migrate -m "Describe the change here"

3) Apply scripts to update DB
flask db upgrade

4) Rollback
flask db downgrade