import yaml

games_data = yaml.load(open('games-data.yaml'), Loader=yaml.FullLoader)


def publication_years():
    years = set()
    for item in games_data.values():
        years.add(int(item['publication_year']))
    return years


def players_numbers():
    players = set()
    for item in games_data.values():
        players.add(int(item['min_players']))
        players.add(int(item['max_players']))
    return players


def max_playtime():
    playtime = set()
    for item in games_data.values():
        playtime.add(int(item['min_playtime']))
    return max(playtime)
