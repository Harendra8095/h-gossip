from flask.globals import session
from flask_login import current_user, login_user, login_required, logout_user
from flask import redirect, url_for, flash, render_template, request
from flask_babel import _
from werkzeug.urls import url_parse

from hgossipBack.email import send_password_reset_email
from hgossipBack.forms import RegistrationForm, LoginFrom, EditProfile, ResetPasswordRequestForm, ResetPasswordForm
from hgossipBack.models import User


from flask import Blueprint
userBP = Blueprint('userApi', __name__)


@userBP.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('homeApi.index'))
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email= form.email.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        session.close()
        connection.close()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('userApi.login'))
    session.close()
    connection.close()
    return render_template('auth/register.html', title=_('Register'), form=form)


@userBP.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homeApi.index'))
    from server import SQLSession
    form = LoginFrom()
    session = SQLSession()
    connection = session.connection()
    if form.validate_on_submit():
        user = session.query(User).filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            session.close()
            connection.close()
            return redirect(url_for('userApi.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('homeApi.index')
        session.close()
        connection.close()
        return redirect(next_page)
    session.close()
    connection.close()
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@userBP.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    form = EditProfile(current_user.username)
    u = session.query(User).filter_by(username=current_user.username).first()
    if form.validate_on_submit():
        u.username = form.username.data
        u.bio = form.bio.data
        session.commit()
        session.close()
        connection.close()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('homeApi.user', username=u.username))
    elif request.method == 'GET':
        form.username.data = u.username
        form.bio.data = u.bio
    session.close()
    connection.close()
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@userBP.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('homeApi.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        from server import SQLSession
        session = SQLSession()
        connection = session.connection()
        user = session.query(User).filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        session.close()
        connection.close()
        return redirect(url_for('userApi.login'))
    return render_template('auth/reset_pass.html', title=_('Reset Password'), form=form)


@userBP.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('homeApi.index'))
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    user = User.verify_reset_password(token)
    if not user:
        session.close()
        connection.close()
        return redirect(url_for('homeApi.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        u = session.query(User).filter_by(username=user.username).first()
        u.set_password(form.password.data)
        session.commit()
        session.close()
        connection.close()
        flash(_('Your Password has been reset.'))
        return redirect(url_for('userApi.login'))
    session.close()
    connection.close()
    return render_template('auth/reset_password.html', form=form)


@userBP.route('/logout')
def logout():
    from server import SQLSession
    session = SQLSession()
    connection = session.connection()
    session.close()
    connection.close()
    logout_user()
    return redirect(url_for('homeApi.index'))
