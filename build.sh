#!/bin/bash
set -e
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate