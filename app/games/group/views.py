# Group related ##################################################################
from flask import render_template
from flask_login import login_required, current_user

from . import group as gp
from app.models import Group


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
    return render_template('group.html', stylesheet='group', group=group)


@gp.route('/my_groups')
@login_required
def my_groups():
    """
    Render the groups template on the /my_groups route
    """
    groups_data = []
    for participation in current_user.participations:
        groups_data.append(participation.group)
    return render_template('my_groups.html', stylesheet='groups', groups_data=groups_data,
                           managed_groups=list(current_user.managed_groups))
