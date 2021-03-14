from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required
from .models.form import AddSession
import datetime
from . import session as session_bp
from app.models import Session, TimeSlot


@session_bp.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    """
    Render the sessions template on the /sessions route
    """
    return render_template('sessions.html', stylesheet='sessions')

@session_bp.route('/sessions_incomming', methods=['GET', 'POST'])
@login_required
def sessions_incomming():
    """
    Render the sessions template on the /sessions route
    """
    return render_template('sessions.html', stylesheet='sessions')

@session_bp.route('/sessions_passed', methods=['GET', 'POST'])
@login_required
def sessions_passed():
    """
    Render the sessions template on the /sessions route
    """
    return render_template('sessions.html', stylesheet='sessions')

@session_bp.route('/session-<int:session_id>', methods=['GET', 'POST'])
@login_required
def session(session_id):
    """
    Render the session template on the /session route
    """
    session = Session.from_id(session_id)
    return render_template('session.html', stylesheet='session', session = session, games=session.get_games(), players=session.get_players())


@session_bp.route('/addplayer_tosession-<int:session_id>', methods=['GET', 'POST'])
@login_required
def add_player(session_id):
    """
    Render the session template on the /session route
    """
    session = Session.from_id(session_id)
    return render_template('add_player.html', stylesheet='session', session = session)


@session_bp.route('/addgame_tosession-<int:session_id>', methods=['GET', 'POST'])
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
        date = form.day.data
        timeB = form.timeB.data
        timeE = form.timeE.data

        is_ok = True

        print(date)
        print(timeB)
        print(timeE)

        # check format day
        if (date == None):
            is_ok = False
            flash("Le format de la date ne correspond pas à AAAA-MM-JJ et/ou le numéro du mois (1-12) et/ou du jour(1-29/30/31 selon le mois) est incorrecte", "warning")

        # check format timeB
        if (timeB == None):
            is_ok = False
            flash("Le format de l'heure de début ne correspond pas à HH:MM, et/ou le numéro de l'heure (0-23) et/ou le nombre de minutes (0-59) est incorecte", "warning")
        
        # check format timeE
        if (timeE == None):
            is_ok = False
            flash("Le format de l'heure de fin ne correspond pas à HH:MM, et/ou le numéro de l'heure (0-23) et/ou le nombre de minutes (0-59) est incorecte", "warning")

        if is_ok:
            timeB.replace(second=0)
            timeE.replace(second=0)

            datetimeform = date.isoformat()+"T"+timeB.strftime('%H:%M:%S')

            actual = datetime.datetime.now().replace(microsecond = 0).isoformat() #give a sting in ISO 8601 : "YYYY-MM-DDTHH:MM:SS"

            if actual > datetimeform:
                is_ok = False
                flash("Vous ne pouvez pas créer une session pour une date antérieur à aujoud'hui", "warning")
                return redirect(url_for('session.organize_session'))
            
            else: 
                timeout = datetime.date(year=date.year, month=date.month, day=date.day+2)

                timeslot = TimeSlot (timeB.strftime('%H:%M:%S'), timeE.strftime('%H:%M:%S'), date.isoformat())
                # timeslot.add_to_db()
                session = Session(0,timeout.strftime('%Y-%m-%d %H:%M:%S'),1)
                # session.add_to_db()

                return redirect(url_for('session.session',session_id=1))
        else:
            return redirect(url_for("session.organize_session"))
    
    else:
        return render_template('organize_session.html', stylesheet='organize_session', form=form, dest="session.organize_session")
