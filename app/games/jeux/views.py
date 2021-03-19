# Games adding/editing related ###################################################
from flask import render_template, redirect, url_for, request
from app.models import Game, Wish, Collect, KnowRules, Note
from app.site.models.forms import GamesSearchForm, UpdateInformationForm, AddGamesSearchForm, AddGameForm
from flask_login import login_required, current_user
from . import jeux
from .models.games_form_tools import populate_games_form, beautify_games_form, add_default_values_game_form
from .models.jeux_tools import get_numero_page, TITLES, DEFAULT_TITLE, get_catalog_payload, id_query_to_set
from app import db


@jeux.route('/catalog', methods=['GET', 'POST'])
@login_required
def catalog():
    """
    Render the catalog template on the /catalog route
    """
    form = GamesSearchForm()
    page = get_numero_page()
    payload = get_catalog_payload(current_user, form, page)

    return render_template('catalog.html', stylesheet='catalog', **payload)


@jeux.route('/add-games', methods=['GET', 'POST'])
@login_required
def add_games():
    """
    Render the add-games template on the /add-games route
    """
    search_form = AddGamesSearchForm()
    populate_games_form(search_form)
    beautify_games_form(search_form)
    add_default_values_game_form(search_form)
    add_game_form = AddGameForm()
    if search_form.validate_on_submit():
        Game.from_title(search_form.title.data)
        return render_template('add-games.html', form=search_form, stylesheet='add-games', add_game_form=add_game_form)
    if add_game_form.validate_on_submit():
        game_id = Game.max_id() + 1
        Game.add_game(game_id,
                      {'title': add_game_form.title.data, 'publication_year': add_game_form.years.data,
                       'min_players': int(add_game_form.min_players.data),
                       'max_players': int(add_game_form.max_players.data),
                       'min_playtime': int(add_game_form.min_playtime.data), 'image': add_game_form.image.data})
        return redirect(url_for('jeux.game', game_id=game_id))
    return render_template('add-games.html', stylesheet='add-games', add_game_form=add_game_form)


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
                           owned_games=id_query_to_set(current_user.get_owned_games(True)),
                           wished_games=id_query_to_set(current_user.get_wished_games(True)),
                           noted_games=id_query_to_set(current_user.get_noted_games(True)),
                           ratings=Note.from_both_ids(current_user.id, game_id),
                           average_grade=Note.average_grade(game_id),
                           messages=Note.get_messages(game_id, 5))


@jeux.route('/add-wishes', methods=['GET', 'POST'])
@jeux.route('/add-wishes/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_wish(game_id):
    db.session.add(Wish(user_id=current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove-wishes', methods=['GET', 'POST'])
@jeux.route('/remove-wishes/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_wish(game_id):
    db.session.delete(Wish.query.filter_by(user_id=current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/add-collection', methods=['GET', 'POST'])
@jeux.route('/add-collection/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_collection(game_id):
    db.session.add(Collect(user_id=current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove-collection', methods=['GET', 'POST'])
@jeux.route('/remove-collection/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_collection(game_id):
    db.session.delete(Collect.query.filter_by(user_id=current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/add-known', methods=['GET', 'POST'])
@jeux.route('/add-known/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_known(game_id):
    db.session.add(KnowRules(user_id=current_user.id, game_id=game_id))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove-known', methods=['GET', 'POST'])
@jeux.route('/remove-known/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_known(game_id):
    db.session.delete(KnowRules.query.filter_by(user_id=current_user.id, game_id=game_id).first())
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/add-note', methods=['GET', 'POST'])
@jeux.route('/add-note/<game_id>', methods=['GET', 'POST'])
@login_required
def add_game_note(game_id):
    note = request.form.get("note", False)
    message = request.form.get("message-text", False)
    db.session.add(Note(user_id=current_user.id, game_id=game_id, note=note, message=message))
    db.session.commit()
    return redirect(request.referrer)


@jeux.route('/remove-noted', methods=['GET', 'POST'])
@jeux.route('/remove-noted/<game_id>', methods=['GET', 'POST'])
@login_required
def remove_game_note(game_id):
    db.session.delete(Note.query.filter_by(user_id=current_user.id, game_id=game_id).first())
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
