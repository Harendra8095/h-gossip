from .meta import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from datetime import datetime
from time import time
import json


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


class Notification(Base):
    """ Notiication table for keep tracking user notifications """
    __tablename__ = 'Notification'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    timestamp = Column(Float, index=True, default=time)
    payload_json = Column(Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
