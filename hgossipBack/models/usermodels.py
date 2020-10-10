from re import U
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

from server import login, SQLSession

from .meta import Base
from .follower import followers
from .postsmodels import Post

from time import time
import jwt

class User(Base, UserMixin):
    """ User Model for storing user related details """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True)
    email = Column(String(127), unique=True, index=True)
    password_hash = Column(String(127))
    posts = relationship('Post', backref='author', lazy='dynamic')
    bio = Column(String(127))
    last_seen = Column(DateTime, default=datetime.utcnow)

    followed = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id
        ).count() > 0


    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    # TODO unfollow not working
    def unfollow(self, user):
        if not self.is_following(user):
            self.followed.remove(user)

    
    def followed_posts(self):
        session = SQLSession()
        connection = session.connection()
        followed = session.query(Post).join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(
            followers.c.follower_id == self.id
        )
        own = session.query(Post).filter_by(user_id=self.id)
        session.close()
        connection.close()
        return followed.union(own).order_by(Post.timestamp.desc())


    def get_reset_password_token(self, expires_in=6000):
        from server import app
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')
    

    def __repr__(self):
        return '<User {}>'.format(self.username)


    @staticmethod
    def verify_reset_password(token):
        from server import app
        session = SQLSession()
        connection = session.connection()
        try:
            id=jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            session.close()
            connection.close()
            return
        user_ = session.query(User).get(id)
        session.close()
        connection.close()
        return user_

@login.user_loader
def load_user(id):
    session = SQLSession()
    connection = session.connection()
    user_ = session.query(User).get(int(id))
    session.close()
    connection.close()
    return user_
    