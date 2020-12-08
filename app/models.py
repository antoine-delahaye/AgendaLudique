# app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    """
    Create an User table
    """

    # as is the name of the model
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(32), index=True, unique=True)
    first_name = db.Column(db.String(32), index=True)
    last_name = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    profile_picture = db.Column(db.String(512),
                                default='https://i.pinimg.com/originals/7d/b8/fe/7db8fe54d55fb987b2e73cbceaf22072.jpg')

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


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Game(UserMixin, db.Model):
    """
    Create an Game table
    """

    # as is the name of the model
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    publication_year = db.Column(db.Integer)
    min_players = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    min_playtime = db.Column(db.Integer)
    image = db.Column(db.String(256))

    def __repr__(self):
        return f'<Game: {self.title}>'
