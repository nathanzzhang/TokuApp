import os
import sqlite3
import datetime
import models as models
import jwt as jwt_decode
from flask import Flask, session, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect

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
    return User.query.filter_by(username=username, current_token=jti).first() == None

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html"), 200
    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")
        confirm_password = req.get("confirmpassword")
        access_token = password == confirm_password
        name = req.get("name")
        birthday = req.get("birthday")
        gender = req.get("gender")
        email = req.get("email")
        new_user = models.User(username, password, access_token, name, birthday, gender, email, str(datetime.datetime.utcnow()), None)
        user = models.User.query.filter_by(username=new_user.username).first()
        if user:
            return jsonify({"message": "User already exists."}), 400
        if new_user.access_token:
            return jsonify({"message": "Passwords don't match."}), 400
        db.session.add(new_user)
        db.session.commit()

    return render_template('profile.html', name=new_user.name), 200

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("index.html")

@app.route("/logout", methods=["DELETE"])
@jwt_required
def logout():
    """Endpoint for revoking the current users access token"""
    jti = get_raw_jwt().get("jti")
    u = User.query.filter_by(current_token=jti)
    u.current_token = None
    db.session.commit()
    return jsonify({"msg": "Successfully logged out"}), 200

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
