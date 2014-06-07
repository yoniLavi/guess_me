import os
import random
from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)

users_data = {}

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])

    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
    return 'There is no such page, <a href="%s">go back to the game</a>' % url_for('game'), 404


#guess the number using sessions; keep high scores in a server-side dict
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
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

    if 'the_number' not in session:
        session['the_number'] = random.randrange(1000)

    if guess < session['the_number']:
        return 'too low'
    elif guess > session['the_number']:
        return 'too high'
    else:
        session.pop('the_number', None)
        return 'Awesome, you won!'

#TBD: dashboard with all logged in users. Their record guess number, average guess number and current guess number
@app.route('/dashboard')
def dashboard():
    return '\n'.join(session.keys())

if __name__ == "__main__":
    app.secret_key = 'noOneWillGuessThis'
    app.run(debug=True)
