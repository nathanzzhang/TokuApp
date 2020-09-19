import os
import random

base = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "".join([chr(random.randint(65, 92)) for _ in range(50)])
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]