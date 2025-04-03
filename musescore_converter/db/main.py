from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base

DATABASE_URL = "sqlite:///score_metadata.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
