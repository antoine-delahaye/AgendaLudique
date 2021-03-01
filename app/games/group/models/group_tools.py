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


def check_private_group(group):
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
    if check_private_group(group):
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
        return False
    elif group.is_private:
        flash('Vous ne pouvez pas rejoindre un groupe privé sans un code.', 'danger')
        return False
    db.session.add(Participate(group_id=group_id, member_id=current_user.id))
    db.session.commit()
    return True


def quit_group_form(group_id):
    """
    Kick the current_user from a group.
    Chose an other manager if they were the manager.
    Delete the group is now empty.
    """
    group = Group.from_id(group_id)
    res = True
    if group is None:
        abort(404)
        return False

    participation = Participate.from_both_ids(current_user.id, group_id)
    if participation is None:
        flash("Vous ne pouvez pas quitter un groupe dont vous n'êtes pas membre.",'warning')
        return False
    else:
        db.session.delete(participation)

    participations = group.participations.all()

    if len(participations) == 0:  # if the group in now empty
        db.session.delete(group)
        res = False
        flash("Le groupe a été supprimé","warning")
    elif current_user.id == group.manager_id:  # if the group doesnt have a manager anymore
        group.manager_id = participations[0].member_id  # nominate a new manager

    db.session.commit()
    return res


def kick_group_form(group_id, member_id):
    """
    Kick a user from a group
    """
    group = Group.from_id(group_id)
    if group is None:
        abort(404)

    if current_user.id == group.manager_id:
        participation = Participate.from_both_ids(member_id, group_id)
        if participation is None:
            flash("Vous ne pouvez pas kick quelqu'un qui n'est pas dans ce groupe","warning")
        else:
            db.session.delete(participation)
    else:
        flash("Vous ne pouvez pas kick quelqu'un d'un groupe dont vous n'êtes pas le chef","warning")

    db.session.commit()


def add_group_form(form):
    """
    Create a new Group table
    :param form:
    :return: if the group can be added, return the id of the group, else return False
    """
    name = form.name.data
    if Group.from_name(name) is not None:
        flash("Ce groupe existe déjà","danger")
        return False

    is_private = (form.is_private.data == 'private')

    password = form.password.data
    if password is "" and is_private==True:
        flash("Vous devez mettre un mot de passe pour un groupe privé","danger")
        return False

    db.session.add(Group(
        name=name,
        is_private=is_private,
        password=password,
        manager_id=current_user.id))
    group_id = Group.from_name(name).id
    db.session.add(Participate(group_id=group_id, member_id=current_user.id))
    db.session.commit()
    return group_id
