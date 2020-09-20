import os
import sqlite3
import datetime
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


@app.route("/")
def index():
    db_users = models.User.query.all()
    users_dict = {user.username: user.username for user in db_users}
    return render_template("index.html")


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token["jti"]
    username = decrypted_token["identity"]
    return models.User.query.filter_by(username=username, current_token=jti).first() == None

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

        global new_user
        new_user = models.User(username, password, current_token, name, birthday, gender, email, str(datetime.datetime.utcnow()), "", "", friend)
        
        temp_user = models.User.query.filter_by(username=new_user.username).first()
        if temp_user:
            return jsonify({"message": "User already exists."}), 400

    return redirect(url_for('languages')), 200

@app.route('/languages', methods=["POST", "GET"])
def languages():
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
        new_user.user_languages = str(user_languages).strip('[]')
        new_user.match_languages = str(match_languages).strip('[]')
        db.session.add(new_user)
        db.session.commit()
    return render_template("profile.html", name=new_user.name, birthday=new_user.birthday, gender=new_user.gender, date_created=new_user.created), 200

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
        access_token = create_access_token(identity=user.username)
        decoded = jwt_decode.decode(access_token, verify=False)
        user.current_token = decoded["jti"]
        db.session.commit()
    return render_template("profile.html"), 200

@app.route("/logout", methods=["DELETE"])
@jwt_required
def logout():
    """Endpoint for revoking the current users access token"""
    jti = get_raw_jwt().get("jti")
    user = models.User.query.filter_by(current_token=jti)
    user.current_token = None
    db.session.commit()
    return jsonify({"message": "Successfully logged out"}), 200

@app.route("/protected", methods=["GET"])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route("/match", methods=["POST", "GET"])
def match():
    jti = get_raw_jwt().get("jti")
    if not jti:
        return jsonify({"message": "Missing Authorization Header"}), 400
    user = models.User.query.filter_by(current_token=jti).first()
    language = request.args.get('language')
    matches = models.Friend.query.filter_by(language=language).all()
    matches_dict = {match.username: match.username for match in matches}
    friend = models.Friend(id, username, name, languages, user_id)
    user.poems.append(friend)
    db.session.commit()
    return redirect(url_for("/friends", match=match)), 200

@app.route("/friends", methods=["POST"])
@jwt_required
def get_friends():
    jti = get_raw_jwt().get("jti")
    if not jti:
        return jsonify({"message": "Missing Authorization Header"}), 400
    user = models.User.query.filter_by(current_token=jti).first()

    # if not request.is_json:
    #     return jsonify({"message": "Missing JSON in request"}), 400
    # title = request.json.get("title")
    # body = request.json.get("body")

    
    friends = Friend.query.filter_by(user_id=user).all()
    return jsonify([friend.to_dict() for friend in friends])
    return jsonify(message="Successfully created poem"), 200

    
@app.route("/users", methods=["GET"])
def get_users():
    """
    Endpoint that returns all users

    responses:
        200:
        all users as list
    """
    users = models.User.query.all()
    return jsonify([user.to_dict() for user in users])

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
