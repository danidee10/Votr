from votr import votr, db, celery
from multiprocessing import Process
import requests
import os
import time
from tasks import close_poll


class Testvotr():

    @classmethod
    def setUpClass(cls):
        votr.config['DEBUG'] = False
        votr.config['TESTING'] = True
        cls.DB_PATH = os.path.join(os.path.dirname(__file__), 'votr_test.db')
        votr.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(cls.DB_PATH)
        celery.conf.update(CELERY_ALWAYS_EAGER=True)
        cls.hostname = 'http://localhost:7000'
        cls.session = requests.Session()

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

        # create new admin user
        signup_data = {'email': 'admin@gmail.com', 'username': 'Administrator',
                       'password': 'admin'}
        requests.post(cls.hostname + '/signup', data=signup_data).text

    def setUp(self):
        self.poll = {"title": "who's the fastest footballer",
                     "options": ["Hector bellerin", "Gareth Bale", "Arjen robben"],
                     "close_date": 1581556683}

    def test_new_user(self):
        signup_data = {'email': 'user@gmail.com', 'username': 'User',
                       'password': 'password'}

        result = requests.post(self.hostname + '/signup', data=signup_data).text

        assert 'Thanks for signing up please login' in result

    def test_login(self):

        # Login data
        data = {'username': 'Administrator', 'password': 'admin'}
        result = self.session.post(self.hostname + '/login', data=data).text

        assert 'Create a poll' in result

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
        result = requests.post(self.hostname + '/api/polls', json=self.poll).json()
        assert {'message': 'Poll was created succesfully'} == result

    def vote(self):
        result = self.session.patch(self.hostname + '/api/poll/vote',
                                    json={'poll_title': self.poll['title'],
                                          'option': self.poll['options'][0]}).json()
        return result

    def test_voting(self):
        result = self.vote()
        assert {'message': 'Thank you for voting'} == result

    def test_voting_twice(self):
        result = self.vote()
        assert {'message': 'Sorry! multiple votes are not allowed'} == result

    def test_celery_task(self):

        result = close_poll.apply((1, votr.config['SQLALCHEMY_DATABASE_URI'])).get()

        assert 'poll closed succesfully' == result

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.DB_PATH)
        cls.p.terminate()
