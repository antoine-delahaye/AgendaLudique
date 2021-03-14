# app/site/views.py

from flask import render_template, redirect, url_for, request, make_response, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User, HideUser, BookmarkUser, Game, ResultsSortType
from app.site import site
from app.site.models.forms import UpdateInformationForm, UsersSearchForm
from app.site.models.site_tools import update_user_with_form


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
    fav_only = form.display_favorites_players_only.data if form.display_favorites_players_only.data else request.args.get(
        'favOnly', None, type=bool)
    hidden = form.display_masked_players.data if form.display_masked_players.data else request.args.get('hidden', None,
                                                                                                        type=bool)

    # Get the sort order. If not defined, the users will be sorted alphabetically.
    sort_order = form.sort_order.data if form.sort_order.data else request.args.get(
        'sortOrder', ResultsSortType.ALPHABETICAL, type=str)

    # Fill search bar with parameters when changing page
    if not form.username_hint.data:
        form.username_hint.data = request.args.get('username', '', type=str)

    # Check the box if the parameters are True
    form.display_favorites_players_only.data = fav_only
    form.display_masked_players.data = hidden

    search_results = current_user.users_search_with_pagination(form.username_hint.data, fav_only, hidden, page, 20,
                                                 sort_type=sort_order)

    return render_template('users.html', stylesheet='users', form=form, current_user_id=current_user.id,
                           users_data=search_results, favOnly=fav_only, hidden=hidden,
                           username_hint=form.username_hint.data, sort_order=sort_order)


@site.route('/user')
@site.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def user(id=None):
    """
    Render the user template on the /user route
    """
    user = User.query.get_or_404(id)

    # Bookmarked users
    bookmarked_users = user.get_bookmarked_users()
    current_user_data = current_user.users_search("", False, True)  # Retrieve the data for the current user

    # Games collection
    user_games_collection = user.get_owned_games()
    # Will work later when the search engine will be updated
    current_user_wished_games = current_user.games_search("", "title", "wished").items

    return render_template('user.html', stylesheet='user', user=user, current_user_id=current_user.id,
                           users_data=current_user_data, bookmarked_users=bookmarked_users,
                           games_collection=user_games_collection, wished_games=current_user_wished_games)


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
        form.profile_picture.render_kw.update({'disabled': ''})  # better than redefining it ;)

    if request.method == 'POST':
        if user is not None:
            try:
                update_user_with_form(form, user)
                flash("Votre profil a bien été mis à jour.", "success")
            except IntegrityError:
                flash("Ce nom d'utilisateur est déjà pris.", "danger")
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
