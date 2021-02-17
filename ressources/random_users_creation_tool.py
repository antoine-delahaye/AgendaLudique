# Random Users Creation Tool
# A tool created to help the Agenda Ludique contributors to test the users-related functionalities.
# It allows the creation of a large amount of users on the website in a few second, right from the terminal.

import random
import mariadb
import sys
from werkzeug.security import generate_password_hash


def read_names(file, amount):
    """
    Reads the names from a file, and returns a randomly generated list which contains them.
    :param file: A text file
    :param amount: The size of the list to return
    :return: A randomly generated list that contains users' first names
    """
    if amount > 200:
        print('The amount of users to be generated should be <= 200.')
        sys.exit(1)

    try:
        f = open(file, "r")
        content = f.read()
    except OSError as e:
        print(f'Error: {e}')
        sys.exit(1)

    names = content.split(';')

    res = []

    for i in range(amount):
        random_int = random.randint(0, len(names) - 1)
        res.append(names[random_int])

    return res


def send_users(names, base_password):
    """
    Creates user accounts on the database.
    :param names: A list of names
    :param base_password: The base password for all the accounts
    """
    try:
        connection = mariadb.connect(
            user='al_admin',
            password='al_admin',
            host='agenda-ludique.ddns.net',
            port=3306,
            database='agendaludique'
        )
    except mariadb.Error as e:
        print(f'Error connecting to MariaDB Platform: {e}')
        sys.exit(1)
    cursor = connection.cursor()

    i = 1

    for first_name in names:
        username = first_name + str(i)
        email = username + "@example.com"
        last_name = first_name
        password = generate_password_hash(base_password + first_name)

        try:
            cursor.execute(
                "INSERT INTO users (email, username, first_name, last_name, password_hash) VALUES (?, ?, ?, ?, ?)",
                (email, username, first_name, last_name, password))
        except mariadb.Error as e:
            print(f'Error: {e}')

        i += 1

    connection.commit()
    connection.close()


print('Welcome to Agenda Ludique Random Users Creation Tool. For development and debug purposes only.')

file = input('Please enter the name of the file which contains the first names:')
amount = int(input('Please enter the amount of users to be created:'))
base_password = input('Please enter a base password for the created users:')
names = read_names(file, amount)
print(names)
send_users(names, base_password)
