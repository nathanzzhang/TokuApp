import os
import sqlite3
import datetime
import json
import models as models
import jwt as jwt_decode
from flask import Flask, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
)

app = Flask(__name__)

#load main config
app.config.from_pyfile('../config.py') 
jwt = JWTManager(app)
db = SQLAlchemy(app)
db.app = app
db.init_app(app)
DEBUG = True
blacklist = set()


@app.route("/")
def index():
    db_users = models.User.query.all()
    users_dict = {user.username: user.username for user in db_users}
    return render_template("index.html")



@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html"), 200
    if request.method == "POST":
        req = request.form
        username = req.get("username", None)
        password = req.get("password", None)
        confirm_password = req.get("confirmpassword", None)
        if not password == confirm_password:
            return jsonify({"message": "Error, passwords don't match"}), 400
        name = req.get("name", None)
        birthday = req.get("birthday")
        gender = req.get("gender")
        email = req.get("email")
        friend = models.Friend(None, None, None, None)

        access_token = create_access_token(identity=username)
        decoded = jwt_decode.decode(access_token, verify=False)
        current_token = decoded["jti"]

        new_user = models.User(username, password, current_token, name, birthday, gender, email, str(datetime.datetime.utcnow()), "", "", friend)
        
        temp_user = models.User.query.filter_by(username=new_user.username).first()
        if temp_user:
            return jsonify({"message": "User already exists."}), 400
    return render_template("languages.html",username=username), 200

@app.route('/languages', methods=["POST", "GET"])
def languages():
    username = request.args.get('username')
    user = models.User.query.filter_by(username=username).first()
    if request.method == "GET":
        return render_template("languages.html")
    if request.method == "POST":
        default = ["English", "Korean", "Japanese", "Chinese", "Spanish", "French"]
        user_languages = []
        match_languages = []
        req = request.form
        for language in default:
            print(req.get(language+"1"))
            if(req.get(language + "1")):
                user_languages.append(language)
            if(req.get(language + "2")):
                match_languages.append(language)
        if user_languages and match_languages:
            user.user_languages.set_user_languages(str(user_languages).strip('[]'))
            user.match_languages.set_match_languages(str(match_languages).strip('[]'))
            db.session.add(new_user)
            db.session.commit()
        else:
            return jsonify({"message": "Must select at least one language for both"})
    return redirect('/profile'), 200

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

        temp_user = models.User.query.filter_by(username=username).first()
        if not temp_user:
            return jsonify({"message": "User not found."}), 400
        if not temp_user.password == password:
            return jsonify({"message": "Invalid password."}), 400

        user = temp_user
        access_token = create_access_token(identity=username)
        session['current_token'] = access_token
        db.session.commit()
    return render_template("profile.html", username=user.username, name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created, access_token=access_token), 200


@app.route("/logout", methods=["PUT","GET"])
def logout():
    """Endpoint for revoking the current users access token"""
    session.pop('current_token', None)
    return render_template("index.html"), 200


@app.route("/profile", methods=["POST", "GET"])
def profile():
    current_token = session['current_token']
    user = models.User.query.filter_by(current_token=current_token).first()
    if request.method == "PUT":
        req = request.form
        user.set_name(req.get('name'))
        user.set_birthday(req.get('birthday'))
        user.set_email(req.get('email'))
        user.set_gender(req.get('gender'))
    return render_template("profile.html", name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created), 200

        

@app.route("/match", methods=["POST", "GET"])
def match():
    current_token = session['current_token']
    user = models.User.query.filter_by(current_token=current_token).first()
    match_usernames = []
    for language in user.match_languages:
        matches = models.User.query.filter_by(language=language).all()
        for match in matches:
            if match.username is not user.username:
                match_usernames.append(match.username)
    # friend = models.Friend(id, username, name, languages, user_id)
    return jsonify({"matches":matches}), 200

@app.route("/friends", methods=["POST"])
@jwt_required
def get_friends():
    current_token = session['current_token']
    user = models.User.query.filter_by(current_token=current_token).first()

    # if not request.is_json:
    #     return jsonify({"message": "Missing JSON in request"}), 400
    # title = request.json.get("title")
    # body = request.json.get("body")

    friends = Friend.query.filter_by(user_id=user.username).all()
    return jsonify([friend.to_dict() for friend in friends]), 200

    
@app.route("/users", methods=["GET"])
def get_users():
    users = models.User.query.all()
    return json.dumps([user.username for user in users])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

# @app.route("/post", methods=["POST"])
# def post():
#     if request.method == "POST":
#         print(request)
#         post_info = request.get_json()
#         new_post = Post(title=post_info['title'], description=post_info['description'])
#         db.session.add(new_post)
#         db.session.commit()
#     return redirect("/")

# @app.route("/change_facts", methods=["POST"])
# def change_facts():
#     if request.method == "POST":
#         change_facts = request.get_json()
#         for key, value in change_facts.items():
#             if Fact.query.filter(Fact.name == key).first() is None:
#                 new_fact = Fact(name=key, value=value)
#                 db.session.add(new_fact)
#         db.session.commit()
#     return redirect("/")
