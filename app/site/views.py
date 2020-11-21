# app/site/views.py

from flask import render_template
from flask_login import login_required

from . import site


@site.route('/')
def home():
    """
    Render the homepage template on the / route
    """
    return render_template('home.html', stylesheet='home')


@site.route('/library')
@login_required
def library():
    """
    Render the library template on the /library route
    """
    return render_template('library.html', stylesheet='library')
