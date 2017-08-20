web: gunicorn wsgi:application --log-file -
worker: celery -A tasks.celery worker --loglevel=info
