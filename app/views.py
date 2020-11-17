from flask import request, redirect, url_for, render_template
from .app import app
from .models import data


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('home.html', stylesheet='home')


@app.route('/auth-method', methods=['GET', 'POST'])
def auth_method():
    if request.method == 'POST':
        if request.form['auth-button'] == "sign-in":
            return redirect(url_for('sign_in'))
        elif request.form['auth-button'] == 'sign-up':
            return redirect(url_for('sign_up'))


@app.route('/sign-in')
def sign_in():
    return render_template('sign-in.html', stylesheet='sign-in')


@app.route('/sign-up')
def sign_up():
    return render_template('sign-up.html', stylesheet='sign-up')


@app.route('/library')
def games():
    return render_template('library.html', stylesheet='library', data=data)
