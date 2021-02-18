# Games adding/editing related ###################################################
import flask_login
from flask import render_template, redirect, url_for, request

from app.models import User, Game, Wish, Collect, KnowRules, Note
from app.site.models.forms import GamesSimpleSearchForm, UpdateInformationForm, GamesSearchForm, AddGameForm
from flask_login import login_required, current_user
from . import jeux
from .models.jeux_tools import get_numero_page, get_search_parameter, get_search_type, get_search_game, TITLES, \
    DEFAULT_TITLE, get_known_noted_games
from app import db
from ..group.models.group_tools import populate_games_form, beautify_games_form, add_default_values_game_form


@jeux.route('/catalog', methods=['GET', 'POST'])
@login_required
def catalog():
    """
    Render the catalog template on the /catalog route
    """
    form = GamesSimpleSearchForm()
    page = get_numero_page()
    ratings = {}

    search_parameter = get_search_parameter(form.display_search_parameter.data)

    # Save the search filter
    form.display_search_type.data = get_search_type(form.display_search_type.data)
    # Fill search bar with parameters when changing page
    form.games_hint.data = get_search_game(form.games_hint.data)

    # If no hint was typed change search type back to title search (avoid crash)
    if not form.games_hint.data:
        form.display_search_type.data = 'title'

    # Change title of the page in function of search_parameter
    title = TITLES.get(search_parameter, DEFAULT_TITLE)

    # We want to remove already owned and wished games from the page
    owned_games = User.get_owned_games(current_user.id, True)
    wished_games = User.get_wished_games(current_user.id, True)

    # But wewant to know what games the user already knows or has noted
    known_games, noted_games = get_known_noted_games(current_user, search_parameter)
    for id in noted_games:
        ratings[id] = Note.from_both_ids(current_user.id, id)
    search_results = Game.search_with_pagination(flask_login.current_user.id, form.games_hint.data,
                                                 form.display_search_type.data, search_parameter, page, 20)

    # print(form.display_search_type.data)

    return render_template('catalog.html', stylesheet='catalog', title=title, form=form, games=search_results,
                           owned_games=owned_games, wished_games=wished_games, known_games=known_games,
                           noted_games=noted_games, search_parameter=search_parameter,
                           type=form.display_search_type.data, games_hint=form.games_hint.data, ratings=ratings)


@jeux.route('/add-games', methods=['GET', 'POST'])
@login_required
def add_games():
    """
    Render the add-games template on the /add-games route
    """
    search_form = GamesSearchForm()

    populate_games_form(search_form)
    beautify_games_form(search_form)
    add_default_values_game_form()

    add_game_form = AddGameForm()
    if search_form.validate_on_submit():
        researched_game = Game.from_title(search_form.title.data)
        # print(researched_game)
        return render_template('add-games.html', form=search_form, stylesheet='add-games',
                               researched_game=researched_game, add_game_form=add_game_form)
    if add_game_form.validate_on_submit():
        game_id = Game.max_id() + 1
        Game.add_game(game_id,
                      {'title': add_game_form.title.data, 'publication_year': add_game_form.years.data,
                       'min_players': int(add_game_form.min_players.data),
                       'max_players': int(add_game_form.max_players.data),
                       'min_playtime': int(add_game_form.min_playtime.data), 'image': add_game_form.image.data})
        return redirect(url_for('jeux.game', game_id=game_id))
    return render_template('add-games.html', stylesheet='add-games', form=search_form,
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
    return render_template('game.html', game=Game.from_id(game_id),
                           owned_games=User.get_owned_games(flask_login.current_user.id, True),
                           wished_games=User.get_wished_games(flask_login.current_user.id, True))


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


@jeux.route('/add-collection', methods=['GET', 'POST'])
@jeux.route('/add-collection/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_collection(game_id):
    db.session.add(Collect(user_id=flask_login.current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove-collection', methods=['GET', 'POST'])
@jeux.route('/remove-collection/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_collection(game_id):
    db.session.delete(Collect.query.filter_by(user_id=flask_login.current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/add-known', methods=['GET', 'POST'])
@jeux.route('/add-known/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_known(game_id):
    db.session.add(KnowRules(user_id=flask_login.current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove-known', methods=['GET', 'POST'])
@jeux.route('/remove-known/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_known(game_id):
    db.session.delete(KnowRules.query.filter_by(user_id=flask_login.current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/add-note', methods=['GET', 'POST'])
@jeux.route('/add-note/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_note(game_id):
    note = request.form.get("note", False)
    message = request.form.get("message-text", False)
    db.session.add(Note(user_id=flask_login.current_user.id, game_id=game_id, note=note, message=message))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove-noted', methods=['GET', 'POST'])
@jeux.route('/remove-noted/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_note(game_id):
    db.session.delete(Note.query.filter_by(user_id=flask_login.current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/update-noted', methods=['GET', 'POST'])
@jeux.route('/update-noted/<game_id>', methods=['GET', 'POST'])
@login_required
def update_game_note(game_id):
    remove_game_note(game_id)
    add_game_note(game_id)
    db.session.commit()
    return redirect(request.referrer)

