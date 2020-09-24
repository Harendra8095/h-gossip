import os
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from sqlalchemy_paginator import Paginator

from hgossipBack.forms.login import LoginFrom
from hgossipBack.forms.register import RegistrationForm
from hgossipBack.forms.editprofile import EditProfile
from hgossipBack.forms.follow import EmptyForm
from hgossipBack.forms.post import PostForm
from hgossipBack.forms.reset import ResetPasswordRequestForm, ResetPasswordForm
from hgossipBack.config import *
from hgossipBack import create_db_engine, create_db_sessionFactory
from hgossipBack.models import User, Post

from flask_mail import Mail
from flask_mail import Message

from dotenv import load_dotenv

load_dotenv()

engine = create_db_engine(DbEngine_config)
SQLSession = create_db_sessionFactory(engine)
session = SQLSession()
conn = session.connection()


app = Flask(__name__)
app.config.from_object(ProductionConfig())
app.config.from_object(DbEngine_config())
app.config.from_object(MailConfig())
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
login = LoginManager(app)
login.login_view = 'login'


mail = Mail(app)

def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail('[hgossip] Reset Your Password',
        sender=app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt',
            user=user,
            token=token
            ),
        html_body=render_template('email/reset_password.html',
                user=user,
                token=token
            )
    )


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


# TODO Create the api and error handler class

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    session.rollback()
    return render_template('500.html'), 500


@login.user_loader
def load_user(id):
    return session.query(User).get(int(id))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        u = session.query(User).filter_by(username=current_user.username).first()
        u.last_seen = datetime.utcnow()
        session.commit()


@app.route('/')
def get():
    return "<h1> Hello, Welcome to backend of h-gossip </h1>"


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        session.add(post)
        session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = current_user.followed_posts().all()
    return render_template("index.html", title='Home Page', form=form, posts=posts)


@app.route('/explore')
@login_required
def explore():
    posts = session.query(Post).order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginFrom()
    if form.validate_on_submit():
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
        user = User(username=form.username.data, email= form.email.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile(current_user.username)
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


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_pass.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        u = session.query(User).filter_by(username=user.username).first()
        u.set_password(form.password.data)
        session.commit()
        session.close()
        flash('Your Password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username):
    user = session.query(User).filter_by(username=username).first()
    # page_no = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc())
    paginator = Paginator(posts, app.config['POSTS_PER_PAGE'])
    page = paginator.page(page_number=1)
    # paginator(
    #    page, app.config['POSTS_PER_PAGE'], False
    # )
    next_url = url_for('user', username=user.username, page_no=page.next_page_number) \
        if page.has_next() else None
    prev_url = url_for('user', username=user.username, page_no=page.previous_page_number) \
        if page.has_previous() else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, next_url=next_url, prev_url=prev_url, form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        u = session.query(User).filter_by(username=current_user.username).first()
        u.follow(user)
        session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        u = session.query(User).filter_by(username=current_user.username).first()
        u.unfollow(user)
        session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
