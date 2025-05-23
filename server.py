#!/usr/bin/env python
"""
Robust server script for Railway deployment.
Uses Django's built-in WSGI handler with waitress server.
"""
import os
import sys
import logging
import traceback
import time
import django
from waitress import serve
from django.core.management import execute_from_command_line

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Print diagnostic information
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Environment variables: {', '.join([f'{k}={v}' for k, v in os.environ.items() if not k.startswith('_')])}")

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
logger.info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

# Make sure DATABASE_URL is set
if not os.environ.get('DATABASE_URL'):
    logger.warning("DATABASE_URL is not set! Using SQLite as fallback.")
    os.environ['DATABASE_URL'] = f"sqlite:///{os.path.join(os.getcwd(), 'db.sqlite3')}"

logger.info(f"Using database: {os.environ.get('DATABASE_URL').split('@')[0].split('://')[0]} database")

# Initialize Django
try:
    logger.info("Setting up Django...")
    django.setup()
    logger.info("Django setup complete")
except Exception as e:
    logger.error(f"Error setting up Django: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

# Ensure Django is properly loaded
try:
    from django.conf import settings
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
    logger.info(f"Installed apps: {', '.join(settings.INSTALLED_APPS)}")
except Exception as e:
    logger.error(f"Error accessing Django settings: {e}")
    logger.error(traceback.format_exc())

# Import the WSGI application first to detect import errors early
try:
    logger.info("Importing WSGI application...")
    from main.wsgi import application
    logger.info("WSGI application imported successfully")
except Exception as e:
    logger.error(f"Error importing WSGI application: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

# Run migrations if needed
try:
    logger.info("Applying database migrations...")
    execute_from_command_line(["manage.py", "migrate", "--noinput"])
    logger.info("Database migrations complete")
except Exception as e:
    logger.error(f"Error applying migrations: {e}")
    logger.error(traceback.format_exc())
    # Continue despite migration errors

# Create default superuser if needed
try:
    logger.info("Creating default superuser if needed...")
    execute_from_command_line(["manage.py", "create_default_superuser"])
    logger.info("Superuser check complete")
except Exception as e:
    logger.error(f"Error creating superuser: {e}")
    logger.error(traceback.format_exc())
    # Continue despite superuser creation errors

# Collect static files
try:
    logger.info("Collecting static files...")
    execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
    logger.info("Static files collected")
except Exception as e:
    logger.error(f"Error collecting static files: {e}")
    logger.error(traceback.format_exc())
    # Continue despite static file errors

# Create media directory with special handling for Railway's ephemeral filesystem
try:
    from django.conf import settings
    # Ensure media directory exists
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    logger.info(f"Created media directory at {settings.MEDIA_ROOT}")
    
    # Create a directory in /tmp which persists during the current session
    persistent_media_dir = '/tmp/toul_events_media'
    os.makedirs(persistent_media_dir, exist_ok=True)
    
    # Create symlink from media directory to persistent directory for each subdirectory
    # This helps preserve uploaded files during the session
    for item in ['uploads']:
        source_dir = os.path.join(settings.MEDIA_ROOT, item)
        target_dir = os.path.join(persistent_media_dir, item)
        
        # Create subdirectories if they don't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # If the source exists but is not a symlink, back it up
        if os.path.exists(source_dir) and not os.path.islink(source_dir):
            backup_dir = f"{source_dir}_backup_{int(time.time())}"
            os.rename(source_dir, backup_dir)
            logger.info(f"Backed up {source_dir} to {backup_dir}")
        
        # Remove existing symlink if any
        if os.path.islink(source_dir):
            os.unlink(source_dir)
        
        # Create symlink from media/uploads to persistent directory
        os.symlink(target_dir, source_dir)
        logger.info(f"Created symlink from {source_dir} to {target_dir}")
    
    # Ensure the media directory is writable
    test_file = os.path.join(settings.MEDIA_ROOT, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('Test file to ensure media directory is writable')
    os.remove(test_file)
    logger.info("Media directory is writable")
    
    # Print out all files in the persistent media directory
    for root, dirs, files in os.walk(persistent_media_dir):
        for file in files:
            logger.info(f"Found file: {os.path.join(root, file)}")
            
except Exception as e:
    logger.error(f"Error setting up media directory: {e}")
    logger.error(traceback.format_exc())
    # Continue despite media directory errors

# Define a simple health check view
def health_check(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'OK']

# Wrap the application with health check
class WSGIAppWithHealthCheck:
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO') == '/health':
            return health_check(environ, start_response)
        return self.app(environ, start_response)

# Start the server
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Starting waitress server on port {port}...")
        serve(WSGIAppWithHealthCheck(application), host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
