import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db = os.getenv("DB_NAME")

DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

engine = create_engine(DB_URL, pool_recycle=28000, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pg_user = os.getenv("PG_DB_USER")
pg_passwd = os.getenv("PG_DB_PASSWD")
pg_host = os.getenv("PG_DB_HOST")
pg_port = os.getenv("PG_DB_PORT")
pg_db = os.getenv("PG_DB_NAME")

PG_DB_URL = f'mysql+pymysql://{pg_user}:{pg_passwd}@{pg_host}:{pg_port}/{pg_db}?charset=utf8'

pg_engine = create_engine(PG_DB_URL, pool_recycle=28000, pool_pre_ping=True)
PlaygroundSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)
PlaygroundBase = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_playground_db():
    db = PlaygroundSessionLocal()
    try:
        yield db
    finally:
        db.close()
