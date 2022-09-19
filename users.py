import os
from db import db
from flask import abort, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import dog

def login(username, password):
  #  print("module users function login beginning")
    sql = "SELECT id, password FROM Users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
 #   print("module users function login, after db operations")
    if not user:
 #       print("Not user")
        return False
    else:
  #      print("is user")
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = username
            #session["csrf_token"] = os.urandom(16).hex()
            session["csrf_token"] = secrets.token_hex(16)            
            #print(f"in login function csrf_token {session['csrf_token']}") #tämä rivi pitää poisaa
            return True
        else:
            return False
        #session["csrf_token"] = secrets.token_hex(16)   

def user_id():
    return session.get("user_id")

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
#        print(sql)
#        print(username)
#        print(password)
 #       print(hash_value)
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
    except:
        print("Database error in module users function register")
        return False
        #return login(username, password)
    return True
#    return login(username, password)

def csrf_check():
    if session["csrf_token"] != request.form["csrf_token"]:
        print("failed csrf_check")
        abort(403)