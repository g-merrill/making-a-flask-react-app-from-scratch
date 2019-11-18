import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
  app = Flask(__name__)

  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

  db.init_app(app)

  from .views import api
  app.register_blueprint(api)

  return app