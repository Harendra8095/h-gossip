from flask_login import current_user, login_required
from datetime import datetime
from flask import g, flash, redirect, url_for, render_template
from flask_babel import _, get_locale
from sqlalchemy_paginator import Paginator


from hgossipBack.models.usermodels import User
from hgossipBack.models.postsmodels import Post


from hgossipBack.forms import PostForm, EmptyForm


from server import SQLSession

from flask import Blueprint
homeBP = Blueprint('homeApi', __name__)

@homeBP.before_app_request
def before_request():
    session = SQLSession()
    if current_user.is_authenticated:
        u = session.query(User).filter_by(username=current_user.username).first()
        u.last_seen = datetime.utcnow()
        session.commit()
        session.close()
    g.locale = str(get_locale())


@homeBP.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    session = SQLSession()
    connection = session.connection()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        session.merge(post)
        session.commit()
        session.close()
        connection.close()
        flash(_('Your post is now live!'))
        return redirect(url_for('homeApi.index'))
    posts = current_user.followed_posts().all()
    return render_template("index.html", title=_('Home Page'), form=form, posts=posts)


@homeBP.route('/explore')
@login_required
def explore():
    session = SQLSession()
    posts = session.query(Post).order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title=_('Explore'), posts=posts)


@homeBP.route('/user/<username>')
@login_required
def user(username):
    session = SQLSession()
    user = session.query(User).filter_by(username=username).first()
    # page_no = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc())
    paginator = Paginator(posts, 25)
    page = paginator.page(page_number=1)
    # paginator(
    #    page, app.config['POSTS_PER_PAGE'], False
    # )
    next_url = url_for('homeApi.user', username=user.username, page_no=page.next_page_number) \
        if page.has_next() else None
    prev_url = url_for('homeApi.user', username=user.username, page_no=page.previous_page_number) \
        if page.has_previous() else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, next_url=next_url, prev_url=prev_url, form=form)


@homeBP.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
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
