from app.models import Game, Group, Participate
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


def join_private_group_form(form):
    """
    create a new Participate relationship
    :param form:
    """
    code = form.code.data
    group = Group.from_code(code)
    if group is None:
        flash('Ce code ne correspond à aucun groupe.', 'danger')
    elif Participate.from_both_ids(current_user.id, group.id) is not None:
        flash('Vous êtes déjà dans le groupe ' + group.name, 'warning')
    else:
        db.session.add(Participate(group_id=group.id, member_id=current_user.id))
        db.session.commit()
        return redirect(url_for("group.group",id=group.id))


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
        return redirect(url_for("group.group",id=group.id))


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


def populate_games_form(form):
    """
    populate form data from database
    :param form: a GamesSearchForm
    """
    for data in Game.all():
        form.title.choices.append(data.title)
        if data.publication_year not in form.years.choices:
            form.years.choices.append(data.publication_year)
        if data.min_players not in form.min_players.choices:
            form.min_players.choices.append(data.min_players)
        if data.max_players not in form.max_players.choices:
            form.max_players.choices.append(data.max_players)
        if data.min_playtime not in form.min_playtime.choices and data.min_playtime not in form.max_playtime.choices:
            form.min_playtime.choices.append(data.min_playtime)
            form.max_playtime.choices.append(data.min_playtime)


def beautify_games_form(form):
    """
    sort every data of the form
    :param form: a GamesSearchForm
    """
    form.years.choices.sort()
    form.min_players.choices.sort()
    form.max_players.choices.sort()
    form.min_playtime.choices.sort()
    form.max_playtime.choices.sort()


def add_default_values_game_form(form):
    """
    add the "Aucun.e" value to the beginning of every choices
    :param form: a GamesSearchForm
    """
    form.title.choices.insert(0, 'Aucun')
    form.years.choices.insert(0, 'Aucune')
    form.min_players.choices.insert(0, 'Aucun')
    form.max_players.choices.insert(0, 'Aucun')
    form.min_playtime.choices.insert(0, 'Aucune')
    form.max_playtime.choices.insert(0, 'Aucune')
