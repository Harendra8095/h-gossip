import os
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

from hgossipBack.forms.login import LoginFrom
from hgossipBack.forms.register import RegistrationForm
from hgossipBack.forms.editprofile import EditProfile
from hgossipBack.config import DbEngine_config, DevelopmentConfig
from hgossipBack import create_db_engine, create_db_sessionFactory
from hgossipBack.models import User

from dotenv import load_dotenv

load_dotenv()

engine = create_db_engine(DbEngine_config)
SQLSession = create_db_sessionFactory(engine)


app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
app.config.from_object(DbEngine_config())
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
login = LoginManager(app)
login.login_view = 'login'


@login.user_loader
def load_user(id):
    session = SQLSession()
    conn = session.connection()
    return session.query(User).get(int(id))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        session = SQLSession()
        conn = session.connection()
        u = session.query(User).filter_by(username=current_user.username).first()
        u.last_seen = datetime.utcnow()
        session.commit()
        session.close()


@app.route('/')
def get():
    return "<h1> Hello, Welcome to backend of h-gossip </h1>"


@app.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'kajal'},
            'body': 'Build it asap!'
        },
        {
            'author': {'username': 'urmila'},
            'body': 'Refactor Refactor Refactor!!!!'
        }
    ]
    return render_template('/index.html',title='Home Page', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginFrom()
    if form.validate_on_submit():
        session = SQLSession()
        conn = session.connection()
        user = session.query(User).filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('/login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        session = SQLSession()
        conn = session.connection()
        user = User(username=form.username.data, email= form.email.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        flash('Congratulations, you are now a registered user!')
        session.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile()
    session = SQLSession()
    conn = session.connection()
    u = session.query(User).filter_by(username=current_user.username).first()
    if form.validate_on_submit():
        u.username = form.username.data
        u.bio = form.bio.data
        session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=u.username))
    elif request.method == 'GET':
        form.username.data = u.username
        form.bio.data = u.bio
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username):
    session = SQLSession()
    conn = session.connection()
    user = session.query(User).filter_by(username=username).first()
    posts = [
        {'author':user, 'body':'Test post #1'},
        {'author':user, 'body':'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


if __name__ == "__main__":
    app.run()
