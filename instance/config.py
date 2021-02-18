import os


class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://al_admin:al_admin@agenda-ludique.ddns.net/agendaludique'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465,
    MAIL_USERNAME = 'noreply.agendaludique@gmail.com'
    MAIL_DEFAULT_SENDER = 'Agenda Ludique'
    MAIL_PASSWORD = 'uteokhqmpqwyjgdj'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    BOOTSTRAP_SERVER_LOCAL = True


class DevelopmentConfig(Config):
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = True


class ProductionConfig(Config):
    SSL_REDIRECT = False


class LocalConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://al_admin:al_admin@localhost/agendaludique'


class TestingConfig(Config):
    FLASK_DEBUG = 0
    TESTING = True
    # local database for testing
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'local': LocalConfig,

    'default': DevelopmentConfig,
}

# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://al_admin:al_admin@localhost/agendaludique'
