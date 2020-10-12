import os
import sqlite3
import datetime
import json
import models as models
from flask import Flask, session, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for


from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

app = Flask(__name__)

#load main config
app.config.from_pyfile('../config.py') 
db = SQLAlchemy(app)
db.app = app
db.init_app(app)
DEBUG = True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    return models.User.get(user_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html"), 200

    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")
        confirm_password = req.get("confirmpassword")
        if not password == confirm_password:
            return jsonify({"message": "Error, passwords don't match"}), 400
        name = req.get("name", None)
        birthday = req.get("birthday")
        gender = req.get("gender")
        email = req.get("email")
        current_token = ""

        new_user = models.User(
            username,
            password,
            current_token,
            name,
            birthday,
            gender,
            email,
            str(datetime.datetime.utcnow()),
            "",
            ""
        )
        new_user.set_password(password)
        """check if user exists"""
        temp_user = models.User.query.filter_by(username=username).first()
        if temp_user:
            return jsonify({"message": "User already exists."}), 400
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        print(new_user.created)
    return render_template("languages.html"), 200

@app.route('/languages', methods=["POST", "GET"])
def languages():
    username = session['username']
    user = models.User.query.filter_by(username=username).first()
    print(username)
    if request.method == "GET":
        return render_template("languages.html")
    if request.method == "POST":
        default = ["English", "Korean", "Japanese", "Chinese", "Spanish", "French"]
        user_languages = []
        match_languages = []
        req = request.form
        for language in default:
            print(req.get(language+"1"))
            print(req.get(language+"2"))
            if(req.get(language + "1")):
                user_languages.append(language)
            if(req.get(language + "2")):
                match_languages.append(language)
        if user_languages != [] and match_languages != []:
            user.set_user_languages(str(user_languages).strip('[]'))
            user.set_match_languages(str(match_languages).strip('[]'))
            print(user.match_languages)
            login_user(user)
            db.session.add(user)
            db.session.commit()
        else:
            return jsonify({"message": "Must select at least one language for both"})
    return render_template("profile.html", username=user.username, name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created), 200


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html"), 200
    if request.method == "POST":
        req = request.form
        username = req.get("username", None)
        password = req.get("password", None)
        
        if not username:
            return jsonify({"message": "Username is required."}), 400
        if not password:
            return jsonify({"message": "Password is required."}), 400

        user = models.User.query.filter_by(username=username).first()
        print(user)
        print(user.match_languages)
        if not user:
            return jsonify({"message": "User not found."}), 400
        if not user.check_password(password):
            return jsonify({"message": "Invalid password."}), 400
        login_user(user)
    return render_template("profile.html", username=user.username, name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created), 200


@app.route("/logout", methods=["PUT","GET"])
@login_required
def logout():
    """Endpoint for revoking the current users access token"""
    logout_user()
    return render_template("index.html"), 200


@app.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    username = current_user.username
    user = models.User.query.filter_by(username=username).first()
    if request.method == "POST":
        req = request.form
        if(req.get('name')):
            user.set_name(req.get('name'))
        if(req.get('birthday')):
            user.set_birthday(req.get('birthday'))
        if(req.get('email')):
            user.set_email(req.get('email'))
        if(req.get('gender')):
            user.set_gender(req.get('gender'))
    
    return render_template("profile.html",name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created), 200

        

@app.route("/match", methods=["POST", "GET"])
@login_required 
def match():
    return render_template("matchpage.html", matches=get_matches())

def get_matches():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    username = current_user.username
    user = models.User.query.filter_by(username=username).first()
    print(user.match_languages)
    matches = {}
    if "," in user.match_languages:
        match_language_list = list(user.match_languages.split(","))
    else:
        match_language_list = [user.match_languages]
    for language in match_language_list: #for every language that you want to learn
        for match in models.User.query.all(): #for every user in the database
            if match.username is not user.username: #if you are not matched with yourself
                match_user_languages = list(match.user_languages.split(","))
                print(match_user_languages)
                if language in match_user_languages: #if the language you want to learn is a language that the user is fluent in
                    matches[match.username] = language #a new element is made with key = username and its value equal to the language dictionary
    print(matches)
    return matches

@app.route("/friends", methods=["POST", "GET"])
@login_required
def get_friends():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    user = current_user
    #user = models.User.query.filter_by(current_token=current_token).first()
    friends = models.Friend.query.filter_by(user_id=user.username).all()
    return json.dumps([friend.username for friend in friends]), 200

    
@app.route("/users", methods=["GET"])
@login_required
def get_users():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    users = models.User.query.all()
    return json.dumps([user.username for user in users])

if __name__ == '__main__':
    if DEBUG:
        #db.drop_all()
        db.create_all()

        u1 = models.User(username="u1",
            password="test",
            current_token="token",
            name="u1",
            birthday="XX/XX/XXXX",
            gender="Male",
            email="u1@gmail.com",
            created = str(datetime.datetime.utcnow()),
            user_languages = "English, French, Korean",
            match_languages = "Chinese, Spanish")
        u1.set_password("test")
        
        u2 = models.User(username="u2",
            password="test",
            current_token="token",
            name="u2",
            birthday="XX/XX/XXXX",
            gender="Male",
            email="u2@gmail.com",
            created = str(datetime.datetime.utcnow()),
            user_languages = "Chinese, Spanish",
            match_languages = "English, French, Korean")
        u2.set_password("test")
        
        db.session.add_all([u1, u2])
        db.session.commit()
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)


