from models import db, Polls, Topics, Options, UserPolls
from flask import Blueprint, request, jsonify, _request_ctx_stack
from functools import wraps
from datetime import datetime
import os
import uuid
from helpers import decode_jwt, handle_api_errors

from flask_cors import cross_origin

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
env = os.environ

api = Blueprint('api', __name__, url_prefix='/api')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')

        if not auth:
            return handle_api_errors({'code': 'authorization_header_missing',
                                     'message':
                                      'Authorization header is expected'})

        parts = auth.split()

        if parts[0].lower() != 'bearer':
            return handle_api_errors({'code': 'invalid_header',
                                      'message':
                                      'Authorization header must\
                                            start with Bearer'})

        elif len(parts) == 1:
            return handle_api_errors({'code': 'invalid_header',
                                      'message': 'Token not found'})

        elif len(parts) > 2:
            return handle_api_errors({'code': 'invalid_header',
                                      'message':
                                      'Authorization header must\
                                            be Bearer \s token'})

        token = parts[1]

        payload = decode_jwt(token)

        _request_ctx_stack.top.current_user = payload
        return f(*args, **kwargs)

    return decorated


@api.route('/polls', methods=['GET', 'POST'])
def api_polls():
    """Retrieves/adds polls from/to the database."""
    if request.method == 'POST':
        # get the poll and save it in the database
        poll = request.get_json()

        # simple validation to check if all values are properly set
        for key, value in poll.items():
            if not value:
                return jsonify({'message':
                                'value for {} is empty'.format(key)})

        title = poll['title']

        id_token = poll.get('id_token')

        if id_token:
            user_identifier = decode_jwt(id_token).get('email')
        else:
            user_identifier = None

        # return option that matches a given name
        def options_query(option):
            return Options.query.filter(Options.name.like(option))

        options = [Polls(option=Options(name=option))
                   if options_query(option).count() == 0
                   else Polls(option=options_query(option).first())
                   for option in poll['options']]

        # generate 10 character unique hex string
        uniq_id = uuid.uuid4().hex[:10]

        eta = datetime.utcfromtimestamp(poll['close_date'])
        new_topic = Topics(title=title, user_identifier=user_identifier,
                           options=options, close_date=eta, unique_id=uniq_id)

        db.session.add(new_topic)
        db.session.commit()

        # run the task
        from tasks import close_poll

        close_poll.apply_async((new_topic.id, env['SQLALCHEMY_DATABASE_URI']),
                               eta=eta)

        return jsonify({'message': 'Poll created succesfully',
                        'unique_id': uniq_id})

    else:
        # it's a GET request, return dict representations of the API
        polls = Topics.query.filter_by(status=True).join(Polls)\
                .order_by(Topics.id.desc()).all()

        all_polls = {'Polls':  [poll.to_json() for poll in polls]}

        return jsonify(all_polls)


@api.route('/polls/options')
def api_polls_options():
    """Return all options."""

    all_options = {option.name: '' for option in Options.query.all()}

    return jsonify(all_options)


@api.route('/poll/vote', methods=['PATCH'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def api_poll_vote():
    poll = request.get_json()

    unique_id, option = (poll['unique_id'], poll['option'])

    join_tables = Polls.query.join(Topics).join(Options)

    # Get topic and username
    topic = Topics.query.filter_by(unique_id=unique_id, status=True).first()
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
    option = join_tables.filter(Topics.unique_id == (unique_id)).\
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
                    'Option or Poll not found. Please try again'})


@api.route('/poll/<unique_id>')
def api_poll(unique_id):
    poll = Topics.query.filter_by(unique_id=unique_id).first()

    return jsonify({'Polls': [poll.to_json()]} if poll
                   else {'message': 'poll not found'})
