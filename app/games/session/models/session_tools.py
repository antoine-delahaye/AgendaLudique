from flask import request
from app.models import Session, TimeSlot
from app.games.jeux.models.jeux_tools import get_sort_order, get_search_type, get_search_parameter
import datetime

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
    form.sessions_hint.data = get_search_session(form.sessions_hint.data)

    # If no hint was typed change search type back to game search (avoid crash)
    if not form.sessions_hint.data:
        form.display_search_type.data = "title"

    # We want to keep those informations to be able to show them on the next page
    payload["form"]=form

    # We want to obtain the sessions list that corresponds to what the user asked for
    payload["sessions"] = user.sessions_search_with_pagination(form.sessions_hint.data, form.display_search_type.data, form.display_search_parameter.data, page, 20, form.sort_order.data)

    return payload

def get_search_session(session_hint):
    """
    :param session_hint: suspected session_hint
    :return: searched session_hint
    """
    if session_hint is None:
        session_hint = ""
    return request.args.get('sessions', session_hint, type=str)


def add_session_form(form):
    """
    Create the new objects related to the new organized session
    :return: if the session can be added, return the id of the session, else return False
    """
    date = form.day.data
    timeB = form.timeB.data
    timeE = form.timeE.data

    is_ok = True
    # check format day
    if date is None:
        is_ok = False
        flash("Le format de la date ne correspond pas à AAAA-MM-JJ et/ou le numéro du mois (1-12) et/ou du jour(1-29/30/31 selon le mois) est incorrecte", "warning")

    # check format timeB
    if timeB is None:
        is_ok = False
        flash("Le format de l'heure de début ne correspond pas à HH:MM, et/ou le numéro de l'heure (0-23) et/ou le nombre de minutes (0-59) est incorecte", "warning")

    # check format timeE
    if timeE is None:
        is_ok = False
        flash("Le format de l'heure de fin ne correspond pas à HH:MM, et/ou le numéro de l'heure (0-23) et/ou le nombre de minutes (0-59) est incorecte", "warning")

    if is_ok:
        timeB.replace(second=0)
        timeE.replace(second=0)

        datetimeform = date.isoformat()+"T"+timeB.strftime('%H:%M:%S')

        actual = datetime.datetime.now().replace(microsecond = 0).isoformat() #give a string in ISO 8601 : "YYYY-MM-DDTHH:MM:SS"

        if actual > datetimeform:
            is_ok = False
            flash("Vous ne pouvez pas créer une session pour une date antérieur à aujoud'hui", "warning")
            return False

    else:
        timeout = datetime.date(year=date.year, month=date.month, day=date.day+2)

        timeslot = TimeSlot(timeB.strftime('%H:%M:%S'), timeE.strftime('%H:%M:%S'), date.isoformat())
        # timeslot.add_to_db()
        session = Session(0,timeout.strftime('%Y-%m-%d %H:%M:%S'),1)
        # session.add_to_db()

        return session.id
