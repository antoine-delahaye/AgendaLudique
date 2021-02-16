from flask import Blueprint

jeux = Blueprint("jeux", __name__,
                 template_folder="templates")

from . import views
