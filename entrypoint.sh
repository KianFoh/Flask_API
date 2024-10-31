#!/bin/bash

# Function to check if the database is up
function wait_for_db() {
  until pg_isready -h db -p 5432 -U "$POSTGRES_USER"
  do
    echo "Waiting for database to be ready..."
    sleep 2
  done
}

# Wait for the database to be ready
wait_for_db

# Run the migration script
python3 /app/migrate.py

# Start the Flask application
exec "$@"