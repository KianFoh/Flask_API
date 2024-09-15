Setup

* Step 1: Install database and setup

You need to install PostgreSQL db recommed using PostgreSQL 16
Install PostGIS 3.4 Bundle v3.4.2 from Stack Builder for storing spatial data

Install postgis as extension in your postgreSQL DB

replace the username, password, dbname

Example:
username = 'Clarivate'
password = 'Clarivate231'
db_name = 'Clarivate Employee Privilege'

* Step 2: Setup Flask Migrate to update DB for changes in models.py

# Run this to Initial directory for storing migration files
flask db init

# Create migration scripts
flask db migrate -m "Initial Migration"

# Add additional dependency for migration file
add this import in ./migrations/versions/9306bc95aeab_initial_migration.py
import geoalchemy2

Note: 
- this file 9306bc95aeab_initial_migration.py name could be a bit different
- Scripts generated in migration files by Alembic require user to review first before applying it

# Remove code to prevent creating duplicate index

remove these line of code in the migration files under def upgrade():

    with op.batch_alter_table('locations', schema=None) as batch_op:
        batch_op.create_index('idx_locations_location', ['location'], unique=False, postgresql_using='gist')

    op.drop_table('spatial_ref_sys')

IMPORTANT Note: Always remove these line of code during migration or it can cause error

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