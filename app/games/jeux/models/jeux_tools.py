from flask import request

from app.models import User, Game

TITLES = {"KNOWN": "Jeux que vous connaissez", "NOTED": "Jeux que vous avez déjà notés",
          "WISHED": "Jeux que vous souhaitez", "OWNED": "Jeux que vous possédez"}
DEFAULT_TITLE = "Tous les jeux"


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
