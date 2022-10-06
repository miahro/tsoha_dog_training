import os
from db import db
from flask import abort, request, session
import dog
from app import app
import defaults

def gen_default_places():
#    places = ["koti", "kotipiha", "metsä"]
    places = defaults.default_places
    try:
        for place in places:
 #           print(place)
            sql = '''INSERT INTO Places (place) 
                VALUES (:place) ON CONFLICT DO NOTHING'''
            db.session.execute(sql, {"place":place})
            db.session.commit()
    except:
        print("error in gen_default_places")
        return False
    return True

def gen_default_skills():
    #skills = ["luoksetulo", "istuminen", "maahan meno"]
    skills = defaults.default_skills
    try:
        for skill in skills:
#            print(skill)
            sql = '''INSERT INTO Skills (skill) 
                VALUES (:skill) ON CONFLICT DO NOTHING'''
            db.session.execute(sql, {"skill":skill})
            db.session.commit()
    except:
        print("error in gen_default_skills")
        return False
    return True

def gen_default_disturbances():
#    disturbances = ["toinen koira", "leikkivät lapset", "auto"]
    disturbances = defaults.default_disturbances
    try:
        for disturbance in disturbances:
#            print(disturbance)
            sql = '''INSERT INTO Disturbances (disturbance) 
                VALUES (:disturbance) ON CONFLICT DO NOTHING'''
            db.session.execute(sql, {"disturbance":disturbance})
            db.session.commit()
    except:
        print("error in gen_default_disturbances")
        return False
    return True

def gen_default_plan(dog_id): #error handling must be added

    print(f"in function gen_default_plan dog_id: {dog_id}")
    sql = '''INSERT INTO Plan(dog_id, skill_id, place_id, disturbance_id, target_repeats, visible)
                SELECT :dog_id, Skills.id, Places.id, Disturbances.id, :rep, TRUE
                FROM Skills CROSS JOIN Places CROSS JOIN Disturbances;
    '''

    db.session.execute(sql, {"dog_id": dog_id, "rep":defaults.default_target_repeats})
    db.session.commit()
    #gen_default_progress(dog_id)


def gen_default_progress(dog_id): #error handling must be added
    sql = '''INSERT INTO Progress(plan_id, repeated)
                SELECT Plan.id, 0
                FROM Plan WHERE dog_id =:dog_id;
    '''
    db.session.execute(sql, {"dog_id":dog_id})
    db.session.commit()

#error handling?
def add_skill(newskill):
    sql = '''INSERT INTO Skills(skill) VALUES(:newskill) ON CONFLICT DO NOTHING;'''
    db.session.execute(sql, {"newskill": newskill})
    db.session.commit()

#error handling?
def add_place(newplace):
    sql = '''INSERT INTO Places(place) VALUES(:newplace) ON CONFLICT DO NOTHING;'''
    db.session.execute(sql, {"newplace": newplace})
    db.session.commit()

#error handling?
def add_disturbance(newdisturbance):
    sql = '''INSERT INTO Disturbances(disturbance) VALUES(:newdisturbance) ON CONFLICT DO NOTHING;'''
    db.session.execute(sql, {"newdisturbance": newdisturbance})
    db.session.commit()

#this feature has not been tested in app!!!
#error handling?
def update_selection(dog_id):
    sql = '''INSERT INTO Plan (dog_id, skill_id, place_id, disturbance_id, target_repeats, visible)
            SELECT :dog_id, Skills.id, Places.id, Disturbances.id, 10, FALSE
            FROM Skills, Places, Disturbances
            WHERE NOT EXISTS 
                (SELECT Plan.skill_id, Plan.place_id, Plan.disturbance_id FROM Plan WHERE plan.skill_id=skills.id AND Plan.place_id=Places.id AND Plan.disturbance_id=Disturbances.id);'''
    db.session.execute(sql, {"dog_id": dog_id})
    db.session.commit()