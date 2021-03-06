from flask import render_template, current_app
from flask_babel import _
from threading import Thread
from flask_mail import Message

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    from server import app
    send_mail(_('[hgossip] Reset Your Password'),
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


def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    from server import send_async_email
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
