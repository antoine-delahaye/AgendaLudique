from app.models import Group, Participate
from flask_login import current_user
from flask import redirect, flash, url_for, request, abort
from app import db
from .. import group as gp


def get_all_participation(user):
    """
    return all groups in which the users participate ( except ones which are leaded by him)
    :param user:
    :return:
    """
    groups_data = []
    for participation in user.participations:
        if participation.group.manager_id != user.id:
            groups_data.append(participation.group)
    return groups_data


def check_group(group):
    if group is None:
        flash('Ce code ne correspond à aucun groupe.', 'danger')
        return False
    elif Participate.from_both_ids(current_user.id, group.id) is not None:
        flash('Vous êtes déjà dans le groupe ' + group.name, 'warning')
        return False
    return True


def join_private_group_form(form):
    """
    create a new Participate relationship
    :param form:
    """
    code = form.code.data
    group = Group.from_code(code)
    if check_group(group):
        db.session.add(Participate(group_id=group.id, member_id=current_user.id))
        db.session.commit()
        return False
    return True


def join_public_group_form(group_id):
    """
    create a new Participate relationship
    """
    group = Group.from_id(group_id)
    if group is None:
        abort(404)
    elif group.is_private:
        flash('Vous ne pouvez pas rejoindre un groupe privé sans un code.', 'danger')
        return redirect(url_for('group.groups'))
    else:
        db.session.add(Participate(group_id=group_id, member_id=current_user.id))
        db.session.commit()
        return redirect(url_for("group.group", id=group.id))


def quit_group_form(group_id):
    group = Group.from_id(group_id)
    if group is None:
        abort(404)
    db.session.delete(Participate.from_both_ids(current_user.id, group_id))

    participations = group.participations.all()

    if participations == 0:  # if the group in now empty
        db.session.delete(group)
    elif current_user.id == group.manager_id:  # if the group doesnt have a manager anymore
        group.manager_id = participations[0].member_id  # nominate a new manager

    db.session.commit()
    return redirect(request.referrer)
