from flask import request
from app.games.jeux.models.jeux_tools import get_sort_order, get_search_type, get_search_parameter, get_search_game

TITLES = {"UPCOMING": "Sessions à venir", "PASSED": "Sessions terminées"}
DEFAULT_TITLE = "Toutes les sessions"

def get_sessions_payload(user, form, page):
    """
    :param user: A instance of a user
    :return: a dict that contains every keys used for the sessions view
    """
    payload = dict()

    # Save those informations to display them when changing page
    form.display_search_parameter.data = get_search_parameter(form.display_search_parameter.data)
    form.sort_order.data = get_sort_order(form.sort_order.data)
    form.display_search_type.data = get_search_type(form.display_search_type.data)
    form.sessions_hint.data = get_search_game(form.sessions_hint.data)

    # If no hint was typed change search type back to game search (avoid crash)
    if not form.sessions_hint.data:
        form.display_search_type.data = "title"

    # We want to keep those informations to be able to show them on the next page
    payload["form"]=form

    # We want to obtain the sessions list that corresponds to what the user asked for
    payload["sessions"] = user.sessions_search_with_pagination(form.sessions_hint.data, form.display_search_type.data, form.display_search_parameter.data, page, 20, form.sort_order.data)

    return payload
