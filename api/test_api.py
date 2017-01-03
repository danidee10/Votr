from votr import votr, db, celery
from multiprocessing import Process
import requests
import os
import time
from tasks import close_poll

import jwt
import config

# Load env file
from dotenv import Dotenv
try:
    env = Dotenv('.env')
except IOError:
    env = os.environ


# helper to generate JWT's
def generate_token(payload):
    token = jwt.encode(payload, env[config.AUTH0_CLIENT_SECRET],
                       algorithm='HS256').decode()
    return token


class Testvotr():

    @classmethod
    def setUpClass(cls):
        votr.config['DEBUG'] = False
        votr.config['TESTING'] = True
        cls.DB_PATH = os.path.join(os.path.dirname(__file__), 'votr_test.db')
        votr.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.\
            format(cls.DB_PATH)
        celery.conf.update(CELERY_ALWAYS_EAGER=True)
        cls.hostname = 'http://localhost:7000'

        with votr.app_context():
            db.init_app(votr)
            db.create_all()
            cls.p = Process(target=votr.run, kwargs={'port': 7000})
            cls.p.start()
            time.sleep(2)

        # create new poll
        poll = {"title": "Flask vs Django",
                "options": ["Flask", "Django"],
                "close_date": 1581556683}
        requests.post(cls.hostname + '/api/polls', json=poll).json()

        # There is no need to test Auth0's auth so let's create a JWT
        payload = {'email_verified': True, 'email': 'admin@gmail.com',
                   'aud': env[config.AUTH0_CLIENT_ID]}

        cls.verified_jwt = generate_token(payload)

    def setUp(self):
        self.poll = {"title": "who's the fastest footballer",
                     "options": ["Hector bellerin", "Gareth Bale",
                                 "Arjen robben"],
                     "close_date": 1581556683}

    def test_empty_option(self):
        result = requests.post(self.hostname + '/api/polls',
                               json={"title": self.poll['title'],
                                     "options": []}).json()
        assert {'message': 'value for options is empty'} == result

    def test_empty_title(self):
        result = requests.post(self.hostname + '/api/polls',
                               json={"title": "",
                                     "options": self.poll['options']}).json()
        assert {'message': 'value for title is empty'} == result

    def test_new_poll(self):
        result = requests.post(self.hostname + '/api/polls',
                               json=self.poll).json()
        assert {'message': 'Poll created succesfully'} == result

    def vote(self, jwt):
        headers = {'Authorization': 'Bearer ' + jwt}
        result = requests.patch(self.hostname + '/api/poll/vote',
                                json={'poll_title': self.poll['title'],
                                      'option': self.poll['options'][0]},
                                headers=headers).json()
        return result

    def test_voting(self):
        result = self.vote(self.verified_jwt)
        assert {'message': 'Thank you for voting'} == result

    def test_voting_twice(self):
        result = self.vote(self.verified_jwt)
        assert {'message':
                'Multiple votes are not allowed on this poll'} == result

    def test_not_verified_voter(self):
        # Generate a JWT for a user that hasn't verified their email
        payload = {'email_verified': False, 'email': 'example@gmail.com',
                   'aud': env[config.AUTH0_CLIENT_ID]}
        unverified_jwt = generate_token(payload)
        result = self.vote(unverified_jwt)

        assert {'message':
                'You have to verify your email before you vote'} == result

    def test_celery_task(self):

        result = close_poll.apply((1, votr.config['SQLALCHEMY_DATABASE_URI']))

        assert 'poll closed succesfully' == result.get()

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.DB_PATH)
        cls.p.terminate()
