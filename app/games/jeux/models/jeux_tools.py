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

    # Save the search filter when changing page
    form.display_search_type.data = get_search_type(form.display_search_type.data)
    # Fill search bar with parameters when changing page
    form.games_hint.data = get_search_game(form.games_hint.data)

    # If no hint was typed change search type back to title search (avoid crash)
    if not form.games_hint.data:
        form.display_search_type.data = 'title'

    # We want to remove already owned and wished games from the page
    
    
    payload["games_hint"] = form.games_hint.data
    payload['type'] = form.display_search_type.data

    # We want to know which games the user already knows, wishes, owns or has noted
    noted_games = User.get_noted_games(user.id, True)
    payload["known_games"] = id_query_to_set(User.get_known_games(user.id, True))
    payload["noted_games"] = id_query_to_set(noted_games)
    payload["wished_games"] = id_query_to_set(User.get_wished_games(user.id, True))
    payload["owned_games"] = id_query_to_set(User.get_owned_games(user.id, True))

    payload["ratings"] = User.get_noted_games(user.id, True)

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

def id_query_to_set(query):
    ids = set()
    for game in query:
        ids.add(game.game_id)
    return ids