# app/site/views.py

import flask_login
from flask import render_template, redirect, url_for, request, make_response
from flask_login import login_required, current_user

from app import db
from app.models import User, Game, Group, HideUser, BookmarkUser, Collect, Wish, HideGame
from app.site import site
from app.site.forms import UpdateInformationForm, GamesSimpleSearchForm, GamesSearchForm, UsersSearchForm, AddGameForm


@site.route('/')
def home():
    """
    Render the homepage template on the / route
    """
    return render_template('home.html', stylesheet='home')



# Account/Profil related #########################################################
@site.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    """
    Render the users template on the /users route
    """
    form = UsersSearchForm()
    page = request.args.get('page', 1, type=int)

    # Get search parameters if there are None, set to None
    favOnly = form.display_favorites_players_only.data if form.display_favorites_players_only.data else request.args.get('favOnly', None, type=bool)
    hidden = form.display_masked_players.data if form.display_masked_players.data else request.args.get('hidden', None, type=bool)

    # Fill search bar with parameters when changing page
    if not form.username_hint.data:
        form.username_hint.data = request.args.get('username', '', type=str)

    # Check the box if the parameters are True
    form.display_favorites_players_only.data = favOnly
    form.display_masked_players.data = hidden

    search_results = User.search_with_pagination(current_user, form.username_hint.data, favOnly, hidden, page, 20)

    return render_template('users.html', stylesheet='users', form=form, current_user_id=current_user.id, users_data=search_results, favOnly=favOnly, hidden=hidden, username_hint=form.username_hint.data)


@site.route('/user')
@site.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def user(id=None):
    """
    Render the user template on the /user route
    """
    user = User.query.get_or_404(id)
    data = User.search(current_user, user.username, False, True)    # Retrieve the data from the database, including the hidden users.
    return render_template('user.html', stylesheet='user', user=user, current_user_id=current_user.id, users_data=data)


@site.route('/hidden-users/add', methods=['GET'])
@login_required
def add_hidden_user(user_id=None):
    """
    Add the declared user (property "user" in the query string) to the hidden users
    on the /hidden-users/add route.
    """
    connected_user = current_user
    user_id = request.args.get('user')

    if user_id is not None:
        user_to_hide = User.query.get(user_id)
        if user_to_hide is not None:
            if HideUser.query.filter_by(user_id=connected_user.id, user2_id=user_to_hide.id).count() == 0:
                hidden_user = HideUser(user_id=connected_user.id, user2_id=user_to_hide.id)
                db.session.add(hidden_user)
                db.session.commit()

    return redirect(url_for('site.users'))


@site.route('/hidden-users/remove', methods=['GET'])
@login_required
def remove_hidden_user(user_id=None):
    """
    Remove the declared user (property "user" in the query string) from the hidden users
    on the /hidden-users/remove route.
    """
    connected_user = current_user
    user_id = request.args.get('user')

    if user_id is not None:
        user_to_remove = User.query.get(user_id)
        if user_to_remove is not None:
            hidden_user = HideUser.query.get({"user_id": connected_user.id, "user2_id": user_to_remove.id})
            if hidden_user is not None:
                db.session.delete(hidden_user)
                db.session.commit()

    return redirect(url_for('site.users', searchParameters="HIDDEN"))


@site.route('/bookmarked-users/add', methods=['GET'])
@login_required
def add_bookmarked_user(user_id=None):
    """
    Add the declared user (property "user" in the query string) to the bookmarked users
    on the /bookmarked-users/add route.
    """
    connected_user = current_user
    user_id = request.args.get('user')

    if user_id is not None:
        user_to_bookmark = User.query.get(user_id)
        if user_to_bookmark is not None:
            if BookmarkUser.query.filter_by(user_id=connected_user.id, user2_id=user_to_bookmark.id).count() == 0:
                bookmarked_user = BookmarkUser(user_id=connected_user.id, user2_id=user_to_bookmark.id)
                db.session.add(bookmarked_user)
                db.session.commit()

    return redirect(url_for('site.users'))


@site.route('/bookmarked-users/remove', methods=['GET'])
@login_required
def remove_bookmarked_user(user_id=None):
    """
    Remove the declared user (property "user" in the query string) from the bookmarked users
    on the /bookmarked-users/remove route.
    """
    connected_user = current_user
    user_id = request.args.get('user')

    if user_id is not None:
        user_to_remove = User.query.get(user_id)
        if user_to_remove is not None:
            bookmarked_user = BookmarkUser.query.get({"user_id": connected_user.id, "user2_id": user_to_remove.id})
            if bookmarked_user is not None:
                db.session.delete(bookmarked_user)
                db.session.commit()

    return redirect(url_for('site.users'))


@site.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    Render the account template on the /account route
    """
    form = UpdateInformationForm()

    user = current_user

    if user.use_gravatar:
        form.profile_picture.render_kw = {'disabled': ''}

    if form.validate_on_submit():
        if user is not None:
            user.username = form.username.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.password = form.password.data
            user.use_gravatar = form.use_gravatar.data
            user.profile_picture = user.get_profile_picture()
            db.session.commit()
        return redirect(url_for('site.account'))
    return render_template('account.html', stylesheet='account', form=form)


@site.route('/parameters')
@login_required
def parameters():
    """
    Render the parameters template on the /parameters route
    """
    return render_template('parameters.html')


@site.route('/set_parameters', methods=['POST'])
@login_required
def set_parameters():
    color_theme = "On" if request.form.get('color-theme') is not None else "Off"
    param = make_response(redirect(url_for('site.parameters')))
    param.set_cookie('color-theme', color_theme)
    return param


