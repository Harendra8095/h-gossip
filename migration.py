from flask_migrate import Migrate, MigrateCommand
from hgossipBack.models import Base
from flask_script import Manager
from server import app

migrate = Migrate(app, Base)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
