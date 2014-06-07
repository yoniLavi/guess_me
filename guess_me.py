import random
from flask import Flask, session, redirect, url_for, escape, request, render_template

MAX_NUMBER = 1000  # maximum guessable number
app = Flask(__name__)

users_data = {}


###### web pages ######
@app.route('/')
def index():
    if 'username' in session and session['username'] in users_data:  # logged in
        return redirect(url_for('guess'))

    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        new_username = request.form['username']
        if new_username in users_data:
            return render_template('invalid_username.html', username=new_username), 401

        create_new_user(new_username)
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout/')
def logout():
    if 'username' in session:
        remove_user(session['username'])

    return redirect(url_for('index'))


@app.route('/guess')
def guess(guess=None):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    guess_input = request.args.get("guessed_number")

    if 'the_number' not in session or guess_input is None:
        start_new_game(username)
        return render_template('guess.html', MAX_NUMBER=MAX_NUMBER)

    guess = int(guess_input)
    users_data[username]['current_guesses'] += 1
    current_guesses = users_data[username]['current_guesses']

    if guess != session['the_number']:
        return render_template('guess.html', MAX_NUMBER=MAX_NUMBER,
                               current_guesses=current_guesses, last_guess=guess)

    #Victory!!!
    finish_game(username)
    return render_template('victory.html', username=username, guesses=current_guesses)


@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html', users_data=users_data.items())


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


###### helper_functions ######
def new_average(old_average, current_guesses, games_previously_played):
    new_total_guesses = old_average * games_previously_played + current_guesses
    new_games_played = games_previously_played + 1.0
    return new_total_guesses / new_games_played


def create_new_user(new_username):
        session['username'] = new_username
        users_data[new_username] = {"games_played": 0,
                                    "current_guesses": 0,
                                    "average_guesses": 0,
                                    "best_guesses": 10000000  # just a bad score for noobs
                                   }


def remove_user(username):
    session.clear()
    users_data.pop(username, None)


def start_new_game(username):
    session['the_number'] = random.randrange(MAX_NUMBER + 1)
    users_data[username]["games_played"] += 1
    users_data[username]['current_guesses'] = 0


def finish_game(username):
    session.pop('the_number', None)

    user_dict = users_data[username]
    user_dict["average_guesses"] = new_average(user_dict["average_guesses"],
                                               user_dict["current_guesses"],
                                               user_dict["games_played"])
    user_dict["current_guesses"] = 0
    if user_dict["current_guesses"] < user_dict["best_guesses"]:
        user_dict["best_guesses"] = user_dict["current_guesses"]


app.secret_key = 'noOneWillGuessThis'  # change this before deploying to production

if __name__ == "__main__":
    app.run(debug=True)
