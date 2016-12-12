import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import Topics
from votr import celery


def connect(uri):
    """Connects to the database and return a session"""

    uri = uri

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(uri)

    # create a Session
    Session = sessionmaker(bind=con)
    session = Session()

    return con, session


@celery.task
def close_poll(topic_id, uri):
    con, session = connect(uri)

    topic = session.query(Topics).get(topic_id)
    topic.status = False
    session.commit()

    return 'poll closed succesfully'
