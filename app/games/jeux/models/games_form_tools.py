from app.models import Game


def populate_games_form(form):
    """
    populate form data from database
    :param form: a AddGamesSearchForm
    """
    games = Game.all
    if hasattr(games, '__iter__'):
        for data in games:
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
    :param form: a AddGamesSearchForm
    """
    form.years.choices.sort()
    form.min_players.choices.sort()
    form.max_players.choices.sort()
    form.min_playtime.choices.sort()
    form.max_playtime.choices.sort()


def add_default_values_game_form(form):
    """
    add the "Aucun.e" value to the beginning of every choices
    :param form: a AddGamesSearchForm
    """
    form.title.choices.insert(0, 'Aucun')
    form.years.choices.insert(0, 'Aucune')
    form.min_players.choices.insert(0, 'Aucun')
    form.max_players.choices.insert(0, 'Aucun')
    form.min_playtime.choices.insert(0, 'Aucune')
    form.max_playtime.choices.insert(0, 'Aucune')
