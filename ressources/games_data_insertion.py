import yaml
import mariadb
import sys

password = input('Password : ')

try:
    conn = mariadb.connect(
        user="root",
        password=password,
        host="localhost",
        port=3306,
        database="agendaludique"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

cur.execute("SELECT MAX(game_id) FROM games")
print(cur)

games_data = yaml.load(open('games-data.yaml'), Loader=yaml.FullLoader)
game_id = 0
for max_game_id in cur:
    if type(max_game_id) is tuple:
        game_id = max_game_id

for data in games_data.values():
    game_id = game_id + 1
    try:
        cur.execute("INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?)", (game_id,
                                                                       data['title'],
                                                                       data['years'],
                                                                       data['min_players'],
                                                                       data['max_players'],
                                                                       data['min_playtime'],
                                                                       data['images']['original']))
    except mariadb.Error as e:
        print(f"Error: {e}")
    conn.commit()
