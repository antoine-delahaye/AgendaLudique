from flask import Blueprint

mail = Blueprint("mail", __name__, template_folder="templates")

from . import commands
