from sqlalchemy.orm import sessionmaker, Session


def get_session(maker: sessionmaker[Session]):
    session = maker()
    return session
