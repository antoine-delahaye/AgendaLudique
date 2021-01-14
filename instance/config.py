import os

SECRET_KEY = os.urandom(32)
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://al_admin:al_admin@localhost/agendaludique'
