from app.games.jeux.models.jeux_tools import get_numero_page
from sqlalchemy.sql.functions import current_user
from app.games.session.models.session_tools import get_sessions_payload
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from .models.forms import AddSession, SessionSearchForm
import datetime
from . import session as session_bp
from app.models import Session, TimeSlot
from .models.session_tools import TITLES, DEFAULT_TITLE, get_sessions_payload, add_session_form


@session_bp.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    """
    Render the sessions template on the /sessions route
    """
    form = SessionSearchForm()
    page = get_numero_page()
    payload = get_sessions_payload(current_user, form, page)

    # Change title of the page in function of search_parameter
    title = TITLES.get(payload.get("search_parameter"), DEFAULT_TITLE)

    return render_template('sessions.html',
                            stylesheet='users',
                            title=title,
                            now=datetime.datetime.now(),
                            **payload)


@session_bp.route('/session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def session(session_id):
    """
    Render the session template on the /session route
    """
    session = Session.from_id(session_id)
    return render_template('session.html',
                            stylesheet='session',
                            session = session,
                            games=session.get_games(),
                            players=session.get_players(),
                            users_data = current_user.users_search_with_pagination("", False, False, per_page=15))


@session_bp.route('/addplayer_tosession/<int:session_id>', methods=['GET', 'POST'])
@login_required
def add_player(session_id):
    """
    Render the session template on the /session route
    """
    session = Session.from_id(session_id)
    return render_template('add_player.html', stylesheet='session', session = session)


@session_bp.route('/addgame_tosession/<int:session_id>', methods=['GET', 'POST'])
@login_required
def add_game(session_id):
    """
    Render the session template on the /session route
    """
    session = Session.from_id(session_id)
    return render_template('add_player.html', stylesheet='session', session = session)


@session_bp.route('/organize_session', methods=['GET', 'POST'])
@login_required
def organize_session():
    """
    Render the organize_session template on the /organize_session route
    """

    # get_flashed_messages()
    form = AddSession()

    if request.method == "POST":
        if add_session_form(form):
            return redirect(url_for('session.session',session_id=1))
        else:
            return redirect(url_for("session.organize_session"))
    else:
        return render_template('organize_session.html', stylesheet='organize_session', form=form, dest="session.organize_session")
