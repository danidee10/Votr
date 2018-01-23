"""Production config for votr on Heroku."""

import os

DEBUG = False
SECRET_KEY = 'production key'  # keep secret
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
CELERY_BROKER = os.getenv('RABBITMQ_BIGWIG_RX_URL')
CELERY_RESULT_BACKEND = 'amqp://'
SQLALCHEMY_TRACK_MODIFICATIONS = False
