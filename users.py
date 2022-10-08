#import os
import secrets
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
#import dog

def login(username, password):
    sql = "SELECT id, password FROM Users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if not user:
        return False
    if check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["user_name"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return True
    return False

def user_id():
    return session.get("user_id")

def is_logged_in():
    return user_id() is not None

def logout():
    try:
        session.pop("user_id", None)
        session.pop("user_name", None)
        session.pop("csrf_token", None)
        session.pop("dog_id", None)
        session.pop("dog_name", None)
        session.pop("error_message", None)
    except:
        return False
    return True

def register(username, password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO Users (username, password) VALUES (:username, :password)"
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
    except:
        return False
    return True

def csrf_check():
    if session["csrf_token"] != request.form["csrf_token"]:
        print("failed csrf_check")
        abort(403)


#not used in current app -> leave for possible development versions
def user_name():
    return session.get("user_name",0)
