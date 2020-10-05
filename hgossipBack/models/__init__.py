from .meta import Base
from .usermodels import User
from .postsmodels import Post
from .follower import followers

def createTables(engine):
    print(Base.metadata.tables.keys())
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


def destroyTables(engine):
    Base.metadata.drop_all(engine)
