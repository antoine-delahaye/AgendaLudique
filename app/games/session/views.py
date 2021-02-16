from flask import render_template
from flask_login import login_required

from . import session as session_bp


@session_bp.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    """
    Render the sessions template on the /sessions route
    """
    return render_template('sessions.html', stylesheet='sessions')


@session_bp.route('/session', methods=['GET', 'POST'])
@login_required
def session():
    """
    Render the session template on the /session route
    """
    return render_template('session.html', stylesheet='session')


@session_bp.route('/organize_session', methods=['GET', 'POST'])
@login_required
def organize_session():
    """
    Render the organize_session template on the /organize_session route
    """
    return render_template('organize_session.html', stylesheet='organize_session')
