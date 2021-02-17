# Games adding/editing related ###################################################
import flask_login
from flask import render_template, redirect, url_for, request, make_response

from app.models import User, Game, Wish, Collect, KnowRules, Note
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

    # Get search format and hint if there are one
    search_parameter = form.display_search_parameter.data if form.display_search_parameter.data else request.args.get('searchParameter', None, type=str)

    # We want to remove already owned and wished games from the page
    owned_games = User.get_owned_games(flask_login.current_user.id, True)
    wished_games = User.get_wished_games(flask_login.current_user.id, True)

    # But wewant to know what games the user already knows or has noted
    known_games = User.get_known_games(flask_login.current_user.id, True)
    noted_games = User.get_noted_games(flask_login.current_user.id, True)

    # If no hint was typed change search type back to title search (avoid crash)
    if not form.games_hint.data:
        form.display_search_type.data = 'title'
        # Fill search bar with parameters when changing page
        form.games_hint.data = request.args.get('games', '', type=str)

    # Change title of the page and filters in function of search_parameter
    if search_parameter == "KNOWN":
        title = "Jeux que vous connaissez"
    elif search_parameter == "NOTED":
        title = "Jeux que vous avez déjà notés"
    elif search_parameter == "WISHED":
        title = "Jeux que vous souhaitez"
        wished_games = Game.query.filter(False)
    elif search_parameter == "OWNED":
        title = "Jeux que vous possédez"
        owned_games = Game.query.filter(False)
    else:
        title = "Tous les jeux"
    games = Game.search_with_pagination(flask_login.current_user.id, form.games_hint.data, form.display_search_type.data, search_parameter, page, 20)

    return render_template('catalog.html', stylesheet='catalog', title=title, form=form, games=games, owned_games=owned_games, wished_games=wished_games, known_games=known_games, noted_games=noted_games, search_parameter=search_parameter, games_hint=form.games_hint.data)


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
        game_id = Game.max_id()
        if game_id is None:
            game_id = 0
        game_id += 1
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


@jeux.route('/remove', methods=['GET', 'POST'])
@jeux.route('/remove/<game_id>', methods=['GET', 'POST'])
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


@jeux.route('/remove', methods=['GET', 'POST'])
@jeux.route('/remove/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_known(game_id):
    db.session.delete(KnowRules.query.filter_by(user_id=flask_login.current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/add-note', methods=['GET', 'POST'])
@jeux.route('/add-note/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_note(game_id):
    db.session.add(Note(user_id=flask_login.current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove', methods=['GET', 'POST'])
@jeux.route('/remove/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_note(game_id):
    db.session.delete(Note.query.filter_by(user_id=flask_login.current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)
