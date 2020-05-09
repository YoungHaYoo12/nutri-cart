import os
from flask_script import Manager
from flask_migrate import Migrate
from app import create_app, db

app = create_app('default')
manager = Manager(app)
Migrate(app,db)

########################
#Coverage SetUp
if os.environ.get('FLASK_COVERAGE'):
  import coverage
  COV = coverage.coverage(branch=True,include='app/*')
  COV.start()
########################

@manager.command
def test(coverage=False):
  """Run the Unit Tests"""
  if coverage and not os.environ.get('FLASK_COVERAGE'):
    import sys 
    os.environ['FLASK_COVERAGE'] = '1'
    os.execvp(sys.executable, [sys.executable] + sys.argv)

  import unittest
  tests = unittest.TestLoader().discover('tests')
  unittest.TextTestRunner(verbosity=2).run(tests)

  if COV:
    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir,'tmp/coverage')
    COV.html_report(directory=covdir)
    print('HTML version: file://%s/index.html'%covdir)
    COV.erase()

if __name__ == '__main__':
  manager.run()