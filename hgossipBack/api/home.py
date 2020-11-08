from flask.globals import session
from flask_login import current_user, login_required
from datetime import datetime
from flask import g, flash, redirect, url_for, render_template, jsonify, request
from flask_babel import _, get_locale
from flask_mail import Message
from sqlalchemy_paginator import Paginator
from flask_sqlalchemy import BaseQuery


from hgossipBack.models import User, Post, Message, Notification
# from hgossipBack.models.postsmodels import Post


from hgossipBack.forms import PostForm, EmptyForm, MessageForm


from flask import Blueprint
homeBP = Blueprint('homeApi', __name__)

@homeBP.before_app_request
def before_request():
    if current_user.is_authenticated:
        from server import SQLSession
        session = SQLSession()
        connection = session.connection()
        u = session.query(User).filter_by(username=current_user.username).first()
        u.last_seen = datetime.utcnow()
        session.commit()
        session.close()
        connection.close()
    g.locale = str(get_locale())   


@homeBP.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        from server import SQLSession
        session = SQLSession()
        connection = session.connection()
        post = Post(body=form.post.data, author=current_user)
        session.merge(post)
        session.commit()
        session.close()
        connection.close()
        flash(_('Your post is now live!'))
        return redirect(url_for('homeApi.index'))
    posts = current_user.followed_posts()
    return render_template("index.html", title=_('Home Page'), form=form, posts=posts)


@homeBP.route('/explore')
# @login_required
def explore():
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


@homeBP.route('/user/<username>')
@login_required
def user(username):
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    user = session.query(User).filter_by(username=username).first()
    # user_ = session.query(User).filter_by(username=username)
    # print(user.id)
    # page_no = request.args.get('page', 1, type=int)
    posts = session.query(Post).filter_by(user_id=user.id)
    # paginator = Paginator(posts, 25)
    # page = paginator.page(page_number=1)
    # paginator(
    #    page, app.config['POSTS_PER_PAGE'], False
    # )
    session.close()
    connection.close()
    # next_url = url_for('homeApi.user', username=user.username, page_no=page.next_page_number) \
    #     if page.has_next() else None
    # prev_url = url_for('homeApi.user', username=user.username, page_no=page.previous_page_number) \
    #     if page.has_previous() else None
    form = EmptyForm()
    # return render_template('user.html', user=user, posts=posts, next_url=next_url, prev_url=prev_url, form=form)
    return render_template('user.html', user=user, posts=posts, form=form)

@homeBP.route('/user/<username>/popup')
@login_required
def user_popup(username):
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    user = session.query(User).filter_by(username=username).first()
    form = EmptyForm()
    session.close()
    connection.close()
    return render_template('user_popup.html', user=user, form=form)


@homeBP.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        from server import SQLSession
        session = SQLSession()
        connection = session.connection()
        user = session.query(User).filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('hoemApi.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('homeApi.user', username=username))
        u = session.query(User).filter_by(username=current_user.username).first()
        u.follow(user)
        session.commit()
        session.close()
        connection.close()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('homeApi.user', username=username))
    else:
        return redirect(url_for('homeApi.index'))


@homeBP.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        from server import SQLSession
        session = SQLSession()
        connection = session.connection()
        user = session.query(User).filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('homeApi.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('homeApi.user', username=username))
        u = session.query(User).filter_by(username=current_user.username).first()
        u.unfollow(user)
        session.commit()
        session.close()
        connection.close()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('homeApi.user', username=username))
    else:
        return redirect(url_for('homeApi.index'))


@homeBP.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    user = session.query(User).filter_by(username=recipient).first()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        user.add_notification('unread_message_count', user.new_messages())
        session.add(msg)
        session.commit()
        session.close()
        connection.close()
        flash(_('Your message has been sent.'))
        return redirect(url_for('homeApi.user', username=recipient))
    session.close()
    connection.close()
    return render_template('send_message.html', title=_('Send Message'), form=form, recipient=recipient)

@homeBP.route('/messages')
@login_required
def messages():
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    session.commit()
    messages = current_user.messages_recieved.order_by(
        Message.timestamp.desc())
    paginator = Paginator(messages, 25)
    page = paginator.page(page_number=1)
    # paginator(
    #    page, app.config['POSTS_PER_PAGE'], False
    # )
    next_url = url_for('homeApi.messages', page=page.next_num) \
        if page.has_next() else None
    prev_url = url_for('homeApi.messages', page=page.prev_num) \
        if page.has_previous() else None
    session.close()
    connection.close()
    return render_template('message.html', messages=messages.items, next_url=next_url, prev_url=prev_url)


@homeBP.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])
