from flask import Blueprint

test_blueprint = Blueprint("test", __name__)

from .test_auth import AUTHTest
from .commands import test
