# Group related ##################################################################
from flask import render_template, request, abort
from flask_login import login_required, current_user

from . import group as gp
from app.models import Group, Participate, User
from .models.group_tools import get_all_participation, join_private_group_form, join_public_group_form, quit_group_form
from .models.forms import JoinPrivateGroupForm
from app import db


@gp.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    """
    Render the groups template on the /groups route
    """
    form = JoinPrivateGroupForm()
    if request.method == "POST":
        return join_private_group_form(form)

    groups_data = Group.query.all()
    return render_template('groups.html', stylesheet='groups', groups_data=groups_data, form=form)


@gp.route('/groups_public', methods=['GET', 'POST'])
@login_required
def groups_public():
    """
    Render the groups template on the /groups_public route
    """
    form = JoinPrivateGroupForm()
    if request.method == "POST":
        return join_private_group_form(form)

    groups_data = Group.query.filter(Group.is_private == False).all()
    return render_template('groups.html', stylesheet='groups', groups_data=groups_data, form=form)


@gp.route('/group')
@gp.route('/group/<int:id>', methods=['GET', 'POST'])
@login_required
def group(id=None):
    """
    Render the groups template on the /group route
    """
    group = Group.query.get_or_404(id)
    if group.is_private:
        form = JoinPrivateGroupForm()
        if request.method == "POST":
            return join_private_group_form(form)
    else:
        form=None

    is_member = (Participate.from_both_ids(current_user.id, id) is not None)
    users_data = User.search_with_pagination(current_user, "", False, False, per_page=15)
    return render_template('group.html',
                           stylesheet_list=['group', 'groups', 'users'],
                           group=group,
                           is_member=is_member,
                           is_resp=(current_user.id == group.manager_id),
                           users_data=users_data,
                           current_user_id=current_user.id,
                           form=form)


@gp.route('/my_groups', methods=['GET', 'POST'])
@login_required
def my_groups():
    """
    Render the groups template on the /my_groups route
    """
    form = JoinPrivateGroupForm()
    if request.method == "POST":
        return join_private_group_form(form)
    return render_template('my_groups.html',
                           stylesheet='groups',
                           groups_data=get_all_participation(current_user),
                           managed_groups=list(current_user.managed_groups),
                           form=form)


@gp.route('/join_public_group/<group_id>', methods=['GET', 'POST'])
@login_required
def join_public_group(group_id=None):
    if id is None:
        abort(412)
    return join_public_group_form(group_id)


@gp.route('/quit_group/<group_id>', methods=['GET', 'POST'])
@login_required
def quit_group(group_id):
    return quit_group_form(group_id)
