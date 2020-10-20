from .meta import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime


class Message(Base):
    """ Message models to store private message """
    __tablename__ = 'Message'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('user.id'))
    recipient_id = Column(Integer, ForeignKey('user.id'))
    body = Column(String(255))
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)


    def __repr__(self):
        return '<Message {}>'.format(self.body)