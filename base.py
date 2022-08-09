from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base

engine = create_engine("sqlite:///users.db", echo=True)
metadata = MetaData()
Base = declarative_base()

session = Session(engine, autocommit=True)

def get_session():
    return session
