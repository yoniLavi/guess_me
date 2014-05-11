import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/hello/<name>')
def hello(name):
    return("Hello " + name)

@app.route('/bye/<name>')
def bye(name):
    return("Bye " + name)

@app.errorhandler(404)
def page_not_found(error):
    return "404: You're funny, there's no such page", 404

if __name__ == "__main__":
    app.run(debug=True)
