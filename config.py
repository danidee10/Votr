# configuration file for votr
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'votr.db')
SECRET_KEY = 'development key'  # keep this key secret during production
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
CELERY_BROKER = 'amqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'amqp://'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
