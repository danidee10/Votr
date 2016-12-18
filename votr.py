from flask import Flask, render_template, request, flash, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
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

admin = Admin(votr, name='Dashboard', index_view=TopicView(Topics, db.session, url='/admin', endpoint='admin'))
admin.add_view(AdminView(Users, db.session))
admin.add_view(AdminView(Polls, db.session))
admin.add_view(AdminView(Options, db.session))
admin.add_view(AdminView(UserPolls, db.session))


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


@votr.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        # get the user details from the form
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # hash the password
        password = generate_password_hash(password)

        user = Users(email=email, username=username, password=password)

        db.session.add(user)
        db.session.commit()

        flash('Thanks for signing up please login')

        return redirect(url_for('home'))

    # it's a GET request, just render the template
    return render_template('signup.html')


@votr.route('/login', methods=['POST'])
def login():
    # we don't need to check the request type as flask will raise a bad request
    # error if a request aside from POST is made to this url

    username = request.form['username']
    password = request.form['password']

    # search the database for the User
    user = Users.query.filter_by(username=username).first()

    if user:
        password_hash = user.password

        if check_password_hash(password_hash, password):
            # The hash matches the password in the database log the user in
            session['user'] = username

            flash('Login was succesfull')
    else:
        # user wasn't found in the database
        flash('Username or password is incorrect please try again', 'error')

    return redirect(request.args.get('next') or url_for('home'))


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
