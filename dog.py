import os
from db import db
from flask import abort, request, session
import plan

def list_dogs(owner_id):
    sql = "SELECT id, dogname FROM Dogs WHERE owner_id=:owner_id "
    result = db.session.execute(sql, {"owner_id": owner_id})
    dogs = result.fetchall()
#    print(raw_list)
    #dogs = [x[0] for x in raw_list]
    #dogs = raw_list
    if not dogs:
        return ["ei koiria"]
    else:
        return dogs 


def add_dog_name(dogname, owner_id):
    dogname = dogname.capitalize()
#    print(f"in module dogs function add_dog_name name:{dogname}, owner id: {owner_id}")
    try:
        sql = '''INSERT INTO Dogs (dogname, owner_id) 
            VALUES (:dogname, :owner_id) RETURNING id'''
        result = db.session.execute(sql, {"dogname":dogname, "owner_id":owner_id})
        [dog_id] = result.fetchone()
        db.session.commit()

    except:
        print("something goes wrong in add_dog function")
        return False
 #   print(f"in add_dog function return value of : {dog_id}")
    plan.gen_default_plan(dog_id)
    return True

def plan_progress(dog_id):
 #   print(f"dog.plan_progress dog_id {dog_id}")
 #   print(f"dog.plan_progress owner_id {get_owner(dog_id)}")
    if session["user_id"] != get_owner(dog_id):
        print("owner check not matching")
        abort(403)
    
    try:
        sql='''
            SELECT Dogs.dogname, SKills.skill, Places.place, 
                    Disturbances.disturbance, Plan.target_repeats, Progress.repeated,
                    LEAST((Progress.repeated*1.0)/(Plan.target_repeats*1.0), 1.0) AS achieved
                FROM Dogs, Skills, Places, Disturbances, Plan, Progress
                WHERE Dogs.id=:dog_id 
                    AND Plan.dog_id = Dogs.id
                    AND Skills.id = Plan.skill_id
                    AND Places.id = Plan.place_id
                    AND Disturbances.id = Plan.disturbance_id
                    AND Progress.plan_id = Plan.id
                ORDER BY Skills.id, Places.id, Disturbances.id
            ;'''
        result = db.session.execute(sql, {"dog_id":dog_id}).fetchall()

        return result
    except:
        print("something goes wrong in module dog plan_progress function")
        return False



def get_total_progress(dog_id):
    try:
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
        '''
        result = db.session.execute(sql, {"dog_id":dog_id}).fetchone()
        return result[0]
    except:
        print("Error in module dog, function get_skill_progress")
        return False



def get_skill_progress(dog_id):
    try:
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

        '''
        result = db.session.execute(sql, {"dog_id":dog_id}).fetchall()
        return result
    except:
        print("Error in module dog, function get_skill_progress")
        return False

#not implemented, or needed at the moment
#just reservation for possible future needs
def get_details_by_skill(dog_id, skill_id):
    pass


def get_owner(dog_id):
    sql = "SELECT owner_id FROM Dogs WHERE id=:dog_id"
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchone()
  #  print(result)
    return result[0]

def get_dog_id():
    return session.get("dog_id")

def get_name(dog_id):
    sql = "SELECT dogname FROM Dogs WHERE id=:dog_id"
    result = db.session.execute(sql, {"dog_id":dog_id}).fetchone()
 #   print(f"in dog.get_name {result}")
    return result[0]

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
 #   print(result)
    return result    

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
 #   print(result)
    return result    

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
  #  print(result)
    return result    



def mark_progress(plan_id, repeats):
    print(f"in module dog repeats {repeats}") #debug print remove
    if repeats == 0:
        return True
    try:
        sql = '''UPDATE Progress
                SET repeated = GREATEST(repeated + :repeats, 0)
                WHERE id=:plan_id'''
        result = db.session.execute(sql, {"plan_id":plan_id, "repeats":repeats})
        db.session.commit()
        print("module dog mark_progress succesful") #debug print remove
    except:
        print("something goes wrong in module dog function mark_progress")
        return False
    return True


#backup can be removed after sufficient testing
#ORIGINAL VERSION OF MARKPROGRES BASED ON REPORTING COMPLETED TRAININGS ONE BY ONE
# def mark_progress(plan_id):
#     try:
#         sql = '''UPDATE Progress
#                 SET repeated = repeated +1
#                 WHERE id=:plan_id'''
#         result = db.session.execute(sql, {"plan_id":plan_id})
#         db.session.commit()
#         print("module dog mark_progress succesful")
#     except:
#         print("something goes wrong in module dog function mark_progress")
#         return False
#     return True


def find_plan_id(dog_id, skill_id, place_id, disturbance_id):
    try:
        sql =   '''SELECT
                Plan.id
                FROM Plan
                WHERE Plan.dog_id=:dog_id 
                    AND Plan.skill_id=:skill_id
                    AND Plan.place_id=:place_id
                    AND Plan.disturbance_id=:disturbance_id
                ;'''
        result = db.session.execute(sql, {"dog_id":dog_id, "skill_id":skill_id, \
                    "place_id":place_id, "disturbance_id":disturbance_id}).fetchone()
        print(f"find_plan_id {result}")
        print(type(result))
        print(result[0])
        return result[0]
    except:
        print("something wrong in module dog function find_plan_id")
        return False


