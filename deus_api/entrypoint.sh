#!/bin/sh

# Check if the MIGRATE_DB environment variable is set to true
#if [ "$MIGRATE_DB" = "true" ]; then
    # Apply database migrations
python manage.py flush --no-input
python manage.py makemigrations articles
python manage.py migrate
#fi

# Check if the POPULATE_DB environment variable is set to true
#if [ "$POPULATE_DB" = "true" ]; then
    # Populate the database
python manage.py populate_fake_data
#fi

# Start the Django development server
exec "$@"
