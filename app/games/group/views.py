# Group related ##################################################################
from flask import render_template, redirect, request
from flask_login import login_required, current_user

from . import group as gp
from app.models import Group, Participate
from ... import db


@gp.route('/groups')
@login_required
def groups():
    """
    Render the groups template on the /groups route
    """
    groups_data = Group.query.all()
    return render_template('groups.html', stylesheet='groups', groups_data=groups_data)


@gp.route('/groups_public')
@login_required
def groups_public():
    """
    Render the groups template on the /groups_public route
    """
    groups_data = Group.query.filter(Group.is_private == False).all()
    return render_template('groups.html', stylesheet='groups', groups_data=groups_data)


@gp.route('/group')
@gp.route('/group/<int:id>', methods=['GET', 'POST'])
@login_required
def group(id=None):
    """
    Render the groups template on the /group route
    """
    group = Group.query.get_or_404(id)
    is_member = (Participate.from_both_ids(current_user.id, id) is not None)
    return render_template('group.html',
        stylesheet='group',
        group=group,
        is_member=is_member,
        is_resp=(current_user.id==group.manager_id))


@gp.route('/my_groups')
@login_required
def my_groups():
    """
    Render the groups template on the /my_groups route
    """
    groups_data = []
    for participation in current_user.participations:
        if participation.group.manager_id != current_user.id:
            groups_data.append(participation.group)
    return render_template('my_groups.html', stylesheet='groups', groups_data=groups_data,
                           managed_groups=list(current_user.managed_groups))


@gp.route('/join_group/<group_id>', methods=['GET', 'POST'])
@login_required
def join_group(group_id):
    db.session.add(Participate(group_id=group_id, member_id=current_user.id))
    db.session.commit()
    return redirect(request.referrer)


@gp.route('/quit_group/<group_id>', methods=['GET', 'POST'])
@login_required
def quit_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(Participate.from_both_ids(current_user.id, group_id))

    participations = group.participations.all()
    if participations == 0: # if the group in now empty
        db.session.delete(group)
    elif current_user.id == group.manager_id: # if the group doesnt have a manager anymore
        group.manager_id = participations[0].member_id # nominate a new manager

    db.session.commit()
    return redirect(request.referrer)
