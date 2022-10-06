from app import app
from flask import render_template, request, redirect, session, abort, url_for
import users
import dog
import plan
import secrets
#import app

@app.route("/")
def index(msg=''):  #msg is message for main page, default empty
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET": #GET for opening login menu
        return render_template("login.html")
    if request.method == "POST": #POST for submitting login data
        username = request.form["username"]
        password = request.form["password"]
        session["csrf_token"] = secrets.token_hex(16)
        if users.login(username, password):
            return render_template("index.html", msg="Sisäänkirjautuminen onnistui")
        else:
            return render_template("error.html", message="Väärä tunnus tai salasana")



@app.route("/logout")
def logout():
    if users.logout(): #succesfull logout return to main screen (info not logged in)
        return redirect("/")
    else: #trying to logout when not logged in return error (not fatal)
        return render_template("error.html", message="uloskirjautuminen ei onnistunut")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET": #GET to view registration form
        #print("register with GET")
        return render_template("register.html")
    if request.method == "POST": #POST to submit registration details
        username = request.form["username"]
#        if len(username) < 1 or len(username) > 20:
        if not check_length(username, 1, 20):
            return render_template("/error.html", message="Tunnuksessa tulee olla 1-20 merkkiä")
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat")
        if password1 =="":
            return render_template("error.html", message="Salasana on tyhjä")
        if users.register(username, password1):
            return render_template("index.html", msg="Käyttäjätunnuksen " + username + " luonti onnistui")
        else:
           return render_template("error.html", message="Rekisteröinti ei onnistunut")

@app.route("/dogs", methods = ["GET"])
def dogs():
    if not users.is_logged_in(): #should not be possible to call this if not logged in, but just in case
        return render_template("error.html", message="et ole kirjautunut sisään")
    else: 
        user_id = users.user_id()
        dognames = dog.list_dogs(user_id) #this causes error if not logged in     
        return render_template("dogs.html", dogs=dognames)


@app.route("/add_dog", methods =["GET", "POST"]) 
def add_dog():
    if not users.is_logged_in(): #should not be possible to call this if not logged in, but just in case
        return render_template("error.html", message="et ole kirjautunut sisään")
    if request.method == "GET":
        return render_template("add_dog.html")
    if request.method == "POST":
        users.csrf_check()
        name = request.form["dogname"]
        if len(name) < 1 or len(name)>20:
            return render_template("/error.html", message = "koiran nimessä tulee olla 1-20 merkkiä")
        if dog.add_dog_name(name, users.user_id()):
            dognames = dog.list_dogs(session["user_id"])
            return render_template("dogs.html", dogs=dognames)
        else:
            return render_template("error.html", message="Koiran lisäys ei onnistunut")


@app.route("/dogchoice/<int:dog_id>", methods =["GET"]) 
def dogchoice(dog_id):
    if not users.is_logged_in(): 
        return render_template("error.html", message="et ole kirjautunut sisään")
    if request.method =="GET":
        if users.user_id() != dog.get_owner(dog_id):
            #print("owner check not matching")
            abort(403) #this should only happen when user is manually setting address for other dog than own
            #hence abort should be justified action rather than raising non-fatal error alternative below
            #return render_template("error.html", message="Et ole koiran omistaja")
        session["dog_id"]=dog_id
        session["dog_name"]=dog.get_name(dog_id)
        return render_template("dogchoice.html")  
    else: #should not be possible, but here just for safety
        return render_template("error.html", message="tällaista virhettä ei pitäisi tapahtua, toiminto koiran valinta")

@app.route("/markprogress", methods =["GET", "POST"]) 
def markprogress(): 
    if not users.is_logged_in(): 
        return render_template("error.html", message="et ole kirjautunut sisään")   
    dog_id = dog.get_dog_id()
    if dog_id is None:
        return render_template("error.html", message="koiraa ei valittu")   
    if request.method == "GET":
        skills = dog.get_skills(session["dog_id"]) #needed for reporting form
        places = dog.get_places(session["dog_id"]) #needed for reporting form
        disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form
        prog = dog.get_skill_progress(dog_id)
        plan_progress = dog.plan_progress(dog_id)        
        total_progress = dog.get_total_progress(dog_id)
        return render_template("/markprogress.html", progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances)
    if request.method == "POST":
        users.csrf_check()
        skill_id = request.form["skill"]   
        place_id = request.form["place"] 
        disturbance_id = request.form["disturbance"] 
        repeats = request.form["repeats"]
        print(f"repeats: {repeats}") #debug print(remove)
        plan_id = dog.find_plan_id(dog_id, skill_id, place_id, disturbance_id)
        dog.mark_progress(plan_id, repeats)
        plan_progress = dog.plan_progress(dog_id)
        total_progress = dog.get_total_progress(dog_id) #this line is in wrong places and causes wrong report output
        skills = dog.get_skills(session["dog_id"]) #needed for reporting form
        places = dog.get_places(session["dog_id"]) #needed for reporting form
        disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form
        prog = dog.get_skill_progress(dog_id)
        return render_template("/markprogress.html",progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )

@app.route("/modify_plan", methods=["GET", "POST"])
def modify_plan():
    dog_id = dog.get_dog_id()
    skills = dog.get_skills(session["dog_id"]) #needed for reporting form
    places = dog.get_places(session["dog_id"]) #needed for reporting form
    disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form
    prog = dog.get_skill_progress(dog_id)
    plan_progress = dog.plan_progress(dog_id)        
    total_progress = dog.get_total_progress(dog_id)  
    hidden_items = dog.hidden_items(dog_id)  
    if request.method =="GET":
        print("routes.add_place with GET call") #debug print remove
        return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances)
    if request.method =="POST":
        print("routes.add_place with POST call") #debug print remove
        print(request.form["change_item"]) #debug print remove
        users.csrf_check()
        change_item = request.form["change_item"]
        if change_item == "skill":
            newskill=request.form["newskill"].lower()
            if not check_length(newskill, 1, 30):
                return render_template("error.html",  message="Taidossa tulee olla 1-30 merkkiä")
            else:
                plan.add_skill(newskill)
  #          print(request.form["newskill"])
        elif change_item == "place":
            newplace=request.form["newplace"].lower()
            if not check_length(newplace, 1, 30):
                return render_template("error.html",  message="Paikassa tulee olla 1-30 merkkiä")
            else:
                plan.add_place(newplace)
 #           print(request.form["newplace"])
        elif change_item == "disturbance":
            newdisturbance=request.form["newdisturbance"].lower()
            if not check_length(newdisturbance, 1, 30):
                return render_template("error.html",  message="Häiriössä tulee olla 1-30 merkkiä")
            else:
                plan.add_disturbance(newdisturbance)
        elif change_item == "targets":
            plan_id=int(request.form["targets"])
            plan_items = dog.get_plan_items(plan_id)
            print(f"modify plan change item targets, plan id {plan_id}") #debut print remove, ok so far return correct plan_id
#            change_targets(plan_id)
#            return redirect(url_for("/change_targets.html"))
            #session["msg"]=plan_id 
            #return redirect("/dummy")
 #           session["plan_id"]=plan_id
#            return redirect("/change_targets")
            return render_template("/change_targets.html", plan_items=plan_items)
        elif change_item =="target_change":
            print("we got to target change before crashing")
            newtarget = int(request.form["newtarget"])
            plan_id = int(request.form["plan_id"])
            if newtarget == 0:
                print(plan_id)
                dog.remove_from_plan(plan_id)
                plan_items = dog.get_plan_items(plan_id)
                return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances)
            else:
                dog.change_plan_targets(plan_id, newtarget)
            print(f"in modify plan, target_change detected with change_item {change_item}, newtarget {newtarget}")
        elif change_item == "add_training":
            print("we got to add new training in function modify_plan") #debug print remove
        #    hidden_items = dog.hidden_items(dog_id)
        #    print(hidden_items) #debut print remove
        #    for item in hidden_items: #debug print remove
        #        print(item) #debut print remove
            add_training_id = int(request.form["add_training"])
            print(f"in add training part of modify pland add_training id {add_training_id}")
            dog.add_new_item(add_training_id)
            #tähän lisää koulutus
            return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )
        elif change_item == "update_selection":
            plan.update_selection(dog_id)
            return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )
        else:
            render_template("error.html", msg="tätä ei pitäisi ikinä tapahtua")

#            print(request.form["newdisturbance"])

        return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )

# @app.route("/dummy", methods=["GET", "POST"])
# def dummy():
#     if request.method=="GET":
#         msg=session["msg"]
#         return render_template("dummy.html", msg=msg)
#     if request.method=="POST":
#         msg=session["msg"]
#         return render_template("dummy.html", msg=msg)


@app.route("/change_targets", methods=["GET", "POST"])
def change_targets(plan_items=None):

#    passed_value = request.args.get("passed_value")
   
    if not users.is_logged_in(): #should not be possible to get here
        return render_template("error.html", message="et ole kirjautunut sisään")   
    dog_id = dog.get_dog_id()
    if dog_id is None: #should not be possible to get here
        return render_template("error.html", message="koiraa ei valittu")   
    plan_id = session["plan_id"]
    print(f"in change targets plan_id {plan_id}") #debug print remove
    items = dog.get_plan_items(plan_id)
    print(f"items {items}") 
    print("items one by one") 
    for item in items:
        print(item)
    if request.method == "GET":
        skills = dog.get_skills(session["dog_id"]) #needed for reporting form
        places = dog.get_places(session["dog_id"]) #needed for reporting form
        disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form
    #    prog = dog.get_skill_progress(dog_id)
        plan_progress = dog.plan_progress(dog_id)   #not needed?     
    #    total_progress = dog.get_total_progress(dog_id)
        return render_template("/change_targets.html", plan_items=items)
#orig        return render_template("/change_targets.html", progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances)
    if request.method == "POST":
        users.csrf_check()
        skill_id = request.form["skill"]   #not needed?
        place_id = request.form["place"] #not needed?
        disturbance_id = request.form["disturbance"] #not needed?
        repeats = int(request.form["repeats"]) #not needed?
        print(type(repeats))
        print(f"repeats: {repeats}") #debug print(remove)
        #plan_id = dog.find_plan_id(dog_id, skill_id, place_id, disturbance_id)
        
        print(f"in change_targets items POST {items}")

        
        if repeats == 0:
            dog.remove_from_plan(plan_id)
    #    dog.mark_progress(plan_id, repeats)
        plan_progress = dog.plan_progress(dog_id)
    #    total_progress = dog.get_total_progress(dog_id) #this line is in wrong places and causes wrong report output
        skills = dog.get_skills(session["dog_id"]) #needed for reporting form
        places = dog.get_places(session["dog_id"]) #needed for reporting form
        disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form
     #   prog = dog.get_skill_progress(dog_id)
        return render_template("/change_targets.html", plan_items=items)
#orig        return render_template("/change_targets.html",progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )



def check_length(text, min, max):
    if len(text)>= min and len(text) <= max:
        return True
    else:
        return False

#backup can be removed after sufficient testing
#ORIGINAL VERSION BASED ON REPORTING COMPLETED TRAININGS ONE BY ONE
# @app.route("/markprogress", methods =["GET", "POST"]) 
# def markprogress(): 
#     if not users.is_logged_in(): 
#         return render_template("error.html", message="et ole kirjautunut sisään")   
#     dog_id = dog.get_dog_id()
#     if dog_id is None:
#         return render_template("error.html", message="koiraa ei valittu")   
#     if request.method == "GET":
#         skills = dog.get_skills(session["dog_id"]) #needed for reporting form
#         places = dog.get_places(session["dog_id"]) #needed for reporting form
#         disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form
#         prog = dog.get_skill_progress(dog_id)
#         plan_progress = dog.plan_progress(dog_id)        
#         total_progress = dog.get_total_progress(dog_id)
#         return render_template("/markprogress.html", progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances)
#     if request.method == "POST":
#         users.csrf_check()
#         skill_id = request.form["skill"]   
#         place_id = request.form["place"] 
#         disturbance_id = request.form["disturbance"] 
#         total_progress = dog.get_total_progress(dog_id)
#         plan_id = dog.find_plan_id(dog_id, skill_id, place_id, disturbance_id)
#         skills = dog.get_skills(session["dog_id"]) #needed for reporting form
#         places = dog.get_places(session["dog_id"]) #needed for reporting form
#         disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form
#         dog.mark_progress(plan_id)
#         plan_progress = dog.plan_progress(dog_id)
#         prog = dog.get_skill_progress(dog_id)
#         return render_template("/markprogress.html",progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )