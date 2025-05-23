#!/usr/bin/env python
"""
Robust server script for Railway deployment.
Uses Django's built-in WSGI handler with waitress server.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Add the project directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Set Django settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
    
    # Log environment variables (excluding sensitive ones)
    logger.info(f"Current directory: {current_dir}")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    logger.info(f"DATABASE_URL: {'Set' if os.environ.get('DATABASE_URL') else 'Not set'}")
    
    # Make sure the staticfiles directory exists
    os.makedirs(os.path.join(current_dir, 'staticfiles'), exist_ok=True)
    
    # Import Django and set up the application
    import django
    django.setup()
    
    # Apply migrations automatically
    logger.info("Applying database migrations...")
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "migrate", "--noinput"])
    
    # Collect static files
    logger.info("Collecting static files...")
    os.environ["COLLECTSTATIC_DRYRUN"] = "1"  # Avoid database access during collectstatic
    execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
    
    # Create WSGI application
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    # Start the server
    from waitress import serve
    logger.info("Starting waitress server on port 8080...")
    serve(application, host="0.0.0.0", port=8080)
    
except Exception as e:
    logger.error(f"Error starting server: {e}", exc_info=True)
    raise
