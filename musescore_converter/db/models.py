from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ScoreMetadataModel(Base):
    __tablename__ = "score_metadata"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    composer = Column(String)
