import click
from flask.cli import with_appcontext

from . import db
from .models import Item

@click.command(name='reset_items')
@with_appcontext
def reset_items():
  db.drop_all()
  db.create_all()