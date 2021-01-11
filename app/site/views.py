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

# Account/Profil related #########################################################
@site.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    """
    Render the user template on the /user route
    """
    return render_template('users.html', stylesheet='users')

@site.route('/user')
@site.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def user(id = None):
    """
    Render the user template on the /user route
    """
    user=User.query.get_or_404(id)
    return render_template('user.html', stylesheet='user', user=user)

@site.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    Render the account template on the /account route
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

@site.route('/parameters', methods=['GET', 'POST'])
@login_required
def parameters():
    """
    Render the parameters template on the /parameters route
    """
    return render_template('parameters.html', stylesheet='parameters')

# Group related ##################################################################
@site.route('/groups')
@login_required
def groups():
    """
    Render the groups template on the /groups route
    """
    return render_template('groups.html', stylesheet='groups')

@site.route('/group', methods=['GET', 'POST'])
@login_required
def group():
    """
    Render the group template on the /group route
    """
    return render_template('group.html', stylesheet='group')

# Session related ################################################################
@site.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    """
    Render the sessions template on the /sessions route
    """
    return render_template('sessions.html', stylesheet='sessions')

@site.route('/session', methods=['GET', 'POST'])
@login_required
def session():
    """
    Render the session template on the /session route
    """
    return render_template('session.html', stylesheet='session')

@site.route('/organize_session', methods=['GET', 'POST'])
@login_required
def organize_session():
    """
    Render the organize_session template on the /organize_session route
    """
    return render_template('organize_session.html', stylesheet='organize_session')

# Games adding/editing related ###################################################
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

@site.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    """
    Render the game template on the /game route
    """
    return render_template('game.html', stylesheet='game')

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
    return render_template('add-games.html', stylesheet='add-games', form=form)

@site.route('/edit-games', methods=['GET', 'POST'])
@login_required
def edit_games():
    """
    Render the edit-games template on the /edit-games route
    """
    form = UpdateInformationForm()
    if form.validate_on_submit():
        return redirect(url_for('site.edit-games'))
    return render_template('edit-games.html', stylesheet='edit-games', form=form)