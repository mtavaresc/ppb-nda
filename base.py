from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

engine = create_engine("mysql+pymysql://developer:123456@localhost:3306/playbooks?charset=utf8mb4&binary_prefix=true")
if not database_exists(engine.url):
    create_database(engine.url)

Session = sessionmaker(bind=engine)

Base = declarative_base()
