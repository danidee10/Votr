from models import db, Polls, Topics, Options, UserPolls
from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime
import os


# Load env file
from dotenv import Dotenv
try:
    env = Dotenv('.env')
except IOError:
    env = os.environ

api = Blueprint('api', __name__, url_prefix='/api')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            return jsonify({'message': 'You have to Login to vote!'})

        elif not session.get('profile').get('email_verified'):

            return jsonify(
                {'message':
                    'You have to verify your email before you can vote'}
            )

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
                return jsonify({'message': 'value for {} is empty'.format(key)})

        title = poll['title']
        options_query = lambda option: Options.query.filter(Options.name.like(option))

        options = [Polls(option=Options(name=option))
                   if options_query(option).count() == 0
                   else Polls(option=options_query(option).first()) for option in poll['options']
                   ]
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
@requires_auth
def api_poll_vote():
    poll = request.get_json()

    poll_title, option = (poll['poll_title'], poll['option'])

    join_tables = Polls.query.join(Topics).join(Options)

    # Get topic and username
    topic = Topics.query.filter_by(title=poll_title, status=True).first()
    user = session['profile'].get('email') or session['profile'].get('nickname')

    # if poll was closed in the background before user voted
    if not topic:
        return jsonify({'message': 'Sorry! this poll has been closed'})

    # filter options
    option = join_tables.filter(Topics.title.like(poll_title)).filter(Options.name.like(option)).first()

    # check if the user has voted on this poll
    poll_count = UserPolls.query.filter_by(topic_id=topic.id).filter_by(user_identifier=user).count()
    if poll_count:
        return jsonify({'message': 'Sorry! multiple votes are not allowed'})

    if option:
        # record user and poll
        user_poll = UserPolls(topic_id=topic.id, user_identifier=user)
        db.session.add(user_poll)

        # increment vote_count by 1 if the option was found
        option.vote_count += 1
        db.session.commit()

        return jsonify({'message': 'Thank you for voting'})

    return jsonify({'message': 'option or poll was not found please try again'})


@api.route('/poll/<poll_name>')
def api_poll(poll_name):
    poll = Topics.query.filter(Topics.title.like(poll_name)).first()

    return jsonify({'Polls': [poll.to_json()]}) if poll else jsonify({'message': 'poll not found'})
