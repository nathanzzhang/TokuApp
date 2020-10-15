import os
import sqlite3
import random
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///app.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
Base.metadata.create_all(engine)

base = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "".join([chr(random.randint(65, 92)) for _ in range(50)])


# make data tables
if not os.path.exists("app.db"):
    print("db doesn't exist. creating new db")
    open("app.db", "w+")
print("Connecting to db")
conn = sqlite3.connect("app.db")
print("Saving data to db")
conn.execute('CREATE TABLE IF NOT EXISTS user (username TEXT, password TEXT, current_token TEXT, name TEXT, birthday TEXT, gender TEXT, email TEXT, created TEXT, user_languages TEXT, match_languages TEXT, friends TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS friend (id INT, username TEXT, name TEXT, languages TEXT, user_id TEXT)')

#cursor1 = conn.cursor()
#nate6="nate6"
#cursor1.execute("SELECT * FROM user")
#result = cursor1.fetchall()
#for r in result:
#    print(r)


