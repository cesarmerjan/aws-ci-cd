import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable

import click
from flask import Flask, jsonify, make_response, request
from flask.cli import AppGroup
from flask_sqlalchemy import SQLAlchemy
from jwt.exceptions import PyJWTError

from src import token_service

SECRET_KEY = os.environ.get("SECRET_KEY") or "H4ard t0 Gu3Ss"
DATABASE_URI = os.environ.get("DATABASE_URI") or "sqlite:///database.sqlite"


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

db = SQLAlchemy()
db.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


def login_required(function: Callable[..., Any]):
    @wraps(function)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access-token")
        if token:
            try:
                token_service.validate_token(token.encode(), SECRET_KEY)
                return function(*args, **kwargs)
            except PyJWTError as error:
                return jsonify({"message": "unauthorazied"}), 401
        else:
            return jsonify({"message": "missing access token"}), 400

    return wrapper


@app.post("/login/")
def login():
    body = request.json

    user: User = db.session.query(User).filter_by(email=body["email"]).first()
    if user and user.password == body["password"]:
        token = token_service.generate_token(
            {"user_id": user.id}, SECRET_KEY, datetime.now() + timedelta(days=15)
        )

        response = make_response(jsonify({"message": "ok"}), 200)
        response.set_cookie(key="access-token", value=token, path="/", httponly=True)

        return response
    else:
        return jsonify({"message": "not found"}), 404


@app.get("/logout/")
@login_required
def logout():
    response = make_response(jsonify({"message": "ok"}), 200)
    response.delete_cookie("access-token")
    return response


@app.post("/sign-in/")
def sign_in():
    body = request.json
    user = User(name=body["name"], email=body["email"], password=body["password"])
    db.session.add(user)
    db.session.commit()
    return {"message": "user created successfully"}, 201


@app.get("/")
@login_required
def index():
    return {"message": "index"}, 200


@app.get("/health-check/")
def health_check():
    return {"message": "ok!"}, 200


user_cli = AppGroup("user")


@user_cli.command("create")
@click.argument("name")
@click.argument("email")
@click.argument("password")
def create_user(name, email, password):
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        print(f"User {name} was created.")
    else:
        print(f"User already exists.")


app.cli.add_command(user_cli)
