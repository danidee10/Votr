import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import Topics
import config
from votr import celery


def connect():
    """Connects to the database and return a session"""

    uri = config.SQLALCHEMY_DATABASE_URI

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(uri)

    # create a Session
    Session = sessionmaker(bind=con)
    session = Session()

    return con, session

con, session = connect()


@celery.task
def close_poll(topic_id):
    topic = session.query(Topics).get(topic_id)
    topic.status = False
    session.commit()
