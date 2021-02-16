from flask import Blueprint

# bp qui permet l'administration de l'application
admin_blueprint = Blueprint('admin', __name__)

from . import commands