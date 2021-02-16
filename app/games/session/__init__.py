from flask import Blueprint

session = Blueprint("session", __name__,
                    template_folder="templates")

from . import views
