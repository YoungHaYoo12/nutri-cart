from flask_script import Manager
from flask_migrate import Migrate
from app import create_app, db

app = create_app('default')
manager = Manager(app)
Migrate(app,db)

@manager.command
def test():
  """Run the Unit Tests"""
  import unittest
  tests = unittest.TestLoader().discover('tests')
  unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
  manager.run()