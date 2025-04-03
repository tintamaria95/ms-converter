import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from musescore_converter.Score import ScorePage
from musescore_converter.db.models import Base
from musescore_converter.db.crud import create_score, get_score, delete_score

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
TEST_SCORE_ID = "abc123"
TEST_SCORE = ScorePage(
    id=TEST_SCORE_ID, page="0", title="La Branche", author="MLD", composer="Bekar"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_score(db):

    created_score = create_score(db=db, score=TEST_SCORE)
    assert created_score.id == TEST_SCORE_ID


def test_get_score(db):
    created_score = create_score(db=db, score=TEST_SCORE)
    score = get_score(db, created_score.id)
    assert score is not None
    assert score.id == TEST_SCORE_ID


def test_delete_score(db):
    # Create a user to test deletion
    created_score = create_score(db=db, score=TEST_SCORE)
    result = delete_score(db, created_score.id)
    assert result is True

    deleted_user = get_score(db, created_score.id)
    assert deleted_user is None
