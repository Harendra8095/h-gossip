from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, DateTime
from datetime import datetime
from .meta import Base

class Post(Base):
    """ Posts Model for storing user posts """
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    body = Column(String(255))
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
