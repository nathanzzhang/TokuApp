import os
import sqlite3
import smtplib, ssl
import datetime
import json
import models as models
from flask import Flask, session, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for
from flask_mail import Mail, Message

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

app = Flask(__name__)

#load main config
app.config.from_pyfile('./config.py') 
mail = Mail(app)
db = SQLAlchemy(app)
db.app = app
db.init_app(app)
DEBUG = True

# make data tables
if not os.path.exists("app.db"):
    print("db doesn't exist. creating new db")
    open("app.db", "w+")
print("Connecting to db")
conn = sqlite3.connect("app.db", check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS user (username TEXT, password TEXT, current_token TEXT, name TEXT, birthday TEXT, gender TEXT, email TEXT, created TEXT, user_languages TEXT, match_languages TEXT, friends TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS friend (id INT, username TEXT, name TEXT, languages TEXT, user_id TEXT)')
c = conn.cursor()

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
        
    return render_template("languages.html"), 200

@app.route('/languages', methods=["POST", "GET"])
def languages():
    username = session['username']
    user = models.User.query.filter_by(username=username).first()
    
    if request.method == "GET":
        return render_template("languages.html")
    if request.method == "POST":
        default = ["English", "Korean", "Japanese", "Chinese", "Spanish", "French"]
        user_languages = []
        match_languages = []
        req = request.form
        for language in default:
            if(req.get(language + "1")):
                user_languages.append(language)
            if(req.get(language + "2")):
                match_languages.append(language)
        if user_languages != [] and match_languages != []:
            updated_user_languages = ', '.join(user_languages)
            updated_match_languages = ', '.join(match_languages)
            user.set_user_languages(updated_user_languages)
            user.set_match_languages(updated_match_languages)
            print(updated_user_languages)
            print(updated_match_languages)
            c.execute("""UPDATE user SET user_languages='%s' WHERE username='%s'""" % (updated_user_languages, user.username))
            c.execute("""UPDATE user SET match_languages='%s' WHERE username='%s'""" % (updated_match_languages, user.username))
            db.session.flush()
            db.session.commit()
            login_user(user)
        else:
            return jsonify({"message": "Must select at least one language for both"})
    return render_template("profile.html", username=user.username, name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created, user_languages=user.user_languages, match_languages=user.match_languages), 200


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
        if not user:
            return jsonify({"message": "User not found."}), 400
        if not user.check_password(password):
            return jsonify({"message": "Invalid password."}), 400
        login_user(user)
    #print(c.execute("SELECT * FROM user WHERE username='%s'" % current_user.username).fetchall())
    return render_template("profile.html", username=user.username, name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created, user_languages=user.user_languages, match_languages=user.match_languages), 200


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
        if(req.get('user_languages')):
            user.set_user_languages(req.get('user_languages'))
        if(req.get('match_languages')):
            user.set_match_languages(req.get('match_languages'))
    
    return render_template("profile.html",name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created, user_languages=user.user_languages, match_languages=user.match_languages), 200

    

@app.route("/match", methods=["POST", "GET"])
@login_required 
def match():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    username = current_user.username
    user = models.User.query.filter_by(username=username).first()
    if request.method == "GET":
        return render_template("matchpage.html", matches=get_matches())
    if request.method == "POST":
        current_friends=""
        if user.friends:
            current_friends = str(user.friends) 
        current_friends += request.get_json() + ", " #fix this later
        print(current_friends)
        c.execute("""UPDATE user SET friends='%s' WHERE username='%s'""" % (current_friends, username))
        
        return render_template("matchpage.html", matches=get_matches())

def get_matches():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    username = current_user.username
    user = models.User.query.filter_by(username=username).first()
    #print(user.match_languages)
    matches = {}
    if "," in user.match_languages:
        match_language_list = list(user.match_languages.split(","))
    else:
        match_language_list = [user.match_languages]
    for language in match_language_list: #for every language that you want to learn
        print(language)
        for match in models.User.query.all(): #for every user in the database
            if match.username is not user.username: #if you are not matched with yourself
                if user.friends:
                    if match.username in list(user.friends.split(",")):
                        break
                match_user_languages = list(match.user_languages.split(","))
                if language in match_user_languages: #if the language you want to learn is a language that the user is fluent in
                    matches[match.username] = language #a new element is made with key = username and its value equal to the language dictionary
    print(matches) 
    print(user.friends)               
    return matches

@app.route("/friends", methods=["POST", "GET"])
@login_required
def friends():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    username = current_user.username
    user = models.User.query.filter_by(username=username).first()
    email = user.email
    match_email = 'toku.user2@gmail.com'
    if request.method == "GET":
        return render_template('friends.html', email=email, match_email=match_email, friends=get_friends()), 200
    if request.method == "POST":
        sender = email
        if DEBUG:
            sender = "toku.user1@gmail.com" #test
            recipient_test="skyjung4243@gmail.com"
        password = 'tokutest1!'
        print(password)
        subject = "Toku friend message"
        text = request.form.get("text") 
        print(text)
        message = "Subject: {}\n\n{}".format(subject, text)
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipient_test, message.encode('utf8'))
        smtp_server.close()
    return render_template("friends.html", email=email, match_email=match_email, friends=get_friends()), 200

def get_friends():
    friends = {'user2': 'Spanish'}
    return friends
def get_emails():
    friends = get_friends.keys()
    match_emails = {}
    for friend in friends:
        match_emails[friend] = models.User.query.filter_by(username=friend).first().email
    return match_emails
    

@app.route('/faq', methods=["GET"])
def faq():
    return render_template('faq.html')
    
@app.route("/users", methods=["GET"])
@login_required
def get_users():
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    users = models.User.query.all()
    return json.dumps([user.username for user in users])

if __name__ == '__main__':
    if DEBUG:
        db.create_all()

        user1 = models.User(username="user1",
            password="test",
            current_token="token",
            name="user1",
            birthday="01/10/2000",
            gender="Male",
            email="toku.user1@gmail.com",
            created = str(datetime.datetime.utcnow()),
            user_languages = "English, French, Korean",
            match_languages = "Chinese, Spanish")
        user1.set_password("test")
        
        user2 = models.User(username="user2",
            password="test",
            current_token="token",
            name="user2",
            birthday="05/10/2003",
            gender="Female",
            email="toku.user2@gmail.com",
            created = str(datetime.datetime.utcnow()),
            user_languages = "Chinese, Spanish",
            match_languages = "English, French, Korean")
        user2.set_password("test")

        anna = models.User(username="anna",
            password="password",
            current_token="token",
            name="anna",
            birthday="05/10/2003",
            gender="Female",
            email="toku.user2@gmail.com",
            created = str(datetime.datetime.utcnow()),
            user_languages = "Chinese, English",
            match_languages = "Japanese, French, Korean")
        anna.set_password("password")
        
        db.session.add_all([user1, user2, anna])
        db.session.commit()
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)


