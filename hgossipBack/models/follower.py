from sqlalchemy import Column, Integer, ForeignKey, Table
from .meta import Base

followers =  Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('user.id')),
    Column('followed_id', Integer, ForeignKey('user.id'))
)
