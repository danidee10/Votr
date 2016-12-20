from flask import Flask, render_template, request, flash, session, redirect
from flask import url_for, jsonify
from flask_migrate import Migrate
from models import db, Users, Polls, Topics, Options, UserPolls
from flask_admin import Admin
from admin import AdminView, TopicView

import os
import json
import requests
import config

# Blueprints
from api.api import api

# celery
from celery import Celery

# Load environment variables
from dotenv import Dotenv
try:
    env = Dotenv('.env')
except IOError:
    env = os.environ

import rollbar
import rollbar.contrib.flask
from flask import got_request_exception


def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.update(votr.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    return celery

votr = Flask(__name__)

votr.register_blueprint(api)

# load config from the config file we created earlier
votr.config.from_object('config')

# create the database
db.init_app(votr)
db.create_all(app=votr)

migrate = Migrate(votr, db, render_as_batch=True)

# create celery object
celery = make_celery(votr)

admin = Admin(votr, name='Dashboard',
              index_view=TopicView(Topics, db.session,
                                   url='/admin', endpoint='admin'))
admin.add_view(AdminView(Users, db.session))
admin.add_view(AdminView(Polls, db.session))
admin.add_view(AdminView(Options, db.session))
admin.add_view(AdminView(UserPolls, db.session))


# rollbar
@votr.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token for the demo app: https://rollbar.com/demo
        env['ROLLBAR_TOKEN'],
        # environment name
        'votr',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, votr)


# Auth0 callback
@votr.route('/callback')
def callback_handling():
    code = request.args.get(config.CODE_KEY)
    json_header = {config.CONTENT_TYPE_KEY: config.APP_JSON_KEY}
    token_url = 'https://{auth0_domain}/oauth/token'.format(
                    auth0_domain=env[config.AUTH0_DOMAIN])
    token_payload = {
        config.CLIENT_ID_KEY: env[config.AUTH0_CLIENT_ID],
        config.CLIENT_SECRET_KEY: env[config.AUTH0_CLIENT_SECRET],
        config.REDIRECT_URI_KEY: env[config.AUTH0_CALLBACK_URL],
        config.CODE_KEY: code,
        config.GRANT_TYPE_KEY: config.AUTHORIZATION_CODE_KEY
    }

    token_info = requests.post(token_url, data=json.dumps(token_payload),
                               headers=json_header).json()

    user_url = 'https://{auth0_domain}/userinfo?access_token={access_token}'.\
        format(auth0_domain=env[config.AUTH0_DOMAIN],
               access_token=token_info[config.ACCESS_TOKEN_KEY]
               )

    user_info = requests.get(user_url).json()
    session[config.PROFILE_KEY] = user_info

    return redirect(url_for('home'))


@votr.route('/')
def home():
    return render_template('index.html')


# Fake Auth to bypass Auth0 and create a session so user can vote
# The access_token is compared with the app's secret key to
# prevent anyone from gaining access
@votr.route('/fake_auth', methods=['POST'])
def authenticate():
    data = request.get_json()

    if data.get('access_token') == env['SECRET_KEY']:
        session[config.PROFILE_KEY] = data
        return jsonify({'message': 'Authenticated'})
    else:
        return jsonify({'message': 'What are you trying to do?'})


@votr.route('/logout')
def logout():
    if 'profile' in session:
        session.pop('profile')

        flash('We hope to see you again!')

    return redirect(url_for('home'))


@votr.route('/polls', methods=['GET'])
def polls():
    return render_template('polls.html')


@votr.route('/polls/<poll_name>')
def poll(poll_name):

    return render_template('index.html')
