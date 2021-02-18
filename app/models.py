# app/utils.py
import hashlib

from flask_login import UserMixin
from flask_sqlalchemy import Pagination
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, time, datetime
from app import db, login_manager


class User(UserMixin, db.Model):
    """
    Create an User table
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(32), index=True, unique=True)
    first_name = db.Column(db.String(32), index=True)
    last_name = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    profile_picture = db.Column(db.String(512))
    use_gravatar = db.Column(db.Boolean, default=False)
    token_pwd = db.Column(db.String(32), unique=True)

    statistics = db.relationship(
        "Statistic",
        back_populates="user",
        uselist=False)

    @property
    def password(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def get_profile_picture(self):
        """
        Get the user's profile picture URL.
        :return: The user's profile picture URL.
        """
        if self.use_gravatar:
            return self.get_gravatar()
        elif self.profile_picture != "" and self.profile_picture is not None:
            return self.profile_picture
        return "/static/images/blank_pp.png"

    def set_profile_picture(self, new_picture_url, use_gravatar=False):
        """
        Set the user's profile picture URL, or Gravatar's one if enabled.
        :param new_picture_url: A picture URL.
        :param use_gravatar: If the user wants to use his Gravatar profile picture.
        """
        if use_gravatar:
            self.profile_picture = self.get_gravatar()
        else:
            if new_picture_url is None or new_picture_url == "None":
                self.profile_picture = None
            else:
                self.profile_picture = new_picture_url

    def get_gravatar(self):
        """
        Get the user's profile picture from Gravatar.
        :return: The URL of the user's profile picture on Gravatar.
        """
        return "https://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def __repr__(self):
        return f'<User: {self.username}>'

    @classmethod
    def is_registered(cls, email):
        """
        Check if an email is already used.
        """
        return True if User.query.filter(User.email == email).first() else False

    @classmethod
    def get_known_games(cls, user_id, only_id=False):
        if only_id:
            return [data[0] for data in
                    db.session.query(Game.id).join(KnowRules).filter(KnowRules.user_id == user_id,
                                                                     Game.id == KnowRules.game_id)]
        return db.session.query(Game).join(KnowRules).filter(KnowRules.user_id == user_id, Game.id == KnowRules.game_id)

    @classmethod
    def get_noted_games(cls, user_id, only_id=False):
        if only_id:
            return [data[0] for data in
                    db.session.query(Game.id).join(Note).filter(Note.user_id == user_id, Game.id == Note.game_id)]
        return db.session.query(Game).join(Note).filter(Note.user_id == user_id, Game.id == Note.game_id)

    @classmethod
    def get_owned_games(cls, user_id, only_id=False):
        if only_id:
            return [data[0] for data in
                    db.session.query(Game.id).join(Collect).filter(Collect.user_id == user_id,
                                                                   Game.id == Collect.game_id)]
        return db.session.query(Game).join(Collect).filter(Collect.user_id == user_id, Game.id == Collect.game_id)

    @classmethod
    def get_wished_games(cls, user_id, only_id=False):
        if only_id:
            return [data[0] for data in
                    db.session.query(Game.id).join(Wish).filter(Wish.user_id == user_id, Game.id == Wish.game_id)]
        return db.session.query(Game).join(Wish).filter(Wish.user_id == user_id, Game.id == Wish.game_id)

    @classmethod
    def from_username(cls, username):
        """
        Get an user from its username. Return None if the user does not exist.
        """
        req = User.query.filter(User.username == username).first()
        return req if req else None

    @classmethod
    def from_email(cls, email):
        """
        Get an user from its email. Return None if the user does not exist.
        """
        req = User.query.filter(User.email == email).first()
        return req if req else None

    @classmethod
    def from_token(cls, token):
        """
        Get an user from its email. Return None if the user does not exist.
        """
        req = User.query.filter(User.token_pwd == token).first()
        return req if req else None

    @classmethod
    def search(cls, current_user, username_hint, favOnly, hidden):
        """
        Search users with defined parameters
        :param current_user The user who made the research
        :param username_hint: A hint gave by the user to search similar usernames
        :param favOnly: containing "True" to show only bookmarked users else None
        :param favOnly: containing "True" to show hidden users else None
        :return: A SearchResults object with an items list.
        """
        results = SearchResults()  # Will contain the search results

        # Contain bookmarked users
        bookmarked_users_db = db.session.query(BookmarkUser.user2_id).filter(
            BookmarkUser.user_id == current_user.id)  # ids only -> lighter
        # Contain hidden users
        hidden_users_db = db.session.query(HideUser.user2_id).filter(
            HideUser.user_id == current_user.id)  # ids only -> lighter

        if favOnly:
            users_db = User.query.filter(User.id.in_(bookmarked_users_db),
                                         User.username.like("%" + username_hint + "%"))
        else:
            users_db = User.query.filter(User.username.like('%' + username_hint + '%'))

        # Allows to fill stars icon to yellow
        for bookmarded_user in bookmarked_users_db:
            results.bookmarked_ids.add(bookmarded_user.user2_id)

        if not hidden:
            users_db = users_db.filter(User.id.notin_(hidden_users_db))

        # Allows to fill hidden icon to red
        for hidden_user in hidden_users_db:
            results.hidden_ids.add(hidden_user.user2_id)

        results.items = users_db

        return results

    @classmethod
    def search_with_pagination(cls, current_user, username_hint, favOnly, hidden, current_page=1, per_page=20):
        """
        Search users with defined parameters and return them as a UsersSearchResults object which contains a
        Pagination object.
        :param current_user The user who made the research
        :param username_hint: A hint gave by the user to search similar usernames
        :param parameters: include into the list "HIDDEN" to return the hidden users as well as the others users,
        and/or "ONLY_BOOKMARKED" to return only the bookmarked users.
        :param current_page: The current page number
        :param per_page: The number of users shown on a search results page
        :return: A UsersSearchResults with a Pagination object.
        """
        results = User.search(current_user, username_hint, favOnly, hidden)
        page_elements = results.items.slice((current_page - 1) * per_page,
                                            current_page * per_page)  # the users that will be displayed on the page
        results.pagination = Pagination(None, current_page, per_page, results.items.count(), page_elements)
        results.items = None

        return results

    # Set up user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


class BookmarkUser(db.Model):
    """
    Create a relationship between an User and itself
    """

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)

    user = db.relationship(
        "User",
        backref=db.backref("bookmarked_users", lazy="dynamic"),
        foreign_keys=[user_id])

    user2 = db.relationship(
        "User",
        backref=db.backref("bookmarked_by_users", lazy="dynamic"),
        foreign_keys=[user2_id])

    def __repr__(self):
        return f"BookmarkUser: ({self.user.username}, {self.user2.username})"

    @classmethod
    def from_both_ids(cls, user_id, user2_id):
        """
        Get a BookmarkUser relationship from its game and user ids.
        Return None if the relationship does not exist.
        """
        req = BookmarkUser.query.filter(BookmarkUser.user_id == user_id, BookmarkUser.user2_id == user2_id).first()
        return req if req else None


class HideUser(db.Model):
    """
    Create a relationship between an User and itself
    """

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user2_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)

    user = db.relationship(
        "User",
        backref=db.backref("hidden_users", lazy="dynamic"),
        foreign_keys=[user_id])

    user2 = db.relationship(
        "User",
        backref=db.backref("hidden_by_users", lazy="dynamic"),
        foreign_keys=[user2_id])

    def __repr__(self):
        return f"HideUser: ({self.user.username}, {self.user2.username})"

    @classmethod
    def from_both_ids(cls, user_id, user2_id):
        """
        Get a HideUser relationship from its game and user ids.
        Return None if the relationship does not exist.
        """
        req = HideUser.query.filter(HideUser.user_id == user_id, HideUser.user2_id == user2_id).first()
        return req if req else None


class Statistic(db.Model):
    """
    Create a Statistic table
    """

    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    avg_complexity = db.Column(db.Integer, default=0)
    avg_playtime = db.Column(db.Integer, default=0)
    avg_nb_players = db.Column(db.Integer, default=0)
    frequency = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship(
        "User",
        back_populates="statistics")


class Wish(db.Model):
    """
    Create a relationship between an User and a Game
    """

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("wishes", lazy="dynamic"),
        foreign_keys=[user_id])

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    game = db.relationship(
        "Game",
        backref=db.backref("wished_by_users", lazy="dynamic"),
        foreign_keys=[game_id])

    def __repr__(self):
        return f"Wish: ({self.user.username}, {self.game.title})"

    @classmethod
    def from_both_ids(cls, user_id, game_id):
        """
        Get a Wish from its game and user ids. Return None if the wish does not exist.
        """
        req = Wish.query.filter(Wish.user_id == user_id, Wish.game_id == game_id).first()
        return req if req else None


class Prefer(db.Model):
    """
    Create a relationship between an User and a Game
    """

    frequency = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("preferences", lazy="dynamic"),
        foreign_keys=[user_id])

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    game = db.relationship(
        "Game",
        backref=db.backref("prefered_by_users", lazy="dynamic"),
        foreign_keys=[game_id])

    def __repr__(self):
        return f"Prefer: ({self.user.username}, {self.game.title})"

    @classmethod
    def from_both_ids(cls, user_id, game_id):
        """
        Get a preference from its game and user ids. Return None if the preference does not exist.
        """
        req = Prefer.query.filter(Prefer.user_id == user_id, Prefer.game_id == game_id).first()
        return req if req else None


class KnowRules(db.Model):
    """
    Create a relationship between an User and a Game
    """

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("known", lazy="dynamic"),
        foreign_keys=[user_id])

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    game = db.relationship(
        "Game",
        backref=db.backref("known_by_users", lazy="dynamic"),
        foreign_keys=[game_id])

    def __repr__(self):
        return f"KnowRules: ({self.user.username}, {self.game.title})"

    @classmethod
    def from_both_ids(cls, user_id, game_id):
        """
        Get a KnowRules relationship from its game and user ids. Return None if the relationship does not exist.
        """
        req = KnowRules.query.filter(KnowRules.user_id == user_id, KnowRules.game_id == game_id).first()
        return req if req else None


class Collect(db.Model):
    """
    Create a relationship between an User and a Game
    """

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("collection", lazy="dynamic"),
        foreign_keys=[user_id])

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    game = db.relationship(
        "Game",
        backref=db.backref("owners", lazy="dynamic"),
        foreign_keys=[game_id])

    def __repr__(self):
        return f"Collect: ({self.user.username}, {self.game.title})"

    @classmethod
    def from_both_ids(cls, user_id, game_id):
        """
        Get a Collect relationship from its game and user ids. Return None if the relationship does not exist.
        """
        req = Collect.query.filter(Collect.user_id == user_id, Collect.game_id == game_id).first()
        return req if req else None


class Note(db.Model):
    """
    Create a relationship between an User and a Game
    """

    note = db.Column(db.Integer)
    message = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("notes", lazy="dynamic"),
        foreign_keys=[user_id])

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    game = db.relationship(
        "Game",
        backref=db.backref("notes", lazy="dynamic"),
        foreign_keys=[game_id])

    def __repr__(self):
        return f"Note: ({self.user.username}, {self.game.title})"

    @classmethod
    def from_both_ids(cls, user_id, game_id):
        """
        Get a Note from its game and user ids. Return None if the note does not exist.
        """
        req = Note.query.filter(Note.user_id == user_id, Note.game_id == game_id).first()
        return req if req else None

    @classmethod
    def average_grade(cls, game_id):
        """
        Get an average grade from a game id
        """
        req = Note.query.filter(Note.game_id == game_id).all()
        avg_grade = 0
        count = 0
        for grade in req:
            if grade.note is not None:
                avg_grade += grade.note
                count += 1
        return avg_grade / count

    @classmethod
    def get_messages(cls, game_id, amount=None):
        if amount is None:
            req = Note.query.filter(Note.game_id == game_id).all()
            return req if req else None
        else:
            req = Note.query.filter(Note.game_id == game_id).limit(amount).all()
            return req if req else None


class Game(UserMixin, db.Model):
    """
    Create a Game table
    """

    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(128), unique=True)
    publication_year = db.Column(db.Integer)
    min_players = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    min_playtime = db.Column(db.Integer)
    image = db.Column(db.String(256))

    def __repr__(self):
        return f'<Game: {self.title}>'

    @classmethod
    def all(cls):
        """
        :return: return every games from db
        """
        db.session.query(Game).all()

    @classmethod
    def from_title(cls, title):
        """
        Get a Game from its title. Return None if the game does not exist.
        """
        req = Game.query.filter(Game.title == title).first()
        return req if req else None

    @classmethod
    def from_id(cls, game_id):
        """
        Get a Game from its id. Return None if the game does not exist.
        """
        req = Game.query.filter(Game.id == game_id).first()
        return req if req else None

    @classmethod
    def max_id(cls):
        """ Return the maximum id of the Game class. 0 if don't exist """
        max = db.session.query(func.max(Game.id)).one()[0]
        return max if max is not None else 0

    @classmethod
    def add_game(cls, game_id, game_data):
        """ Add game to table """
        db.session.add(
            Game(id=game_id, title=game_data['title'], publication_year=game_data['publication_year'],
                 min_players=game_data['min_players'], max_players=game_data['max_players'],
                 min_playtime=game_data['min_playtime'], image=game_data['image']))
        db.session.commit()

    @classmethod
    def search(cls, current_user_id, games_hint, typ, search_parameter):
        """
        Search games with defined parameters
        :param current_user The user who made the research
        :param games_hint: A hint gave by the user to search various games
        :param typ: str containing the type of games_hint (search filter)
        :param search_parameter: str containing the name of the search container
        :return: A SearchResults object with an items list.
        """
        results = SearchResults()  # Will contain the search results

        # Search games via a known parameter
        if search_parameter == "KNOWN":
            search_results = User.get_known_games(current_user_id)
        elif search_parameter == "NOTED":
            search_results = User.get_noted_games(current_user_id)
        elif search_parameter == "WISHED":
            search_results = User.get_wished_games(current_user_id)
        elif search_parameter == "OWNED":
            search_results = User.get_owned_games(current_user_id)
        else:
            search_results = Game.query

        # Search games in search_results that corresponds to the type and the hint
        if typ == "year":
            games_db = search_results.filter(Game.publication_year == int(games_hint))
        elif typ == "genre":
            games_ids = db.session.query(Classification.game_id).filter(Classification.genre_id.in_(
                db.session.query(Genre.id).filter(Genre.name.like("%" + games_hint + "%"))
            ))
            games_db = search_results.filter(Game.id.in_(games_ids))
        else:
            games_db = search_results.filter(Game.title.like("%" + games_hint + "%"))

        for data in games_db:
            results.items.append(
                {'id': int(data.id), 'title': data.title, 'publication_year': data.publication_year,
                 'min_players': data.min_players, 'max_players': data.max_players, 'image': data.image})
        return results

    @classmethod
    def search_with_pagination(cls, current_user_id, games_hint, typ, parameters_list, current_page=1, per_page=20):
        results = Game.search(current_user_id, games_hint, typ, parameters_list)

        page_elements = results.items[(
                                                  current_page - 1) * per_page:current_page * per_page]  # the games that will be displayed on the page
        results.pagination = Pagination(None, current_page, per_page, len(results.items), page_elements)
        results.items = None
        return results


class Genre(db.Model):
    """
    Create a Genre table
    """

    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(32), unique=True)

    def __repr__(self):
        return f'<Genre: {self.name}>'

    @classmethod
    def from_name(cls, name):
        """
        Get a Genre from its name. Return None if the game does not exist.
        """
        req = Genre.query.filter(Genre.name == name).first()
        req = Genre
        return req if req else None


class Classification(db.Model):
    """
    Create a relationship between a Game and a Genre
    """

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    game = db.relationship(
        "Game",
        backref=db.backref("classifications", lazy="dynamic"),
        foreign_keys=[game_id])

    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), primary_key=True)
    genre = db.relationship(
        "Genre",
        backref=db.backref("classifications", lazy="dynamic"),
        foreign_keys=[genre_id])

    def __repr__(self):
        return f"Classification: ({self.game.title}, {self.genre.name})"

    @classmethod
    def from_both_ids(cls, game_id, genre_id):
        """
        Get a Classification relationship from its Game and Genre ids.
        Return None if the relationship does not exist.
        """
        req = Classification.query.filter(Classification.game_id == game_id,
                                          Classification.genre_id == genre_id).first()
        return req if req else None


class Group(db.Model):
    """
    Create a Group table
    """

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    is_private = db.Column(db.Boolean)
    password = db.Column(db.String(10))

    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    manager = db.relationship(
        "User",
        backref=db.backref("managed_groups", lazy="dynamic"),
        foreign_keys=[manager_id])

    def __repr__(self):
        return f"Group: {self.name}"

    @classmethod
    def from_name(cls, name):
        """
        Get a Group from its name. Return None if the group does not exist.
        """
        req = Group.query.filter(Group.name == name).first()
        return req if req else None

    @classmethod
    def from_id(cls, id):
        """
        Get a Group from its id. Return None if the group does not exist.
        """
        req = Group.query.filter(Group.id == id).first()
        return req if req else None

    @classmethod
    def from_code(cls, code):
        """
        Get a Group from its code. Return None if the group does not exist.
        """
        req = Group.query.filter(Group.password == code).first()
        return req if req else None


class Participate(db.Model):
    """
    Create a relationship between a Group and an User
    """

    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), primary_key=True)

    member = db.relationship(
        "User",
        backref=db.backref("participations", lazy="dynamic"),
        foreign_keys=[member_id])

    group = db.relationship(
        "Group",
        backref=db.backref("participations", lazy="dynamic"),
        foreign_keys=[group_id])

    def __repr__(self):
        return f"Participate: ({self.member.username}, {self.group.name})"

    @classmethod
    def from_both_ids(cls, member_id, group_id):
        """
        Get a Participate relationship from its user and group ids.
        Return None if the relationship does not exist.
        """
        req = Participate.query.filter(Participate.member_id == member_id, Participate.group_id == group_id).first()
        return req if req else None


class TimeSlot(db.Model):
    """
    Create a TimeSlot table
    """

    __tablename__ = 'timeslots'

    id = db.Column(db.Integer, primary_key=True)
    beginning = db.Column(db.Time)
    end = db.Column(db.Time)
    day = db.Column(db.Date)

    def __init__(self, beginning, end, day):
        """
        Create a TimeSlot object.
        :param beginning: string in ISO 8601 format HH:MM:SS
        :param end: string in ISO 8601 format HH:MM:SS
        :param day: string in ISO 8601 format YYYY-MM-DD
        """
        self.beginning = time.fromisoformat(beginning)
        self.end = time.fromisoformat(end)
        self.day = date.fromisoformat(day)

    def __repr__(self):
        return f'<TimeSlot: from {self.beginning} to {self.end} the {self.day}>'


class Available(db.Model):
    """
    Create a relationship between a TimeSlot and a User
    """

    periodicity = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("availabilities", lazy="dynamic"),
        foreign_keys=[user_id])

    timeslot_id = db.Column(db.Integer, db.ForeignKey("timeslots.id"), primary_key=True)
    timeslot = db.relationship(
        "TimeSlot",
        backref=db.backref("availabilities", lazy="dynamic"),
        foreign_keys=[timeslot_id])

    @classmethod
    def from_both_ids(cls, user_id, timeslot_id):
        """
        Get a Available relationship from its user and timeslot ids.
        Return None if the relationship does not exist.
        """
        req = Available.query.filter(Available.user_id == user_id, Available.timeslot_id == timeslot_id).first()
        return req if req else None


class Vote(db.Model):
    """
    Create a Vote table
    """

    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    nb_participants_required = db.Column(db.Integer)
    timeout = db.Column(db.DateTime)


class HideGame(db.Model):
    """
    Create a realtionship between a Game, a User and a Vote
    """

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("hidden_games", lazy="dynamic"),
        foreign_keys=[user_id])

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    game = db.relationship(
        "Game",
        backref=db.backref("hidden_games", lazy="dynamic"),
        foreign_keys=[game_id])

    vote_id = db.Column(db.Integer, db.ForeignKey("votes.id"), primary_key=True)
    vote = db.relationship(
        "Vote",
        backref=db.backref("hidden_games", lazy="dynamic"),
        foreign_keys=[vote_id])


class Revolution(db.Model):
    """
    Create a relationship between a Group, a User and a Vote
    """

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("revolutions", lazy="dynamic"),
        foreign_keys=[user_id])

    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), primary_key=True)
    group = db.relationship(
        "Group",
        backref=db.backref("revolutions", lazy="dynamic"),
        foreign_keys=[group_id])

    vote_id = db.Column(db.Integer, db.ForeignKey("votes.id"), primary_key=True)
    vote = db.relationship(
        "Vote",
        backref=db.backref("revolutions", lazy="dynamic"),
        foreign_keys=[vote_id])


class Session(db.Model):
    """
    Create a Session table
    """

    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    nb_players_required = db.Column(db.Integer)
    notifactions_sent = db.Column(db.Boolean)
    confirmed = db.Column(db.Boolean)
    timeout = db.Column(db.DateTime)
    archived = db.Column(db.Boolean)

    timeslot_id = db.Column(db.Integer, db.ForeignKey("timeslots.id"), default=None)
    timeslot = db.relationship(
        "TimeSlot",
        backref=db.backref("sessions", lazy="dynamic"),
        foreign_keys=[timeslot_id])

    def __init__(self, nb_players_required, timeout, notifactions_sent=False, confirmed=False, archived=False):
        """
        Create a Session object.
        :param timeout: a string in ISO 8601 format YYYY-MM-DDTHH-MM-SS
        """
        self.nb_players_required = nb_players_required
        self.notifactions_sent = notifactions_sent
        self.confirmed = confirmed
        self.timeout = datetime.fromisoformat(timeout)
        self.archived = archived


class Play(db.Model):
    """
    Create a relationship between a Session and an User
    """

    confirmed = db.Column(db.Boolean, default=False)
    won = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("played_sessions", lazy="dynamic"),
        foreign_keys=[user_id])

    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), primary_key=True)
    session = db.relationship(
        "Session",
        backref=db.backref("players", lazy="dynamic"),
        foreign_keys=[session_id])

    @classmethod
    def from_both_ids(cls, user_id, session_id):
        """
        Get a Play relationship from its user and session ids.
        Return None if the relationship does not exist.
        """
        req = Play.query.filter(Play.user_id == user_id, Play.session_id == session_id).first()
        return req if req else None


class Comment(db.Model):
    """
    Create a relationship between a Session and an User
    """

    message = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    user = db.relationship(
        "User",
        backref=db.backref("commented_sessions", lazy="dynamic"),
        foreign_keys=[user_id])

    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), primary_key=True)
    session = db.relationship(
        "Session",
        backref=db.backref("commented_by_users", lazy="dynamic"),
        foreign_keys=[session_id])

    @classmethod
    def from_both_ids(cls, user_id, session_id):
        """
        Get a Comment relationship from its user and session ids.
        Return None if the relationship does not exist.
        """
        req = Comment.query.filter(Comment.user_id == user_id, Comment.session_id == session_id).first()
        return req if req else None


class Use(db.Model):
    """
    Create a relationship between a Session and a Game
    """

    expected_time = db.Column(db.Time)
    real_time = db.Column(db.Time, default=None)

    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), primary_key=True)
    session = db.relationship(
        "Session",
        backref=db.backref("sessions", lazy="dynamic"),
        foreign_keys=[session_id])

    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), primary_key=True)
    game = db.relationship(
        "Game",
        backref=db.backref("games", lazy="dynamic"),
        foreign_keys=[game_id])

    def __init__(self, expected_time, session_id, game_id, real_time=None):
        """
        Create a Use instance with expected_time and real_time using the format
        HH:MM:SS
        """
        self.session_id = session_id
        self.game_id = game_id
        self.expected_time = time.fromisoformat(expected_time)
        if real_time:
            self.real_time = time.fromisoformat(real_time)

    @classmethod
    def from_both_ids(cls, session_id, game_id):
        """
        Get a Use relationship from its session and game ids
        Return None if the relationship does not exist.
        """
        req = Use.query.filter(Use.session_id == session_id, Use.game_id == game_id).first()
        return req if req else None


class SearchResults:
    """
    An utility class that stores objects search results.
    """

    def __init__(self):
        """
        Initializes a SearchResults object.
        :param items: Found objects in a list, list() if the search results doesn't use an items list.
        :param pagination: Found objects in a Pagination object, None if the search results doesn't use SQLAlchemy's
        pagination system.
        :param hidden_ids: A list which contains the hidden objects ids, list() if not used.
        :param bookmarked_ids: A list which contains the bookmarked objtects ids, list() if not used.
        """
        self.items = list()
        self.pagination = None
        self.hidden_ids = set()
        self.bookmarked_ids = set()
