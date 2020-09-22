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
)
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
jwt = JWTManager(app)
db = SQLAlchemy(app)
db.app = app
db.init_app(app)
DEBUG = True

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return models.User.query.filter_by(id=user_id).first()


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
        friend = models.Friend(username="", name="", languages="")
        current_token = create_access_token(identity=username)
        new_user = models.User(
            username=username,
            password=password,
            current_token=current_token,
            name=name,
            birthday=birthday,
            gender=gender,
            email=email,
            created=datetime.datetime.utcnow(),
            user_languages="",
            match_languages="",
        )
        temp_user = models.User.query.filter_by(username=username).first()
        if temp_user:
            return jsonify({"message": "User already exists."}), 400

        login_user(new_user)
        db.session.add(new_user)
        db.session.commit()
    return render_template("languages.html", username=username), 200

@app.route('/languages', methods=["POST", "GET"])
def languages():
    username=request.args.get("username")
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
        if user_languages != [] and match_languages != []:
            user.set_user_languages(str(user_languages).strip('[]'))
            user.set_match_languages(str(match_languages).strip('[]'))
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
        if not user:
            return jsonify({"message": "User not found."}), 400
        if not user.password == password:
            return jsonify({"message": "Invalid password."}), 400

        user.set_password(password)
        login_user(user)
        db.session.commit()
    return redirect(url_for("profile"), username=current_user.username), 200
    return render_template("profile.html", username=user.username, name=user.name, birthday=user.birthday, gender=user.gender, email=user.email, date_created=user.created), 200


@app.route("/logout", methods=["PUT","GET"])
def logout():
    """Endpoint for revoking the current users access token"""
    logout_user()
    return render_template("index.html"), 200


@app.route("/profile", methods=["POST", "GET"])
def profile():
    username = request.args.get("username")
    user = models.User.query.filter_by(username=username).first()
    if request.method == "POST" and form.validate_on_submit():
        req = request.form
        user.set_name(req.get('name'))
        user.set_birthday(req.get('birthday'))
        user.set_email(req.get('email'))
        user.set_gender(req.get('gender'))
    
    return render_template("profile.html"), 200

        

@app.route("/match", methods=["POST", "GET"])
def match():
    # if request.method == "GET":
    #     current_token = session['current_token']
    #     if not current_token:
    #         return jsonify({"message": "Please log back in."})
    # if request.method == "POST":
    #     current_token = request.args.get("get_current_token")
    #     print(current_token)
    user = current_user
    #user = models.User.query.filter_by(current_token=current_token).first()
    matches = {}
    for language in user.match_languages:
        for match in models.User.query.all():
            if match.username is not user.username:
                for language2 in match.user_languages:
                    if language == language2:
                        languages = {}
                        languages[language2] = language
                        matches[match.username] = languages
    
    return render_template("matchpage.html", matches=matches)
    return jsonify({"matches":matches}), 200

@app.route("/friends", methods=["POST", "GET"])
def get_friends():
    user = current_user
    #user = models.User.query.filter_by(current_token=current_token).first()
    friends = models.Friend.query.filter_by(user_id=user.username).all()
    return json.dumps([friend.username for friend in friends]), 200

    
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
