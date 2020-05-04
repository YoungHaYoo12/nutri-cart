from flask_script import Manager
from flask_migrate import Migrate
from app import create_app, db

app = create_app('default')
manager = Manager(app)
Migrate(app,db)

if __name__ == '__main__':
  manager.run()