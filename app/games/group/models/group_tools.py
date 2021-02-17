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
