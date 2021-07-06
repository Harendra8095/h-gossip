from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, render_template
from flask_moment import Moment
from flask_babel import Babel
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap

from hgossipBack.config import *
from hgossipBack.models import Post
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


def send_async_email(app, msg):
    from server import mail
    with app.app_context():
        mail.send(msg)

@app.route('/')
def get():
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    posts = session.query(Post).order_by(Post.timestamp.desc())
    # posts = [{
    #     "id": i.id,
    #     "body": i.body,
    #     "timestamp": i.timestamp,
    #     "author": i.user_id
    # } for i in posts_q]
    # print(posts)
    session.close()
    connection.close()
    # posts.__class__ = BaseQuery
    return render_template('index.html', title=_('Explore'), posts=posts)

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
