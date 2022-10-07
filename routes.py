from app import app
from flask import render_template, request, redirect, session, abort, url_for
import users
import dog
import plan
import secrets
#import app

@app.route("/")
def index(msg=''):  #msg is message for main page, default empty
    return render_template("index.html", msg=msg)


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
            session["error_message"]="Väärä tunnus tai salasana"
            return redirect("error")

@app.route("/logout")
def logout():
    if users.logout(): #succesfull logout return to main screen (info not logged in)
        return redirect("/")
    else: #trying to logout when not logged in return error (not fatal)
        session["error_message"]="Uloskirjautuminen ei onnistunut"
        return redirect("/error")

@app.route("/error", methods=["GET"])
def error(message=''):
    msg=session["error_message"]
    session["error_message"]=""
    if request.method == "GET":
        return render_template("error.html", message=msg)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET": #GET to view registration form
        return render_template("register.html")
    if request.method == "POST": #POST to submit registration details
        username = request.form["username"]
        if not check_length(username, 1, 20):
            session["error_message"]="Tunnuksessa tulee olla 1-20 merkkiä"
            return redirect("/error")
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            session["error_message"]="Salasanat eroavat"
            return redirect("/error")
        if password1 =="":
            session["error_message"]="Salasana on tyhjä"
            return redirect("/error")
        if users.register(username, password1):
            return render_template("index.html", msg="Käyttäjätunnuksen " + username + " luonti onnistui")
        else:
            session["error_message"]="Käyttäjätunnus on jo olemassa"
            return redirect("/error")

@app.route("/dogs", methods = ["GET"])
def dogs():
    if not users.is_logged_in(): 
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")
    else: 
        user_id = users.user_id()
        dognames = dog.list_dogs(user_id) 
        return render_template("dogs.html", dogs=dognames)


@app.route("/add_dog", methods =["GET", "POST"]) 
def add_dog():
    if not users.is_logged_in(): 
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")
    if request.method == "GET":
        return render_template("add_dog.html")
    if request.method == "POST":
        users.csrf_check()
        name = request.form["dogname"]
        if len(name) < 1 or len(name)>20:
            session["error_message"]="Koiran nimessä tulee olla 1-20 merkkiä"
            return redirect("/error")
        if dog.add_dog_name(name, users.user_id()):
            dognames = dog.list_dogs(session["user_id"])
            return render_template("dogs.html", dogs=dognames)
        else:
            session["error_message"]="Koiran lisäys ei onnistunut"
            return redirect("/error")


@app.route("/dogchoice/<int:dog_id>", methods =["GET"]) 
def dogchoice(dog_id):
    if not users.is_logged_in(): 
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")       
    if request.method =="GET":
        if users.user_id() != dog.get_owner(dog_id):
            abort(403) #this should only happen when user is manually setting address for other dog than own
            #hence abort should be justified action rather than raising non-fatal error alternative below
            #session["error_message"]="Et ole koiran omistaja"
            #return redirect("error.html")
        session["dog_id"]=dog_id
        session["dog_name"]=dog.get_name(dog_id)
        return render_template("dogchoice.html")  
    else: #should not be possible, but here just for safety
        session["error_message"]="Tunnistamaton virhe"
        return redirect("/error")            

@app.route("/markprogress", methods =["GET", "POST"]) 
def markprogress(): 
    if not users.is_logged_in(): 
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")       
    dog_id = dog.get_dog_id()
    if dog_id is None:
        session["error_message"]="Koiraa ei valittu"
        return redirect("/error")    
    if request.method == "GET":
    #    skills = dog.get_skills(session["dog_id"]) #needed for reporting form, is it? test
    #    places = dog.get_places(session["dog_id"]) #needed for reporting form, is it? test
    #    disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form, is it? test
        prog = dog.get_skill_progress(dog_id)
        plan_progress = dog.plan_progress(dog_id)        
        total_progress = dog.get_total_progress(dog_id)
        return render_template("/markprogress.html", progress=prog, plan_progress=plan_progress, total_progress=total_progress)
    if request.method == "POST":
        users.csrf_check()
        # skill_id = request.form["skill"]   
        # place_id = request.form["place"] 
        # disturbance_id = request.form["disturbance"] 
        repeats = request.form["repeats"]
        plan_id = request.form["plan_id"]
 #       print(f"in function markprogress plan id {plan_id}") #debug print remove
 #       print(f"repeats: {repeats}") #debug print(remove)
  #      plan_id = dog.find_plan_id(dog_id, skill_id, place_id, disturbance_id)
        dog.mark_progress(plan_id, repeats)
        plan_progress = dog.plan_progress(dog_id)
        total_progress = dog.get_total_progress(dog_id) #this line is in wrong places and causes wrong report output
#        skills = dog.get_skills(session["dog_id"]) #needed for reporting form, or is it? test
#        places = dog.get_places(session["dog_id"]) #needed for reporting form, or is it? check
#        disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form, or is it? check
        prog = dog.get_skill_progress(dog_id)
        return render_template("/markprogress.html",progress=prog, plan_progress=plan_progress, total_progress=total_progress)

@app.route("/modify_plan", methods=["GET", "POST"])
def modify_plan():
    if not users.is_logged_in(): 
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")        
    dog_id = dog.get_dog_id()
    if dog_id is None:
        session["error_message"]="Koiraa ei valittu"
        return redirect("/error")    
    dog_id = dog.get_dog_id()
  #  skills = dog.get_skills(session["dog_id"]) #needed for reporting form? check
  #  places = dog.get_places(session["dog_id"]) #needed for reporting form? check
  #  disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form? check
 #   prog = dog.get_skill_progress(dog_id)
    plan_progress = dog.plan_progress(dog_id)        
 #   total_progress = dog.get_total_progress(dog_id)  
    hidden_items = dog.hidden_items(dog_id)  
    print(hidden_items) #debug print remove
    if request.method =="GET":
#        print("routes.add_place with GET call") #debug print remove
        return render_template("/modify_plan.html",hidden_items=hidden_items, plan_progress=plan_progress)
#        return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress)
#        return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances)
    if request.method =="POST":
 #       print("routes.add_place with POST call") #debug print remove
 #       print(request.form["change_item"]) #debug print remove
        users.csrf_check()
        change_item = request.form["change_item"]
        if change_item == "skill":
            newskill=request.form["newskill"].lower()
            if not check_length(newskill, 1, 30):
                session["error_message"]="Taidossa tulee olla 1-30 merkkiä"
                return redirect("/error")
            else:
                plan.add_skill(newskill)
        elif change_item == "place":
            newplace=request.form["newplace"].lower()
            if not check_length(newplace, 1, 30):
                session["error_message"]="Paikassa tulee olla 1-30 merkkiä"
                return redirect("/error")
            else:
                plan.add_place(newplace)
 #           print(request.form["newplace"])
        elif change_item == "disturbance":
            newdisturbance=request.form["newdisturbance"].lower()
            if not check_length(newdisturbance, 1, 30):
                session["error_message"]="Häiriössä tulee olla 1-30 merkkiä"
                return redirect("/error")
            else:
                plan.add_disturbance(newdisturbance)
        elif change_item == "targets":
            plan_id=int(request.form["targets"])
            plan_items = dog.get_plan_items(plan_id)
            print(f"modify plan change item targets, plan id {plan_id}") #debug print remove
            return render_template("/change_targets.html", plan_items=plan_items)
        elif change_item =="target_change":
    #        print("we got to target change before crashing")
            newtarget = int(request.form["newtarget"])
            plan_id = int(request.form["plan_id"])
            if newtarget == 0:
     #           print(plan_id)
                dog.remove_from_plan(plan_id)
                plan_items = dog.get_plan_items(plan_id)
#                return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances)
            else:
                dog.change_plan_targets(plan_id, newtarget)
   #         print(f"in modify plan, target_change detected with change_item {change_item}, newtarget {newtarget}")
        elif change_item == "add_training":
    #        print("we got to add new training in function modify_plan") #debug print remove
            add_training_id = int(request.form["add_training"])
     #       print(f"in add training part of modify pland add_training id {add_training_id}")
            dog.add_new_item(add_training_id)
#            return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )
        elif change_item == "update_selection":
#            print(f" update selection dog_id {dog_id}")
            plan.update_selection(dog_id)
    #        hidden_items = dog.hidden_items(dog_id)  
    #        print(hidden_items)
#            return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )
        else:
            session["error_message"]="Tunnistamaton virhe"
            return redirect("/error")
   #     prog = dog.get_skill_progress(dog_id)
        plan_progress = dog.plan_progress(dog_id)        
  #      total_progress = dog.get_total_progress(dog_id)        
        hidden_items = dog.hidden_items(dog_id)
        return render_template("/modify_plan.html",hidden_items=hidden_items, plan_progress=plan_progress)
#                return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress)
#        return render_template("/modify_plan.html",hidden_items=hidden_items, progress=prog, plan_progress=plan_progress, total_progress=total_progress, skills=skills, places=places, disturbances=disturbances )




@app.route("/change_targets", methods=["GET", "POST"])
def change_targets(plan_items=None):
    if not users.is_logged_in(): 
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")    
    dog_id = dog.get_dog_id()
    if dog_id is None: 
        session["error_message"]="Koiraa ei valittu"
        return redirect("/error")    
    plan_id = session["plan_id"]
#    print(f"in change targets plan_id {plan_id}") #debug print remove
    items = dog.get_plan_items(plan_id)
#    print(f"items {items}") 
#    print("items one by one") 
    for item in items:
        print(item)
    if request.method == "GET":
        skills = dog.get_skills(session["dog_id"]) #needed for reporting form? recheck
        places = dog.get_places(session["dog_id"]) #needed for reporting form? recheck
        disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form? recheck
        plan_progress = dog.plan_progress(dog_id)   #not needed?     
    #    total_progress = dog.get_total_progress(dog_id)
        return render_template("/change_targets.html", plan_items=items)
    if request.method == "POST":
        users.csrf_check()
        skill_id = request.form["skill"]   #not needed?
        place_id = request.form["place"] #not needed?
        disturbance_id = request.form["disturbance"] #not needed?
        repeats = int(request.form["repeats"]) #not needed?
#        print(type(repeats))
#        print(f"repeats: {repeats}") #debug print(remove)
#        print(f"in change_targets items POST {items}")
        
        if repeats == 0:
            dog.remove_from_plan(plan_id)
    #    dog.mark_progress(plan_id, repeats)
        plan_progress = dog.plan_progress(dog_id)
        skills = dog.get_skills(session["dog_id"]) #needed for reporting form? check
        places = dog.get_places(session["dog_id"]) #needed for reporting form? check
        disturbances = dog.get_disturbances(session["dog_id"]) #needed for reporting form? check
        return render_template("/change_targets.html", plan_items=items)

def check_length(text, min, max):
    if len(text)>= min and len(text) <= max:
        return True
    else:
        return False

