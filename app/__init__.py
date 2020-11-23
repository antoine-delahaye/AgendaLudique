# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()

# login_manager variable initialization
login_manager = LoginManager()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['BOOTSTRAP_SERVER_LOCAL'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    Bootstrap(app)
    from .site import site as site_blueprint
    app.register_blueprint(site_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in to access this page.'
    login_manager.login_view = 'auth.login'
    migrate = Migrate(app, db)
    from . import models
    return app
