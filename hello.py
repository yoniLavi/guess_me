import random
from flask import Flask, session, redirect, url_for, escape, request

MAX_NUMBER = 1000  # maximum guessable number
app = Flask(__name__)

users_data = {}


#helper_functions
def new_average(old_average, current_guesses, games_previously_played):
    new_total_guesses = old_average * games_previously_played + current_guesses
    new_games_played = games_previously_played + 1.0
    return new_total_guesses / new_games_played


def create_new_user(new_username):
        session['username'] = new_username
        users_data[new_username] = {"games_played": 0,
                                    "current_guesses": 0,
                                    "average_guesses": 0,
                                    "best_guesses": 10000000
                                   }


def finish_game(username):
    session.pop('the_number', None)

    user_dict = users_data[username]
    user_dict["average_guesses"] = new_average(user_dict["average_guesses"],
                                               user_dict["current_guesses"],
                                               user_dict["games_played"])
    user_dict["games_played"] += 1
    if user_dict["current_guesses"] < user_dict["best_guesses"]:
        user_dict["best_guesses"] = user_dict["current_guesses"]


def start_new_game(username):
    session['the_number'] = random.randrange(MAX_NUMBER + 1)
    users_data[username]['current_guesses'] = 0


#controllers:
@app.route('/')
def index():
    if 'username' in session and session['username'] in users_data:
        return 'Logged in as %s' % escape(session['username'])

    return redirect(url_for('login'))


#guess the number using sessions; keep high scores in a server-side dict
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        new_username = request.form['username']
        if new_username in users_data:
            return 'The username <b>%s</b> is already taken' % new_username, 401

        create_new_user(new_username)
        return redirect(url_for('index'))

    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

#TO BE DELETED
@app.route('/game')
def game():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'the_number' not in session:
        session['the_number'] = random.randrange(1000)

    return str(session['the_number'])


@app.route('/guess/<int:guess>')
def guess(guess):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    if 'the_number' not in session:
        start_new_game(username)

    users_data[username]['current_guesses'] += 1

    if guess < session['the_number']:
        return 'Too low'
    elif guess > session['the_number']:
        return 'Too high'
    else:
        finish_game(username)
        return 'Awesome, %s! You won the game after %s guesses!' % (
            username, users_data[username]['current_guesses'])


@app.route('/dashboard')
def dashboard():
    return str(users_data)


@app.errorhandler(404)
def page_not_found(error):
    return 'There is no such page, <a href="%s">go back to the game</a>' % url_for('game'), 404


if __name__ == "__main__":
    app.secret_key = 'noOneWillGuessThis'
    app.run(debug=True)
