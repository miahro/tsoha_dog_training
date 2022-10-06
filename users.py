import os
from db import db
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import dog

#error handling?
def login(username, password):
    sql = "SELECT id, password FROM Users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = username
            session["csrf_token"] = secrets.token_hex(16)            
            return True
        else:
            return False

def user_id():
    return session.get("user_id")

#probably not used anywhere?
def user_name():
    return session.get("user_name",0)

def is_logged_in():
    if user_id() != None:
        return True
    else:
        return False

def logout(): #should work ok even when dog not selected
    try:
        session.pop("user_id", None)
        session.pop("user_name", None)
        session.pop("csrf_token", None)
        session.pop("dog_id", None)
        session.pop("dog_name", None)
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