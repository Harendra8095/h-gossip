from .meta import Base
from .usermodels import User
from .postsmodels import Post


def createTables(engine):
    # print("Binding")
    print(Base.metadata.tables.keys())
    Base.metadata.bind = engine
    # print("binding done")
    Base.metadata.create_all(engine)


def destroyTables(engine):
    Base.metadata.drop_all(engine)
