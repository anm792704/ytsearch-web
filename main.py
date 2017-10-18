#!flask/bin/python
from app import app


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = False
  app.run()