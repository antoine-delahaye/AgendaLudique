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


@site.route('/catalog')
@login_required
def catalog():
    """
    Render the library template on the /library route
    """
    return render_template('catalog.html', stylesheet='catalog')
