import random
from flask import Flask, session, redirect, url_for, escape, request, render_template

MAX_NUMBER = 1000  # maximum guessable number
app = Flask(__name__)
app.secret_key = "noOneWillGuessThis"  # change this before deploying to production

# A minimal data store of user data; databases are covered later
datastore = {}


###### web pages ######
@app.route("/")
def index():
    if "username" in session and session["username"] in datastore:  # logged in
        return redirect(url_for("guess"))

    return redirect(url_for("login"))


@app.route("/login/", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login/", methods=["POST"])
def login():
    username = request.form["username"]
    if not username:  # if they bypassed the form validation
        return redirect(url_for("login"))

    if username in datastore:
        return render_template("username_taken.html", username=username)

    create_new_user(username)
    return redirect(url_for("guess"))


@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/guess")
def guess(guess=None):
    if "username" not in session or session["username"] not in datastore:
        return redirect(url_for("login"))

    username = session["username"]

    guess_input = request.args.get("guessed_number")
    if "the_number" not in session or guess_input is None:
        start_new_game(username)
        return render_template(
            "guess.html", MAX_NUMBER=MAX_NUMBER, current_guesses=0
        )

    guess = int(guess_input)
    datastore[username]["current_guesses"] += 1
    current_guesses = datastore[username]["current_guesses"]

    if guess == session["the_number"]:  # Victory!!!
        finish_game(username)
        return render_template(
            "victory.html", username=username, guesses=current_guesses
        )

    return render_template(
        "guess.html",
        MAX_NUMBER=MAX_NUMBER,
        current_guesses=current_guesses,
        last_guess=guess,
    )


@app.route("/dashboard/")
def dashboard():
    return render_template("dashboard.html", users_data=datastore.items())


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


###### helpers ######
def new_average(old_average, current_guesses, games_previously_played):
    new_total_guesses = old_average * games_previously_played + current_guesses
    return new_total_guesses / (games_previously_played + 1)


def create_new_user(new_username):
    session["username"] = new_username
    datastore[new_username] = {
        "games_played": 0,
        "current_guesses": 0,
        "average_guesses": 0,
        "best_guesses": 10000000,  # a default, very poor score
    }


def start_new_game(username):
    session["the_number"] = random.randrange(1, MAX_NUMBER + 1)
    datastore[username]["current_guesses"] = 0


def finish_game(username):
    session.pop("the_number", None)

    user_dict = datastore[username]
    user_dict["average_guesses"] = new_average(
        user_dict["average_guesses"],
        user_dict["current_guesses"],
        user_dict["games_played"],
    )
    user_dict["games_played"] += 1

    if user_dict["current_guesses"] < user_dict["best_guesses"]:
        user_dict["best_guesses"] = user_dict["current_guesses"]
