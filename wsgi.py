"""
Root WSGI config file to simplify deployment.
"""

import os
import sys

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
