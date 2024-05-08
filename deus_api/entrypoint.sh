#!/bin/sh

# Check if the MIGRATE_DB environment variable is set to true
if [ "$MIGRATE_DB" = "true" ]; then
    # Apply database migrations
    python manage.py makemigrations articles
    python manage.py migrate
fi

# Check if the POPULATE_DB environment variable is set to true
echo "POPULATE_DB is set to: $POPULATE_DB"
if [ "$POPULATE_DB" = "true" ]; then
    python manage.py flush --no-input
    # Populate the database
    python manage.py populate_fake_data
fi
echo "RUN_TESTS is set to: $RUN_TESTS"
if [ "$RUN_TESTS" = "true" ]; then
    python manage.py test
fi
# Start the Django development server
exec "$@"
