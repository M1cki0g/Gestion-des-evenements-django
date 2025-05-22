release: python manage.py migrate
web: gunicorn --workers=4 --threads=4 main.wsgi:application --log-file -
