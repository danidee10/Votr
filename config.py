# configuration file for votr
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'votr.db')
SECRET_KEY = 'development key'  # keep this key secret during production
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
CELERY_BROKER = 'amqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'amqp://'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True

# Constants file for Auth0's seed project
ACCESS_TOKEN_KEY = 'access_token'
APP_JSON_KEY = 'application/json'
AUTH0_CLIENT_ID = 'AUTH0_CLIENT_ID'
AUTH0_CLIENT_SECRET = 'AUTH0_CLIENT_SECRET'
AUTH0_CALLBACK_URL = 'AUTH0_CALLBACK_URL'
AUTH0_DOMAIN = 'AUTH0_DOMAIN'
AUTHORIZATION_CODE_KEY = 'authorization_code'
CLIENT_ID_KEY = 'client_id'
CLIENT_SECRET_KEY = 'client_secret'
CODE_KEY = 'code'
CONTENT_TYPE_KEY = 'content-type'
GRANT_TYPE_KEY = 'grant_type'
PROFILE_KEY = 'profile'
REDIRECT_URI_KEY = 'redirect_uri'
SECRET_KEY = 'ThisIsTheSecretKey'
