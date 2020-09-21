from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Sequence
from .meta import Base

from server import SQLSession

session = SQLSession

class User(Base):
    """ User Model for storing user related details """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True)
    email = Column(String(127), unique=True, index=True)
    password_hash = Column(String(127))

    def __repr__(self):
        return '<User {}>'.format(self.username)