# configuration file for votr
import os

# Load environment variables
from dotenv import Dotenv
try:
    env = Dotenv('.env')
except IOError:
    env = os.environ

SECRET_KEY = env['SECRET_KEY']
SQLALCHEMY_DATABASE_URI = env['SQLALCHEMY_DATABASE_URI']
CELERY_BROKER = env['CELERY_BROKER']
CELERY_RESULT_BACKEND = env['CELERY_RESULT_BACKEND']
SQLALCHEMY_TRACK_MODIFICATIONS = env['SQLALCHEMY_TRACK_MODIFICATIONS']
DEBUG = env['DEBUG']

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
