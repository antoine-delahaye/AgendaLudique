from flask import render_template
from app import app
from models import data


@app.route('/home.html')
def home():
    return render_template("home.html", stylesheet="home")


@app.route('/sign-in.html')
def sign_in():
    return render_template("sign-in.html", stylesheet="sign-in")


@app.route('/sign-up.html')
def sign_up():
    return render_template("sign-up.html", stylesheet="sign-up")


@app.route('/games.html')
def games():
    return render_template("games.html", stylesheet="games", data=data)
