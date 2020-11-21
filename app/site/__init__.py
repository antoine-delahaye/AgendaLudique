# app/site/__init__.py

from flask import Blueprint

site = Blueprint('site', __name__)

from . import views
