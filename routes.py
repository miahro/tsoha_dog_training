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
        username = request.form.get("username")
        password = request.form.get("password")
        session["csrf_token"] = secrets.token_hex(16)
        if users.login(username, password):
            return render_template("index.html", msg="Sisäänkirjautuminen onnistui")
        return render_template("/login.html", error_message=["Väärä tunnus tai salasana"])


@app.route("/logout")
def logout():
    if users.logout(): #succesfull logout return to main screen (info not logged in)
        return redirect("/")
    return render_template("logout.html", error_message=["Uloskirjautuminen ei onnistunut"])


@app.route("/register", methods=["GET", "POST"])
def register():
    error = []
    if request.method == "GET": #GET to view registration form
        return render_template("register.html")
    if request.method == "POST": #POST to submit registration details
        username = request.form.get("username")
        if not check_length(username, 1, 20):
            error.append("Tunnuksessa tulee olla 1-20 merkkiä")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if password1 != password2:
            error.append("Salasanat eroavat")
        if password1 =="" or password2=="":
            error.append("Salasana on tyhjä")
        if error:
            for item in error:
                print(item)
            return render_template("/register.html", error_message=error)
        if users.register(username, password1):
            return render_template \
                ("index.html", msg="Käyttäjätunnuksen " + username + " luonti onnistui")
        return render_template("/register.html", error_message=["Käyttäjätunnus on jo olemassa"])


@app.route("/dogs", methods = ["GET"])
def dogs():
    if not users.is_logged_in():
        return render_template("/dogs.html", error_message=["Et ole kirjautunut sisään"])
    user_id = users.user_id()
    dognames = dog.list_dogs(user_id)
    return render_template("dogs.html", dogs=dognames)

@app.route("/add_dog", methods =["GET", "POST"])
def add_dog():
    if not users.is_logged_in():
        return render_template("/add_dog.html", error_message=["Et ole kirjautunut sisään"])
    if request.method == "GET":
        return render_template("/add_dog.html")
    if request.method == "POST":
        users.csrf_check()
        name = request.form.get("dogname")
        if not check_length(name, 1, 20):
            return render_template("add_dog.html",\
                    error_message=["Koiran nimessä tulee olla 1-20 merkkiä"])
        if dog.add_dog_name(name, users.user_id()):
            dognames = dog.list_dogs(session["user_id"])
            return render_template("/dogs.html", dogs=dognames, msg="Koiran lisäys onnistui")
        return render_template("/add_dog.html",\
                error_message=["käyttäjällä ei voi olla kahta samannimistä koiraa"])


@app.route("/dogchoice/<int:dog_id>", methods =["GET"])
def dogchoice(dog_id=None):
    if not users.is_logged_in():
        return render_template("/dogs.html", error_message=["Et ole kirjautunut sisään"])
    if request.method =="GET":
        if users.user_id() != dog.get_owner(dog_id):
            abort(403) #should only happen if user is manually sets address for other dog than own
            #hence abort should be justified action
            # rather than raising non-fatal error
        session["dog_id"]=dog_id
        session["dog_name"]=dog.get_name(dog_id)
        return redirect("/markprogress")
    #should not be possible, but here just for safety
    return render_template("/dogs.html", error_message=["Tunnistamaton virhe"])

@app.route("/markprogress", methods =["GET", "POST"])
def markprogress():
    error = []
    if not users.is_logged_in():
        error.append("Et ole kirjautunut sisään")
    dog_id = dog.get_dog_id()
    if dog_id is None:
        error.append("Koiraa ei valittu")
    if error:
        return render_template("/markprogress.html", error_message=error)
    if request.method == "GET":
        prog = dog.get_skill_progress(dog_id)
        plan_progress = dog.plan_progress(dog_id)
        total_progress = dog.get_total_progress(dog_id)
        return render_template("/markprogress.html",\
                        progress = prog, plan_progress=plan_progress, total_progress=total_progress)
    if request.method == "POST":
        users.csrf_check()
        repeats = request.form.get("repeats")
        plan_id = request.form.get("plan_id")
        dog.mark_progress(plan_id, repeats)
        prog = dog.get_skill_progress(dog_id)
        plan_progress = dog.plan_progress(dog_id)
        total_progress = dog.get_total_progress(dog_id)
        return render_template("/markprogress.html", progress=prog, plan_progress=plan_progress,\
                total_progress=total_progress, msg="Koulutus kuitattu tehdyksi")


@app.route("/modify_plan", methods=["GET", "POST"])
def modify_plan():
    error = []
    if not users.is_logged_in():
        error.append("Et ole kirjautunut sisään")
    dog_id = dog.get_dog_id()
    if dog_id is None:
        error.append("Koiraa ei valittu")
    if error:
        return render_template("/modify_plan.html", error_message=error)
    plan_progress = dog.plan_progress(dog_id)
    hidden_items = dog.hidden_items(dog_id)
    if request.method =="GET":
        return render_template \
                ("/modify_plan.html",hidden_items=hidden_items, plan_progress=plan_progress)
    if request.method =="POST":
        users.csrf_check()
        change_item = request.form.get("change_item")
        if change_item in ["skill", "place", "disturbance"]:
            newitem =request.form.get("newitem")
            if not check_length(newitem, 1, 30):
                error.append("Taito, paikka tai häiriö tulee olla 1-30 merkkiä")
            elif change_item == "skill":
                plan.add_skill(newitem)
            elif change_item == "place":
                plan.add_place(newitem)
            elif change_item == "disturbance":
                plan.add_disturbance(newitem)
        elif change_item == "targets":
            plan_id=request.form.get("targets")
            newtarget = request.form.get("newtarget")
            if not newtarget.isdigit():
                error.append("Tavoitteen on oltava lukuarvo")
            else:
                dog.change_plan_targets(plan_id, newtarget)
        elif change_item == "add_training":
            add_training_id = request.form.get("add_training")
            dog.add_new_item(add_training_id)
        elif change_item == "update_selection":
            plan.update_selection(dog_id)
        plan_progress = dog.plan_progress(dog_id)
        hidden_items = dog.hidden_items(dog_id)
        if error:
            return render_template("/modify_plan.html", hidden_items=hidden_items,\
                                    plan_progress=plan_progress, error_message = error)
        return render_template("/modify_plan.html",hidden_items=hidden_items,\
                plan_progress=plan_progress, msg="Koulutusohjelman muokkaus tehty onnistuneesti")


def check_length(text, min_len, max_len):
    return len(text)>= min_len and len(text) <= max_len
