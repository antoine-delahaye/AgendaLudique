from flask import request

from app.models import Game

TITLES = {"KNOWN": "Jeux que vous connaissez", "NOTED": "Jeux que vous avez déjà notés",
          "WISHED": "Jeux que vous souhaitez", "OWNED": "Jeux que vous possédez"}
DEFAULT_TITLE = "Tous les jeux"


def get_catalog_payload(user, form, page):
    """
    :param form: GamesSearchForm
    :return: a dict that contains every keys used for the catalog view
    """
    payload = dict()

    # Save those informations to display them when changing page
    form.display_search_parameter.data = get_search_parameter(form.display_search_parameter.data)
    form.sort_order.data = get_sort_order(form.sort_order.data)
    form.results_per_page.data = get_results_per_page(form.results_per_page.data)
    form.display_search_type.data = get_search_type(form.display_search_type.data)
    form.games_hint.data = get_search_game(form.games_hint.data)

    # If no hint was typed change search type back to title search (avoid crash)
    if not form.games_hint.data:
        form.display_search_type.data = "title"

    # We want to keep those informations to be able to show them on the next page
    payload["form"]=form

    # Change title of the page in function of search_parameter
    payload["title"]=TITLES.get(form.display_search_parameter.data, DEFAULT_TITLE)

    # We want to know games notes and comments made by the current user
    payload["ratings"] = user.get_noted_games(False, True)
    # We want to know games frequences set by the current user
    payload["freqs"] = user.get_freq_games(False, True)

    # We want to know which games the user already knows, wishes, owns or has noted
    payload["known_games"] = id_query_to_set(user.get_known_games(True))
    payload["noted_games"] = id_query_to_set(payload["ratings"])
    payload["freq_games"] = id_query_to_set(payload["freqs"])
    payload["wished_games"] = id_query_to_set(user.get_wished_games(True))
    payload["owned_games"] = id_query_to_set(user.get_owned_games(True))

    # We want to obtain the games list that corresponds to what the user asked for
    payload["games"] = user.games_search_with_pagination(form.games_hint.data, form.display_search_type.data, form.display_search_parameter.data, page, int(form.results_per_page.data), form.sort_order.data)

    return payload


def get_numero_page():
    """
    :return: int that correspond to the current page number
    """
    return request.args.get('page', 1, type=int)


def get_search_parameter(search_parameter):
    """
    :param search_parameter: suposed search_parameter
    :return: search parameter if exists
    """
    return request.args.get('searchParameter', search_parameter, type=str)

def get_search_type(search_type):
    """

    :param search_type: current search type
    :return: searched type
    """
    return request.args.get('type', search_type, type=str)

def get_search_game(game_hint):
    """
    :param game_hint: suspected game_hint
    :return: searched game_hint
    """
    if game_hint is None:
        game_hint = ""
    return request.args.get('games', game_hint, type=str)

def get_sort_order(sort_order):
    """
    :param sort_order: current sort_order
    :return: sort ordering of the search
    """
    return request.args.get('sort_order', sort_order, type=str)

def get_results_per_page(per_page):
    """
    :return: int that corresponds to number of game cards per page
    """
    if per_page is None:
        per_page = "20"
    return request.args.get('per_page', per_page, type=str)


def id_query_to_set(query):
    ids = set()
    for game in query:
        ids.add(game.game_id)
    return ids