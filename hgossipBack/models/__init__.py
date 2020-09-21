from .meta import Base
from .usermodels import User

def createTables(engine):
    # print("Binding")
    print(Base.metadata.tables.keys())
    Base.metadata.bind = engine
    # print("binding done")
    Base.metadata.create_all(engine)


def destroyTables(engine):
    Base.metadata.drop_all(engine)