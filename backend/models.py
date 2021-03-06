from app import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField
from flask_login import UserMixin



class User(UserMixin, db.Model):
	username = db.Column(db.String, primary_key=True, unique=True, nullable=False)
	password = db.Column(db.String, unique=True, nullable=False)
	current_token = db.Column(db.String)
	name = db.Column(db.String)
	birthday = db.Column(db.String)
	gender = db.Column(db.String)
	email = db.Column(db.String)
	created = db.Column(db.String, nullable=False)
	user_languages = db.Column(db.String, nullable=False)
	match_languages = db.Column(db.String, nullable=False)
	friends = db.Column(db.String)

	def set_name(self, name):
		self.name = name
	def set_email(self, email):
		self.email = email
	def set_birthday(self, birthday):
		self.birthday = birthday
	def set_gender(self, gender):
		self.gender = gender
	def set_user_languages(self, user_languages):
		self.user_languages = user_languages
	def set_match_languages(self, match_languages):
		self.match_languages = match_languages
	def set_current_token(self, current_token):
		self.current_token = current_token

	def check_password(self, password):
		return check_password_hash(self.password, password)
	
	def set_password(self, password):
		self.password = generate_password_hash(password)
	
	def get_id(self):
		return self.username

	def get(user_id):
		return User.query.filter_by(username=user_id).first()

	def is_authenticated(self):
		return User.query.filter_by(username=self.username).first().password == self.password

	def is_active(self):
		return is_authenticated(self)
	
	def is_anonymous(self):
		return False

	def to_dict(self):
		"""returns dict representation of User"""
		return {
			"username": self.username,
			"password": self.password,
			"name": self.name,
			"birthday": self.birthday,
			"gender": self.gender,
			"email": self.email,
			"created": self.created,
			"user_languages": self.user_languages,
			"match_languages": self.match_languages,
			#"friends": [friend.to_dict() for friend in self.friends]
			
		}
	def __init__(self, username, password, current_token, name, birthday, gender, email, created, user_languages, match_languages):
		self.username=username
		self.password=password
		self.current_token=current_token
		self.name=name
		self.birthday=birthday
		self.gender=gender
		self.email=email
		self.created=created
		self.user_languages=user_languages
		self.match_languages=match_languages


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	description = db.Column(db.String(500))

class Friend(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String)
	name = db.Column(db.String)
	languages = db.Column(db.String)
	user_id = db.Column(db.String, db.ForeignKey("user.username"))
	def __init__(self, username, name, languages, user_id):
	 	self.username=username
	 	self.name=name
	 	self.languages=languages
	 	self.user_id=user_id

	def to_dict(self):
		"""return dictionary representation of Friend"""
		return {
			"username": self.username,
			"name": self.name,
			"languages": self.languages
		}


class Blacklist(db.Model):
	jwt_token = db.Column(db.String, unique=True, nullable=False, primary_key=True)



