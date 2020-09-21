from flask_migrate import Migrate, MigrateCommand
from hgossipBack.models import *
from flask_script import Manager
from server import app

manager = Manager(app)
migrate = Migrate(app, Base)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
