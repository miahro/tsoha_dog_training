import secrets
from flask import render_template, request, redirect, session, abort
import users
import dog
import plan
from app import app

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
        session["error_message"]="Väärä tunnus tai salasana"
        return redirect("error")

@app.route("/logout")
def logout():
    if users.logout(): #succesfull logout return to main screen (info not logged in)
        return redirect("/")
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
            return render_template \
                ("index.html", msg="Käyttäjätunnuksen " + username + " luonti onnistui")
        session["error_message"]="Käyttäjätunnus on jo olemassa"
        return redirect("/error")

@app.route("/dogs", methods = ["GET"])
def dogs():
    if not users.is_logged_in():
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")
    user_id = users.user_id()
    dognames = dog.list_dogs(user_id)
    if len(dognames)==0:
        dognames is None
    return render_template("dogs.html", dogs=dognames)

@app.route("/add_dog", methods =["GET", "POST"])
def add_dog():
    if not users.is_logged_in():
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")
    if request.method == "GET":
        return render_template("/add_dog.html")
    if request.method == "POST":
        users.csrf_check()
        name = request.form["dogname"]
        if len(name) < 1 or len(name)>20:
            session["error_message"]="Koiran nimessä tulee olla 1-20 merkkiä"
            return redirect("/error")
        if dog.add_dog_name(name, users.user_id()):
            dognames = dog.list_dogs(session["user_id"])
            return render_template("/dogs.html", dogs=dognames, msg="Koiran lisäys onnistui")
        session["error_message"]="Koiran lisäys ei onnistunut \
            - käyttäjällä ei voi olla kahta samannimistä koiraa"
        return redirect("/error")


@app.route("/dogchoice/<int:dog_id>", methods =["GET"])
def dogchoice(dog_id):
    if not users.is_logged_in():
        session["error_message"]="Et ole kirjautunut sisään"
        return redirect("/error")
    if request.method =="GET":
        if users.user_id() != dog.get_owner(dog_id):
            abort(403) #should only happen if user is manually sets address for other dog than own
            #hence abort should be justified action
            # rather than raising non-fatal error alternative below
            #session["error_message"]="Et ole koiran omistaja"
            #return redirect("error.html")
        session["dog_id"]=dog_id
        session["dog_name"]=dog.get_name(dog_id)
        return redirect("/markprogress")
    session["error_message"]="Tunnistamaton virhe" #should not be possible, but here just for safety
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
        prog = dog.get_skill_progress(dog_id)
        plan_progress = dog.plan_progress(dog_id)
        total_progress = dog.get_total_progress(dog_id)
        return render_template("/markprogress.html",\
                        progress = prog, plan_progress=plan_progress, total_progress=total_progress)
    if request.method == "POST":
        users.csrf_check()
        repeats = request.form["repeats"]
        plan_id = request.form["plan_id"]
        dog.mark_progress(plan_id, repeats)
        prog = dog.get_skill_progress(dog_id)
        plan_progress = dog.plan_progress(dog_id)
        total_progress = dog.get_total_progress(dog_id)
        return render_template("/markprogress.html", progress=prog, plan_progress=plan_progress,\
                total_progress=total_progress, msg="Koulutus kuitattu tehdyksi")

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
    plan_progress = dog.plan_progress(dog_id)
    hidden_items = dog.hidden_items(dog_id)
    if request.method =="GET":
        return render_template \
                ("/modify_plan.html",hidden_items=hidden_items, plan_progress=plan_progress)
    if request.method =="POST":
        users.csrf_check()
        change_item = request.form["change_item"]
        if change_item == "skill":
            newskill=request.form["newskill"].lower()
            if not check_length(newskill, 1, 30):
                session["error_message"]="Taidossa tulee olla 1-30 merkkiä"
                return redirect("/error")
            plan.add_skill(newskill)
        elif change_item == "place":
            newplace=request.form["newplace"].lower()
            if not check_length(newplace, 1, 30):
                session["error_message"]="Paikassa tulee olla 1-30 merkkiä"
                return redirect("/error")
            plan.add_place(newplace)
        elif change_item == "disturbance":
            newdisturbance=request.form["newdisturbance"].lower()
            if not check_length(newdisturbance, 1, 30):
                session["error_message"]="Häiriössä tulee olla 1-30 merkkiä"
                return redirect("/error")
            plan.add_disturbance(newdisturbance)
        elif change_item == "targets":
            plan_id=int(request.form["targets"])
            plan_items = dog.get_plan_items(plan_id)
            return render_template("/change_targets.html", plan_items=plan_items)
        elif change_item =="target_change":
            newtarget = int(request.form["newtarget"])
            plan_id = int(request.form["plan_id"])
            if newtarget == 0:
                dog.remove_from_plan(plan_id)
                plan_items = dog.get_plan_items(plan_id)
            else:
                dog.change_plan_targets(plan_id, newtarget)
        elif change_item == "add_training":
            add_training_id = int(request.form["add_training"])
            dog.add_new_item(add_training_id)
        elif change_item == "update_selection":
            plan.update_selection(dog_id)
        else:
            session["error_message"]="Tunnistamaton virhe"
            return redirect("/error")
        plan_progress = dog.plan_progress(dog_id)
        hidden_items = dog.hidden_items(dog_id)
        return render_template("/modify_plan.html",hidden_items=hidden_items,\
                plan_progress=plan_progress, msg="Koulutusohjelman muokkaus tehty onnistuneesti")

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
    items = dog.get_plan_items(plan_id)
    for item in items:
        print(item)
    if request.method == "GET":
        return render_template("/change_targets.html", plan_items=items)
    if request.method == "POST":
        users.csrf_check()
        repeats = int(request.form["repeats"])
        if repeats == 0:
            dog.remove_from_plan(plan_id)
        return render_template("/change_targets.html", plan_items=items)

def check_length(text, min_len, max_len):
    return len(text)>= min_len and len(text) <= max_len
#    if len(text)>= min_len and len(text) <= max_len:
#        return True
#    else:
#        return False
