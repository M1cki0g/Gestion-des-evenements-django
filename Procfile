release: pip install -r requirements.txt && python manage.py migrate
web: DJANGO_SETTINGS_MODULE=main.production gunicorn main.wsgi --log-file -
