# Games adding/editing related ###################################################
import flask_login
from flask import render_template, redirect, url_for, request, make_response

from app.models import User, Game, Wish, Collect
from app.site.forms import GamesSimpleSearchForm, UpdateInformationForm, GamesSearchForm, AddGameForm
from flask_login import login_required, current_user
from . import jeux
from ... import db


@jeux.route('/catalog', methods=['GET', 'POST'])
@login_required
def catalog():
    """
    Render the catalog template on the /catalog route
    """
    form = GamesSimpleSearchForm()
    page = request.args.get('page', 1, type=int)
    games_hint = request.args.get('games', '', type=str)
    search_parameters = []
    qs_search_parameters = request.args.get('searchParameters', None, type=str)

    if form.validate_on_submit():
        games_hint = form.games_hint.data
        if form.display_known_games.data:
            search_parameters.append("KNOWN")
        if form.display_noted_games.data:
            search_parameters.append("NOTED")

    if qs_search_parameters:
        # Add the search parameters contained in the query string into the search_parameters list
        parameters_list = qs_search_parameters.split(',')
        for parameter in parameters_list:
            search_parameters.append(parameter)
            # Show in the advanced search menu the enabled parameters
            if parameter == "KNOWN":
                form.display_known_games.data = True
            if parameter == "NOTED":
                form.display_noted_games.data = True
        games = Game.search_with_pagination(flask_login.current_user.id, games_hint, request.args.get("type"),
                                            search_parameters, page, 20)
    else:
        games = Game.search_with_pagination(flask_login.current_user.id, games_hint, request.args.get("type"),
                                            search_parameters, page, 20)

    owned_games = User.get_owned_games(flask_login.current_user.id, True)
    wished_games = User.get_wished_games(flask_login.current_user.id, True)

    return render_template('catalog.html', stylesheet='catalog', form=form, games=games, owned_games=owned_games,
                           wished_games=wished_games)


@jeux.route('/add-games', methods=['GET', 'POST'])
@login_required
def add_games():
    """
    Render the add-games template on the /add-games route
    """
    games_search_form = GamesSearchForm()
    for data in db.session.query(Game).all():
        games_search_form.title.choices.append(data.title)
        if data.publication_year not in games_search_form.years.choices:
            games_search_form.years.choices.append(data.publication_year)
        if data.min_players not in games_search_form.min_players.choices:
            games_search_form.min_players.choices.append(data.min_players)
        if data.max_players not in games_search_form.max_players.choices:
            games_search_form.max_players.choices.append(data.max_players)
        if data.min_playtime not in games_search_form.min_playtime.choices and data.min_playtime not in games_search_form.max_playtime.choices:
            games_search_form.min_playtime.choices.append(data.min_playtime)
            games_search_form.max_playtime.choices.append(data.min_playtime)
    games_search_form.years.choices.sort()
    games_search_form.min_players.choices.sort()
    games_search_form.max_players.choices.sort()
    games_search_form.min_playtime.choices.sort()
    games_search_form.max_playtime.choices.sort()
    games_search_form.title.choices.insert(0, 'Aucun')
    games_search_form.years.choices.insert(0, 'Aucune')
    games_search_form.min_players.choices.insert(0, 'Aucun')
    games_search_form.max_players.choices.insert(0, 'Aucun')
    games_search_form.min_playtime.choices.insert(0, 'Aucune')
    games_search_form.max_playtime.choices.insert(0, 'Aucune')
    add_game_form = AddGameForm()
    if games_search_form.validate_on_submit():
        researched_game = Game.query.filter_by(title=games_search_form.title.data).first()
        print(researched_game)
        return render_template('add-games.html', games_search_form=games_search_form, stylesheet='add-games',
                               researched_game=researched_game, add_game_form=add_game_form)
    if add_game_form.validate_on_submit():
        game_id = Game.max_id() + 1
        if game_id is None:
            game_id = 0
        Game.add_game(game_id,
                      {'title': add_game_form.title.data, 'publication_year': add_game_form.years.data,
                       'min_players': int(add_game_form.min_players.data),
                       'max_players': int(add_game_form.max_players.data),
                       'min_playtime': int(add_game_form.min_playtime.data), 'image': add_game_form.image.data})
        return redirect(url_for('jeux.game', game_id=game_id))
    return render_template('add-games.html', stylesheet='add-games', games_search_form=games_search_form,
                           add_game_form=add_game_form)


@jeux.route('/edit-games', methods=['GET', 'POST'])
@login_required
def edit_games():
    """
    Render the edit-games template on the /edit-games route
    """
    form = UpdateInformationForm()
    if form.validate_on_submit():
        return redirect(url_for('site.edit-games'))
    return render_template('edit-games.html', stylesheet='edit-games', form=form)


@jeux.route('/game', methods=['GET', 'POST'])
@jeux.route('/game/<game_id>', methods=['GET', 'POST'])
@login_required
def game(game_id):
    """
    Render the game template on the /game route
    """
    return render_template('game.html', stylesheet=None, game=Game.from_id(game_id),
                           owned_games=User.get_owned_games(flask_login.current_user.id, True))


@jeux.route('/wishes')
@login_required
def wishes():
    """
    Render the library template on the /wish route
    """
    page = request.args.get('page', 1, type=int)
    wished_games = User.get_wished_games(flask_login.current_user.id).paginate(page=page, per_page=20)
    owned_games = User.get_owned_games(flask_login.current_user.id, True)
    return render_template('wishes.html', stylesheet='library', wished_games=wished_games, owned_games=owned_games)


@jeux.route('/add-wishes', methods=['GET', 'POST'])
@jeux.route('/add-wishes/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_wish(game_id):
    db.session.add(Wish(user_id=flask_login.current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove-wishes', methods=['GET', 'POST'])
@jeux.route('/remove-wishes/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_wish(game_id):
    db.session.delete(Wish.query.filter_by(user_id=flask_login.current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/library')
@login_required
def library():
    """
    Render the library template on the /library route
    """
    page = request.args.get('page', 1, type=int)
    owned_games = User.get_owned_games(flask_login.current_user.id).paginate(page=page, per_page=20)
    wished_games = User.get_wished_games(flask_login.current_user.id, True)
    return render_template('library.html', stylesheet='library', owned_games=owned_games, wished_games=wished_games)


@jeux.route('/add-collection', methods=['GET', 'POST'])
@jeux.route('/add-collection/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_collection(game_id):
    db.session.add(Collect(user_id=flask_login.current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove', methods=['GET', 'POST'])
@jeux.route('/remove/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_collection(game_id):
    db.session.delete(Collect.query.filter_by(user_id=flask_login.current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)