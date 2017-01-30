from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func
import uuid

# create a new SQLAlchemy object
db = SQLAlchemy()


# Base model that for other models to inherit from
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


# Model to store user details
class Users(Base):
    client_id = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(50), unique=True)  # TODO remove
    password = db.Column(db.String(300))  # TODO remove

    def __repr__(self):
        return self.email


class Topics(Base):
    """Model for poll topics."""

    title = db.Column(db.String(500))
    status = db.Column(db.Boolean, default=True)  # to close or open poll
    create_uid = db.Column(db.ForeignKey('users.id'))
    close_date = db.Column(db.DateTime)
    unique_id = db.Column(db.String(11))  # unique 10 char hex string

    user_identifier = db.Column(db.String(100))

    # user friendly way to display the object
    def __repr__(self):
        return self.title

    # returns dictionary that can easily be jsonified
    def to_json(self):
        return {
                'title': self.title,
                'unique_id': self.unique_id,
                'options': [{'name': option.option.name,
                            'vote_count': option.vote_count}
                            for option in self.options.all()],
                'close_date': self.close_date,
                'status': self.status,
                'total_vote_count': self.total_vote_count
            }

    @hybrid_property
    def total_vote_count(self, total=0):
        for option in self.options.all():
            total += option.vote_count

        return total

    @total_vote_count.expression
    def total_vote_count(cls):
        return select([func.sum(Polls.vote_count)]).\
               where(Polls.topic_id == cls.id)


# Model for poll options
class Options(Base):
    name = db.Column(db.String(200), unique=True)

    def __repr__(self):
        return self.name

    def to_json(self):
        return {
                'id': uuid.uuid4(),  # Generates a random uuid
                'name': self.name
        }


# Polls model to connect topics and options together
class Polls(Base):

    # Columns declaration
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'))
    vote_count = db.Column(db.Integer, default=0)

    topic = db.relationship('Topics', foreign_keys=[topic_id],
                            backref=db.backref('options', lazy='dynamic'))
    option = db.relationship('Options', foreign_keys=[option_id])

    def __repr__(self):
        # a user friendly way to view our objects in the terminal
        return self.option.name


class UserPolls(Base):

    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    user_identifier = db.Column(db.String(100))

    topics = db.relationship('Topics', foreign_keys=[topic_id],
                             backref=db.backref('voted_on_by', lazy='dynamic'))

    def __repr__(self):
        return self.user_identifier
