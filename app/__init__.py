# app/__init__.py

# Third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from .utils.mail import MailTool
# Local imports
from config import app_config

# SQLAlchemy variable initialization
db = SQLAlchemy()

# LoginManager variable initialization
login_manager = LoginManager()
# Blueprint imports
from app.site import site as site_blueprint
from app.auth import auth as auth_blueprint
from .commands import admin_blueprint

app = None
mail = None


def create_app(config_name):
    # Models import
    from app import models

    # App configuration
    app = config_app(config_name)
    # Register blueprints
    register_blueprint(app)
    # Initialize db and login_manager
    init_db(app)
    # Initialize Bootstrap
    Bootstrap(app)
    # Initialize mails
    config_mail(app)

    return app


def config_app(config_name):
    """
    config app
    :return: app to be served
    """
    global app

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['BOOTSTRAP_SERVER_LOCAL'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app


def config_mail(app):
    """
    config mail settings
    :param app: app to be served
    """
    global mail
    mail_config = {
        'MAIL_SERVER': 'smtp.gmail.com',
        'MAIL_PORT': 465,
        'MAIL_USERNAME': 'noreply.agendaludique@gmail.com',
        'MAIL_DEFAULT_SENDER': 'Agenda Ludique',
        'MAIL_PASSWORD': 'uteokhqmpqwyjgdj',
        'MAIL_USE_TLS': False,
        'MAIL_USE_SSL': True
    }
    app.config.update(mail_config)
    mail = MailTool(app)


def register_blueprint(app):
    """
    add every blueprint that will be used
    :param app: app to be served
    """
    app.register_blueprint(site_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)


def init_db(app):
    """
    init everything that is related to the db
    :param app: app to be served
    """
    global db

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = 'Vous devez être connecté pour avoir accès à cette page'
    login_manager.login_view = 'auth.login'
    # Initialize Migrate
    migrate = Migrate(app, db)
