#!/bin/bash
set -e

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn server..."
DJANGO_SETTINGS_MODULE=main.settings gunicorn --bind 0.0.0.0:8080 main.wsgi:application
