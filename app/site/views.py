# app/site/views.py
import flask_login
from flask import render_template, redirect, url_for
from flask_login import login_required

from app.site import site
from app.site.forms import UpdateInformationForm, GamesSearchForm
from app import db
from app.models import User, Game


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
            {'id': int(data.id), 'title': data.title, 'publication_year': int(data.publication_year), 'min_players': int(data.min_players),
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
            {'id': int(data.id), 'title': data.title, 'publication_year': int(data.publication_year), 'min_players': int(data.min_players),
             'max_players': int(data.max_players), 'image': data.image})
    return render_template('library.html', stylesheet='library', games_data=games_data)


@site.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    Render the homepage template on the / route
    """
    form = UpdateInformationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=flask_login.current_user.email).first()
        if user is not None:
            user.username = form.username.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.password = form.password.data
            user.profile_picture = form.profile_picture.data
            db.session.commit()
        return redirect(url_for('site.account'))
    return render_template('account.html', stylesheet='account', form=form)


@site.route('/add-games', methods=['GET', 'POST'])
@login_required
def add_games():
    """
    Render the add-games template on the /add-games route
    """
    form = GamesSearchForm()
    for data in db.session.query(Game).all():
        form.title.choices.append(data.title)
        if data.publication_year not in form.years.choices:
            form.years.choices.append(data.publication_year)
        if data.min_players not in form.min_players.choices:
            form.min_players.choices.append(data.min_players)
        if data.max_players not in form.max_players.choices:
            form.max_players.choices.append(data.max_players)
        if data.min_playtime not in form.min_playtime.choices and data.min_playtime not in form.max_playtime.choices:
            form.min_playtime.choices.append(data.min_playtime)
            form.max_playtime.choices.append(data.min_playtime)
    form.years.choices.sort()
    form.min_players.choices.sort()
    form.max_players.choices.sort()
    form.min_playtime.choices.sort()
    form.max_playtime.choices.sort()
    form.title.choices.insert(0, 'Aucun')
    form.years.choices.insert(0, 'Aucune')
    form.min_players.choices.insert(0, 'Aucun')
    form.max_players.choices.insert(0, 'Aucun')
    form.min_playtime.choices.insert(0, 'Aucune')
    form.max_playtime.choices.insert(0, 'Aucune')
    if form.validate_on_submit():
        researched_game = Game.query.filter_by(title=form.title.data).first()
        print(researched_game)
        return render_template('add-games.html', form=form, stylesheet='add-games', researched_game=researched_game)
    return render_template('add-games.html', form=form, stylesheet='add-games')
