# app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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
    profile_picture = db.Column(db.String(512),
                                default='https://acsmmontreal.qc.ca/wp-content/uploads/2020/09/blank-profile-picture'
                                        '-973460_1280-7.png')

    # statistics_id = db.Column(db.Integer, db.ForeignKey("statistics.id"))
    # statistics = db.relationship(
    #     "Statistic",
    #     back_populates="user",
    #     foreign_keys=[statistics_id])

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

    def __repr__(self):
        return f'<Employee: {self.username}>'

    @classmethod
    def from_username(cls, username):
        """
        Get an user from its username. Return None if the user does not exist.
        """
        req = User.query.filter(User.username==username).first()
        return req if req else None

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


# class Statistic(db.Model):
#     """
#     Create a Statistic table
#     """
#
#     __tablename__ = 'statistics'
#
#     id = db.Column(db.Integer, primary_key=True)
#     avg_complexity = db.Column(db.Integer, default=0)
#     avg_playtime = db.Column(db.Integer, default=0)
#     avg_nb_players = db.Column(db.Integer, default=0)
#     frequency = db.Column(db.Integer, default=0)
#
#     # user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
#     user = db.relationship(
#         "User",
#         back_populates="statistics",
#         uselist=False)


class Wich(db.Model):
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

    @classmethod
    def from_both_ids(cls, user_id, game_id):
        """
        Get a Note from its game and user ids. Return None if the note does not exist.
        """
        req = Note.query.filter(Note.user_id==user_id,Note.game_id==game_id).first()
        return req if req else None


class Game(UserMixin, db.Model):
    """
    Create a Game table
    """

    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    publication_year = db.Column(db.Integer)
    min_players = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    min_playtime = db.Column(db.Integer)
    image = db.Column(db.String(256))

    def __repr__(self):
        return f'<Game: {self.title}>'

    @classmethod
    def from_title(cls, title):
        """
        Get a Game from its title. Return None if the game does not exist.
        """
        req = Game.query.filter(Game.title==title).first()
        return req if req else None


class Group(db.Model):
    """
    Create a Group table
    """

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    is_private = db.Column(db.Boolean)
    password = db.Column(db.String(10))

    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    manager = db.relationship(
        "User",
        backref=db.backref("managed_groups", lazy="dynamic"),
        foreign_keys=[manager_id])


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


class TimeSlot(db.Model):
    """
    Create a TimeSlot table
    """

    __tablename__ = 'timeslots'

    id = db.Column(db.Integer, primary_key=True)
    beginning = db.Column(db.Time)
    end = db.Column(db.Time)
    day = db.Column(db.Date) # db.Column(db.Date) ?


class Available(db.Model):
    """
    Create a relationship between a TimeSlot and a User
    """

    periodicity = db.Column(db.Integer) # db.Column(db.String) ?

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

    timeslot_id = db.Column(db.Integer, db.ForeignKey("timeslots.id"))
    timeslot = db.relationship(
        "TimeSlot",
        backref=db.backref("sessions", lazy="dynamic"),
        foreign_keys=[timeslot_id])


class Play(db.Model):
    """
    Create a relationship between a Session and an User
    """

    confirmed = db.Column(db.Boolean)
    won = db.Column(db.Boolean)

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
