from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Sequence
from .meta import Base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(Base, UserMixin):
    """ User Model for storing user related details """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True)
    email = Column(String(127), unique=True, index=True)
    password_hash = Column(String(127))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def __repr__(self):
        return '<User {}>'.format(self.username)