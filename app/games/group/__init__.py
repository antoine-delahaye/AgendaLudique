from flask import Blueprint

group = Blueprint("group", __name__,
                  template_folder="templates")

from . import views
