import os
from flask import Flask, render_template, flash, redirect, url_for

from hgossipBack.forms.login import LoginFrom
from hgossipBack.config import DevelopmentConfig, DbEngine_config

from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.config.from_object(DevelopmentConfig())
app.config.from_object(DbEngine_config())


@app.route('/')
def get():
    return "<h1> Hello, Welcome to backend of h-gossip </h1>"

@app.route('/index')
def index():
    user = {'username': 'Harry'}
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
    return render_template('/index.html', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginFrom()
    if form.validate_on_submit():
        flash('Login requested from the user {}, remember_me {}'.format(
            form.username.data, form.remember_me.data
        ))
        return redirect(url_for('index'))
    return render_template('/login.html', title='Sign In', form=form)

if __name__ == "__main__":
    app.run()
