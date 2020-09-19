import os
import sqlite3
import data as data
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
    form = models.UserForm()
    if request.method == "GET":
        return render_template("register.html", form=form), 200
    if request.method == "POST":
        if form.validate_on_submit():
            if DEBUG:
                print(form.username.data) # username
                print(form.name.data)  # name
                print(form.email.data)  # email
            access_token = create_access_token(identity=form.username.data)
            new_user = models.User(form.username.data, form.password.data, str(access_token), form.name.data, form.birthday.data, form.gender.data, form.email.data, str(datetime.datetime.utcnow()), None)
            #new_user.set_password(password)
            user = models.User.query.filter_by(username=new_user.username).first()
            if user:
                return jsonify({"message": "User already exists."}), 400
            decoded = jwt_decode.decode(access_token, verify=False)
            new_user.current_token = decoded["jti"]
            db.session.add(new_user)
            db.session.commit()
        else:
            return jsonify(message="Error"), 400

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
