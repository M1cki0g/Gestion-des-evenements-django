#!/usr/bin/env python
"""
Simple server script for Railway deployment.
Uses Django's built-in WSGI handler with a simple HTTP server.
"""
import os
import sys
from waitress import serve

# Add the project directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

# Import Django WSGI application
import django
django.setup()

from django.core.wsgi import get_wsgi_application

# Create WSGI application
application = get_wsgi_application()

if __name__ == "__main__":
    print("Starting waitress server on port 8080...")
    serve(application, host="0.0.0.0", port=8080)
