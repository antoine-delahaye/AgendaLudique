# app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import join

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

    def __repr__(self):
        return f'<User: {self.username}>'

    @classmethod
    def is_registered(cls, email):
        """
        Check if an email is already used.
        """
        req = User.query.filter(User.email == email).first()
        return True if req else False

    @classmethod
    def from_username(cls, username):
        """
        Get an user from its username. Return None if the user does not exist.
        """
        req = User.query.filter(User.username == username).first()
        return req if req else None

    @classmethod
    def search(cls, current_user, username_hint="", parameters=[]):
        """
        Search users with defined parameters
        :param current_user The user who made the research
        :param username_hint: A hint gave by the user to search similar usernames
        :param parameters: include into the list "HIDDEN" to return the hidden users as well as the others users,
        and/or "ONLY_BOOKMARKED" to return only the bookmarked users.
        :return: A list of users
        """
        users_db = []
        result = []

        if "ONLY_BOOKMARKED" not in parameters:  # Displays only bookmarked users
            users_db = db.session.query(User).filter(User.username.like('%' + username_hint + '%')).all()
        else:
            bookmarked_users_db = User.query.get(current_user.id).bookmarked_users.all()
            for bookmarked_user in bookmarked_users_db:
                users_db.append(User.query.get(bookmarked_user.user2_id))

        if "HIDDEN" not in parameters:  # Removes all the users hidden by the user from the search results
            hidden_users_db = User.query.get(current_user.id).hidden_users.all()
            for hidden_user in hidden_users_db:
                user_to_be_removed = User.query.get(hidden_user.user2_id)
                if user_to_be_removed in users_db:
                    users_db.remove(user_to_be_removed)

        for data in users_db:
            result.append(
                {'id': int(data.id), 'username': data.username, 'first_name': data.first_name,
                 'last_name': data.last_name,
                 'profile_picture': data.profile_picture})

        return result


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
        req = Game.query.filter(Game.title == title).first()
        return req if req else None


class Genre(db.Model):
    """
    Create a Genre table
    """

    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)

    def __repr__(self):
        return f'<Genre: {self.name}>'

    @classmethod
    def from_name(cls, name):
        """
        Get a Genre from its name. Return None if the game does not exist.
        """
        req = Genre.query.filter(Genre.name == name).first()
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

    timeslot_id = db.Column(db.Integer, db.ForeignKey("timeslots.id"))
    timeslot = db.relationship(
        "TimeSlot",
        backref=db.backref("sessions", lazy="dynamic"),
        foreign_keys=[timeslot_id])


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

    @classmethod
    def from_both_ids(cls, session_id, game_id):
        """
        Get a Use relationship from its session and game ids
        Return None if the relationship does not exist.
        """
        req = Use.query.filter(Use.session_id == session_id, Use.game_id == game_id).first()
        return req if req else None
