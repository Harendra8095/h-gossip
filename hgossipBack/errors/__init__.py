from flask import Blueprint

bp = Blueprint('errors', __name__)

from hgossipBack.errors import handlers
