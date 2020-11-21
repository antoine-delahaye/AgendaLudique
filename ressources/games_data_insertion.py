import yaml
import mariadb
import sys

try:
    conn = mariadb.connect(
        user='al_admin',
        password='al_admin',
        host='localhost',
        port=3306,
        database='agendaludique'

    )
except mariadb.Error as e:
    print(f'Error connecting to MariaDB Platform: {e}')
    sys.exit(1)

cur = conn.cursor()

cur.execute("SELECT MAX(id) FROM games")
print(cur)

games_data = yaml.load(open('games-data.yaml'), Loader=yaml.FullLoader)
game_id = 0
for max_game_id in cur:
    if max_game_id[0] is not None:
        game_id = int(max_game_id)

for data in games_data.values():
    game_id = game_id + 1
    try:
        cur.execute("INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?)", (game_id,
                                                                       data['title'],
                                                                       int(data['publication_year']),
                                                                       int(data['min_players']),
                                                                       int(data['max_players']),
                                                                       int(data['min_playtime']),
                                                                       data['images']['original']))
    except mariadb.Error as e:
        print(f'Error: {e}')
    conn.commit()
