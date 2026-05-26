import sqlite3
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import db
import secrets
import users
import rcps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# pages

@app.route("/")
def mainapge():
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")

    visit_ammount = (db.query("SELECT COUNT(*) FROM visits"))[0][0]
    last_visit = db.query("SELECT visited_at FROM visits ORDER BY visited_at DESC LIMIT 1")[0][0]

    recipes = rcps.get_recipes()
    return render_template("mainpage.html", visits = visit_ammount, date = last_visit,
                            recipes = recipes)

@app.route("/recipe/<int:recipe_id>") # update recipe.html
def show_recipe(recipe_id):
    recipe = rcps.get_recipe(recipe_id)
    return render_template("recipe.html", recipe=recipe)

# user

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", filled={})

    if request.method == "POST":
        username = request.form["username"]
        if len(username) > 16:
            abort(403)
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        # could add password checking feature 
        # ie password has to be at least n chracters long...

        if password1 != password2:
            flash("VIRHE: Antamasi salasanat eivät ole samat")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        try:
            password_hash = generate_password_hash(password1)
            db.execute("INSERT INTO users(username, password_hash) VALUES(?, ?)", 
                       (username, password_hash))
            flash("Tunnuksen luominen onnistui, voit nyt kirjautua sisään")
            return redirect("/")

        except sqlite3.IntegrityError:
            flash("VIRHE: Valitsemasi tunnus on jo varattu")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

@app.route("/login", methods=["GET", "POST"]) # add next page?
def login():
    if request.method == "GET":
        return render_template("login.html", next_page=request.referrer)

    if request.method == "POST":
        global username
        username = request.form["username"]
        password = request.form["password"]
        next_page = "/"

        user_id = users.check_login(username, password)

        if user_id:
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(next_page)
        
        else:
            flash("VIRHE: Väärä tunnus tai salasana")
            return render_template("login.html", next_page=next_page)

@app.route("/logout")
def logout():
    del session["user_id"]
    flash("Olet kirjautunut ulos.")
    return redirect("/")

# posts

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/send", methods=["POST"]) # add poster
def send():
    title = request.form["title"]
    ingredients = request.form["ingredients"]
    instructions = request.form["instructions"]

    db.execute("""INSERT INTO recipes(title, ingredients, instructions, status, date) 
               VALUES(?, ?, ?, 1, datetime('now'))""",
               [title, ingredients, instructions]) 
                                                   
    return redirect("/")

@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe = rcps.get_recipe(recipe_id)

    if request.method == "GET":
        return render_template("edit.html", recipe=recipe)

    if request.method == "POST":
        title = request.form["title"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]

        rcps.update_recipe(recipe["id"], title, ingredients, instructions)
        return redirect("/recipe/" + str(recipe_id))

@app.route("/delete/<int:recipe_id>", methods=["GET", "POST"])
def delete_recipe(recipe_id):
    recipe = rcps.get_recipe(recipe_id)

    if request.method == "GET":
        return render_template("delete.html", recipe=recipe)
    
    if request.method == "POST":
        if "continue" in request.form:
            rcps.delete_recipe(recipe_id)
            return redirect("/")
        
        else:
            return redirect("/recipe/" + str(recipe_id))

# to add
# delete posts 
# edit posts 
# post creator

@app.route("/mole")
def mole():
    return render_template("mole.html")