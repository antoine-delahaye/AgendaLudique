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
    Render the catalog template on the /catalog route
    """
    games_data = []
    for data in db.session.query(Game).all():
        games_data.append(
            {'title': data.title, 'publication_year': int(data.publication_year), 'min_players': int(data.min_players),
             'max_players': int(data.max_players), 'image': data.image})
    return render_template('catalog.html', stylesheet='catalog', games_data=games_data)


@site.route('/library')
@login_required
def library():
    """
    Render the library template on the /library route
    """
    games_data = []
    for data in db.session.query(Game).all():
        games_data.append(
            {'title': data.title, 'publication_year': int(data.publication_year), 'min_players': int(data.min_players),
             'max_players': int(data.max_players), 'image': data.image})
    return render_template('library.html', stylesheet='library', games_data=games_data)


@site.route('/add-games')
@login_required
def add_games():
    """
    Render the add-games template on the /add-games route
    """
    games_data = []
    years = set()
    players = set()
    playtime = set()
    for data in db.session.query(Game).all():
        games_data.append(
            {'title': data.title, 'publication_year': int(data.publication_year), 'min_players': int(data.min_players),
             'max_players': int(data.max_players), 'image': data.image})
        years.add(int(data.publication_year))
        players.add(int(data.min_players))
        players.add(int(data.max_players))
        playtime.add(int(data.min_playtime))
    return render_template('add-games.html', stylesheet='add-games', games_data=games_data, publication_years=years,
                           players_numbers=players, max_playtime=max(playtime), data=False)


# @site.route('/add-games', methods=['GET', 'POST'])
# @login_required
# def games_search():
