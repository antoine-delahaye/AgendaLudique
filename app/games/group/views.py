# Group related ##################################################################
from flask import render_template, request, abort, redirect, url_for
from flask_login import login_required, current_user

from . import group as gp
from app.models import Group, Participate, User
from .models.group_tools import get_all_participation, join_private_group_form, join_public_group_form, quit_group_form, add_group_form, kick_group_form, lead_group_form, get_group_payload
from .models.forms import JoinPrivateGroupForm, AddGroupForm
from app.site.models.forms import GroupsSearchForm
from app import db


def handle_join_private(form):
    if join_private_group_form(form):
        return redirect(request.referrer)
    return redirect(url_for("group.group", id=group.id))


@gp.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    """
    Render the groups template on the /groups route
    """
    searchform = GroupsSearchForm()
    form = JoinPrivateGroupForm()
    if request.method == "POST":
        if join_private_group_form(form):
            return handle_join_private(form)
    payload = get_group_payload(searchform)

    return render_template('groups.html', stylesheet='groups', form=form, **payload)


@gp.route('/groups_public', methods=['GET', 'POST'])
@login_required
def groups_public():
    """
    Render the groups template on the /groups_public route
    """
    searchform = GroupsSearchForm()
    form = JoinPrivateGroupForm()
    if request.method == "POST":
        if join_private_group_form(form):
            return handle_join_private(form)
    payload = get_group_payload(searchform, Group.query.filter(Group.is_private == False))
    return render_template('groups.html', stylesheet='groups', form=form, **payload)


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
            if join_private_group_form(form):
                return handle_join_private(form)
    else:
        form = None

    is_member = (Participate.from_both_ids(current_user.id, id) is not None)
    users_data = current_user.users_search_with_pagination("", False, False, per_page=15)
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
    form.validate_on_submit()
    if request.method == "POST":
        if join_private_group_form(form):
            return handle_join_private(form)
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
    elif join_public_group_form(group_id):
        return redirect(url_for("group.group", id=group_id))
    return redirect(url_for('group.groups'))


@gp.route('/quit_group/<group_id>', methods=['GET', 'POST'])
@login_required
def quit_group(group_id):
    if quit_group_form(group_id):
        return redirect(request.referrer)
    return redirect(url_for('group.groups'))


@gp.route('/kick_group/<group_id>-<member_id>')
@login_required
def kick_group(group_id, member_id):
    kick_group_form(group_id, member_id)
    return redirect(request.referrer)


@gp.route('/lead_group/<group_id>-<member_id>')
@login_required
def lead_group(group_id, member_id):
    lead_group_form(group_id, member_id)
    return redirect(request.referrer)


@gp.route('/add_group', methods=['GET', 'POST'])
@login_required
def add_group():
    form = AddGroupForm()
    if request.method == 'POST':
        group_id = add_group_form(form)
        if group_id:
            return redirect(url_for('group.group', id=group_id))
        return redirect(request.referrer)

    return render_template('add_group.html', form=form)
