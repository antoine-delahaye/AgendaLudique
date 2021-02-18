# Group related ##################################################################
from flask import render_template, redirect, request, abort, flash, url_for
from flask_login import login_required, current_user

from . import group as gp
from app.models import Group, Participate, User
from .models.group_tools import get_all_participation
from .models.forms import JoinPrivateGroupForm
from app import db


@gp.route('/groups')
@login_required
def groups():
    """
    Render the groups template on the /groups route
    """
    groups_data = Group.query.all()
    return render_template('groups.html', stylesheet='groups', groups_data=groups_data)


@gp.route('/groups_public', methods=['GET', 'POST'])
@login_required
def groups_public():
    """
    Render the groups template on the /groups_public route
    """
    form = JoinPrivateGroupForm()
    if request.method == "POST":
        code=form.code.data
        group = Group.from_code(code)
        if group is None:
            flash('Ce code ne correspond à aucun groupe.', 'danger')
        elif Participate.from_both_ids(current_user.id, group.id) is not None:
            flash('Vous êtes déjà dans ce groupe', 'warning')
        else:
            db.session.add(Participate(group_id=group.id, member_id=current_user.id))
            db.session.commit()
            return redirect(url_for("group.group",id=group.id))

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
    is_member = (Participate.from_both_ids(current_user.id, id) is not None)
    users_data = User.search_with_pagination(current_user, "", False, False, per_page=16)
    return render_template('group.html',
                           stylesheet_list=['group', 'groups', 'users'],
                           group=group,
                           is_member=is_member,
                           is_resp=(current_user.id == group.manager_id),
                           users_data=users_data,
                           current_user_id=current_user.id)


@gp.route('/my_groups')
@login_required
def my_groups():
    """
    Render the groups template on the /my_groups route
    """
    groups_data = get_all_participation(current_user)
    return render_template('my_groups.html', stylesheet='groups', groups_data=groups_data,
                           managed_groups=list(current_user.managed_groups))


@gp.route('/join_public_group/<group_id>', methods=['GET', 'POST'])
@login_required
def join_public_group(group_id=None):
    if id is not None: # public group by id
        group = Group.from_id(group_id)
        if group is None:
            abort(404)
        elif group.is_private:
            flash('Vous ne pouvez pas rejoindre un groupe privé sans un code.', 'danger')
            return redirect(url_for('group.groups'))
        else:
            db.session.add(Participate(group_id=group_id, member_id=current_user.id))
            db.session.commit()
    else:
        abort(412)

    return redirect(request.referrer)


@gp.route('/quit_group/<group_id>', methods=['GET', 'POST'])
@login_required
def quit_group(group_id):
    group = Group.from_id(group_id)
    if group is None:
        abort(412)
    db.session.delete(Participate.from_both_ids(current_user.id, group_id))

    participations = group.participations.all()

    if participations == 0:  # if the group in now empty
        db.session.delete(group)
    elif current_user.id == group.manager_id:  # if the group doesnt have a manager anymore
        group.manager_id = participations[0].member_id  # nominate a new manager

    db.session.commit()
    return redirect(request.referrer)
