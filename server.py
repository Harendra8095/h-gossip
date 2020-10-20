from flask import Flask, request
from flask_moment import Moment
from flask_babel import Babel
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap

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


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@login.user_loader
def load_user(id):
    from hgossipBack.models import User
    session = SQLSession()
    connection = session.connection()
    user_ = session.query(User).get(int(id))
    session.close()
    connection.close()
    return user_


if __name__ == "__main__":
    app.run()
