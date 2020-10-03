import os
from flask import Flask, request
from flask_moment import Moment
from flask_babel import Babel
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap

from flask.globals import session
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from hgossipBack.config import *
from hgossipBack import create_db_engine, create_db_sessionFactory
from flask_babel import _, lazy_gettext as _l

engine = create_db_engine(DbEngine_config)
SQLSession = create_db_sessionFactory(engine)

app = Flask(__name__)
app.config.from_object(ProductionConfig())
app.config.from_object(DbEngine_config())
app.config.from_object(MailConfig())
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

moment = Moment(app)
babel = Babel(app)
login = LoginManager(app)
login.login_view = 'userApi.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail(app)
bootstrap = Bootstrap(app)

from hgossipBack.errors import bp as errors_bp
from hgossipBack.api import *


@app.route('/')
def get():
    return "<h1> Hello, Welcome to backend of h-gossip </h1>"


app.register_blueprint(errors_bp)
app.register_blueprint(userBP, url_prefix='/{}/user'.format(API_VERSION))
app.register_blueprint(homeBP, url_prefix='/{}/home'.format(API_VERSION))


# TODO Testing of mail service

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='H-gossip Failure',
            credentials=auth, secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/hgossip.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('H-gossip startup')


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


if __name__ == "__main__":
    app.run()
