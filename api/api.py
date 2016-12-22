from models import db, Polls, Topics, Options, UserPolls
from flask import Blueprint, request, jsonify, _request_ctx_stack
from functools import wraps
from datetime import datetime
import jwt
import os
import config

from flask_cors import cross_origin

# Load env file
from dotenv import Dotenv
try:
    env = Dotenv('.env')
except IOError:
    env = os.environ

api = Blueprint('api', __name__, url_prefix='/api')


# Authentication attribute
def authenticate(error):
    resp = jsonify(error)

    resp.status_code = 401

    return resp


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')

        if not auth:
            return authenticate({'code': 'authorization_header_missing',
                                'message': 'Authorization header is expected'})

        parts = auth.split()

        if parts[0].lower() != 'bearer':
            return {'code': 'invalid_header',
                    'message': 'Authorization header must start with Bearer'}
        elif len(parts) == 1:
            return {'code': 'invalid_header',
                    'message': 'Token not found'}
        elif len(parts) > 2:
            return {'code': 'invalid_header',
                    'message': 'Authorization header must be Bearer \s token'}

        token = parts[1]
        try:
            payload = jwt.decode(
                        token, env[config.AUTH0_CLIENT_SECRET],
                        audience=env[config.AUTH0_CLIENT_ID],
                        algorithms=['HS256'],
                        options={'verify_iat': False}
                    )

        except jwt.ExpiredSignature:
            return authenticate({'code': 'token_expired',
                                'message': 'token is expired'})
        except jwt.InvalidAudienceError:
            return authenticate({'code': 'invalid_audience',
                                'message': 'incorrect audience'})
        except jwt.DecodeError:
            return authenticate({'code': 'token_invalid_signature',
                                'message': 'token signature is invalid'})

        _request_ctx_stack.top.current_user = payload
        return f(*args, **kwargs)

    return decorated


@api.route('/polls', methods=['GET', 'POST'])
# retrieves/adds polls from/to the database
def api_polls():
    if request.method == 'POST':
        # get the poll and save it in the database
        poll = request.get_json()

        # simple validation to check if all values are properly set
        for key, value in poll.items():
            if not value:
                return jsonify({'message':
                                'value for {} is empty'.format(key)})

        title = poll['title']

        # return option that matches a given name
        def options_query(option):
            return Options.query.filter(Options.name.like(option))

        options = [Polls(option=Options(name=option))
                   if options_query(option).count() == 0
                   else Polls(option=options_query(option).first())
                   for option in poll['options']]

        eta = datetime.utcfromtimestamp(poll['close_date'])
        new_topic = Topics(title=title, options=options, close_date=eta)

        db.session.add(new_topic)
        db.session.commit()

        # run the task
        from tasks import close_poll

        close_poll.apply_async((new_topic.id, env['SQLALCHEMY_DATABASE_URI']),
                               eta=eta)

        return jsonify({'message': 'Poll was created succesfully'})

    else:
        # it's a GET request, return dict representations of the API
        polls = Topics.query.filter_by(status=True).join(Polls)\
                .order_by(Topics.id.desc()).all()

        all_polls = {'Polls':  [poll.to_json() for poll in polls]}

        return jsonify(all_polls)


@api.route('/polls/options')
def api_polls_options():

    all_options = {option.name: '' for option in Options.query.all()}

    return jsonify(all_options)


@api.route('/poll/vote', methods=['PATCH'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def api_poll_vote():
    poll = request.get_json()

    poll_title, option = (poll['poll_title'], poll['option'])

    join_tables = Polls.query.join(Topics).join(Options)

    # Get topic and username
    topic = Topics.query.filter_by(title=poll_title, status=True).first()
    user = _request_ctx_stack.top.current_user
    user_identifier = user.get('email') or user.get('nickname')

    # if the user has not verified their email abort
    if not user.get('email_verified'):
        return jsonify({'message':
                        'You have to verify your email before you vote'})

    # if poll was closed in the background before user voted
    if not topic:
        return jsonify({'message': 'Sorry! this poll has been closed'})

    # filter options
    option = join_tables.filter(Topics.title.like(poll_title)).\
        filter(Options.name.like(option)).first()

    # check if the user has voted on this poll
    poll_count = UserPolls.query.filter_by(topic_id=topic.id).\
        filter_by(user_identifier=user_identifier).count()

    if poll_count:
        return jsonify({'message':
                        'Multiple votes are not allowed on this poll'})

    if option:
        # record user and poll
        user_poll = UserPolls(topic_id=topic.id,
                              user_identifier=user_identifier)
        db.session.add(user_poll)

        # increment vote_count by 1 if the option was found
        option.vote_count += 1
        db.session.commit()

        return jsonify({'message': 'Thank you for voting'})

    return jsonify({'message':
                    'Option or poll was not found please try again'})


@api.route('/poll/<poll_name>')
def api_poll(poll_name):
    poll = Topics.query.filter(Topics.title.like(poll_name)).first()

    return jsonify({'Polls': [poll.to_json()]} if poll
                   else {'message': 'poll not found'})
