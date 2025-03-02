# Procfile
web: gunicorn dashboard.app:app
worker: celery -A src.utils.helpers worker --loglevel=info