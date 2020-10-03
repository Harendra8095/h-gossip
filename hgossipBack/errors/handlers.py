from flask import render_template
from server import SQLSession
from hgossipBack.errors import bp


session = SQLSession()


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    session.rollback()
    return render_template('errors/500.html'), 500