import os
from db import db
from flask import abort, request, session
import plan

#SQL error handling?
def list_dogs(owner_id):
    sql = "SELECT id, dogname FROM Dogs WHERE owner_id=:owner_id "
    result = db.session.execute(sql, {"owner_id": owner_id})
    dogs = result.fetchall()
    return dogs

def add_dog_name(dogname, owner_id):
    dogname = dogname.capitalize()
    try:
        sql = '''INSERT INTO Dogs (dogname, owner_id) 
            VALUES (:dogname, :owner_id) RETURNING id'''
        result = db.session.execute(sql, {"dogname":dogname, "owner_id":owner_id})
        [dog_id] = result.fetchone()
        db.session.commit()
    except:
        return False
    plan.gen_default_plan(dog_id)
    plan.gen_default_progress(dog_id) 
    return True

def plan_progress(dog_id):
    sql='''
            SELECT Plan.id, Dogs.dogname, SKills.skill, Places.place, 
                    Disturbances.disturbance, Plan.target_repeats, Progress.repeated,
                    LEAST((Progress.repeated*1.0)/(Plan.target_repeats*1.0), 1.0) AS achieved
                FROM Dogs, Skills, Places, Disturbances, Plan, Progress
                WHERE Dogs.id=:dog_id 
                    AND Plan.dog_id = Dogs.id
                    AND Skills.id = Plan.skill_id
                    AND Places.id = Plan.place_id
                    AND Disturbances.id = Plan.disturbance_id
                    AND Progress.plan_id = Plan.id
                    AND Plan.visible=TRUE
                ORDER BY Skills.id, Places.id, Disturbances.id
        ;'''
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchall()
    return result

def get_total_progress(dog_id):
    sql='''
            SELECT 
                ROUND(100*AVG(LEAST((Progress.repeated * 1.0)/(Plan.target_repeats*1.0), 1.0))::numeric,1) AS achieved
                FROM Dogs, Skills, Places, Disturbances, Plan, Progress
                    WHERE Dogs.id=:dog_id 
                        AND Plan.dog_id = Dogs.id
                        AND Skills.id = Plan.skill_id
                        AND Places.id = Plan.place_id
                        AND Disturbances.id = Plan.disturbance_id
                        AND Progress.plan_id = Plan.id
                        AND Plan.visible = TRUE
        ;'''
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchone()
    return result[0]

def get_skill_progress(dog_id):
    sql='''
            SELECT Skills.skill, 
                ROUND(100*AVG(LEAST((Progress.repeated * 1.0)/(Plan.target_repeats*1.0), 1.0))::numeric,1) AS achieved
                FROM Dogs, Skills, Places, Disturbances, Plan, Progress
                    WHERE Dogs.id=:dog_id 
                        AND Plan.dog_id = Dogs.id
                        AND Skills.id = Plan.skill_id
                        AND Places.id = Plan.place_id
                        AND Disturbances.id = Plan.disturbance_id
                        AND Progress.plan_id = Plan.id
                        AND Plan.visible = TRUE
                GROUP BY Skills.skill
                ORDER BY Skills.skill
        ;'''
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchall()
    return result

def get_owner(dog_id):
    sql = "SELECT owner_id FROM Dogs WHERE id=:dog_id"
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchone()
    return result[0]

def get_dog_id():
    return session.get("dog_id")

def get_name(dog_id):
    sql = "SELECT dogname FROM Dogs WHERE id=:dog_id"
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchone()
    return result[0]

def mark_progress(plan_id, repeats):
    if repeats == 0:
        return True
    print(f"plan_id {plan_id} repeats: {repeats}")
    sql = '''UPDATE Progress
                SET repeated = GREATEST(repeated + :repeats, 0)
                WHERE id=:plan_id'''
    result = db.session.execute(sql, {"plan_id":plan_id, "repeats":repeats})
    db.session.commit()

def find_plan_id(dog_id, skill_id, place_id, disturbance_id):
    sql =   '''SELECT
                 Plan.id
                FROM Plan
                WHERE Plan.dog_id=:dog_id 
                    AND Plan.skill_id=:skill_id
                    AND Plan.place_id=:place_id
                    AND Plan.disturbance_id=:disturbance_id
            ;'''
    result = db.session.execute(sql, {"dog_id":dog_id, "skill_id":skill_id, "place_id":place_id, "disturbance_id":disturbance_id}).fetchone()
    return result[0]

def get_plan_items(plan_id):
    sql =   '''SELECT Plan.id, SKills.skill, Places.place, Disturbances.disturbance, Plan.target_repeats
                FROM Dogs, Skills, Places, Disturbances, Plan
                WHERE   Plan.id =:plan_id
                        AND Dogs.id = Plan.dog_id                     
                        AND  Places.id = Plan.place_id
                        AND Skills.id = Plan.skill_id
                        AND Places.id = Plan.place_id
                        AND Disturbances.id = Plan.disturbance_id
                        AND Plan.visible=TRUE;'''
    result = db.session.execute(sql, {"plan_id":plan_id}).fetchone()
    return result

def remove_from_plan(plan_id):
    sql = '''UPDATE Plan
            SET visible=FALSE
            WHERE Plan.id=:plan_id;
            '''
    result = db.session.execute(sql, {"plan_id":plan_id})
    db.session.commit()
    return True


def change_plan_targets(plan_id, newtarget):
    sql = '''UPDATE Plan
            SET target_repeats=:newtarget
            WHERE Plan.id=:plan_id
          '''
    result = db.session.execute(sql, {"plan_id":plan_id, "newtarget":newtarget})
    db.session.commit()
    return True

def add_new_item(plan_id):
    sql = '''UPDATE Plan
            SET visible=TRUE
            WHERE Plan.id=:plan_id
          '''
    result = db.session.execute(sql, {"plan_id":plan_id})
    db.session.commit()
    return True


def hidden_items(dog_id):
    sql = '''SELECT Plan.id, SKills.skill, Places.place, Disturbances.disturbance, Plan.target_repeats
                    FROM Dogs, Skills, Places, Disturbances, Plan
                    WHERE   
                            Plan.dog_id =:dog_id
                            AND Dogs.id = Plan.dog_id                     
                            AND  Places.id = Plan.place_id
                            AND Skills.id = Plan.skill_id
                            AND Places.id = Plan.place_id
                            AND Disturbances.id = Plan.disturbance_id
                            AND Plan.visible=FALSE
            ;'''
    result = db.session.execute(sql, {"dog_id": dog_id}).fetchall()
    return result

#not used in current app: left here for possible future versions
def get_skills(dog_id):
    sql = '''
            SELECT 
                DISTINCT Skills.id, Skills.skill
            FROM Skills, Plan
            WHERE Plan.dog_id=:dog_id 
                AND Plan.visible = TRUE
                AND Plan.skill_id = Skills.id
            ORDER BY Skills.id
            '''
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchall()
    return result    

#not used in current app: left here for possible future versions
def get_places(dog_id):
    sql = '''
            SELECT 
                DISTINCT Places.id, Places.place
            FROM Places, Plan
            WHERE Plan.dog_id=:dog_id 
                AND Plan.place_id = Places.id
                AND Plan.visible = TRUE
            ORDER BY Places.id
            ;'''
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchall()
    return result    

#not used in current app: left here for possible future versions
def get_disturbances(dog_id):
    sql = '''
            SELECT 
                DISTINCT Disturbances.id, Disturbances.disturbance
            FROM Disturbances, Plan
            WHERE Plan.dog_id=:dog_id 
                AND Plan.disturbance_id = Disturbances.id 
                AND Plan.visible = TRUE
            ORDER BY Disturbances.id
            ;'''
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchall()
    return result    