from flask import render_template
from models import data


def home():
    return render_template("games.html", name="Jeux", stylesheet="games", data=data)
