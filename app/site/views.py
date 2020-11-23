# app/site/views.py

from flask import render_template
from flask_login import login_required

from . import site
from .. import db
from ..models import Game


@site.route('/')
def home():
    """
    Render the homepage template on the / route
    """
    return render_template('home.html', stylesheet='home')


@site.route('/catalog')
@login_required
def catalog():
    """
    Render the library template on the /catalog route
    """
    games_data = []
    for data in db.session.query(Game).all():
        games_data.append(
            {'title': data.title, 'publication_year': int(data.publication_year), 'min_players': int(data.min_players),
             'max_players': int(data.max_players), 'image': data.image})
    return render_template('catalog.html', stylesheet='catalog', games_data=games_data)
