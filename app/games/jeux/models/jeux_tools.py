from flask import request

from app.models import User, Game, Note

TITLES = {"KNOWN": "Jeux que vous connaissez", "NOTED": "Jeux que vous avez déjà notés",
          "WISHED": "Jeux que vous souhaitez", "OWNED": "Jeux que vous possédez"}
DEFAULT_TITLE = "Tous les jeux"


def get_catalog_payload(form, user, page):
    """
    :param form: GamesSimpleSearchForm
    :return: a dict that contains every keys used for the catalog view
    """
    payload = dict()
    search_parameter = get_search_parameter(form.display_search_parameter.data)
    payload["search_parameter"] = search_parameter

    # Save the search filter
    form.display_search_type.data = get_search_type(form.display_search_type.data)
    # Fill search bar with parameters when changing page
    form.games_hint.data = get_search_game(form.games_hint.data)

    # If no hint was typed change search type back to title search (avoid crash)
    if not form.games_hint.data:
        form.display_search_type.data = 'title'

    # We want to remove already owned and wished games from the page
    payload["owned_games"] = User.get_owned_games(user.id, True)
    payload["wished_games"] = User.get_wished_games(user.id, True)
    payload["games_hint"] = form.games_hint.data
    payload['type'] = form.display_search_type.data

    # But wewant to know what games the user already knows or has noted
    known_games, noted_games = get_known_noted_games(user, search_parameter)
    payload["known_games"] = known_games
    payload["noted_games"] = noted_games
    payload["ratings"] = {}
    for id in noted_games:
        payload.get("ratings")[id] = Note.from_both_ids(user.id, id)
    payload["games"] = Game.search_with_pagination(user.id, form.games_hint.data,
                                                   form.display_search_type.data, search_parameter, page, 20)

    return payload


def get_numero_page():
    """
    :return: int that correspond to the current page number
    """
    return request.args.get('page', 1, type=int)


def get_search_parameter(search_parameter):
    """
    :param search_parameter: supossed search_parameter
    :return: search parameter if exists
    """
    if search_parameter is None:
        return request.args.get('searchParameter', None, type=str)
    return search_parameter


def get_search_type(search_type):
    """

    :param search_type: current search type
    :return: searched type
    """
    return request.args.get('type', search_type, type=str)


def get_search_game(game_hint):
    """

    :param game_hint: suspected game_hint
    :return: searched game
    """
    if game_hint is None:
        game_hint = ""
    return request.args.get('games', game_hint, type=str)


def get_known_noted_games(user, search_parameter):
    """
    :param user: user in which we are interested
    :param search_parameter: user search filter
    :return: tuple (known_games, noted_games)
    """
    known_games = User.get_known_games(user.id, True)
    noted_games = User.get_noted_games(user.id, True)

    # Change filters in function of search_parameter
    if search_parameter == "WISHED":
        wished_games = Game.query.filter(False)
    elif search_parameter == "OWNED":
        owned_games = Game.query.filter(False)
    return known_games, noted_games
