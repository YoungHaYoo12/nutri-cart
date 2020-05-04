from app.core import core 

@core.route('/')
def index():
  return "<h1>Hello Nutri Cart!</h1>"