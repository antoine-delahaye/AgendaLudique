# app/site/views.py
import flask_login
from flask import render_template, redirect, url_for, request, make_response
from flask_login import login_required, current_user

from app.site import site
from app.site.forms import UpdateInformationForm, GamesSearchForm, UsersSearchForm
from app import db
from app.models import User, Game, Group, HideUser, BookmarkUser, Collect


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
    page = request.args.get('page', 1, type=int)
    games = Game.query.paginate(page=page, per_page=20)
    user_collection = []
    for data in Collect.query.filter_by(user_id=flask_login.current_user.id).all():
        user_collection.append(data.game_id)
    return render_template('library.html', stylesheet='library', games=games, user_collection=user_collection)


@site.route('/remove', methods=['GET', 'POST'])
@site.route('/remove/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_collection(game_id):
    db.session.delete(Collect.query.filter_by(user_id=flask_login.current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


# Account/Profil related #########################################################
@site.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    """
    Render the users template on the /users route
    """
    form = UsersSearchForm()

    db_players = []
    result_users_data = []

    if form.validate_on_submit():
        username_hint = form.username_hint.data
        if username_hint is not None:
            db_players = db.session.query(User).filter(User.username.like('%' + username_hint + '%'))
    else:
        db_players = db.session.query(User).limit(12).all()

    for data in db_players:
        result_users_data.append(
            {'id': int(data.id), 'username': data.username, 'first_name': data.first_name, 'last_name': data.last_name,
             'profile_picture': data.profile_picture})

    return render_template('users.html', stylesheet='users', form=form, users_data=result_users_data)


@site.route('/user')
@site.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def user(id=None):
    """
    Render the user template on the /user route
    """
    user = User.query.get_or_404(id)
    return render_template('user.html', stylesheet='user', user=user)


@site.route('/hide-user', methods=['GET'])
@login_required
def hide_user(user_id=None):
    """
    Add the declared user (property "user" in the query string) to the hidden users
    on the /hide-user route.
    """
    connected_user = current_user
    user_id = request.args.get('user')

    if user_id is not None:
        user_to_hide = User.query.get(user_id)
        if user_to_hide is not None:
            hidden_user = HideUser(user_id=connected_user.id, user2_id=user_to_hide.id)
            db.session.add(hidden_user)
            db.session.commit()

    return redirect(url_for('site.users'))


@site.route('/bookmark-user', methods=['GET'])
@login_required
def bookmark_user(user_id=None):
    """
    Add the declared user (property "user" in the query string) to the bookmarked users
    on the /bookmark-user route.
    """
    connected_user = current_user
    user_id = request.args.get('user')

    if user_id is not None:
        user_to_bookmark = User.query.get(user_id)
        if user_to_bookmark is not None:
            bookmarked_user = BookmarkUser(user_id=connected_user.id, user2_id=user_to_bookmark.id)
            db.session.add(bookmarked_user)
            db.session.commit()

    return redirect(url_for('site.users'))


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


@site.route('/parameters')
@login_required
def parameters():
    """
    Render the parameters template on the /parameters route
    """
    return render_template('parameters.html', stylesheet=None)


@site.route('/set_parameters', methods=['POST'])
@login_required
def set_parameters():
    color_theme = "On" if request.form.get('color-theme') != None else "Off"
    param = make_response(redirect(url_for('site.parameters')))
    param.set_cookie('color-theme', color_theme)
    return param


# Group related ##################################################################
@site.route('/groups')
@login_required
def groups():
    """
    Render the groups template on the /groups route
    """
    groups_data = []
    for data in db.session.query(Group).all():
        groups_data.append(
            {'id': int(data.id), 'name': data.name})
    return render_template('groups.html', stylesheet='groups', groups_data=groups_data)


@site.route('/groups_private')
@login_required
def groups_private():
    """
    Render the groups template on the /groups_private route
    """
    groups_data = []
    for data in db.session.query(Group).all():
        if data.is_private == False:
            groups_data.append(
                {'id': int(data.id), 'name': data.name})
    return render_template('groups_private.html', stylesheet='groups', groups_data=groups_data)


@site.route('/group')
@site.route('/group/<int:id>', methods=['GET', 'POST'])
@login_required
def group(id=None):
    """
    Render the groups template on the /group route
    """
    group = Group.query.get_or_404(id)
    return render_template('group.html', stylesheet='group', group=group)


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
    page = request.args.get('page', 1, type=int)
    games = Game.query.paginate(page=page, per_page=20)
    user_collection = []
    for data in Collect.query.filter_by(user_id=flask_login.current_user.id).all():
        user_collection.append(data.game_id)
    return render_template('catalog.html', stylesheet='catalog', games=games, user_collection=user_collection)


@site.route('/add', methods=['GET', 'POST'])
@site.route('/add/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_collection(game_id):
    db.session.add(Collect(user_id=flask_login.current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


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
