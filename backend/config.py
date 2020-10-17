import os
import sqlite3
import random
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///../app.db', echo=True)
Session = sessionmaker(bind=engine, autoflush=False)
session = Session()
Base = declarative_base()
Base.metadata.create_all(engine)

base = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base, '../app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "".join([chr(random.randint(65, 92)) for _ in range(50)])



