from flask import render_template
from threading import Thread
from flask_mail import Message
from server import mail

def send_async_email(app, msg):
    pass