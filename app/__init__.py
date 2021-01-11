# app/__init__.py

# Third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

# Local imports
from config import app_config

# SQLAlchemy variable initialization
db = SQLAlchemy()

# LoginManager variable initialization
login_manager = LoginManager()


def create_app(config_name):
    # Models import
    from app import models
    # Blueprint imports
    from app.site import site as site_blueprint
    from app.auth import auth as auth_blueprint
    # App configuration
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['BOOTSTRAP_SERVER_LOCAL'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Register blueprints
    app.register_blueprint(site_blueprint)
    app.register_blueprint(auth_blueprint)
    # Initialize db
    db.init_app(app)
    # Initialize login_manager
    login_manager.init_app(app)
    login_manager.login_message = 'Vous devez être connecté pour avoir accès à cette page'
    login_manager.login_view = 'auth.login'
    # Initialize Migrate
    migrate = Migrate(app, db)
    # Initialize Bootstrap
    Bootstrap(app)
    return app
