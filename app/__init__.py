import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .commands import reset_items

def create_app():
  app = Flask(__name__, static_folder='build')

  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

  db.init_app(app)

  from .views import api
  app.register_blueprint(api)

  # Serve React App
  @app.route('/', defaults={'path': ''})
  @app.route('/<path:path>')
  def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
      return send_from_directory(app.static_folder, path)
    else:
      return send_from_directory(app.static_folder, 'index.html')
  
  app.cli.add_command(reset_items)

  return app